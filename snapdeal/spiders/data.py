import datetime
import json
import os.path
import re
import sys
from typing import Iterable
from snapdeal.image_dimensions import get_image_dimensions
import scrapy
from scrapy import Request
from snapdeal.common_func import headers, create_md5_hash, page_write, today_date
from scrapy.cmdline import execute as ex
from snapdeal.db_config import DbConfig
from snapdeal.items import SnapdealItem

obj = DbConfig()


class DataSpider(scrapy.Spider):
    name = "data"
    # handle_httpstatus_list = [415]

    def __init__(self, start, end, zipcode, city):
        self.start = int(start)
        self.end = int(end)
        self.zipcode = zipcode
        self.city = city

    def start_requests(self):
        # zipcodes = ['560001', '400001', '110001', '700020']

        qr = f"select * from {obj.pl_table} where status='0' limit {self.start}, {self.end}"
        obj.cur.execute(qr)
        rows = obj.cur.fetchall()
        for row in rows:
            # link = 'https://www.snapdeal.com/product/rangita-black-banarasi-silk-saree/6917529710856049263'
            link = row['url']
            hashid = create_md5_hash(link)
            pagesave_dir = rf"C:/Users/Actowiz/Desktop/pagesave/{obj.database}/{today_date}"
            file_name = fr"{pagesave_dir}/{hashid}.html"
            row['hashid'] = hashid
            row['pagesave_dir'] = pagesave_dir
            row['file_name'] = file_name
            if os.path.exists(file_name):
                yield scrapy.Request(url = 'file:///'+file_name, callback=self.parse, cb_kwargs=row)
            else:
                yield scrapy.Request(link, callback=self.parse, cb_kwargs=row)

    def parse(self, response, **kwargs):
        filename = kwargs['file_name']
        pagesave_dir = kwargs['pagesave_dir']

        if not os.path.exists(filename):
            page_write(pagesave_dir, filename, response.text)


        # supc_raw = re.findall('supc=`.*?`', response.text)[0]
        # supc = supc_raw.replace('supc=`', '').replace('`', '')

        supc = response.xpath("//div[contains(@class, 'buy-button-container')]//div/@supc").get()

        product_info = response.xpath('//div[@id="attributesJson"]/text()').get()
        product_info_jsn = json.loads(product_info)

        product_id_raw = re.findall('"pogId": ".*?,', response.text)[0]
        product_id = product_id_raw.replace('"pogId": "', '').replace('"', '').replace(',', '')
        title = response.xpath('//h1[@itemprop="name"]/@title').get()


        images_list_path = response.xpath(f'''//a//img[contains(@title,"{title}")]''')
        images_list = list()
        for img in images_list_path:
            image = img.xpath(".//@src").get()
            images_list.append(image)
        # images_list = list()

        # for product_inf in product_info_jsn:
        #     product_supc = product_inf['supc']
        #     if product_supc == supc:
        #         images_raw = product_inf['images']
        #         for image in images_raw:
        #             image = f'https://n2.sdlcdn.com/{image}'
        #             images_list.append(image)

        # images = ' | '.join(images_list)
        images = images_list[0]
        images_count = len(images_list)

        manufacturer_raw = response.xpath('''//td[contains(text(),"Manufacturer's Name & Address")]/following-sibling::td/text()''').get()
        manufacturer = manufacturer_raw.split(',')[0]

        seller_name = response.xpath("//div[contains(@class,'sellerNameContainer')]//span[@itemprop='name']/text()").get()

        breadcrumbs_list = response.xpath('//div[@id="breadCrumbWrapper"]//a/@label').getall()
        category_lvl1 = breadcrumbs_list[0]

        brand = response.xpath('//input[@id="brandName"]/@value').get()




        try:category_lvl2 = breadcrumbs_list[1]
        except:category_lvl2 = ''

        product_rating = response.xpath('//span[@itemprop="ratingValue"]/text()').get()
        product_rating_count = response.xpath('//span[@itemprop="ratingCount"]/text()').get()

        kwargs['supc'] = supc
        kwargs['category_lvl1'] = category_lvl1
        kwargs['category_lvl2'] = category_lvl2
        kwargs['title'] = title
        kwargs['brand'] = brand
        kwargs['product_id'] = product_id
        kwargs['images'] = images
        kwargs['images_count'] = images_count
        kwargs['product_rating'] = product_rating
        kwargs['product_rating_count'] = product_rating_count




        url = "https://www.snapdeal.com/acors/web/getServicablity/v2/1"
        payload = json.dumps([
            {
                "supc": supc,
                "pincode": self.zipcode,
                "isAutomobile": False,
                "vendorCode": None,
                "exchangeApplied": False,
                "make2Order": False
            }
        ])
        hashid_delivery = create_md5_hash(url+str(self.zipcode))
        pagesave_dir_delivery = rf"C:/Users/Actowiz/Desktop/pagesave/{obj.database}/{today_date}"
        file_name_delivery = fr"{pagesave_dir_delivery}/{hashid_delivery}.json"
        kwargs['hashid_delivery'] = hashid_delivery
        kwargs['pagesave_dir_delivery'] = pagesave_dir_delivery
        kwargs['file_name_delivery'] = file_name_delivery
        if os.path.exists(file_name_delivery):
            yield scrapy.Request(url='file:///'+file_name_delivery, callback=self.final_parse, cb_kwargs=kwargs)
        else:
            yield scrapy.Request(method='POST', url=url, headers=headers(), body=payload, callback=self.final_parse, cb_kwargs=kwargs)


    def final_parse(self, response, **kwargs):
        pagesave_dir_delivery = kwargs['pagesave_dir_delivery']
        file_name_delivery = kwargs['file_name_delivery']
        category_lvl1 = kwargs['category_lvl1']
        category_lvl2 = kwargs['category_lvl2']
        brand = kwargs['brand']
        product_id = kwargs['product_id']
        title = kwargs['title']
        images = kwargs['images']
        images_count = kwargs['images_count']
        product_rating = kwargs['product_rating']
        product_rating_count = kwargs['product_rating_count']

        if not os.path.exists(file_name_delivery):
            page_write(pagesave_dir_delivery, file_name_delivery, response.text)

        supc = kwargs['supc']
        jsn = json.loads(response.text)
        selling_price = jsn[supc]['vendors'][0]['sellingPrice']
        main_price = jsn[supc]['vendors'][0]['price']
        discount_percentage = jsn[supc]['vendors'][0]['effectivePercentOff']
        try:
            min_delivery_days = jsn[supc]['vendors'][0]['otoDRange']['min']
            max_delivery_days = jsn[supc]['vendors'][0]['otoDRange']['max']
        except:
            min_delivery_days =
        seller_ratings = jsn[supc]['vendors'][0]['rating']
        seller_id = jsn[supc]['vendors'][0]['vendorCode']
        seller_display_name = jsn[supc]['vendors'][0]['vendorDisplayName']

        delivery_date = datetime.datetime.today() + datetime.timedelta(days=min_delivery_days)

        stock = 'True'
        delivery_charges = jsn[supc]['vendors'][0]['cutOffMessages']['stdCutOffMsg']['deliveryCharges']

        snapdeal_display_price_incl_shipping = int(selling_price) + int(delivery_charges)

        item = SnapdealItem()
        item['seller_id'] = seller_id
        item['category_by_snapdeal_l1'] = category_lvl1
        item['category_by_snapdeal_l2'] = category_lvl2
        item['snapdeal_brand'] = brand
        item['snapdeal_display_price_incl_shipping'] = snapdeal_display_price_incl_shipping
        item['product_url_snapdeal'] = kwargs['url']
        item['pincode'] = self.zipcode
        item['city'] = self.city
        item['sku_id_snapdeal'] = product_id
        item['seller_display_name_snapdeal'] = seller_display_name
        item['product_title_snapdeal'] = title
        item['image_url_snapdeal'] = images
        item['count_of_images_snapdeal'] = images_count
        item['pixel_size_of_the_main_image_snapdeal'] = ''
        item['discount_percent_snapdeal'] = discount_percentage
        item['mrp_snapdeal'] = main_price
        item['display_price_on_pdp_price_after_discount_snapdeal'] = selling_price
        item['in_stock_status_snapdeal'] = stock
        item['delivery_charges_snapdeal'] = delivery_charges
        item['product_ratings_snapdeal'] = product_rating
        item['volume_of_product_rating_snapdeal'] = product_rating_count
        item['seller_rating_snapdeal'] = seller_ratings
        item['delivery_date_snapdeal'] = delivery_date
        item['pagesave_main'] = kwargs['filename']
        item['pagesave_delivery'] = file_name_delivery

        yield item




if __name__ == '__main__':
    try:
        zipcode = sys.argv[1]
        city = sys.argv[2]
        start = sys.argv[3]
        end = sys.argv[4]
    except:
        zipcode = '560001'
        city = 'Banglore'
        start = 0
        end = 1

    ex(f"scrapy crawl data -a zipcode='{zipcode}' -a city='{city}' -a start={start} -a end={end}".split())
