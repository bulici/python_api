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
import random
import jsonpath
from library.ddt import ddt,data
from common.handleexcel import Excel
from common.handlepath import DATADIR
from common.handleconfig import conf
from common.handlereplace import ReplaceData
from common.handlerequests import Requests
from common.handlemylog import log
from common.handle_sign import HandleSign
from common.handelmysql import DB

@ddt
class TestMainstreaming(unittest.TestCase):
    excel = Excel(os.path.join(DATADIR,"apicases.xlsx"),"mainstreaming")
    cases = excel.read_data()
    request = Requests()
    db = DB()

    @data(*cases)
    def testmainstreaming(self,case):
        """
        接口测试项目主流程测试用例
        :param case: Excel文档中的用例
        :return:
        """
        #第一步：准备测试数据
        url = conf.get("env", "url") + ReplaceData.replace_data(case["url"])
        method = case["method"]
        expected = eval(case["expected"])
        headers = eval(conf.get("env","headers"))
        title = case["title"]
        row = case["case_id"] + 1
        #判断是注册接口，则生成一个随机手机号，并保存为类属性
        if case["interface"] == "register":
            ReplaceData.mobile_phone = self.random_phone()
        case["data"] = ReplaceData.replace_data(case["data"])
        data = eval(case["data"])

        #判断不是注册、登录、项目列表接口就在请求头中添加token鉴权信息
        if case["interface"] != "register" and case["interface"] != "login" :
            headers["Authorization"] = ReplaceData.Authorization
            # 添加时间戳和签名到json请求体
            sign = HandleSign.generate_sign(ReplaceData.token)
            data.update(sign)

        #第二步：发送请求，获取结果
        response = self.request.send(url=url,method=method,headers=headers,params=data,json=data)
        res = response.json()

        #判断是否是登录接口，提取用户的id，提取鉴权token值，保存为类属性
        if case["interface"] == "login":
            ReplaceData.member_id = str(jsonpath.jsonpath(res,"$..id")[0])
            ReplaceData.token = jsonpath.jsonpath(res,"$..token")[0]
            token_type = jsonpath.jsonpath(res,"$..token_type")[0]
            ReplaceData.Authorization = token_type + " " + ReplaceData.token

        # 判断是否是添加项目接口，提取项目的id，保存为类属性
        if case["interface"] == "add" and case["title"] == "管理员添加项目一":
            ReplaceData.pass_loan_id = str(jsonpath.jsonpath(res,"$..id")[0])
        elif case["interface"] == "add" and case["title"] == "管理员添加项目二":
            ReplaceData.file_loan_id = str(jsonpath.jsonpath(res,"$..id")[0])

        #第三步：断言，比对预期结果与实际结果
        try:
            self.assertEqual(expected["code"],res["code"])
            self.assertEqual(expected["msg"],res["msg"])
        except AssertionError as e :
            print("预期结果：{}".format(expected))
            print("实际结果：{}".format(res))
            self.excel.write_data(row=row,column=8,value="未通过")
            log.error("用例未通过：{}，错误原因：{}".format(title,e))
            raise e
        else:
            self.excel.write_data(row=row, column=8, value="通过")
            log.debug("用例通过：{}".format(title))



    def random_phone(self):
        """
        随机生成手机号的方法
        :return:
        """
        while True:
            phone = "155"
            for i in range(0, 8):
                n = random.randint(0, 9)
                phone += str(n)
            sql = "SELECT * FROM futureloan.member WHERE mobile_phone={}".format(phone)
            res_phone = self.db.find_count(sql)
            if res_phone == 0:
                break

        return phone
