"""
=================================================
Author : Bulici
Time : 2020/2/22 12:02 
Email : 294666094@qq.com
Motto : Clumsy birds have to start flying early.
=================================================
"""
import logging
import os
from common.handlepath import LOGDIR
from common.handleconfig import conf

class Mylog(object):

    @staticmethod  #设置静态方法
    def write_log():
        #创建一个日志收集器对象并命名
        lg = logging.getLogger(conf.get("log","lg_name"))
        #日志收集等级
        lg.setLevel(conf.get("log","lg_setLevel"))
        
        #创建日志输出对象为控制台
        output1 = logging.StreamHandler()
        #日志输出等级
        output1.setLevel(conf.get("log","output1_setLevel"))
        #将输出对象与收集器绑定
        lg.addHandler(output1)

        # 创建日志输出对象为文件
        output2 = logging.FileHandler(os.path.join(LOGDIR,"mylog.log"),encoding='utf8')
        # 日志输出等级
        output2.setLevel(conf.get("log","output2_setLevel"))
        # 将输出对象与收集器绑定
        lg.addHandler(output2)
        
        #创建日志输出格式
        layout = '%(asctime)s - %(filename)s - line%(lineno)s - > %(levelname)s : %(message)s'
        #将输出格式应用到控制台输出对象
        la1 = logging.Formatter(layout)
        output1.setFormatter(la1)
        # 将输出格式应用到文件输出对象
        la2 = logging.Formatter(layout)
        output2.setFormatter(la2)

        return lg

log = Mylog.write_log()




