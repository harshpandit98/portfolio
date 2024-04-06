from crawler import Crawler
from ingest import put_to_db

if __name__ == "__main__":
    output_filename = "data.json"
    start_url = "https://www.pascalcoste-shopping.com/esthetique/fond-de-teint.html"
    crawler_obj = Crawler(start_url, output_filename)
    crawler_obj.init_crawl()
    put_to_db(filename=output_filename)
