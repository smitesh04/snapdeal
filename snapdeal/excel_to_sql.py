import pandas as pd
from db_config import  DbConfig
obj = DbConfig()

df = pd.read_excel(r"C:/Users/Actowiz/Downloads/Snapdeal (5).xlsx")

for row in df.iterrows():
    url = row[1]['Product_Url_sd']
    # pogid = row[1]['PogId']
    url = url.strip()
    try:
        # obj.cur.execute(f"insert into {obj.pl_table} (URL, pogId) values('{url}', '{pogid}')")
        obj.cur.execute(f"insert into {obj.pl_table} (sd_url) values('{url}')")
        obj.con.commit()
    except Exception as e:print(e)





    print()
