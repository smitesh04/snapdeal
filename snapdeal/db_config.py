import pymysql

class DbConfig():


    def __init__(self):
        self.database = 'snapdeal'
        self.con = pymysql.Connect(host='localhost',
                              user='root',
                              password='actowiz',
                              database= self.database)
        self.cur = self.con.cursor(pymysql.cursors.DictCursor)
        self.data_table = 'data'
        self.pl_table = 'pl'


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


        except Exception as e:
            print(e)

    def update_pl_status(self, link):
        try:
            self.cur.execute(f"update {self.pl_table} set status='1' where url='{link}'")
            self.con.commit()
        except Exception as e:print(e)


