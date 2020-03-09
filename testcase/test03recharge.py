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
class TestRecharge(unittest.TestCase):
    excel = Excel(os.path.join(DATADIR,"apicases.xlsx"),"recharge")
    cases = excel.read_data()
    request = Requests()
    db = DB()

    @classmethod
    def setUpClass(cls):
        login_url = conf.get("env", "url") + "/member/login"
        login_data = {"mobile_phone": conf.get("test_data","phone"), "pwd": conf.get("test_data","pwd")}
        headers = eval(conf.get("env", "headers"))
        res = cls.request.send(url=login_url, method="post",json=login_data, headers=headers)
        # 提取鉴权token值，并保存为类属性
        ReplaceData.token = jsonpath.jsonpath(res.json(), "$..token")[0]
        ReplaceData.Authorization = jsonpath.jsonpath(res.json(), "$..token_type")[0] + " " + jsonpath.jsonpath(res.json(), "$..token")[0]
        #提取用户id，并保存为类属性
        ReplaceData.member_id = str(jsonpath.jsonpath(res.json(),"$..id")[0])


    @data(*cases)
    def testrecharge(self,case):
        """充值单元测试用例"""
        #准备测试数据
        url = conf.get("env","url") + case["url"]
        method = case["method"]
        expected = eval(case["expected"])
        row = case["case_id"] + 1
        #在请求头中动态填入鉴权token值
        headers = eval(conf.get("env","headers"))
        headers["Authorization"] = getattr(ReplaceData,"Authorization")
        #动态填入用户id
        case["data"] = ReplaceData.replace_data(case["data"])
        data = eval(case["data"])
        #添加时间戳和签名到json请求体
        sign = HandleSign.generate_sign(ReplaceData.token)
        data.update(sign)

        #获取充值前的可用余额
        start_amount = self.db.find_one("SELECT leave_amount FROM futureloan.member WHERE mobile_phone={}".format(
            conf.get('test_data','phone')))["leave_amount"]
        #实际结果
        respons = self.request.send(url=url,method=method,headers=headers,json=data)

        #断言：比对预期结果和实际结果
        try:
            self.assertEqual(expected["code"],respons.json()["code"])
            self.assertEqual(expected["msg"],respons.json()["msg"])
            if case["sql_check"]:
                # 获取充值完成后的可用余额
                end_amount = self.db.find_one("SELECT leave_amount FROM futureloan.member WHERE mobile_phone={}".format(
                    conf.get('test_data', 'phone')))["leave_amount"]
                #对Excel中“sql_check”值为1的用例进行leaveamount断言
                self.assertEqual(Decimal(str(data["amount"])),end_amount-start_amount)
        except AssertionError as e :
            print("预期结果：{}".format(expected))
            print("实际结果：{}".format(respons.json()))
            self.excel.write_data(row=row,column=8,value="未通过")
            log.error("{}:用例未通过，原因为：{}".format(case["title"],e))
            raise e
        else:
            self.excel.write_data(row=row, column=8, value="通过")
            log.debug("{}:用例通过".format(case["title"]))

