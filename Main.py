"""
！！！请不要在任何地方引用这个文件，否则会触发回环引用异常！！！
!!! Do not import this library anywhere, otherwise a circular reference exception will be triggered !!!

Author: 于小丘 海枫 Yuerchu HeyFun
Date: 2024-07-28 15:31:46
LastEditors: Yuerchu admin@yuxiaoqiu.cn
LastEditTime: 2024-11-06 01:18:17
FilePath: /HeyAuth/Main.py
Description: 海枫授权系统HeyAuth 主程序Main

Copyright (c) 2018-2024 by 于小丘Yuerchu, All Rights Reserved.
"""


# 先检查一下有没有头铁的哥们把这个库引用了 Check if there is a foolhardy guy who has referenced this library
if not __name__ in {"__main__", "__mp_main__"}:
    raise Exception('说了别引用别引用，会触发回环引用异常，怎么就是不听呢((╬ಠิ﹏ಠิ))'
                    'Do not reference this library, otherwise a circular reference exception will be triggered')

# Main 必须库文件 Required library files
import configparser                                             # 配置文件解析 Config file parser
from fastapi import Request                                     # FastAPI请求(检查客户端相关信息) FastAPI request (check client related information)
from pkg import version                                         # 版本信息 Version information
from fastapi.responses import RedirectResponse                  # 重定向 Redirect
from fastapi.responses import PlainTextResponse                 # 文本响应 Plain text response
from fastapi.responses import JSONResponse                      # JSON响应 JSON response
from starlette.middleware.base import BaseHTTPMiddleware        # FastAPI中间件(OAuth2认证) FastAPI middleware (OAuth2 authentication)
from nicegui import Client, app, ui, __version__                # 前端 Front-end
import traceback                                                # 异常处理 Exception handling
import asyncio                                                  # 异步处理 Asynchronous processing
import logging                                                  # 底层日志 Logging
import os                                                       # 系统操作 System operation

# 自建包文件 Self-built package files
import pkg.log as log                                           # HeyAuth 日志 HeyAuth logging
from pkg.model import database                               # HeyAuth 数据库 HeyAuth database
from pkg.tool import *                                          # HeyAuth 工具 HeyAuth tools

# 其他组件库需要依赖 (防止Cython编译后无法读取依赖)
# Other component libraries need to depend on (prevent Cython compilation from failing to read dependencies)
import io, sys                                                  # 系统IO System IO
import aiosqlite                                                # 异步SQLite Asynchronous SQLite
import random                                                   # 随机数 Random number
import string                                                   # 字符串
import argparse                                                 # 命令行参数 Command line parameters
import hashlib                                                  # 哈希 Hash
import platform                                                 # 平台 Platform
from fastapi import HTTPException                               # FastAPI异常 FastAPI exception
from typing import Literal, Optional                            # 类型提示
from pydantic import BaseModel                                  # Pydantic模型 Pydantic model
import requests                                                 # 请求 Request
import inspect                                                  # 检查 Inspection
import smtplib                                                  # SMTP SMTP
from email.mime.text import MIMEText                            # 邮件 MIMEText
from email.utils import formataddr                              # 邮件 formataddr



# 中间件配置文件
AUTH_CONFIG = {
    "restricted_routes": {'/admin'},
    "login_url": "/login",
    "cookie_name": "session",
    "session_expire": 3600  # 会话过期时间
}

# 登录验证中间件 Login verification middleware
class AuthMiddleware(BaseHTTPMiddleware):
    # 异步处理每个请求
    async def dispatch(self, request: Request, call_next):
        try:
            log.debug(f"Request: {request.url.path},"
                         f"Authenticated: {app.storage.user.get('authenticated')}")
            if not app.storage.user.get('authenticated', False):
                # 如果请求的路径在Client.page_routes.values()中，并且不在unrestricted_page_routes中
                if request.url.path in Client.page_routes.values() \
                and request.url.path in AUTH_CONFIG["restricted_routes"]:
                    log.warning(f"未认证用户尝试访问: {request.url.path}")
                    # 记录用户想访问的路径 Record the user's intended path
                    app.storage.user['referrer_path'] = request.url.path
                    # 重定向到登录页面 Redirect to the login page
                    return RedirectResponse(AUTH_CONFIG["login_url"])
            # 否则，继续处理请求 Otherwise, continue processing the request
            return await call_next(request)

        except Exception as e:
            # 记录错误日志
            log.error(f"Server error: {str(traceback.format_exc())}")
            # 返回适当的错误响应
            return JSONResponse(
                status_code=500,
                content={"detail": "Server error: " + str(e)}
            )
        
# 添加静态文件 Add static files
app.add_static_files('/static/lang', 'lang')

# 异步启动函数 Asynchronous startup function
async def asyncStart():
    db = database()
    await db.init()
    siteName = await db.getSiteName()
    storageSecret = await db.getStrorageSecret()
    siteIcon = await db.getSetting('siteIcon')
    return {"siteName": siteName, "storageSecret": storageSecret, "siteIcon": siteIcon}

# 异常捕获函数 Exception capture function
def onException():
    errorInfo = traceback.format_exc()
    log.warning("程序出现了异常，请启用Debug模式查看详细信息，若屡次出现故障，请复制终端中所有内容并联系admin@yuxiaoqiu.cn，"
                "不要截图Web端，因为那里不包含任何程序异常原因！"
                "程序异常信息：" + str(errorInfo))

# 添加中间件与异常捕获项 Add middleware and exception capture items
app.add_middleware(AuthMiddleware)
app.on_exception(onException)

# 获取默认配置 Get default configuration
def get_default_config():
    """返回默认配置"""
    config = configparser.ConfigParser()
    config.add_section("app")
    default_settings = {
        "host": "0.0.0.0",
        "port": "8080", 
        "loglevel": "info",
        "core": "False",
        "forceResetDatabase": "False",
        "resetAdminPassword": "False"
    }
    for key, value in default_settings.items(): config.set("app", key, value)
    return config

# 加载或创建配置文件 Load or create configuration file
def load_config():
    """加载或创建配置文件"""
    if not os.path.exists("config.ini"):
        log.debug('未检测到配置文件，准备释放...')
        config = get_default_config()
        with open("config.ini", "w") as configfile: config.write(configfile)
    else:
        log.debug('Loading config...')
        config = configparser.ConfigParser()
        config.read('config.ini')
    return config

# 设置日志级别 Set logging level
def setup_logging(config) -> str:
    """设置日志级别"""
    log_levels = {
        'debug': logging.DEBUG,
        'info': logging.INFO,
        'warning': logging.WARNING,
        'error': logging.ERROR
    }
    
    log_level = config.get('app', 'loglevel').lower()
    if log_level not in log_levels:
        log.error(f'无效的日志级别:[red bold]{log_level}[/red bold]，请检查配置文件\n'
                  f'接受的日志级别: [cyan]debug[/cyan] 、 [blue]info[/blue] 、 '
                  f'[yellow]warning[/yellow] 、 [red]error[/red]')
        quit(1)
        
    logging.basicConfig(level=log_levels[log_level])
    log.success(f'seting loggging level: [bold green]{log_level}[/bold green]')
    return log_level

# 加载API路由 Load API routes
def load_routers():
    """加载API路由"""
    import api
    routers = [
        api.user.userApiRouter,
        api.site.siteApiRouter,
        api.auth.authApiRouter,
        api.select.selectApiRouter,
        api.product.productApiRouter,
        api.pirate.pirateApiRouter,
        api.easypay_return.authApiRouter,
    ]
    for router in routers:
        app.include_router(router)

# 加载前端页面 Load front-end pages
def load_pages():
    """加载前端页面"""
    import page
    pages = [
            page.admin,
            page.dash,
            page.user,
            page.login,
            page.main_page
        ]
    for page in pages:
        page.create()

# 启动函数 Startup function
def startup():
    # 显示版本信息
    log.title()
    log.title(f'Version:{version.version}\t\tAuthor:{version.versionAuthor}\t\t'
              f'Website：https://auth.yxqi.cn\n', size='h2')

    # 准备配置文件要在设置日志级别之前
    log.info('Preparing configuration file……')
    config = load_config()  # 先加载配置
    
    global LogLevel
    LogLevel = 'info'
    # 设置日志级别 Set logging level
    LogLevel = setup_logging(config)  # 然后再设置日志级别

    if LogLevel == 'debug':
        from nicegui_toolkit import inject_layout_tool
        inject_layout_tool()

    # 重置管理员密码 Reset the admin password
    if config.get('app', 'resetAdminPassword').lower() == 'true':
        db = database()
        asyncio.run(db.resetAdminPassword())
        log.info('Admin password has been reset.')
        config.set('app', 'resetAdminPassword', 'False')
        quit(code=0)

    log.info('Starting HeyAuth Core……')
    
    # 加载API路由 Load API routes
    load_routers()

    # 加载前端
    if not config.get('app', 'core') == 'True':
        log.info('Preparing to load page routes……')
        log.debug('Front-end version: ' + str(__version__))

        # 导入页面路由
        try: load_pages()
        except:
            with ui.card().classes('absolute-center'):

                # 添加标题
                ui.button(icon='error', color='red').props('outline round').classes('mx-auto w-auto shadow-sm w-fill')
                ui.label('HeyAuth 错误捕获器').classes('text-h5 w-full text-center')
                ui.label('页面启动异常，请检查！').classes('text-bold w-full text-center')
                ui.label('The front-end startup failed. Please check!').classes('text-bold w-full text-center')
                
                ui.label('错误信息：')

                logErrorInfo = ui.log()
                logErrorInfo.push(str(traceback.format_exc()))
                ui.button('向开发者反馈此问题', 
                          on_click=lambda: ui.navigate.to(
                              'mailto:admin@yuxiaoqiu.cn?subject=HeyAuth%20页面启动异常&body=' \
                                +str(traceback.format_exc()))) \
                    .classes('items-center w-full').props('rounded')
    else:
        log.info('Pure backend mode has been enabled.')

    # 暗模式设置 Dark mode setting
    @app.post('/dark_mode')
    async def __post_dark_mode(request: Request) -> None:
        app.storage.browser['dark_mode'] = (await request.json()).get('value')

    # 异步启动函数执行结果
    result = asyncio.run(asyncStart())
    siteName = result['siteName']
    storageSecret = result['storageSecret']
    siteIcon = str(result['siteIcon'][0][0])

    log.info('Starting to listen on port: [blue bold]{}[/blue bold]'.format(config.get('app', 'port')))
    ui.run(
        host=config.get('app', 'host'),
        favicon=siteIcon,
        port=int(config.get('app', 'port')),
        title=siteName,
        storage_secret=storageSecret,
        native=False,
        language='zh-CN',
        fastapi_docs={
            "title": "海枫授权系统 HeyAuth",
            "summary": "海枫授权系统的内置API文档，用于开发者参考，在生产环境中请使用 Debug=False 来关闭此文档。",
            "description": "A short description",
            "version": version.version,
            "terms_of_service": "https://auth.yxqi.cn",
            "contact": {
                "name": "于小丘 广州海枫网络科技",
                "url": "https://www.yxqi.cn",
                "email": "admin@yuxiaoqiu.cn"
            }
        } if LogLevel == 'debug' else False, 
        show_welcome_message=False)


if __name__ in {"__main__", "__mp_main__"}:
    startup()