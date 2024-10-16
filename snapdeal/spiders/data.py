import json
import re
from typing import Iterable
from snapdeal.image_dimensions import get_image_dimensions
import scrapy
from scrapy import Request
from snapdeal.common_func import headers
from scrapy.cmdline import execute as ex



class DataSpider(scrapy.Spider):
    name = "data"
    # handle_httpstatus_list = [415]
    # allowed_domains = ["."]
    # start_urls = ["https://."]
    def start_requests(self):
        url = 'https://www.snapdeal.com/product/rangita-black-banarasi-silk-saree/6917529710856049263'
        yield scrapy.Request(url, callback=self.parse)

    def parse(self, response, **kwargs):

        supc_raw = re.findall('supc=`.*?`', response.text)[0]
        supc = supc_raw.replace('supc=`', '').replace('`', '')
        product_info = response.xpath('//div[@id="attributesJson"]/text()').get()
        product_info_jsn = json.loads(product_info)
        images_list = list()

        for product_inf in product_info_jsn:
            product_supc = product_inf['supc']
            if product_supc == supc:
                images_raw = product_inf['images']
                for image in images_raw:
                    image = f'https://n2.sdlcdn.com/{image}'
                    images_list.append(image)

        images = ' | '.join(images_list)

        manufacturer_raw = response.xpath('''//td[contains(text(),"Manufacturer's Name & Address")]/following-sibling::td/text()''').get()
        manufacturer = manufacturer_raw.split(',')[0]

        url = "https://www.snapdeal.com/acors/web/getServicablity/v2/1"
        payload = json.dumps([
            {
                "supc": supc,
                "pincode": "400001",
                "isAutomobile": False,
                "vendorCode": None,
                "exchangeApplied": False,
                "make2Order": False
            }
        ])

        yield scrapy.Request(method='POST', url=url, headers=headers(), body=payload, callback=self.final_parse)


    def final_parse(self, response, **kwargs):

        jsn = json.loads(response.text)
        selling_price = jsn[supc]['vendors'][0]['sellingPrice']
        main_price = jsn[supc]['vendors'][0]['price']
        discount_percentage = jsn[supc]['vendors'][0]['effectivePercentOff']
        min_delivery_days = jsn[supc]['vendors'][0]['otoDRange']['min']
        max_delivery_days = jsn[supc]['vendors'][0]['otoDRange']['max']


        print()

if __name__ == '__main__':
    ex("scrapy crawl data".split())
