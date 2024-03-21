import json
import random
import time
from typing import Optional, Union

import requests
from bs4 import BeautifulSoup, Tag
from requests.exceptions import Timeout


class Crawler:
    def __init__(self, start_url: str, output_filename: str) -> None:
        self.start_url = start_url
        self.filename = output_filename
        self.data = []

    def init_crawl(self):
        initial_page_html = self.request_page(self.start_url)
        self.process_page(initial_page_html)
        self.dump(self.filename)

    def dump(self, filename):
        with open(filename, "w") as file:
            json.dump(self.data, file, indent=4)
            print(f"Exported data to {filename}")

    def request_page(self, url: str) -> Union[str, None]:
        cookies = {
            "language": "fr_FR",
            "ledgerCurrency": "EUR",
            "section_data_ids": "%7B%7D",
        }

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Referer": "https://www.pascalcoste-shopping.com/",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Pragma": "no-cache",
            "Cache-Control": "no-cache",
        }
        try:
            response = requests.get(url, cookies=cookies, headers=headers, timeout=40)
            print(f"received response for page: {url}")
            return response.text
        except (Timeout, Exception) as e:
            print(f"Failed request: {url}\n{e}")
        time.sleep(random.uniform(0.3, 1.0))

    @staticmethod
    def prepare_bs_obj(html: str) -> BeautifulSoup:
        return BeautifulSoup(html, features="html.parser")

    @staticmethod
    def get_text(res: Union[Tag, None], attr: str) -> Union[str, None]:
        if isinstance(res, Tag):
            if attr:
                return res.get(attr)
            return res.get_text()

    def parse_selector(
        self, tag: Tag, sel: str, attr: Optional[str] = ""
    ) -> Union[str, None]:
        res = tag.select_one(sel)
        return self.get_text(res, attr)

    @staticmethod
    def transform_price_str(price: str) -> float:
        price_clean = price.replace("€", "").replace(",", ".")
        try:
            return round(float(price_clean), 2)
        except ValueError:
            pass

    def process_page(self, html: str):
        soup = self.prepare_bs_obj(html)
        self.process_listings(soup)
        next_page_url = self.parse_selector(
            tag=soup, sel='link[rel="next"]', attr="href"
        )
        if next_page_url:
            if next_page := self.request_page(next_page_url):
                self.process_page(next_page)

    def process_listings(self, soup):
        listings = soup.select(".products-grid > div")
        for listing in listings:
            price_str = self.parse_selector(tag=listing, sel="span.uk-price")
            price = self.transform_price_str(price_str) if price_str else None
            item = {
                "name": self.parse_selector(tag=listing, sel="h3 > a"),
                "brand": self.parse_selector(tag=listing, sel="div.uk-width-expand"),
                "price": price,
                "image_url": self.parse_selector(
                    tag=listing, sel="img", attr="data-amsrc"
                ),
                "product_url": self.parse_selector(tag=listing, sel="a", attr="href"),
            }
            self.data.append(item)
