"""
=================================================
Author : Bulici
Time : 2020/3/11 22:48 
Email : 294666094@qq.com
Motto : Clumsy birds have to start flying early.
=================================================
"""
import unittest
import os
from library.ddt import ddt,data
from common.handleexcel import Excel
from common.handlepath import DATADIR
from common.handleconfig import conf
from common.handlerequests import Requests
from common.handlemylog import log
from common.handlereplace import ReplaceData
from common.handledata import Randomdata

@ddt
class TestCount(unittest.TestCase):
    excel = Excel(os.path.join(DATADIR,"apicases.xlsx"),'count')
    cases = excel.read_data()
    request = Requests()
    rd = Randomdata()

    @data(*cases)
    def testcount(self,case):
        """查询（用户名/邮箱）单元测试用例"""
        #准备测试数据
        method = case["method"]
        #随机生成用户名和邮箱并保存为类属性
        ReplaceData.name = self.rd.name_10()
        ReplaceData.email = self.rd.email()
        data = eval(case["data"])
        url = conf.get("env", "url") + ReplaceData.replace_data(case["url"])
        expected = eval(case["expected"])
        row = case["case_id"] + 1
        #实际结果
        respons = self.request.send(url=url,method=method,params=data)
        code = respons.status_code
        #断言：比对预期结果和实际结果
        try:
            self.assertEqual(expected["code"],code)
        except AssertionError as e :
            print("预期结果：{}".format(expected))
            print("实际结果：'code':{},{}".format(code,respons.json()))
            self.excel.write_data(row=row,column=8,value="未通过")
            log.error("{}:用例未通过，原因为：{}".format(case["title"],e))
            raise e
        else:
            self.excel.write_data(row=row, column=8, value="通过")
            log.debug("{}:用例通过".format(case["title"]))