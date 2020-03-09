"""
=================================================
Author : Bulici
Time : 2020/2/27 10:39 
Email : 294666094@qq.com
Motto : Clumsy birds have to start flying early.
=================================================
"""
import unittest
import os
import jsonpath
from decimal import Decimal
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
class TestWithdraw(unittest.TestCase):
    excel = Excel(os.path.join(DATADIR,"apicases.xlsx"),"withdraw")
    cases = excel.read_data()
    request = Requests()
    db = DB()

    @data(*cases)
    def testwithdraw(self,case):
        #准备测试数据，对登录接口用例替换相应的测试手机号、密码
        url = conf.get("env", "url") + case["url"]
        method = case["method"]
        headers = eval(conf.get("env", "headers"))
        expected = eval(case["expected"])
        row = case["case_id"] + 1
        title = case["title"]
        case["data"] = ReplaceData.replace_data(case["data"])
        data = eval(case["data"])
        # 判断是否是取现接口，取现接口则加上请求头，替换相应的用户id，添加时间戳和签名到json请求体
        if case["interface"] == "withdraw":
            headers["Authorization"] = ReplaceData.Authorization
            sign = HandleSign.generate_sign(ReplaceData.token)
            data.update(sign)

        # 判断是否需要进行sql校验
        if case["sql_check"]:
            #查询充值前用户的可用余额
            start_leave_amount = self.db.find_one(case["sql_check"].format(conf.get("test_data","phone")))["leave_amount"]
        #发送请求，获取实际结果
        respons = self.request.send(url=url,method=method,headers=headers,json=data)
        res = respons.json()
        # 判断是否是登录接口
        if case["interface"] == "login":
            # 提取token,保存为类属性
            ReplaceData.token = jsonpath.jsonpath(res, "$..token")[0]
            token_type = jsonpath.jsonpath(res, "$..token_type")[0]
            ReplaceData.Authorization = token_type + " " + ReplaceData.token
            # 提取用户id保存为类属性
            ReplaceData.member_id = str(jsonpath.jsonpath(res,"$..id")[0])
        #断言，比对结果
        try:
            self.assertEqual(expected["code"],res["code"])
            self.assertEqual(expected["msg"],res["msg"])
            if case["sql_check"]:
                end_leave_amount = self.db.find_one(case["sql_check"].format(conf.get("test_data","phone")))["leave_amount"]
                self.assertEqual(Decimal(str(data["amount"])),start_leave_amount-end_leave_amount)
        except AssertionError as e :
            print("预期结果：{}".format(expected))
            print("实际结果：{}".format(res))
            self.excel.write_data(row=row,column=8,value="未通过")
            log.error("用例未通过：{}，错误原因：{}".format(title,e))
            raise e
        else:
            self.excel.write_data(row=row, column=8, value="通过")
            log.debug("用例通过：{}".format(title))

