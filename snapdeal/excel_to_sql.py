import pandas as pd
from db_config import  DbConfig
obj = DbConfig()

df = pd.read_excel(r"C:/Users/Actowiz/Downloads/Top_Visited_POGs.xlsx")

for row in df.iterrows():
    url = row[1]['URL ']
    pogid = row[1]['pogId']
    url = url.strip()
    try:
        obj.cur.execute(f"insert into pl_13_11_2024 (URL, pogId) values('{url}', '{pogid}')")
        obj.con.commit()
    except Exception as e:print(e)





    print()
