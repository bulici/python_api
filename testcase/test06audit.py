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
from common.handle_sign import HandleSign

@ddt
class TestAudit(unittest.TestCase):

    excel = Excel(os.path.join(DATADIR,"apicases.xlsx"),"audit")
    cases = excel.read_data()
    request = Requests()
    db = DB()

    @classmethod
    def setUpClass(cls):
        """登录普通用户，提取token值和用户ID"""
        login_url = conf.get("env", "url") + "/member/login"
        login_data = {"mobile_phone": conf.get("test_data", "phone"), "pwd": conf.get("test_data", "pwd")}
        headers = eval(conf.get("env", "headers"))
        res = cls.request.send(url=login_url, method="post", json=login_data, headers=headers)

        # 提取鉴权token值，并保存为类属性
        ReplaceData.token = jsonpath.jsonpath(res.json(), "$..token")[0]
        ReplaceData.Authorization = jsonpath.jsonpath(res.json(), "$..token_type")[0] + " " + \
                                    jsonpath.jsonpath(res.json(), "$..token")[0]
        # 提取用户id，并保存为类属性
        ReplaceData.loan_member_id = jsonpath.jsonpath(res.json(), "$..id")[0]
        print(ReplaceData.loan_member_id)

    def setUp(self):
        """每条用例执行前添加一个项目"""
        loan_url = conf.get("env", "url") + "/loan/add"
        loan_method = "post"
        loan_headers = eval(conf.get("env", "headers"))
        loan_headers["Authorization"] = getattr(ReplaceData,"Authorization")
        loan_data = {"member_id":getattr(ReplaceData,"loan_member_id"),"title":"审核测试用例类项目","amount":1000,
                     "loan_rate":10.0,"loan_term":6,"loan_date_type":1,"bidding_days":6}
        # 添加时间戳和签名到json请求体
        sign = HandleSign.generate_sign(ReplaceData.token)
        loan_data.update(sign)
        #发送加标请求
        loan_res = self.request.send(url=loan_url,method=loan_method,json=loan_data,headers=loan_headers)

        # 提取项目id，并保存为类属性
        ReplaceData.loan_id = str(jsonpath.jsonpath(loan_res.json(), "$..id")[0])

    @data(*cases)
    def testaudit(self,case):

        #准备测试数据，对登录接口用例替换相应的管理员手机号、密码
        url = conf.get("env", "url") + case["url"]
        method = case["method"]
        headers = eval(conf.get("env", "headers"))
        expected = eval(case["expected"])
        row = case["case_id"] + 1
        title = case["title"]
        case["data"] = ReplaceData.replace_data(case["data"])
        data = eval(case["data"])

        # 判断是否是添加项目接口，添加项目接口则加上请求头，替换相应的用户id
        if case["interface"] == "audit" :
            headers["Authorization"] = getattr(ReplaceData,"Authorization")
            # 添加时间戳和签名到json请求体
            sign = HandleSign.generate_sign(ReplaceData.token)
            data.update(sign)
        elif case["interface"] == "admin_audit":
            headers["Authorization"] = getattr(ReplaceData, "admin_Authorization")
            # 添加时间戳和签名到json请求体
            admin_sign = HandleSign.generate_sign(ReplaceData.admin_token)
            data.update(admin_sign)


        #发送请求，获取实际结果
        respons = self.request.send(url=url,method=method,headers=headers,json=data)
        res = respons.json()

        # 判断是否是登录接口
        if case["interface"] == "login":
            # 提取token,保存为类属性
            ReplaceData.admin_token = jsonpath.jsonpath(res,"$..token")[0]
            token_type = jsonpath.jsonpath(res, "$..token_type")[0]
            ReplaceData.admin_Authorization = token_type + " " + ReplaceData.admin_token

        if res["code"] == 0 and case["title"] == "审核成功-正常通过流程":
            ReplaceData.pass_loan_id = str(data["loan_id"])

        #断言:比对预期结果和实际结果
        try:
            self.assertEqual(expected["code"],res["code"])
            self.assertEqual(expected["msg"],res["msg"])
            if case["sql_check"]:
                # 查询用例执行后当前项目的审核状态
                status = self.db.find_one(case["sql_check"].format(
                    ReplaceData.loan_id))["status"]
                self.assertEqual(expected["status"],status)

        except AssertionError as e :
            print("预期结果：{}".format(expected))
            print("实际结果：{}".format(res))
            self.excel.write_data(row=row,column=8,value="未通过")
            log.error("用例未通过：{}，错误原因：{}".format(title,e))
            raise e
        else:
            self.excel.write_data(row=row, column=8, value="通过")
            log.debug("用例通过：{}".format(title))