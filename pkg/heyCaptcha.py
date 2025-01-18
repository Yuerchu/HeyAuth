'''
海枫授权系统 验证码组件 HeyAuth Captcha
---

使用方法：

    >>> import pkg.heyCaptcha
        char, img = pkg.heyCaptcha.HeyCaptcha.get_captcha()
'''

'''
- 作者 Author                 : 于小丘 海枫
- 网址 url                    : xiaoqiu.in
- 制作日期 MakeDate           : 2024-09-20
- 上次修改日期 LastEditTime   : 2024-09-20
- 邮箱 Email                 : admin@yuxiaoqiu.cn
- 项目名 Project             : 海枫授权系统
- 介绍 Description          : 一款针对B+C端的应用授权系统
- 请阅读 Read me            : 感谢您使用海枫授权系统，程序源码有详细的注释，支持二次开发。
- 注意 Remind              : 使用盗版海枫授权系统会存在各种未知风险。支持正版，从我做起！
'''

import sys, getopt
from captcha.image import ImageCaptcha
from random import randint
import base64
from io import BytesIO

class HeyCaptcha:
    @classmethod
    def get_captcha(cls, char: str = None):
        if char == None:
            list = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
                    
                    'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J',
                    'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T',
                    'U', 'V', 'W', 'X', 'Y', 'Z',
                    
                    'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j',
                    'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't',
                    'u', 'v', 'w', 'x', 'y', 'z']
            char = ''
            for i in range(4):
                char += list[randint(0, 61)]
        image = ImageCaptcha().generate_image(char)

        buffered = BytesIO()
        image.save(buffered, format="PNG")
        img = b"data:image/png;base64," + base64.b64encode(buffered.getvalue())

        return char, img
        