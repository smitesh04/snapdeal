
from db_config import  DbConfig
obj = DbConfig()
zipcodes = [560001, 400001, 110001, 700020]
for zipcode in zipcodes:
    obj.cur.execute(f"update {obj.pl_table} set status_{zipcode}='0'")
    obj.con.commit()