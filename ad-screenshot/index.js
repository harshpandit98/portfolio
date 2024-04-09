const puppeteer = require('puppeteer');
const crypto = require('crypto')
const FileSystem = require("fs");


function delay(time) {
	return new Promise(function (resolve) {
		setTimeout(resolve, time)
	});
}


function allowedRequest(r) {
	const rsrc_url = r.url()
	const blockedResourceTypes = [
		"image", "font", "object", "texttrack", "imageset", "bacon", "csp_report",
	];
	const blockedUrls = ['popup', 'cloudflare'];
	if (blockedUrls.some(v => v.includes(rsrc_url))) return false;

	const allowedImage = "bannerslider";
	return !blockedResourceTypes.includes(r.resourceType()) ||
		rsrc_url.indexOf(allowedImage) != -1;
}


async function takeElemScreenshot(page, selector, filename) {
	const el = await page.waitForSelector(selector);
	// // scroll to avoid overlay
	await page.mouse.wheel({ deltaY: 100 });
	await delay(2000)
	await el.screenshot({
		path: filename,
		omitBackground: true,
	});
	console.log(`Stored ad screenshot: ${filename}`)
}


(async (filename) => {
	const browser = await puppeteer.launch(
		{
			// headless: false,
			defaultViewport: null,
			args: [
				'--start-maximized',
				'--no-sandbox',
				'--disable-setuid-sandbox',
				'--disable-infobars',
				'--disable-notifications',
				'--disable-dev-shm-usage',
			],
			ignoreDefaultArgs: ['--enable-automation'],
		}
	);

	try {
		const pages = await browser.pages();
		const page = pages[0];
		await page.setUserAgent('Mozilla/5.0 (Windows NT 5.1; rv:5.0) Gecko/20100101 Firefox/5.0')
		await page.setRequestInterception(true);
		page.on('request', req => {
			if (
				allowedRequest(req)
			)
				req.continue();
			else {
				console.log(`Aborted request: ${req.url()}`);
				req.abort();
			}
		});

		const url = 'https://www.pascalcoste-shopping.com/esthetique/fond-de-teint.html'
		await page.goto(url);
		await page.waitForNetworkIdle();

		const consent_el = await page.waitForSelector('.uk-close-cookie', { visible: true });
		await consent_el.click();
		await delay(1000);

		const ad_sel = '.uk-promo-sidebar .uk-active';
		const screenshotFn = `${filename}.png`
		await takeElemScreenshot(page, ad_sel, screenshotFn)

		const imgSel = '.uk-promo-sidebar .uk-active > img';
		const imgUrl = await page.$eval(imgSel, el => el.src);
		const imgHash = crypto.createHash('md5').update(imgUrl).digest('hex')

		const data = {
			"id": imgHash,
			"img_link": imgUrl,
			"image_url": screenshotFn,
			"format": "Left Side Banner",
		}
		const jsonFn = `${filename}_data.json`
		FileSystem.writeFile(jsonFn, JSON.stringify(data), (error) => {
			if (error) {
				console.log('Failed to store the data');
				throw error;
			}
			console.log(`Stored data: ${jsonFn}`);
		});

	} catch (e) {
		console.log(e)
	} finally {
		await browser.close();
	}
})('ad_screenshot');