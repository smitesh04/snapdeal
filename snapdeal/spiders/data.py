import scrapy


class DataSpider(scrapy.Spider):
    name = "data"
    allowed_domains = ["."]
    start_urls = ["https://."]

    def parse(self, response):
        pass
