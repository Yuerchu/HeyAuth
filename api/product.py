'''
Author: 于小丘 海枫
Date: 2024-10-02 15:23:34
LastEditors: Yuerchu admin@yuxiaoqiu.cn
LastEditTime: 2024-10-06 21:37:24
FilePath: /HeyAuth/api/product.py
Description: 海枫授权系统 产品信息 API Product_Info_API

Copyright (c) 2018-2024 by 于小丘Yuerchu, All Rights Reserved. 
'''


from nicegui import APIRouter
from pydantic import BaseModel
from pkg.model import database as database
import pkg.log as log
import traceback

productApiRouter = APIRouter(prefix='/api', 
                             responses={404: {"description": "Not found"}},
                             tags=['产品信息'])

@productApiRouter.get('/product')
async def auth(product_id: int = 0):
    db = database()
    # 数据库查询
    product_info = await db.getProductInfo(product_id=product_id)
    if product_info != None:
        data = {
            'product_id': product_info[0],
            'product_name': product_info[1],
            'creat_at': product_info[2],
            'delete_at': product_info[3],
            'price': product_info[4],
            'number': product_info[5],
            'change': product_info[6]
        }
        data = {
            'code': 200,
            'data': data,
            'msg': ''
        }
    else:
        data = {
            'code': 40001,
            'data': '',
            'msg': '未找到产品信息'
        }
    return data