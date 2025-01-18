'''
Author: 于小丘 海枫
Date: 2024-08-15 19:01:09
LastEditors: Yuerchu admin@yuxiaoqiu.cn
LastEditTime: 2024-11-30 18:15:56
FilePath: /HeyAuth/api/auth.py
Description: 海枫授权系统 API Auth路由 API Auth

Copyright (c) 2018-2024 by 于小丘Yuerchu, All Rights Reserved. 
'''


from nicegui import APIRouter
from pydantic import BaseModel
from pkg.model import database as database
from pkg.tool import timestamp
import pkg.log as log
import traceback

authApiRouter = APIRouter(prefix='/api/auth', 
                          responses={404: {"description": "Not found"}},
                          tags=['授权路由'])


class bApplicationAuthV1(BaseModel):
    product_id: int | None = None
    domain: str | None = None
    key: str | None = None
    pri_key: str | None = None


@authApiRouter.post(path='/b/v1',
                    summary='B端授权 V1接口',
                    description='''
                    B端授权 V1接口.
                    ''',)
async def auth(auth: bApplicationAuthV1):
    '''
    获取授权信息
    '''
    if auth.product_id == None:
        return {
            'code': 50000,
            'message': '产品ID不能为空',
            'status': 'error'
            }
    elif auth.domain == None:
        return {
            'code': 50001, 
            'message': '授权域名不能为空', 
            'status': 'error'
            }
    elif auth.key == None:
        return {
            'code': 50002, 
            'message': '授权码不能为空', 
            'status': 'error'
            }
    try:
        db = database()
        auth = await db.checkAuth(
            product_id=auth.product_id, 
            domain=auth.domain, 
            key=auth.key)
        if auth == None:
            return {
                'code': 40000, 
                'message': '产品未授权或产品ID/域名/授权码不匹配', 
                'status': 'error'
                }
        elif auth[3] == 'ban':
            return {
                'code': 40001, 
                'message': '授权已被封禁', 
                'status': 'error'
                }
        elif auth[3] == 'lapse':
            return {
                'code': 40002, 
                'message': '授权已被删除或更换', 
                'time': auth[8], 
                'status': 'error'
                }
        elif auth[7] != '9999-12-31 23:59:59' \
        and timestamp() > timestamp(auth[7]):
                return {
                    'code': 40003, 
                    'message': '授权已过期', 
                    'time': auth[7], 
                    'status': 'error'
                    }
        else: return {
                'code': 200, 
                'time': auth[6], 
                'message': '授权成功', 
                'status': 'ok'
                }
    except Exception as e:
        log.error(traceback.format_exc())
        return {
            'code': 500, 
            'message': '参数异常', 
            'status': 'error'
            }
