'''
Author: 于小丘 海枫
Date: 2024-08-13 13:53:05
LastEditors: Yuerchu admin@yuxiaoqiu.cn
LastEditTime: 2024-12-01 02:09:48
FilePath: /HeyAuth/api/site.py
Description: 海枫授权系统 API Site路由 API Site

Copyright (c) 2018-2024 by 于小丘Yuerchu, All Rights Reserved. 
'''


from nicegui import APIRouter
from pydantic import BaseModel
from fastapi import Request
from pkg.model import database as database
import pkg.log as log

siteApiRouter = APIRouter(prefix='/api/site', 
                          responses={404: {"description": "Not found"}},
                          tags=['站点信息'])

class bApplicationAuth(BaseModel):
    product_id: int | None = None
    domain: str | None = None
    key: str | None = None
    pri_key: str | None = None

class bApplicationPrivate(BaseModel):
    product_id: int
    domain: str
    ip: str
    db_name: str
    db_username: str
    db_password: str

@siteApiRouter.get('/ping',
                   summary='站点心跳',
                   description='此API用于检查您的站点是否正常运行，以及您的应用程序是否能够正常连接到海枫授权系统。\n\n'
                               '同时也将返回当前站点的域名/IP与客户端的IP地址。\n\n'
                               '此API不需要任何参数，您可以直接访问此API来检查您的站点是否正常运行。')
async def ping(request: Request):
    log.info('/api/site/ping')
    return {
        'code': 200, 
        'data': {
            'domain': request.base_url.hostname, 
            'client_ip': request.client.host
        },
        'msg': 'Pong'
        }

@siteApiRouter.get('/config')
async def config():
    log.info('/api/site/config')
    db = database()
    siteTitle = await db.getSiteName()
    siteNotice = await db.getSiteNotice()
    return {'code': 200,
            'data': {
                'title': siteTitle,
                'loginCaptcha': False,
                'regCaptcha': False,
                'forgetCaptcha': False,
                'emailActive': True,
                'phoneActive': True,
                'site_notice': siteNotice,
                'captcha_type': 'normal',
                'captcha_ReCaptchaKey': '',
                'tcaptcha_captcha_app_id': ''
            },
             'msg': ''}