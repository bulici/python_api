"""
=================================================
Author : Bulici
Time : 2020/2/27 16:33 
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
class TestTestcases(unittest.TestCase):

    excel = Excel(os.path.join(DATADIR,"apicases.xlsx"),"testcases")
    cases = excel.read_data()
    request = Requests()
    rd = Randomdata()

    @data(*cases)
    def testtestcases(self,case):
        """添加用例单元测试用例"""
        #准备测试数据，对登录接口用例替换相应的用户名、密码
        url = conf.get("env", "url") + case["url"]
        method = case["method"]
        headers = {}
        #在请求头中动态填入鉴权token值
        if case["interface"] != "login":
            headers["Authorization"] = ReplaceData.Authorization
        expected = eval(case["expected"])
        row = case["case_id"] + 1
        title = case["title"]
        # 随机生成用户名并保存为类属性
        ReplaceData.name = self.rd.name_10()
        ReplaceData.name_50 = self.rd.name_50()
        case["data"] = ReplaceData.replace_data(case["data"])
        data = eval(case["data"])

        #发送请求，获取实际结果
        respons = self.request.send(url=url,method=method,headers=headers,json=data)
        code = respons.status_code
        res = respons.json()

        # 判断是否是登录接口
        if case["interface"] == "login":
            token = jsonpath.jsonpath(res, "$.token")[0]
            ReplaceData.Authorization = "JWT " + token
        # 判断是否是创建项目接口
        if case["interface"] == "projects":
            # 项目id，并保存为类属性
            ReplaceData.p_id = str(jsonpath.jsonpath(res, "$.id")[0])
        # 判断是否是添加接口的接口
        if case["interface"] == "interfaces":
            # 项目id，并保存为类属性
            ReplaceData.i_id = str(jsonpath.jsonpath(res, "$.id")[0])

        #断言:比对预期结果和实际结果
        try:
            self.assertEqual(expected["code"],code)
        except AssertionError as e :
            print("预期结果：{}".format(expected))
            print("实际结果：'code':{},{}".format(code,res))
            self.excel.write_data(row=row,column=8,value="未通过")
            log.error("用例未通过：{}，错误原因：{}".format(title,e))
            raise e
        else:
            self.excel.write_data(row=row, column=8, value="通过")
            log.debug("用例通过：{}".format(title))




