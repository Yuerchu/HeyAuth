'''
Author: 于小丘 海枫
Date: 2024-10-02 15:23:34
LastEditors: Yuerchu admin@yuxiaoqiu.cn
LastEditTime: 2024-12-01 18:23:07
FilePath: /HeyAuth/api/user.py
Description: 海枫授权系统 用户 API 路由 User API

Copyright (c) 2018-2024 by 于小丘Yuerchu, All Rights Reserved. 
'''


from nicegui import APIRouter, app
from pydantic import BaseModel
from fastapi import HTTPException, status, Response
from pkg.model import database as database
import pkg.tool
import pkg.log as log
import traceback

userApiRouter = APIRouter(prefix='/api/user', 
                          responses={404: {"description": "Not found"}},
                          tags=['用户路由'])

class apiLogin(BaseModel):
    username: str | None = None
    password: str | None = None

@userApiRouter.post(path='/login',
                    summary='用户登录',
                    description='此API用于用户登录。',
                    responses={
                        200: {"description": "登录成功",
                              "content": {
                                "application/json": {
                                    "example": {
                                        "code": 200, 
                                        "msg": "登录成功", 
                                        "status": "ok"
                                        },
                                    },
                                },
                            }, 
                        400: {"description": "错误的请求，可能的情况：`账号或密码为空`",
                              "content": {
                                "application/json": {
                                    "example": {
                                        "code": 40006, 
                                        "msg": "账号或密码不能为空", 
                                        "status": "error"
                                        },
                                    },
                                },
                            }, 
                        401: {"description": "未通过用户登录，可能的情况为：`用户名或密码错误`",
                              "content": {
                                "application/json": {
                                    "example": {
                                        'code': 40005,
                                        'msg': '用户名或密码错误',
                                        'status': 'error'
                                        },
                                    },
                                },
                            },
                        403: {"description": "服务器拒绝访问，可能的情况为：`账号已被封禁`、`账号未验证`",
                              "content": {
                                "application/json": {
                                    "example": {
                                        'code': 40001,
                                        'msg': '账号已被封禁',
                                        'status': 'error'
                                        },
                                    },
                                },
                            },
                        404: {"description": "未找到，可能的情况为：`账号不存在`",
                              "content": {
                                "application/json": {
                                    "example": {
                                        'code': 40004,
                                        'msg': '账号不存在',
                                        'status': 'error'
                                        },
                                    },
                                },
                            },
                        422: {"description": "请求格式正确，但是由于语义错误，无法响应",
                              "content": {
                                "application/json": {
                                    "example": {
                                        'code': 40003,
                                        'msg': '账号异常',
                                        'status': 'error'
                                        },
                                    },
                                },
                            }
                    })
async def auth(loginner: apiLogin, response: Response):
    db = database()
    # 账号密码为空的判断
    if loginner.username == '' \
    or loginner.password == '':
        # 提示用户名或密码错误
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {
            'code': 40006,
            'msg': '账号或密码不能为空',
            'status': 'error'
            }
    # 数据库查询
    pwd = await db.getUserPassword(account=loginner.username)
    # 如果没有密码，就说明账号不存在
    if pwd == 'None':
        response.status_code = status.HTTP_404_NOT_FOUND
        return {
                'code': 40004,
                'msg': '账号不存在',
                'status': 'error'
                }
    password_code = pkg.tool.hash_password(loginner.password)
    if pwd != password_code:
        # 提示用户名或密码错误
        response.status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
        return {
            'code': 40005,
            'msg': '用户名或密码错误',
            'status': 'error'
            }
    # 获取用户id
    user_id = await db.getUserId(username=loginner.username)
    # 获取用户状态
    user_status = await db.getUserStatus(id=user_id)
    if user_status == 'ok':
        # 获取用户昵称
        nickname = await db.getUserNickName(id=user_id)
        # 存储用户信息
        app.storage.user.update({
                'id': user_id,
                'username': loginner.username,
                'nickname': nickname,
                'authenticated': True
            })
        return {
            'code': 200,
            'msg': '登录成功',
            'status': 'ok'
            }
    elif user_status == 'ban':
        response.status_code = status.HTTP_403_FORBIDDEN
        return {
            'code': 40001,
            'msg': '账号已被封禁',
            'status': 'error'
            }
    elif user_status == 'verify':
        response.status_code = status.HTTP_403_FORBIDDEN
        return {
            'code': 40002,
            'msg': '账号未验证',
            'status': 'error'
            }
    else:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {
            'code': 40003,
            'msg': '账号异常',
            'status': 'error'
            }

    
@userApiRouter.get('/logout',
                   summary='用户注销',
                   description='此API用于用户注销。')
async def logout():
    app.storage.user.clear()
    return {
        'code': 200,
        'msg': '注销成功',
        'status': 'ok'
        }

@userApiRouter.get('/auth',
                   summary='获取当前用户所有授权信息',
                   description='此API用于用户授权，需要登录后才可使用')
async def auth():
    if app.storage.user.get('authenticated') != True:
        return {
            'code': 40001,
            'msg': '未登录',
            'status': 'error'
            }
    else:
        # 获取当前用户ID
        user_id = app.storage.user.get('id')

        # 获取授权
        db = database()
        UserAuth = await db.getUserAuthsB(id=user_id)
        
        auth_data = []
        productName = await db.getProductNames()
        for i in range(len(UserAuth)):
            auth_data.append({
                'product_name': productName[int(UserAuth[i][2])], 
                'product_id': int(UserAuth[i][2]),
                'domain': UserAuth[i][4], 
                'status': UserAuth[i][3], 
                'key': UserAuth[i][5], 
                'time': UserAuth[i][7]
            })
        data = {
            'code': 200,
            'data': auth_data,
            'msg': ""
        }
        return data