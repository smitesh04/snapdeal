import datetime

import pymysql

dd_mm_YYYY = datetime.datetime.today().strftime('%d_%m_%Y')
YYYYmmdd = datetime.datetime.today().strftime('%Y%m%d')


class DbConfig():

    def __init__(self):
        self.database = 'sd_meesho_master'
        # self.database = 'snapdeal'
        self.con = pymysql.Connect(host='172.27.131.60',
        # self.con = pymysql.Connect(host='localhost',
                              user='root',
                              password='actowiz',
                              database= self.database)
        self.cur = self.con.cursor(pymysql.cursors.DictCursor)
        self.data_table = f'sd_data_{YYYYmmdd}'
        # self.data_table = f'sd_data_{YYYYmmdd}_2'
        self.pl_table = f'sd_product_links_{YYYYmmdd}'
        # self.pl_table = f'sd_product_links_{YYYYmmdd}_2'

    def check_table_exists(self, table_name):
        query = f"SHOW TABLES LIKE '{table_name}';"
        self.cur.execute(query)
        return self.cur.fetchone() is not None

    def create_data_table(self, data_table):
        if not self.check_table_exists(data_table):
            query = f'''
                   CREATE TABLE if not exists `{data_table}` (
                  `id` int NOT NULL AUTO_INCREMENT,
                  `seller_id` varchar(255) DEFAULT NULL,
                  `category_by_SD_l1` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
                  `category_by_SD_l2` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
                  `SD_brand` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
                  `SD_display_price_incl_shipping` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
                  `product_url_SD` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
                  `pincode` varchar(255) DEFAULT NULL,
                  `city` varchar(255) DEFAULT NULL,
                  `sku_id_SD` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
                  `seller_display_name_SD` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
                  `product_title_SD` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
                  `image_url_SD` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
                  `count_of_images_SD` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
                  `pixel_size_of_the_main_image_SD` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
                  `discount_percent_SD` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
                  `mrp_SD` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
                  `display_price_on_pdp_price_after_discount_SD` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
                  `in_stock_status_SD` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
                  `delivery_charges_SD` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
                  `product_ratings_SD` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
                  `volume_of_product_rating_SD` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
                  `seller_rating_SD` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
                  `delivery_date_SD` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
                  `scraped_date` varchar(255) DEFAULT NULL,
                  `No_Delivery_Days_from_Scrape_Date_SD` varchar(255) DEFAULT NULL,
                   PRIMARY KEY (`id`)
                )
                '''

            self.cur.execute(query)
            self.con.commit()
            print(f'Table {data_table} has been created! ')


    def insert_data(self, item):
        field_list = []
        value_list = []
        for field in item:
            field_list.append(str(field))
            value_list.append('%s')
        fields = ','.join(field_list)
        values = ", ".join(value_list)
        insert_db = f"insert into {self.data_table}( " + fields + " ) values ( " + values + " )"

        try:
            self.cur.execute(insert_db, tuple(item.values()))
            self.con.commit()
            self.update_pl_status(item['product_url_sd'], item['pincode'])
        except Exception as e:
            print(e)

    def update_pl_status(self, link, zipcode):
        try:
            self.cur.execute(f"update {self.pl_table} set status_{zipcode}='done' where sd_url='{link}'")
            self.con.commit()
        except Exception as e:print(e)

DbConfig().create_data_table(DbConfig().data_table)

