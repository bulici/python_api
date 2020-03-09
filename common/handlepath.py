"""
=================================================
Author : Bulici
Time : 2020/2/22 10:31 
Email : 294666094@qq.com
Motto : Clumsy birds have to start flying early.
=================================================
"""
import os

#项目目录路径
BASEDIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

#公共文件目录路径
COMMONDIR = os.path.join(BASEDIR,"common")

#配置文件目录路径
CONFDIR = os.path.join(BASEDIR,"conf")

#测试数据目录路径
DATADIR = os.path.join(BASEDIR,"data")

#日志文件目录路径
LOGDIR = os.path.join(BASEDIR,"log")

#测试报告目录路径
REPORTDIR = os.path.join(BASEDIR,"report")

#测试用例目录路径
TESTCASEDIR = os.path.join(BASEDIR,"testcase")

