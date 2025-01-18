'''
Author: 于小丘 海枫
Date: 2024-09-12 23:11:51
LastEditors: Yuerchu admin@yuxiaoqiu.cn
LastEditTime: 2024-12-26 23:12:16
FilePath: /HeyAuth/api/easypay_return.py
Description: 海枫授权系统 易支付回调路由 EasyPay Return

Copyright (c) 2018-2024 by 于小丘Yuerchu, All Rights Reserved. 
'''


from nicegui import APIRouter, ui
from pydantic import BaseModel
from pkg.model import database
from fastapi import BackgroundTasks, HTTPException
from fastapi.responses import PlainTextResponse
import asyncio
import pkg.log as log
import pkg.emailer
import traceback
import pkg.tool as tool

db = database()

async def updateOrderStatus(out_trade_no, trade_status, money):
    """
    更新订单状态。

    :param out_trade_no: 订单号
    :type out_trade_no: str
    :param trade_status: 交易状态
    :type trade_status: str
    :param money: 交易金额
    :type money: str
    """
    try:
        # 设置订单状态
        conn = await db.setOrderStatus(out_trade_no, trade_status)
        # 获取产品信息
        productInfo = await db.getProductInfo(conn['product_id'])

        # 添加授权行
        await db.addLine(
            product_id=conn['product_id'], 
            user_id=conn['user_id'],
            number=int(productInfo[8]),
            change=int(productInfo[9]))
        # 将用户id转换为整数
        conn['user_id'] = int(conn['user_id'])
        # 获取用户邮箱
        usrEmail = str(await db.getUserEmail(conn['user_id']))
        # 发送产品邮件
        await pkg.emailer.sendProductEmail(
            email=usrEmail,
            product_name=productInfo[1],
            pay_id=out_trade_no,
            product_price=money,
            pay_time=conn['create_at'])
    except Exception as e:
        # 处理异常
        log.error('Error undating order status: ', e)


authApiRouter = APIRouter(prefix='/api/pay/easypay', 
                          responses={404: {"description": "Not found"}},
                          tags=['易支付回调'])

# 同步回调（前端回调）
@authApiRouter.get('/f_return')
async def f_return(
    pid: int, 
    trade_no: str, 
    out_trade_no: str, 
    type: str, 
    name: str, 
    money: str, 
    trade_status: str, 
    sign: str, 
    sign_type: str):
    # 不支持非 MD5 签名
    if sign_type != "MD5":
        raise HTTPException(status_code=403, detail='未知的签名类型')

    # 验证签名
    params = {
        'pid': pid,
        'trade_no': trade_no,
        'out_trade_no': out_trade_no,
        'type': type,
        'name': name,
        'money': money,
        'trade_status': trade_status
    }
    sign_key = await db.getSetting('easyPayKey')
    sign_key = sign_key[0][0]
    if tool.getSign(params=params, sign_key=sign_key) != sign:
        raise HTTPException(status_code=403, detail='签名验证失败')
    
    # 签名验证通过，开始处理订单
    orderInfo = await db.getOrderInfo(trade_no)
    if orderInfo[6] == 'TRADE_SUCCESS':
        ui.navigate.to('/dash')

# 异步回调（后端回调）
@authApiRouter.get('/b_return', response_class=PlainTextResponse)
async def b_return(
    pid: int, 
    trade_no: str, 
    out_trade_no: str, 
    type: str, 
    name: str, 
    money: str, 
    trade_status: str, 
    sign: str, 
    sign_type: str):
    # 验证签名
    if sign_type != "MD5":
        raise HTTPException(status_code=403, detail='未知的签名类型')

    # 验证签名
    params = {
        'pid': pid,
        'trade_no': trade_no,
        'out_trade_no': out_trade_no,
        'type': type,
        'name': name,
        'money': money,
        'trade_status': trade_status
    }
    sign_key = await db.getSetting('easyPayKey')
    sign_key = sign_key[0][0]
    if tool.getSign(params=params, sign_key=sign_key) != sign:
        raise HTTPException(status_code=403, detail='签名验证失败')
    
    # 交易不成功的判断
    if trade_status != 'TRADE_SUCCESS':
        #TODO:交易失败
        pass
    
    # 防止多次发起请求
    orderInfo = await db.getOrderInfo(trade_no)
    if orderInfo[6] == 'TRADE_SUCCESS':
        raise HTTPException(status_code=403, detail='禁止重复发起请求')

    # 后台处理相关任务
    BackgroundTasks.add_task(updateOrderStatus, out_trade_no, trade_status, money)

    # 向易支付回调 HeyAuth 已经成功接收
    return "success"