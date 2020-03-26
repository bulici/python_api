"""
=================================================
Author : Bulici
Time : 2020/2/29 15:14 
Email : 294666094@qq.com
Motto : Clumsy birds have to start flying early.
=================================================
"""
import re
from common.handleconfig import conf



class ReplaceData:

    @staticmethod
    def replace_data(str):
        """处理需要替换的用例数据"""
        while re.search(r"#(.+?)#",str):
            #匹配出一个待替换的数据
            res = re.search(r"#(.+?)#",str)
            #提取出该待替换的数据
            data = res.group()
            #获取待替换的参数名
            key = res.group(1)
            try:
                str = str.replace(data,conf.get("test_data",key))
            except Exception:
                str = str.replace(data, getattr(ReplaceData,key))

        return str




# str = '{"member_id":#member_id#,"amount":#money#}'
# ReplaceData.member_id = "123456"
# ReplaceData.money = "123456"
# res = ReplaceData.replace_data(str)
# print(res)

