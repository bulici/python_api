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
from library.ddt import ddt,data
from common.handleexcel import Excel
from common.handlepath import DATADIR
from common.handleconfig import conf
from common.handlerequests import Requests
from common.handlemylog import log
from common.handledata import Randomdata
from common.handlereplace import ReplaceData

@ddt
class TestLogin(unittest.TestCase):
    excel = Excel(os.path.join(DATADIR,"apicases.xlsx"),'login')
    cases = excel.read_data()
    request = Requests()
    rd = Randomdata()

    @data(*cases)
    def testlogin(self,case):
        """登录单元测试用例"""
        #准备测试数据
        url = conf.get("env","url") + case["url"]
        method = case["method"]
        # 随机生成用户名并保存为类属性
        ReplaceData.name = self.rd.name_10()
        case["data"] = ReplaceData.replace_data(case["data"])
        data = eval(case["data"])
        expected = eval(case["expected"])
        row = case["case_id"] + 1
        #实际结果
        respons = self.request.send(url=url,method=method,json=data)
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
