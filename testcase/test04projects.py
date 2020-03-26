"""
=================================================
Author : Bulici
Time : 2020/2/22 18:18 
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
from common.handlereplace import ReplaceData
from common.handledata import Randomdata

@ddt
class TestProjects(unittest.TestCase):
    excel = Excel(os.path.join(DATADIR,"apicases.xlsx"),"projects")
    cases = excel.read_data()
    request = Requests()
    rd = Randomdata()

    @data(*cases)
    def testprojects(self,case):
        """创建项目单元测试用例"""
        #准备测试数据
        url = conf.get("env","url") + case["url"]
        method = case["method"]
        expected = eval(case["expected"])
        row = case["case_id"] + 1

        # 随机生成用户名并保存为类属性
        ReplaceData.name = self.rd.name_10()
        ReplaceData.name_200 = self.rd.name_200()
        case["data"] = ReplaceData.replace_data(case["data"])
        data = eval(case["data"])
        headers = {}
        #在请求头中动态填入鉴权token值
        if case["interface"] == "projects":
            headers["Authorization"] = ReplaceData.Authorization
        #实际结果
        respons = self.request.send(url=url,method=method,headers=headers,json=data)
        code = respons.status_code

        if case["interface"] == "login":
            token = jsonpath.jsonpath(respons.json(),"$.token")[0]
            ReplaceData.Authorization = "JWT " + token

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

