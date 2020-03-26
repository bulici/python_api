"""
=================================================
Author : Bulici
Time : 2020/3/5 18:46 
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
from common.handlereplace import ReplaceData
from common.handlerequests import Requests
from common.handlemylog import log
from common.handledata import Randomdata

@ddt
class TestMainstreaming(unittest.TestCase):
    excel = Excel(os.path.join(DATADIR,"apicases.xlsx"),"mainstreaming")
    cases = excel.read_data()
    request = Requests()
    rd = Randomdata()

    @data(*cases)
    def testmainstreaming(self,case):
        """
        测试开发平台接口测试项目主流程测试用例
        :param case: Excel文档中的用例
        :return:
        """
        #第一步：准备测试数据
        url = conf.get("env", "url") + ReplaceData.replace_data(case["url"])
        method = case["method"]
        expected = eval(case["expected"])
        headers = {}
        #在请求头中动态填入鉴权token值
        if case["interface"] != "login" and case["interface"] != "register" and case["interface"] != "count":
            headers["Authorization"] = ReplaceData.Authorization
        title = case["title"]
        row = case["case_id"] + 1
        #随机生成用户名和邮箱并保存为类属性
        ReplaceData.name = self.rd.name_10()
        ReplaceData.email = self.rd.email()
        case["data"] = ReplaceData.replace_data(case["data"])
        data = eval(case["data"])

        #第二步：发送请求，获取结果
        response = self.request.send(url=url,method=method,headers=headers,params=data,json=data)
        code = response.status_code
        res = response.json()

        # 判断是否是注册接口
        if case["interface"] == "register":
            ReplaceData.login_name = jsonpath.jsonpath(res, "$.username")[0]
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

        #第三步：断言，比对预期结果与实际结果
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

