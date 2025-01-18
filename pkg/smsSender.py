'''
Author: 于小丘 海枫
Date: 2024-10-08 15:34:04
LastEditors: Yuerchu admin@yuxiaoqiu.cn
LastEditTime: 2024-10-24 17:05:38
FilePath: /HeyAuth/pkg/smsSender.py
Description: 海枫授权系统 短信发送 SMS Sender

Copyright (c) 2018-2024 by 于小丘Yuerchu, All Rights Reserved. 
'''

import requests
from requests import RequestException
import pkg.model as model

async def sendXinYaoMessager(phone="", content=""):
    db = model()
    xinYaoTester = requests.get(
        url = await db.getSetting('xinYaoSmsURL'),
        params={
            'channel': await db.getSetting('xinYaoSmsChannel'),
            'phone': phone,
            'content': content,
            'user_name': await db.getSetting('xinYaoSmsKey'),
            'user_key': await db.getSetting('xinYaoSmsKey')
            })
    if xinYaoTester.status_code == 200:
        if xinYaoTester.json()['code'] == 1:
            return True
        else:
            raise TypeError(xinYaoTester.json()['msg'])
    else:
        raise RequestException('发送失败，网络错误')

# 测试允梦短信
async def SendYunMenMessager(phone = "", content = ""):
    db = model()
    yunMenSmsUrl = 'https://sms.mengdo.cn/sendApi?channel=' + \
                    await db.getSetting('yunMenSmsChannel') + \
                    '&username=' + await db.getSetting('yunMenSmsusername') + \
                    '&key=' + await db.getSetting('yunMenSmsKey') + \
                    '&phone=' + phone + \
                    '&content=' + phone
    yunMenTester = requests.get(url=yunMenSmsUrl)
    if yunMenTester.status_code == 200:
        if yunMenTester.json()['code'] == 1:
            return True
        else:
            raise TypeError(yunMenTester.json()['msg'])
    else:
        raise RequestException('发送失败：网络错误')