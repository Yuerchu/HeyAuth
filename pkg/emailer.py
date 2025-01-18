"""
海枫授权系统 邮箱组件 HeyAuth Emailer
~~~~~~~~~~~~~~~~~~~~~

这是海枫授权系统的邮件组件，用于发送邮件验证码和测试邮件。
最简单的用法：

    >>> import pkg.emailer as emailer
>>> emailer.sendTestEmail('example@example.com')

"""

'''
- 作者 Author                 : 于小丘 海枫
- 网址 url                    : xiaoqiu.in
- 制作日期 MakeDate           : 2024-08-26
- 上次修改日期 LastEditTime   : 2024-08-26
- 邮箱 Email                 : admin@yuxiaoqiu.cn
- 项目名 Project             : 海枫授权系统
- 介绍 Description          : 一款针对B+C端的应用授权系统
- 请阅读 Read me            : 感谢您使用海枫授权系统，程序源码有详细的注释，支持二次开发。
- 注意 Remind              : 使用盗版海枫授权系统会存在各种未知风险。支持正版，从我做起！
'''

import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr
import pkg.log as log
import pkg.tool as tool
from pkg.model import database
import traceback

async def dbgetter(param: str) -> str:
    db = database()
    result = await db.getSetting(param)
    try:
        res = str(result[0][0])
    except IndexError:
        raise Exception('无法获取数据库设置项: ' + param + '，请检查邮件服务是否成功配置！')
    return res

async def sendTestEmail(email: str, name: str ='测试'):
    '''
    发送测试邮件
    :param email: 邮箱
    :param name: 昵称
    :return: 成功返回None，失败返回错误信息
    '''
    db = database()
    # 第三方 SMTP 服务
    log.info("准备发送邮件……")
    mail_host = str(await dbgetter('emailSmtpServer'))   #设置服务器
    mail_port = str(await dbgetter('emailSmtpSeverPort'))    #端口
    mail_user = str(await dbgetter('emailSmtpUsername'))    #用户名
    mail_senderName = str(await dbgetter('emailSendName'))    #发件人
    mail_pass = str(await dbgetter('emailSmtpPassword'))   #口令 
    sender = str(await dbgetter('emailSenderMail'))
    receivers = [email]  # 接收邮件，可设置为你的QQ邮箱或者其他邮箱
    
    mail_msg = """
                <h1>海枫授权系统 邮件发送测试</h1>
                <p>如果你收到了这封邮件，说明你的信息配置正确，快去后台开启邮件发送服务吧！</p>
               """
    message = MIMEText(mail_msg, 'html', 'utf-8')
    message['From'] = formataddr((mail_senderName, mail_user))
    message['To'] =  formataddr((name, email))
    
    subject = '海枫授权系统 SMTP 邮件测试'
    message['Subject'] = subject
    
    try:
        log.debug('准备连接SMTP服务器, 服务器地址为 {} , 端口为 {}'.format(mail_host, mail_port))
        smtpObj = smtplib.SMTP_SSL(host=mail_host, port=mail_port)
        log.debug('准备登录，用户名为 {}，密码为 {}'.format(mail_user, mail_pass))
        smtpObj.login(mail_user,mail_pass)
        log.debug('准备发送邮件……')
        smtpObj.sendmail(sender, receivers, message.as_string())
        log.info("邮件发送成功")
        return None
    except smtplib.SMTPException:
        log.error("无法发送邮件:\n" + traceback.format_exc())
        return str(traceback.format_exc())

async def sendCodeEmail(method: str, email: str, code: int = None):
    '''
    发送验证码邮件
    :param email: 邮箱
    :param code: 验证码（可选，默认为None，将由emailer组件自动生成）
    :return: 成功返回None，失败返回错误信息
    '''
    if code == None:
        code = tool.generate_code(6)
    db = database()
    # 第三方 SMTP 服务
    log.info("准备发送邮件……")
    mail_host = str(await dbgetter('emailSmtpServer'))   #设置服务器
    mail_port = str(await dbgetter('emailSmtpSeverPort'))    #端口
    mail_user = str(await dbgetter('emailSmtpUsername'))    #用户名
    mail_senderName = str(await dbgetter('emailSendName'))    #发件人
    mail_pass = str(await dbgetter('emailSmtpPassword'))   #口令 
    sender = str(await dbgetter('emailSenderMail'))
    receivers = [email]  # 接收邮件，可设置为你的QQ邮箱或者其他邮箱
    
    mail_msg = """
                <h1>海枫授权系统 邮件验证码</h1>
                <p>你的验证码是：{}</p>
                <p>请勿将验证码泄露给他人。</p>
               """.format(code)
    message = MIMEText(mail_msg, 'html', 'utf-8')
    message['From'] = formataddr((mail_senderName, mail_user))
    if method == 'reg':
        message['To'] =  formataddr(('注册账号', email))
    elif method == 'forget':
        message['To'] =  formataddr(('找回密码', email))
    
    subject = '海枫授权系统 邮件验证码'
    message['Subject'] = subject
    
    try:
        log.debug('准备连接SMTP服务器, 服务器地址为 {} , 端口为 {}'.format(mail_host, mail_port))
        smtpObj = smtplib.SMTP_SSL(host=mail_host, port=mail_port)
        log.debug('准备登录，用户名为 {}，密码为 {}'.format(mail_user, mail_pass))
        smtpObj.login(mail_user,mail_pass)
        log.debug('准备发送邮件……')
        smtpObj.sendmail(sender, receivers, message.as_string())
        log.info("邮件发送成功")
        return None
    except smtplib.SMTPException:
        log.error("无法发送邮件:\n" + traceback.format_exc())
        return str(traceback.format_exc())

async def sendProductEmail(email: str, product_name: str,  product_price: str, pay_time: str, pay_id: str = 'undefined',):
    '''
    发送购买成功邮件
    :param email: 邮箱
    :param code: 验证码（可选，默认为None，将由emailer组件自动生成）
    :return: 成功返回None，失败返回错误信息
    '''
    db = database()
    # 第三方 SMTP 服务
    log.info("准备发送邮件……")
    siteName = str(await db.getSiteName())
    mail_host = str(await dbgetter('emailSmtpServer'))   #设置服务器
    mail_port = str(await dbgetter('emailSmtpSeverPort'))    #端口
    mail_user = str(await dbgetter('emailSmtpUsername'))    #用户名
    mail_senderName = str(await dbgetter('emailSendName'))    #发件人
    mail_pass = str(await dbgetter('emailSmtpPassword'))   #口令 
    sender = str(await dbgetter('emailSenderMail'))
    receivers = [email]  # 接收邮件，可设置为你的QQ邮箱或者其他邮箱
    
    mail_msg = """
                <h1>海枫授权系统 订单支付成功</h1>
                <p>您好，</p>
                <p>您在 {} 购买的商品已支付成功</p>
                <p>类型：产品购买</p>
                <p>商品：<b>{}</b></p>
                <p>订单号：{}</p>
                <p>支付金额：{}</p>
                <p>支付时间：{}</p>
                <br />

                <p>如有疑问，请联系客服。</p>
               """.format(siteName, product_name, pay_id, product_price, pay_time)
    message = MIMEText(mail_msg, 'html', 'utf-8')
    message['From'] = formataddr((mail_senderName, mail_user))
    message['To'] =  formataddr(('海枫授权系统用户', email))
    
    subject = '[' + siteName + '] 订单支付成功'
    message['Subject'] = subject
    
    try:
        log.debug('准备连接SMTP服务器, 服务器地址为 {} , 端口为 {}'.format(mail_host, mail_port))
        smtpObj = smtplib.SMTP_SSL(host=mail_host, port=mail_port)
        log.debug('准备登录，用户名为 {}，密码为 {}'.format(mail_user, mail_pass))
        smtpObj.login(mail_user,mail_pass)
        log.debug('准备发送邮件……')
        smtpObj.sendmail(sender, receivers, message.as_string())
        log.info("邮件发送成功")
        return None
    except smtplib.SMTPException:
        log.error("无法发送邮件:\n" + traceback.format_exc())
        return str(traceback.format_exc())