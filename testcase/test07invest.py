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
class TestInvest(unittest.TestCase):

    excel = Excel(os.path.join(DATADIR,"apicases.xlsx"),"invest")
    cases = excel.read_data()
    request = Requests()
    db = DB()

    @data(*cases)
    def testinvest(self,case):
        #准备测试数据，替换用例中相应的手机号、密码、用户id、项目id
        url = conf.get("env", "url") + case["url"]
        method = case["method"]
        headers = eval(conf.get("env", "headers"))
        expected = eval(case["expected"])
        row = case["case_id"] + 1
        title = case["title"]
        case["data"] = ReplaceData.replace_data(case["data"])
        data = eval(case["data"])
        # 判断是否是投资接口，投资接口则加上请求头
        if case["interface"] != "login":
            headers["Authorization"] = ReplaceData.Authorization
            # 添加时间戳和签名到json请求体
            sign = HandleSign.generate_sign(ReplaceData.token)
            data.update(sign)
            #判断是否需要sql校验
            if case["sql_check"]:
                # 判断SQL校验是普通用例还是生成了回款计划的用例
                if case["title"] == "投资金额等于项目剩余可投金额":
                    sql = eval(case["sql_check"])
                    # 查询执行用例前当前用户的可用余额数
                    start_leave_amount = self.db.find_one(sql[0].format(ReplaceData.member_id))["leave_amount"]
                    # 查询执行用例前该项目中当前用户的投资记录总数
                    start_invest = self.db.find_count(sql[1].format(ReplaceData.loan_id,ReplaceData.member_id))
                    # 查询执行用例前当前该项目中当前用户的流水记录总数
                    start_financelog = self.db.find_count(sql[2].format(ReplaceData.member_id))
                    # 查询执行用例前当前该项目中当前用户的回款记录总数
                    start_repayment = self.db.find_count(sql[3].format(ReplaceData.loan_id,ReplaceData.member_id))
                else:
                    # 查询执行用例前该项目中当前用户的投资记录总数
                    start_invest = self.db.find_count(case["sql_check"].format(
                        getattr(ReplaceData, "loan_id"), getattr(ReplaceData, "member_id")))


        #发送请求，获取实际结果
        respons = self.request.send(url=url,method=method,headers=headers,json=data)
        res = respons.json()

        #获取管理员用户id和token值，并保存为类属性
        if case["interface"] == "login":
            ReplaceData.member_id = str(jsonpath.jsonpath(res,"$..id")[0])
            ReplaceData.token = jsonpath.jsonpath(res, "$..token")[0]
            ReplaceData.Authorization = jsonpath.jsonpath(res, "$..token_type")[0] +" " + jsonpath.jsonpath(res, "$..token")[0]
        # 获取加标项目id，并保存为类属性
        if case["interface"] == "add":
            ReplaceData.loan_id = str(jsonpath.jsonpath(res,"$..id")[0])

        #断言:比对预期结果和实际结果
        try:
            self.assertEqual(expected["code"],res["code"])
            self.assertIn(expected["msg"],res["msg"])
            #判断是否需要SQL校验
            if case["sql_check"]:
                #判断SQL校验是普通用例还是生成了回款计划的用例
                if case["title"] == "投资金额等于项目剩余可投金额":
                    sql = eval(case["sql_check"])
                    # 查询执行用例前当前用户的可用余额数
                    end_leave_amount = self.db.find_one(sql[0].format(ReplaceData.member_id))["leave_amount"]
                    self.assertEqual(end_leave_amount,start_leave_amount-Decimal(str(data["amount"])))
                    # 查询执行用例前该项目中当前用户的投资记录总数
                    end_invest = self.db.find_count(sql[1].format(ReplaceData.loan_id, ReplaceData.member_id))
                    self.assertEqual(1, end_invest - start_invest)
                    # 查询执行用例前当前该项目中当前用户的流水记录总数
                    end_financelog = self.db.find_count(sql[2].format(ReplaceData.member_id))
                    self.assertEqual(1, end_financelog - start_financelog)
                    # 查询执行用例前当前该项目中当前用户的回款记录总数
                    end_repayment = self.db.find_count(sql[3].format(ReplaceData.loan_id, ReplaceData.member_id))
                    self.assertEqual(3, end_repayment - start_repayment)
                else:
                    # 查询执行用例前该项目中当前用户的投资记录总数
                    end_invest = self.db.find_count(case["sql_check"].format(ReplaceData.loan_id,ReplaceData.member_id))
                    self.assertEqual(1,end_invest-start_invest)
        except AssertionError as e :
            print("预期结果：{}".format(expected))
            print("实际结果：{}".format(res))
            self.excel.write_data(row=row,column=8,value="未通过")
            log.error("用例未通过：{}，错误原因：{}".format(title,e))
            raise e
        else:
            self.excel.write_data(row=row, column=8, value="通过")
            log.debug("用例通过：{}".format(title))