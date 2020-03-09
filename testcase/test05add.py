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
from common.handelmysql import DB
from common.handlereplace import ReplaceData
from common.handle_sign import HandleSign

@ddt
class TestAdd(unittest.TestCase):

    excel = Excel(os.path.join(DATADIR,"apicases.xlsx"),"add")
    cases = excel.read_data()
    request = Requests()
    db = DB()

    @data(*cases)
    def testadd(self,case):
        #准备测试数据，对登录接口用例替换相应的手机号、密码
        url = conf.get("env", "url") + case["url"]
        method = case["method"]
        headers = eval(conf.get("env", "headers"))
        expected = eval(case["expected"])
        row = case["case_id"] + 1
        title = case["title"]
        case["data"] = ReplaceData.replace_data(case["data"])
        data = eval(case["data"])
        # 判断是否是添加项目接口，添加项目接口则加上请求头，替换相应的用户id
        if case["interface"] == "add":
            headers["Authorization"] = ReplaceData.Authorization
            #添加时间戳和签名到json请求体
            sign = HandleSign.generate_sign(ReplaceData.token)
            data.update(sign)
            #判断是否需要sql校验
            if case["sql_check"]:
                # 查询执行用例前当前用户添加的项目总数
                start_loan = self.db.find_count(case["sql_check"].format(ReplaceData.member_id))

        #发送请求，获取实际结果
        respons = self.request.send(url=url,method=method,headers=headers,json=data)
        res = respons.json()

        # 判断是否是登录接口
        if case["interface"] == "login":
            # 提取token,保存为类属性
            ReplaceData.token = jsonpath.jsonpath(res,"$..token")[0]
            token_type = jsonpath.jsonpath(res, "$..token_type")[0]
            ReplaceData.Authorization = token_type + " " + ReplaceData.token
            # 提取用户id保存为类属性
            ReplaceData.member_id = str(jsonpath.jsonpath(res, "$..id")[0])

        #断言:比对预期结果和实际结果
        try:
            self.assertEqual(expected["code"],res["code"])
            self.assertEqual(expected["msg"],res["msg"])
            if case["sql_check"]:
                # 查询用例执行后当前用户添加的项目总数
                end_loan = self.db.find_count(case["sql_check"].format(ReplaceData.member_id))
                self.assertEqual(1,end_loan-start_loan)
        except AssertionError as e :
            print("预期结果：{}".format(expected))
            print("实际结果：{}".format(res))
            self.excel.write_data(row=row,column=8,value="未通过")
            log.error("用例未通过：{}，错误原因：{}".format(title,e))
            raise e
        else:
            self.excel.write_data(row=row, column=8, value="通过")
            log.debug("用例通过：{}".format(title))




