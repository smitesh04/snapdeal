import pandas as pd
from db_config import  DbConfig
obj = DbConfig()

df = pd.read_excel(r"C:/Users/Actowiz/Downloads/updated_SD.xlsx")

for row in df.iterrows():
    url = row[1]['URL']
    pogid = row[1]['PogId']
    url = url.strip()
    try:
        obj.cur.execute(f"insert into pl_25_11_2024 (URL, pogId) values('{url}', '{pogid}')")
        obj.con.commit()
    except Exception as e:print(e)





    print()
