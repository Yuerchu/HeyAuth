'''
Author: 于小丘 海枫
Date: 2024-10-02 15:23:34
LastEditors: Yuerchu admin@yuxiaoqiu.cn
LastEditTime: 2024-10-25 12:04:41
FilePath: /HeyAuth/pkg/easyPay.py
Description: 海枫授权系统 彩虹易支付组件

Copyright (c) 2018-2024 by 于小丘Yuerchu, All Rights Reserved. 
'''


from pkg.model import database
import pkg.log as log
import pkg.tool as tool
import requests

class easyPay:
    async def __init() -> dict:
        pay_url = str(await easyPay.__dbgetter('easyPayUrl'))
        pay_ID = str(await easyPay.__dbgetter('easyPayID'))
        pay_Key = str(await easyPay.__dbgetter('easyPayKey'))
        return {'pay_Url': pay_url, 'pay_ID': pay_ID, 'pay_Key': pay_Key}

    async def __dbgetter(param: str) -> str:
        db = database()
        result = await db.getSetting(param)
        res = str(result[0][0])
        return res

    async def checkInfo(self):
        '''
        获取商户信息
        '''
        payInfo = await easyPay.__init()
        url = payInfo['pay_Url'] + '/api.php?act=query&pid=' + payInfo['pay_ID'] + '&key=' + payInfo['pay_Key']
        response = requests.get(url)
        # 状态码响应
        if response.status_code == 200:
            response = response.json()
            # 判断是否成功
            if response['code'] == 1:
                # 将数据写入self
                self.active = response['active']
                self.money = response['money']
                self.type = response['type']
                self.account = response['account']
                self.username = response['username']
                self.orders = response['orders']
                self.orders_today = response['orders_today']
                self.orders_lastday = response['orders_lastday']
                return response
            else:
                log.error()
    
    async def submitPay_v1(user_id, product_id, out_trade_no, notify_url, return_url, name, money, *args, **kwargs):
        '''
        ## 页面跳转支付 V1
        :param user_id: 用户ID
        :param product_id: 商品ID
        :param out_trade_no: 订单号
        :param notify_url: 支付成功回调地址
        :param return_url: 支付成功跳转地址
        :param name: 商品名称
        :param money: 商品价格
        :param args kwargs: 其他参数(将会传递给db.addOrder方法)

        :return: 支付URL

        '''
        payInfo = await easyPay.__init()
        # 构造支付Params
        params = {
            'pid': payInfo['pay_ID'],
            'out_trade_no': out_trade_no,
            'notify_url': notify_url,
            'return_url': return_url,
            'name': name,
            'money': money,
            'sign_type': 'MD5'
        }
        # 对params进行签名
        params['sign'] = tool.getSign(params=params, sign_key=str(payInfo['pay_Key']))
        # 将数据写入数据库
        db = database()
        await db.addOrder(
            user_id=user_id, 
            product_id=product_id, 
            product_name=name,
            price=money, payType='easyPay', 
            order_id=out_trade_no,
            *args, **kwargs)
        # 返回支付URL
        return payInfo['pay_Url'] + '/submit.php?' + '&'.join([f'{k}={v}' for k, v in params.items()])
    

if __name__ == '__main__':
    import asyncio
    try:
        Pay = easyPay()
        asyncio.run(Pay.submitPay_v1(out_trade_no='123456789', name='测试商品', money='0.01'))
    except:
        pass