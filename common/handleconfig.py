"""
=================================================
Author : Bulici
Time : 2020/2/22 12:02 
Email : 294666094@qq.com
Motto : Clumsy birds have to start flying early.
=================================================
"""
import os
from configparser import ConfigParser
from common.handlepath import CONFDIR

class Myconfig(ConfigParser):

    def __init__(self,filename):
        """重写__init__()方法"""
        self.filename = filename
        #继承父类__init__()属性
        super().__init__()
        self.read(filename)

    def write_data(self,section,option,value):
        """往配置文件中写入数据"""
        self.set(section,option,value)
        self.write(open(self.filename),'w')

conf = Myconfig(os.path.join(CONFDIR,'conf.ini'))