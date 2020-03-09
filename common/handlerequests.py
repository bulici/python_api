"""
=================================================
Author : Bulici
Time : 2020/2/22 14:39 
Email : 294666094@qq.com
Motto : Clumsy birds have to start flying early.
=================================================
"""
import requests


class Requests(object):

    def __init__(self):
        """创建session对象"""
        self.session = requests.session()

    def send(self,url, method,headers=None, params=None,  json=None, data=None,files=None):
        """发送请求"""
        if method == "get":
            response = self.session.get(url=url,headers=headers,params=params)
        elif method == "post":
            headers["Content-Type"] = "application/json"
            response = self.session.post(url=url,headers=headers,json=json,data=data,files=files)
        elif method == "patch":
            headers["Content-Type"] = "application/json"
            response = self.session.patch(url=url, headers=headers, json=json, data=data, files=files)

        return response


