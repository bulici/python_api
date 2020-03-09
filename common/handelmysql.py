"""
=================================================
Author : Bulici
Time : 2020/2/25 11:25 
Email : 294666094@qq.com
Motto : Clumsy birds have to start flying early.
=================================================
"""
import pymysql
from common.handleconfig import conf

class DB:

    def __init__(self):
        self.conn = pymysql.connect(host=conf.get('mysql','host'),
                               port=conf.getint('mysql','port'),
                               user=conf.get('mysql','name'),
                               password=conf.get('mysql','password'),
                               charset=conf.get('mysql','charset'),
                               cursorclass=pymysql.cursors.DictCursor
                               )
        self.cur = self.conn.cursor()

    def find_one(self,sql):
        #提交事务
        self.conn.commit()
        #执行sql
        self.cur.execute(sql)
        data = self.cur.fetchone()

        return data

    def find_all(self,sql):
        #提交事务
        self.conn.commit()
        #执行sql
        self.cur.execute(sql)
        data = self.cur.fetchall()

        return data

    def find_count(self,sql):
        #提交事务
        self.conn.commit()
        #执行sql
        return self.cur.execute(sql)

# db = DB()
# sql = "SELECT mobile_phone FROM futureloan.member WHERE mobile_phone=15212341234"
# res = db.fetchone(sql)
# print(res)

