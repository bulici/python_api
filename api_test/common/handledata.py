"""
=================================================
Author : Bulici
Time : 2020/3/11 13:29 
Email : 294666094@qq.com
Motto : Clumsy birds have to start flying early.
=================================================
"""
import random
import requests
import jsonpath

class Randomdata:
    """随机生成指定长度名称和邮箱的类"""

    def count(self,name):
        url = "http://api.keyou.site:8000/user/{}/count/".format(name)
        data = {}
        respons = requests.get(url=url,params=data)
        # 提取查询结果：名字/邮箱是否被注册
        res = jsonpath.jsonpath(respons.json(),"$.count")[0]
        return res

    def name_6(self):
        """随机生成6位数"""
        while True:
            name_6 = ""
            for i in range(1,7):
                n = random.randint(0,9)
                name_6 += str(n)
            # 判断该名字是否已被注册
            if self.count(name_6) == 0:
                break
        return name_6

    def name_10(self):
        """随机生成10位数"""
        while True:
            name_10 = ""
            for i in range(1, 11):
                n = random.randint(0, 9)
                name_10 += str(n)
            # 判断该名字是否已被注册
            if self.count(name_10) == 0:
                break
        return name_10

    def name_20(self):
        """随机生成20位数"""
        while True:
            name_20 = ""
            for i in range(1,21):
                n = random.randint(0,9)
                name_20 += str(n)
            # 判断该名字是否已被注册
            if self.count(name_20) == 0:
                break
        return name_20

    def name_50(self):
        """随机生成50位数"""
        name_50 = ""
        for i in range(1,51):
            n = random.randint(0,9)
            name_50 += str(n)
        return name_50

    def name_200(self):
        """随机生成200位数"""
        name_200 = ""
        for i in range(1,201):
            n = random.randint(0,9)
            name_200 += str(n)
        return name_200

    def email(self):
        """随机生成一个email"""
        while True:
            email = "bulici"
            for i in range(1, 7):
                n = random.randint(0, 9)
                email += str(n)
            email += "@163.com"
            #判断该邮箱是否已被注册
            if self.count(email) == 0:
                break
        return email

