"""
=================================================
Author : Bulici
Time : 2020/2/22 14:07 
Email : 294666094@qq.com
Motto : Clumsy birds have to start flying early.
=================================================
"""
import unittest
import os
import random
from library.ddt import ddt,data
from common.handleexcel import Excel
from common.handlepath import DATADIR
from common.handleconfig import conf
from common.handlerequests import Requests
from common.handlemylog import log
from common.handelmysql import DB

@ddt
class TestRigster(unittest.TestCase):
    excel = Excel(os.path.join(DATADIR,"apicases.xlsx"),'register')
    cases = excel.read_data()
    request = Requests()
    db = DB()

    def random_phone(self):
        """
        随机生成手机号的方法
        :return:
        """
        while True:
            phone = "155"
            for i in range(0, 8):
                n = random.randint(0, 9)
                phone += str(n)
            sql = "SELECT * FROM futureloan.member WHERE mobile_phone={}".format(phone)
            res_phone = self.db.find_count(sql)
            if res_phone == 0:
                break

        return phone

    @data(*cases)
    def testregister(self,case):
        """注册单元测试用例"""
        #准备测试数据
        url = conf.get("env","url") + case["url"]
        method = case["method"]
        headers = eval(conf.get("env","headers"))
        #随机生成一个手机号
        phone = self.random_phone()
        case["data"] = case["data"].replace("#phone#",phone)
        data = eval(case["data"])
        expected = eval(case["expected"])
        row = case["case_id"] + 1
        #实际结果
        respons = self.request.send(url=url,method=method,headers=headers,json=data)
        #断言：比对预期结果和实际结果
        try:
            self.assertEqual(expected["code"],respons.json()["code"])
            self.assertEqual(expected["msg"],respons.json()["msg"])
            if case["sql_check"]:
                # 注册后用户的手机号状态
                end_mobile_phone = self.db.find_count("SELECT mobile_phone FROM futureloan.member WHERE mobile_phone={}".format(
                    data["mobile_phone"]))
                #对Excel中“sql_check”值为1的用例进行leaveamount断言
                self.assertEqual(1,end_mobile_phone)
        except AssertionError as e :
            print("预期结果：{}".format(expected))
            print("实际结果：{}".format(respons.json()))
            self.excel.write_data(row=row,column=8,value="未通过")
            log.error("{}:用例未通过，原因为：{}".format(case["title"],e))
            raise e
        else:
            self.excel.write_data(row=row, column=8, value="通过")
            log.debug("{}:用例通过".format(case["title"]))


