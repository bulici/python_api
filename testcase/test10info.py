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
from decimal import Decimal
from common.handle_sign import HandleSign

@ddt
class TestInfo(unittest.TestCase):

    excel = Excel(os.path.join(DATADIR,"apicases.xlsx"),"info")
    cases = excel.read_data()
    request = Requests()
    db = DB()

    @data(*cases)
    def testinfo(self,case):
        #准备测试数据，替换用例中相应的手机号、密码、用户id、项目id
        method = case["method"]
        headers = eval(conf.get("env", "headers"))
        expected = eval(case["expected"])
        row = case["case_id"] + 1
        title = case["title"]
        case["data"] = ReplaceData.replace_data(case["data"])
        data = eval(case["data"])
        # 判断是否是用户信息接口，用户信息接口则加上请求头
        if case["interface"] == "info":
            headers["Authorization"] = ReplaceData.Authorization
            # 添加时间戳和签名到json请求体
            sign = HandleSign.generate_sign(ReplaceData.token)
            data.update(sign)
            case["url"] = ReplaceData.replace_data(case["url"])

        url = conf.get("env", "url") + case["url"]

        #发送请求，获取实际结果
        respons = self.request.send(url=url,method=method,headers=headers,json=data)
        res = respons.json()

        #获取用户id和token值，并保存为类属性
        if case["interface"] == "login":
            ReplaceData.token = jsonpath.jsonpath(res, "$..token")[0]
            ReplaceData.member_id = str(jsonpath.jsonpath(res, "$..id")[0])
            ReplaceData.Authorization = jsonpath.jsonpath(res, "$..token_type")[0] +" " + jsonpath.jsonpath(res, "$..token")[0]

        #断言:比对预期结果和实际结果
        try:
            self.assertEqual(expected["code"],res["code"])
            self.assertIn(expected["msg"],res["msg"])
            #判断是否需要SQL校验
            if case["sql_check"]:
                #获取执行结果的用户可用余额
                info = jsonpath.jsonpath(res, "$..leave_amount")[0]
                # 获取预期结果的用户可用余额
                user_info = self.db.find_one(case["sql_check"].format(ReplaceData.member_id))["leave_amount"]
                self.assertEqual(user_info,Decimal(str(info)))
        except AssertionError as e :
            print("预期结果：{}".format(expected))
            print("实际结果：{}".format(res))
            self.excel.write_data(row=row,column=8,value="未通过")
            log.error("用例未通过：{}，错误原因：{}".format(title,e))
            raise e
        else:
            self.excel.write_data(row=row, column=8, value="通过")
            log.debug("用例通过：{}".format(title))