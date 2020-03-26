"""
=================================================
Author : Bulici
Time : 2020/2/22 10:39 
Email : 294666094@qq.com
Motto : Clumsy birds have to start flying early.
=================================================
"""
import openpyxl
import os
from common.handlepath import DATADIR

class Excel(object):

    def __init__(self,filename,sheetname):
        #初始化文件名、表单名
        self.filename = filename
        self.sheetname = sheetname

    def open(self):
        """打开文件"""
        self.wb = openpyxl.load_workbook(self.filename)
        self.sh = self.wb[self.sheetname]

    def read_data(self):
        """读取用例数据"""
        # 打开文件
        self.open()
        #读取所有行的内容
        datas = list(self.sh.rows)
        #获取测试用例标题
        title = [t.value for t in datas[0]]
        data_cases = []
        for i in datas[1:]:
            value = [v.value for v in i]
            #聚合打包：键名：键值
            res = dict(zip(title,value))
            data_cases.append(res)
        
        return data_cases

    def write_data(self,row,column,value):
        """在指定格子写入数据"""
        #打开文件
        self.open()
        #指定格子和值
        self.sh.cell(row=row,column=column,value=value)
        #保存文件
        self.wb.save(self.filename)

# excel = Excel(os.path.join(DATADIR,"apicases.xlsx"),"register")
# res = excel.read_data()
# print(res)