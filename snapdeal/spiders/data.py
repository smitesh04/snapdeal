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
    handle_httpstatus_list = [500]

    def __init__(self, start, end, zipcode):
        self.start = int(start)
        self.end = int(end)
        self.zipcode = zipcode
        if self.zipcode == '560001':
            self.city = 'Banglore'
        elif self.zipcode == '400001':
            self.city = 'Mumbai'
        elif self.zipcode == '110001':
            self.city = 'Delhi'
        elif self.zipcode == '700020':
            self.city = 'Kolkata'
    def start_requests(self):

        qr = f"select * from {obj.pl_table} where status_{self.zipcode}='0' limit {self.start}, {self.end}"
        # qr = f"select * from {obj.pl_table} where id=7 limit {self.start}, {self.end}"
        # qr = f"select * from {obj.pl_table} where url='https://www.snapdeal.com/product/jmall-corded-blender-blue-electric/657855377901' limit {self.start}, {self.end}"
        obj.cur.execute(qr)
        rows = obj.cur.fetchall()
        for row in rows:
            link = row['url']
            hashid = create_md5_hash(link)
            pagesave_dir = rf"C:/Users/Actowiz/Desktop/pagesave/{obj.database}/{today_date}/{self.zipcode}"
            file_name = fr"{pagesave_dir}/{hashid}.html"
            row['hashid'] = hashid
            row['pagesave_dir'] = pagesave_dir
            row['file_name'] = file_name
            if os.path.exists(file_name):
                yield scrapy.Request(url = 'file:///'+file_name, callback=self.parse, cb_kwargs=row, dont_filter=True)
            else:
                yield scrapy.Request(url=link, callback=self.parse, cb_kwargs=row, dont_filter=True)

    def parse(self, response, **kwargs):
        filename = kwargs['file_name']
        pagesave_dir = kwargs['pagesave_dir']

        if not os.path.exists(filename):
            page_write(pagesave_dir, filename, response.text)

        supc = response.xpath("//div[contains(@class, 'buy-button-container')]//div/@supc").get()
        product_id_raw = re.findall('pogId=`.*?`', response.text)[0]

        product_id = product_id_raw.replace('pogId=`', '').replace('`', '').replace(',', '')
        title = response.xpath('//h1[@itemprop="name"]/@title').get()

        images_list = list()
        try:
            images_raw = re.findall('prodattrlistTB hidden.*?]', response.text)[0]
            images_raw2 = re.findall('imgs/.*?.jpg', images_raw)
            images_raw3 = re.findall('imgs/.*?.png', images_raw)

            for img in images_raw2:
                if img not in images_list:
                    images_list.append(img)
            for img in images_raw3:
                if img not in images_list:
                    images_list.append(img)
        except:
            images_list = list()

        if not images_list:
            images_list_path = response.xpath(f'//img[contains(@title,"{title}")]')
            for img in images_list_path:
                image = img.xpath(".//@src").get()
                if image not in images_list:
                    images_list.append(image)

        images = images_list[0]
        print(images)
        images_count = len(images_list)

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
        hashid_delivery = create_md5_hash(str(kwargs['url'])+str(self.zipcode))
        pagesave_dir_delivery = rf"C:/Users/Actowiz/Desktop/pagesave/{obj.database}/{today_date}/{self.zipcode}"
        file_name_delivery = fr"{pagesave_dir_delivery}/{hashid_delivery}.json"
        kwargs['hashid_delivery'] = hashid_delivery
        kwargs['pagesave_dir_delivery'] = pagesave_dir_delivery
        kwargs['file_name_delivery'] = file_name_delivery
        sold_out_check = response.xpath("//div[@class='sold-out-err' and contains(text(),'This product has been sold out')]")
        if sold_out_check:
            mrp_snapdeal = response.xpath('//span[@itemprop="price"]/text()').get()
            if not mrp_snapdeal:
                mrp_snapdeal = 'N/A'
            kwargs['mrp_snapdeal'] = mrp_snapdeal
            yield scrapy.Request(url='file:///'+filename, callback=self.final_parse_soldout, cb_kwargs=kwargs, dont_filter=True)
        else:
            if os.path.exists(file_name_delivery):
                yield scrapy.Request(url='file:///'+file_name_delivery, callback=self.final_parse, cb_kwargs=kwargs, dont_filter=True)
            else:
                yield scrapy.Request(method='POST', url=url, headers=headers(), body=payload, callback=self.final_parse, cb_kwargs=kwargs, dont_filter=True)

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
            delivery_date = datetime.datetime.today() + datetime.timedelta(days=min_delivery_days)
            delivery_charges = jsn[supc]['vendors'][0]['cutOffMessages']['stdCutOffMsg']['deliveryCharges']
            snapdeal_display_price_incl_shipping = int(selling_price) + int(delivery_charges)
            stock = 'True'
        except:
            min_delivery_days = 'N/A'
            stock = 'False'
            delivery_date = 'N/A'
            delivery_charges = 'N/A'
            snapdeal_display_price_incl_shipping = 'N/A'

        seller_ratings = jsn[supc]['vendors'][0]['rating']
        seller_id = jsn[supc]['vendors'][0]['vendorCode']
        seller_display_name = jsn[supc]['vendors'][0]['vendorDisplayName']

        item = SnapdealItem()
        item['seller_id'] = seller_id
        item['category_by_sd_l1'] = category_lvl1
        item['category_by_sd_l2'] = category_lvl2
        item['sd_brand'] = brand
        item['sd_display_price_incl_shipping'] = snapdeal_display_price_incl_shipping
        item['product_url_sd'] = kwargs['url']
        item['pincode'] = self.zipcode
        item['city'] = self.city
        item['sku_id_sd'] = product_id
        item['seller_display_name_sd'] = seller_display_name
        item['product_title_sd'] = title
        item['image_url_sd'] = images
        item['count_of_images_sd'] = images_count
        item['pixel_size_of_the_main_image_sd'] = ''
        item['discount_percent_sd'] = discount_percentage
        item['mrp_sd'] = main_price
        item['display_price_on_pdp_price_after_discount_sd'] = selling_price
        item['in_stock_status_sd'] = stock
        item['delivery_charges_sd'] = delivery_charges
        if not product_rating:
            product_rating = 'N/A'
        item['product_ratings_sd'] = product_rating
        if not product_rating_count:
            product_rating_count = 'N/A'
        item['volume_of_product_rating_sd'] = product_rating_count
        item['seller_rating_sd'] = seller_ratings
        item['delivery_date_sd'] = delivery_date
        item['scrape_date'] = datetime.datetime.today()

        yield item

    def final_parse_soldout(self, response, **kwargs):

        category_lvl1 = kwargs['category_lvl1']
        category_lvl2 = kwargs['category_lvl2']
        brand = kwargs['brand']
        product_id = kwargs['product_id']
        title = kwargs['title']
        images = kwargs['images']
        if '.sdlcdn.' not in images:
            if 'https://n3.sdlcdn.com' not in images and '/imgs/' in images:
                images = 'https://n3.sdlcdn.com' + images
            elif 'https://n3.sdlcdn.com' not in images and 'imgs/' in images:
                images = 'https://n3.sdlcdn.com/' + images
            elif 'https://n3.sdlcdn.com' not in images and '/imgs' not in images:
                images = 'https://n3.sdlcdn.com/imgs' + images



        img_w,img_h = get_image_dimensions(images)
        image_dimension = f'{img_w}x{img_h}'



        images_count = kwargs['images_count']
        mrp_snapdeal = kwargs['mrp_snapdeal']
        stock = 'False'
        product_rating = kwargs['product_rating']
        product_rating_count = kwargs['product_rating_count']

        item = SnapdealItem()
        item['seller_id'] = 'N/A'
        item['category_by_sd_l1'] = category_lvl1
        item['category_by_sd_l2'] = category_lvl2
        item['sd_brand'] = brand
        item['sd_display_price_incl_shipping'] = 'N/A'
        item['product_url_sd'] = kwargs['url']
        item['pincode'] = self.zipcode
        item['city'] = self.city
        item['sku_id_sd'] = product_id
        item['seller_display_name_sd'] = 'N/A'
        item['product_title_sd'] = title
        item['image_url_sd'] = images
        item['count_of_images_sd'] = images_count
        item['pixel_size_of_the_main_image_sd'] = image_dimension
        item['discount_percent_sd'] = 'N/A'
        item['mrp_sd'] = mrp_snapdeal
        item['display_price_on_pdp_price_after_discount_sd'] = 'N/A'
        item['in_stock_status_sd'] = stock
        item['delivery_charges_sd'] = 'N/A'
        if not product_rating:
            product_rating = 'N/A'
        item['product_ratings_sd'] = product_rating
        if not product_rating_count:
            product_rating_count = 'N/A'
        item['volume_of_product_rating_sd'] = product_rating_count
        item['seller_rating_sd'] = 'N/A'
        item['delivery_date_sd'] = 'N/A'
        item['scrape_date'] = datetime.datetime.today()

        yield item


if __name__ == '__main__':
    # try:
    #     zipcode = sys.argv[1]
    #     start = sys.argv[2]
    #     end = sys.argv[3]
    #     ex(f"scrapy crawl data -a zipcode={zipcode} -a start={start} -a end={end}".split())
    # except:
    #     # zipcode = 560001 #Banglore
    #     # zipcode = 400001 #Mumbai
    #     # zipcode = 110001 #Delhi
    #     # zipcode = 700020 #Kolkata
    #
    #     start = 0
    #     end = 100
    #
    #     # for zipcode in [560001, 400001, 110001, 700020]:
    #     for zipcode in [560001]:
    #         ex(f"scrapy crawl data -a zipcode={zipcode} -a start={start} -a end={end}".split())

    start = 0
    end = 100

    # for zipcode in [560001, 400001, 110001, 700020]:
    for zipcode in [560001]:
        ex(f"scrapy crawl data -a zipcode={zipcode} -a start={start} -a end={end}".split())


