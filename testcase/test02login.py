"""
=================================================
Author : Bulici
Time : 2020/2/22 18:05 
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

@ddt
class TestLogin(unittest.TestCase):
    excel = Excel(os.path.join(DATADIR,"apicases.xlsx"),'login')
    cases = excel.read_data()
    request = Requests()

    def random_phone(self):
        phone = "150"
        for i in range(0,8):
            n = random.randint(0,9)
            phone += str(n)
        return phone

    @data(*cases)
    def testlogin(self,case):
        """登录单元测试用例"""
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
        except AssertionError as e :
            print("预期结果：{}".format(expected))
            print("实际结果：{}".format(respons.json()))
            self.excel.write_data(row=row,column=8,value="未通过")
            log.error("{}:用例未通过，原因为：{}".format(case["title"],e))
            raise e
        else:
            self.excel.write_data(row=row, column=8, value="通过")
            log.debug("{}:用例通过".format(case["title"]))
