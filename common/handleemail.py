"""
=================================================
Author : Bulici
Time : 2020/3/5 22:32 
Email : 294666094@qq.com
Motto : Clumsy birds have to start flying early.
=================================================
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from common.handleconfig import conf

class Email:
    """
    账号：294666094@qq.com  端口：465
    授权码:fekhzaauocczbjjg
    """

    @staticmethod
    def send_email(file_path,text_msg=None,subject="Python代码邮件"):
        """
        发送附件文件的邮件的方法
        :param file_path: 附件路径，必填项
        :param text_msg: 邮件内文本内容，不填则默认为附件内文本；
        :param subject: 邮件的主题名称。
        :return:
        """

        #第一步：根据smtp服务器地址，准备测试账号及授权码
        #smtp服务器地址
        host = conf.get("email","host")
        #端口
        port = conf.getint("email","port")
        #发件人邮箱
        user = conf.get("email","user")
        #发件人邮箱授权码
        password = conf.get("email","password")
        #收件人邮箱
        to_user = eval(conf.get("email","to_user"))
        #附件的文件名
        filename = conf.get("email","filename")

        # 1、连接smtp服务器
        smtp = smtplib.SMTP_SSL(host=host,port=port)
        #2、登录账户
        smtp.login(user=user,password=password)

        # 创建一封多组件的邮件
        email = MIMEMultipart()
        with open(file_path,"rb") as f :
            content = f.read()

        #邮件内的文本信息
        if text_msg == None:
            text_msg = content
        text_email = MIMEText(text_msg, _subtype='html', _charset="utf8")
        # 添加到多组件的邮件中
        email.attach(text_email)

        #邮件的附件信息
        file_email = MIMEApplication(content)
        file_email.add_header("content-disposition", "attachment", filename=filename)
        # 添加到多组件的邮件中
        email.attach(file_email)

        #1、设置邮件主题名
        email["Subject"] = subject
        #2、设置邮件发送人
        email["From"] = user
        #3、设置邮件接收人
        for i in to_user:
            email["To"] = i

        #发送邮件
        smtp.send_message(email,from_addr=user,to_addrs=to_user)

# Email.send_email(text_msg="请下载附件查看详细接口测试报告内容！",subject="前程贷接口测试报告")
