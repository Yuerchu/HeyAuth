'''
Author: 于小丘 海枫
Date: 2024-10-01 09:38:30
LastEditors: Yuerchu admin@yuxiaoqiu.cn
LastEditTime: 2024-12-01 17:41:08
FilePath: /HeyAuth/api/select.py
Description: 查询API

Copyright (c) 2018-2024 by 于小丘Yuerchu, All Rights Reserved. 
'''

from nicegui import APIRouter, app
from pydantic import BaseModel
from fastapi import HTTPException, Path
from pkg.model import database as database
import pkg.tool
import pkg.log as log
import traceback

selectApiRouter = APIRouter(prefix='/api/select', 
                            responses={404: {"description": "Not found"}},
                            tags=['授权查询'])

@selectApiRouter.get('/legal')
async def selectlegal(
    product_id: int = Path(..., title="产品ID", description="待查询授权的产品ID", ge=1),
    domain: str = Path(..., title="域名", description="待查询授权的域名")):
    if product_id == None or domain == None:
        raise HTTPException(status_code=400, detail="参数不能为空")
    db = database()
    legal = await db.getLegal(product_id=product_id, domain=domain)
    if legal == None:
        data = {
            'code': 40004,
            'data': [],
            'msg': "未查询到数据，疑似盗版"
        }
        return data
    data = {
        'code': 20000,
        'data': legal,
        'msg': "查询成功"
    }
    return data

@selectApiRouter.get('/qq')
async def selectQQ(qq: str = None, id: str = None):
    if qq == None: raise HTTPException(status_code=400, detail="QQ不能为空")
    
    db = database()
    userAuth = await db.getUserAuthsB(id=None, qq=qq)
    if userAuth == None:
        data = {
            'code': 40004,
            'data': [],
            'msg': "未查询到数据"
        }
        return data
    
    auth_data = []
    productName = await db.getProductNames()
    if id == None:
        for i in range(len(userAuth)):
            auth_data.append({
                'product_name': productName[int(userAuth[i][2])], 
                'product_id': int(userAuth[i][2]),
                'domain': userAuth[i][4], 
                'status': userAuth[i][3], 
                'key': userAuth[i][5], 
                'time': userAuth[i][7]
                })
    else:
        for i in range(len(userAuth)):
            if str(userAuth[i][2]) == id:
                auth_data.append({
                    'product_name': productName[int(userAuth[i][2])], 
                    'product_id': int(userAuth[i][2]),
                    'domain': userAuth[i][4], 
                    'status': userAuth[i][3], 
                    'key': userAuth[i][5], 
                    'time': userAuth[i][7]
                    })
        if len(auth_data) == 0:
            data = {
                'code': 40004,
                'data': [],
                'msg': "未查询到数据"
            }
            return data
    data = {
        'code': 200,
        'data': auth_data,
        'msg': ""
    }
    return data