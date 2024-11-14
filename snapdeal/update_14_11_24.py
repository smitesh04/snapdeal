from db_config import DbConfig
from common_func import create_md5_hash
from parsel import  Selector
obj = DbConfig()
import re

obj.cur.execute("select * from sd_data_13_11_2024 where id='64'")
rows = obj.cur.fetchall()
for row in rows:
    url = row['product_url_sd']
    hashid = create_md5_hash(url)
    pagesave_dir = rf"C:/Users/Actowiz/Desktop/pagesave/{obj.database}/13_11_2024/560001"
    hashid_delivery = create_md5_hash(url+'560001')
    file_name_delivery = fr"{pagesave_dir}/{hashid_delivery}.json"
    file_name = fr"{pagesave_dir}/{hashid}.html"
    file = open(file_name, 'r')
    response = file.read()
    selector = Selector(response)
    file.close()
    try:
        file = open(file_name_delivery, 'r')
        response_delivery = file.read()
        file.close()
    except:pass
    mrp_snapdeal = selector.xpath('//span[@itemprop="price"]/text()').get()
    mrp_snapdeal = mrp_snapdeal.replace(',', '')
    images_list = list()
    title = selector.xpath('//h1[@itemprop="name"]/@title').get()

    try:
        images_raw = re.findall('prodattrlistTB hidden.*?]', response)[0]
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
        images_list_path = selector.xpath(f'//img[contains(@title,"{title}")]')
        for img in images_list_path:
            image = img.xpath(".//@src").get()
            if image not in images_list:
                images_list.append(image)

    images = images_list[0]
    if ',' in images:
        images_list = images.split(',')
        images = images_list[0]
        images = images.strip()

    seller_ratings = selector.xpath(
        "//div[contains(@class,'sellerInformationInnerContainer')]//span[contains(@class,'overallratingdiv')]/text()").get()
    if not seller_ratings:
        seller_ratings = 0
    else:
        seller_ratings = seller_ratings.replace('(', '').replace(')', '')
    seller_name = selector.xpath("//div[contains(@class,'sellerNameContainer')]//span/text()").get()
    if not seller_name:
        seller_name = 'N/A'
    seller_id_raw = selector.xpath("//div[contains(@class,'sellerNameContainer')]//a/@href").get()
    seller_id = seller_id_raw.split('/')[-1]

    print()




