from db_config import  DbConfig
obj = DbConfig()

obj.cur.execute(f"select * from {obj.data_table}")
rows = obj.cur.fetchall()
for row in rows:
    link = row['product_url_sd']
    sku = row['sku_id_sd']
    if sku not in link:
        print(str(row['id']) +' '+link)