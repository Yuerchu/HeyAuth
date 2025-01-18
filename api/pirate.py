'''
Author: 于小丘 海枫
Date: 2024-08-15 19:02:01
LastEditors: Yuerchu admin@yuxiaoqiu.cn
LastEditTime: 2024-10-06 21:37:13
FilePath: /HeyAuth/api/pirate.py
Description: 海枫授权系统 API Pirate路由 API Pirate

Copyright (c) 2018-2024 by 于小丘Yuerchu, All Rights Reserved. 
'''


from nicegui import APIRouter
from pydantic import BaseModel
from pkg.model import database
import pkg.log as log
import traceback

pirateApiRouter = APIRouter(prefix='/api/pirate', 
                            responses={404: {"description": "Not found"}},
                            tags=['盗版入库'])

class bApplicationPrivate(BaseModel):
    product_id: int
    domain: str
    ip: str
    db_name: str
    db_username: str
    db_password: str

@pirateApiRouter.post('/b/v1')
async def pirate(pirate: bApplicationPrivate):
    db = database()
    private = await db.addPirate(
        product_id=pirate.product_id, 
        domain=pirate.domain, 
        ip=pirate.ip, 
        db_name=pirate.db_name, 
        db_username=pirate.db_username, 
        db_password=pirate.db_password)
    if private == True:
        return {
            'code': 200, 
            'message': '盗版举报成功'
            }
    else:
        return {
            'code': 40000, 
            'message': private
            }