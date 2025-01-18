"""
## 海枫授权系统 小工具 Tool
为海枫授权系统定制的小功能模块。
"""

from nicegui import ui, app
from typing import List
import os
import random
import string
import hashlib
import binascii
from datetime import datetime
import pkg.log

# 控制台输出
async def echoLog(title="Powered By HeyAuth", background="#3983e2", content="https://auth.yxqi.cn") -> None:
     '''
     在控制台输出内容，需要在协程中运行

     :param title: 标题(日志左侧)
     :type title: str
     :param background: 背景颜色(日志左侧，推荐用不同颜色做日志分级)
     :type background: str
     :param content: 内容(日志右侧)
     :type content: str
     '''
     # 来自CoreNext主题  console.log("%c               %c                ", "color:#fff;background:      #3983e2     ;padding:5px 0;", "color:#eee;background:#f0f0f0;padding:5px 10px;");
     ui.run_javascript('console.log("%c ' + title + ' %c ' + content + '", "color:#fff;background:' + background + ';padding:5px 0;", "color:#eee;background:#f0f0f0;padding:5px 10px;");')

# 哈希值获取
def get_md5(s: str = None) -> str | None:
        md5 = hashlib.md5()
        if s != None:
            md5.update(s.encode('utf-8'))
            return md5.hexdigest()
        else:
            return None

def hash_password(password: str) -> str:
    """
    生成密码的加盐哈希值。

    :param password: 需要哈希的原始密码
    :type password: str
    :return: 包含盐值和哈希值的字符串
    :rtype: str

    使用SHA-256和PBKDF2算法对密码进行加盐哈希,返回盐值和哈希值的组合。
    """
    salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')
    pwdhash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    pwdhash = binascii.hexlify(pwdhash)
    return (salt + pwdhash).decode('ascii')

def verify_password(stored_password: str, provided_password: str) -> bool:
    """
    验证存储的密码哈希值与用户提供的密码是否匹配。

    :param stored_password: 存储的密码哈希值(包含盐值)
    :type stored_password: str
    :param provided_password: 用户提供的密码
    :type provided_password: str
    :return: 如果密码匹配返回True,否则返回False
    :rtype: bool

    从存储的密码哈希中提取盐值,使用相同的哈希算法验证用户提供的密码。
    """
    salt = stored_password[:64]
    stored_password = stored_password[64:]
    pwdhash = hashlib.pbkdf2_hmac('sha256', 
                                  provided_password.encode('utf-8'), 
                                  salt.encode('ascii'), 
                                  100000)
    pwdhash = binascii.hexlify(pwdhash).decode('ascii')
    return pwdhash == stored_password

# 生成4-6位数的验证码
def generate_code(length: int) -> str:
    if length > 6:
        raise ValueError("验证码长度不能超过6位数")
    # 先生成一个6位数的随机数
    key = str(random.randint(100000, 999999))
    # 根据length取前length位
    code = key[:length]
    return code

# 检查字符串是否仅包含数字、字母、减号和下划线
def check_string(s) -> bool:
    # 使用集合来存储所有允许的字符
    allowed_chars = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_@.')
    # 将输入字符串转换成集合，去除空格
    input_chars = set(s.replace(" ", ""))
    # 判断输入的字符集合是否完全由允许的字符集合组成
    return input_chars.issubset(allowed_chars)

# 检查是或否
def checkingToF(value) -> bool:
     if value == [('False',)]:
        return False
     else:
        return True

# 为管理员生成密码
def generate_password(length) -> str:
    # 定义密码字符集，大小写字母和数字
    characters = string.ascii_letters + string.digits
    # 随机选择length个字符，生成密码
    password = ''.join(random.choice(characters) for i in range(length))
    return password

# 易支付获取签名
def getSign(sign_key, params) -> str:
        """
        易支付获取签名

        直接传入构建请求的params即可，传入后会自动进行排序并生成签名

        :param sign_key: 易支付密钥
        :param params: 请求参数字典
        :return: 生成的签名字符串
        :note: sign和sign_type字段以及空值不参与签名，会自动过滤
        """
        # 对参数进行排序
        sorted_params = sorted(params.items())
        sign_str = ''

        # 遍历排序后的参数，将key=value&拼接起来
        for k, v in sorted_params:
            # 如果k不是sign或sign_type，且v不为空，则拼接
            if k != 'sign' and k != 'sign_type' and v != '':
                sign_str += f'{k}={v}&'
        # 去掉拼接后的参数末尾的&
        sign_str = sign_str[:-1]
        # 将sign_str和易支付密钥拼接起来
        sign_str += sign_key
        # 对拼接后的字符串进行md5加密
        sign = hashlib.md5(sign_str.encode()).hexdigest()

        # 返回加密后的字符串
        return sign

def link_target(name: str, offset: str = '0') -> ui.link_target:
    """Create a link target that can be linked to with a hash."""
    target = ui.link_target(name).style(f'position: absolute; top: {offset}; left: 0')
    assert target.parent_slot is not None
    target.parent_slot.parent.classes('relative')
    return target

def section_heading(subtitle_: str, title_: str) -> None:
    """Render a section heading with a subtitle."""
    ui.label(subtitle_).classes('md:text-lg font-bold font-blue')
    ui.markdown(title_).classes('text-3xl md:text-5xl font-bold mt-[-12px] fancy-em')

def features(icon: str, title_: str, items: List[str]) -> None:
    """Render a list of features."""
    with ui.column().classes('gap-1'):
        ui.icon(icon).classes('max-sm:hidden text-3xl md:text-5xl mb-3 text-primary opacity-80')
        ui.label(title_).classes('font-bold mb-3')
        ui.markdown('\n'.join(f'- {item}' for item in items)).classes('bold-links arrow-links -ml-4')

def timestamp(time = "") -> int:
    time = time if time else datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    dt = datetime.strptime(time, '%Y-%m-%d %H:%M:%S')
    return int(dt.timestamp())

if __name__ == '__main__':
    print(hash_password('11111111'))