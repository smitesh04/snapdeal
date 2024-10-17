import pandas as pd
from db_config import  DbConfig
obj = DbConfig()

df = pd.read_excel(r"C:/Users/Actowiz/Desktop/Smitesh_Docs/Project/snapdeal/blank_.xlsx")

for row in df.iterrows():
    url = row[1]['Product_Url_snapdeal']
    url = url.strip()
    try:
        obj.cur.execute(f"insert into {obj.pl_table} (url) values('{url}')")
        obj.con.commit()
    except Exception as e:print(e)





    print()
