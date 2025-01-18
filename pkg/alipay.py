'''
Author: 于小丘 海枫
Date: 2024-08-25 21:45:55
LastEditors: Yuerchu admin@yuxiaoqiu.cn
LastEditTime: 2024-09-29 19:15:41
FilePath: /HeyAuth/pkg/alipay.py
Description: 支付宝当面付组件

Copyright (c) 2018-2024 by 于小丘Yuerchu, All Rights Reserved. 
'''


import requests
import json

debug = True

if debug:
    url = 'https://openapi-sandbox.dl.alipaydev.com/gateway.do'
else:
    url = 'https://openapi.alipay.com/gateway.do'

params = {
    'charset':'UTF-8',                      # 请求使用的编码格式，如utf-8,gbk,gb2312等
    'method': 'alipay.trade.precreate',     # 接口方法
    'format': 'json',                       # 仅支持json
    'sign': '${sign}',                      # 商户请求参数的签名串
    'app_id': '${appid}',                   # 支付宝分配给开发者的应用ID
    'version': '1.0',                       # 调用的接口版本，固定为：1.0
    'sign_type': 'RSA2',                    # 商户生成签名字符串所使用的签名算法类型，目前支持RSA2和RSA，推荐使用RSA2
    'timestamp': '${now}'                   # 发送请求的时间，格式"yyyy-MM-dd HH:mm:ss"
    }

payload = {
    'app_auth_token': '${app_auth_token}',
    'biz_content': json.dumps({
        "out_trade_no": "20150320010101001",        # 商户订单号
        "total_amount": "88.88",                    # 订单总金额，单位为元，精确到小数点后两位，取值范围[0.01,100000000]。
        "subject": "Iphone6 16G",                   # 订单标题
        "product_code": "FACE_TO_FACE_PAYMENT",     # 销售产品码，默认为
        "seller_id": "2088102146225135",
        "body": "Iphone6 16G",
        "goods_detail": [
            {
                "goods_name": "ipad",
                "quantity": 1,
                "price": "2000",
                "goods_id": "apple-01",
                "goods_category": "34543238",
                "categories_tree": "124868003|126232002|126252004",
                "show_url": "http://www.alipay.com/xxx.jpg"
            }
        ],
        "extend_params": {
            "sys_service_provider_id": "2088511833207846",
            "specified_seller_name": "XXX的跨境小铺",
            "card_type": "S0JP0000"
        },
        "business_params": {
            "mc_create_trade_ip": "127.0.0.1"
        },
        "discountable_amount": "80.00",
        "store_id": "NJ_001",
        "operator_id": "yx_001",
        "terminal_id": "NJ_T_001",
        "merchant_order_no": "20161008001"
    })
}

response = requests.post(url, params=params, data=payload)

print(response.text)