"""
=================================================
Author : Bulici
Time : 2020/3/1 11:53 
Email : 294666094@qq.com
Motto : Clumsy birds have to start flying early.
=================================================
"""
import unittest
import os
import jsonpath
from library.ddt import ddt,data
from common.handleexcel import Excel
from common.handlepath import DATADIR
from common.handleconfig import conf
from common.handlerequests import Requests
from common.handlemylog import log
from common.handelmysql import DB
from common.handlereplace import ReplaceData

@ddt
class TestLoans(unittest.TestCase):

    excel = Excel(os.path.join(DATADIR,"apicases.xlsx"),"loans")
    cases = excel.read_data()
    request = Requests()
    db = DB()

    @data(*cases)
    def testloans(self,case):
        #准备测试数据，替换用例中相应的手机号、密码、用户id、项目id
        url = conf.get("env", "url") + case["url"]
        method = case["method"]
        headers = eval(conf.get("env", "headers"))
        expected = eval(case["expected"])
        row = case["case_id"] + 1
        title = case["title"]
        case["data"] = ReplaceData.replace_data(case["data"])
        data = eval(case["data"])

        #发送请求，获取实际结果
        respons = self.request.send(url=url, method=method, headers=headers, params=data,json=data)
        res = respons.json()

        #断言:比对预期结果和实际结果
        try:
            self.assertEqual(expected["code"],res["code"])
            self.assertIn(expected["msg"],res["msg"])
        except AssertionError as e :
            print("预期结果：{}".format(expected))
            print("实际结果：{}".format(res))
            self.excel.write_data(row=row,column=8,value="未通过")
            log.error("用例未通过：{}，错误原因：{}".format(title,e))
            raise e
        else:
            self.excel.write_data(row=row, column=8, value="通过")
            log.debug("用例通过：{}".format(title))