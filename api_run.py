"""
=================================================
Author : Bulici
Time : 2020/2/22 10:25 
Email : 294666094@qq.com
Motto : Clumsy birds have to start flying early.
=================================================
"""
"""
1、完成项目其他接口用例的编写和测试用例类的编写
"""
import unittest
import os
from HTMLTestRunnerNew import HTMLTestRunner
from common.handlepath import REPORTDIR,TESTCASEDIR
from common.handleemail import Email

#创建一个测试套件对象
suite = unittest.TestSuite()

#创建用例加载对象并加载用例到套件
loader = unittest.TestLoader()
suite.addTest(loader.discover(TESTCASEDIR))

#单独运行主流程测试用例
# from testcase import test11mainstreaming
# suite.addTest(loader.loadTestsFromModule(test11mainstreaming))

#创建用例运行程序并执行用例
# file_path = os.path.join(REPORTDIR,'report.html')
# runner = HTMLTestRunner(stream=open(file_path,'wb'),
#                         title='接口自动化测试报告',
#                         description='报告描述：前程贷接口自动化测试的报告。',
#                         tester='布里茨')
# runner.run(suite)

import datetime
#创建一个时间格式
date = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

#另外一种测试报告:BeautifulReport
from BeautifulReport import BeautifulReport
file_path = os.path.join(REPORTDIR,'{}_接口自动化测试报告.html'.format(date))
br_runner = BeautifulReport(suite)
br_runner.report(description='报告描述：前程贷接口自动化测试的报告。',
                 filename='{}_接口自动化测试报告.html'.format(date),
                 report_dir=REPORTDIR)

#发送测试报告邮件至邮箱
text_msg = "请下载附件查看详细接口测试报告内容！"
subject = "前程贷接口自动化测试报告邮件"
Email.send_email(file_path=file_path,text_msg=text_msg,subject=subject)




