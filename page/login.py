'''
Author: 于小丘 海枫
Date: 2024-10-02 15:23:34
LastEditors: Yuerchu admin@yuxiaoqiu.cn
LastEditTime: 2024-12-26 22:44:52
FilePath: /HeyAuth/page/login.py
Description: 海枫授权系统 登录界面 Login

Copyright (c) 2018-2024 by 于小丘Yuerchu, All Rights Reserved. 
'''

# 防止被独立启动
if __name__ == '__main__':
    print("不支持单测，请使用main.py启动")
    exit(1)

from nicegui import ui, app
from pkg.tool import *
from typing import Optional
import traceback
import asyncio
import pkg.heyCaptcha as heyCaptcha
from pkg import log
from fastapi import BackgroundTasks
from fastapi.responses import RedirectResponse
from pkg.model import database as database
import pkg.emailer as emailer
import template.dialog

def create() -> Optional[RedirectResponse]:
    @ui.page('/login')
    async def session():
        await echoLog()
        # 检测是否已登录
        if app.storage.user.get('authenticated', False):
            return ui.navigate.to('/dash')
        
        dark_mode = ui.dark_mode(value=app.storage.browser.get('dark_mode'), on_change=lambda e: ui.run_javascript(f'''
                                fetch('/dark_mode', {{
                                    method: 'POST',
                                    headers: {{'Content-Type': 'application/json'}},
                                    body: JSON.stringify({{value: {e.value}}}),
                                }});
                            '''))
        
        # 防止移动端缩放
        ui.add_head_html(
            '<meta content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=0;" name="viewport" />'
        )
        ui.add_head_html(
            '<meta name="apple-mobile-web-app-capable" content="yes"> '
        )
        
        # 获取相关信息
        db = database()
        ui.page_title('登录/注册 ' + await db.getSiteName())
        async def try_login() -> None:

            try:
                if username.value == '' or password.value == '':
                    # 提示用户名或密码错误
                    ui.notify('账号或密码不能为空', color='negative')
                    return
                
                # 数据库查询
                pwd = await db.getUserPassword(account=username.value)
                
                if pwd == 'None':
                    ui.notify('账号不存在', color='negative')
                    return
                
                # 验证密码
                if not verify_password(pwd, password.value):
                    ui.notify('密码错误', color='negative')
                    return
                
                # 获取用户id
                user_id = await db.getUserId(username=username.value)
                # 获取用户状态
                user_status = await db.getUserStatus(id=user_id)

                if user_status == 'ban':
                    ui.notify('账号已被封禁', color='negative')
                elif user_status == 'verify':
                    ui.notify('账号未验证，如无法验证请前往注册页面重新注册账号', color='negative')
                elif user_status == 'ok':
                    # 获取用户昵称
                    nickname = await db.getUserNickName(id=user_id)
                    # 获取用户QQ
                    UserQQ = await db.getUserQQ(id=user_id)
                    # 存储用户信息
                    app.storage.user.update({
                            'id': user_id,
                            'username': username.value,
                            'nickname': nickname,
                            'qq': UserQQ,
                            'authenticated': True
                        })
                    # 跳转到用户上一页
                    ui.navigate.to(app.storage.user.get('referrer_path', '/'))

                else: ui.notify('账号异常', color='negative')
            except Exception as e:
                error = traceback.format_exc()
                ui.notify('系统异常，请联系站点管理员', color='negative')
                log.error(str(error))
        
        async def sendRegEmail():
            email = signup_username.value

            # 处理不允许注册的情况
            if not email: ui.notify('邮箱不能为空', color='negative'); return
            if await db.getUserExist(account=email): ui.notify('该账号已注册', color='negative'); return
            
            # 发送邮件
            code = generate_code(6)
            # db.addCode(email=email, code=code)
            try:
                response = await emailer.sendCodeEmail(method="reg", email=email, code=code)
                if response == None:
                    await db.addUser(account=email, code=code)
                    ui.notify('发送成功，请查收邮件', color='positive')
                else:
                    log.error("邮件发送失败:\n" + response)
                    ui.notify('邮件发送失败:' + response, color='negative')  
            except:
                log.error("邮件发送失败:\n" + traceback.format_exc())
                ui.notify('邮件发送失败:' + traceback.format_exc(), color='negative')
                
                
        
        async def sendforgetEmail():
            email = forget_username.value

            # 处理不允许找回密码的情况
            if not email: ui.notify('邮箱不能为空', color='negative'); return
            if not await db.getUserExist(account=email): ui.notify('该账号不存在', color='negative'); return
            
            # 发送邮件
            code = generate_code(6)
            await db.setCode(user_name=email, code=code)
            response = await emailer.sendCodeEmail(method="forget", email=email, code=code)
            if response == None: ui.notify('发送成功，请查收邮件', color='positive')
            else: ui.notify('发送失败，请联系管理员', color='negative')
                
        
        async def register():
            # 检查用户名与密码框是否为空
            if signup_nickname.value == '' \
            or signup_username.value == '' \
            or signup_password.value == '' \
            or signup_password2.value == '' \
            or signup_qq.value == '': ui.notify('请先填写完整', color='negative'); return
            
            elif signup_password.value != signup_password2.value:
                ui.notify('两次密码不一致', color='negative')
                return
            
            elif await db.getUserStatus(account=signup_username.value) == "ok":
                ui.notify('该用户已注册', color='negative')
                return

            elif await db.getUserStatus(account=signup_username.value) == "ban":
                ui.notify('用户被封禁', color='negative')
                return

            # 检查验证码是否正确
            if await db.getUserCode(account=signup_username.value) != int(signup_code.value):
                ui.notify('验证码错误', color='negative')
                return
            
            else:
                # 注册用户
                try:
                    await db.setUserPassVerify(
                        nickName=signup_nickname.value,
                        account=signup_username.value, 
                        password=hash_password(signup_password.value),
                        qq=signup_qq.value)
                    
                except ValueError: ui.notify('当前QQ已被绑定，请更换')
                else: ui.notify('注册成功，请登录', color='positive')
                signup.close()
                
        
        async def fogetPassword():
            # 检查用户名与密码框是否为空
            if forget_username == '' \
            or forget_password.value == '' \
            or forget_password2.value == '':
                ui.notify('邮箱或者密码不能为空', color='negative')

            # 检查两次输入的密码是否一致
            elif forget_password.value != forget_password2.value:
                ui.notify('两次密码不一致', color='negative')
            
            # 获取用户是否注册
            elif await db.getUserStatus(account=forget_username.value) == "ok" \
            or await db.getUserStatus(account=forget_username.value) == "verify":
                # 检查验证码是否正确
                if await db.getUserCode(account=forget_username.value) == int(forget_code.value):
                    # 为用户重置密码
                    await db.setUserPassVerify(account=forget_username.value, password=hash_password(forget_password.value))
                    ui.notify('密码找回成功', color='positive')
                    forget.close()
                else:
                    ui.notify('验证码错误', color='negative')
            elif await db.getUserStatus(account=forget_username.value) == "ban":
                ui.notify('用户被封禁', color='negative')
                    
                
        
        with ui.header() \
            .classes('items-center duration-300 py-2 px-5 no-wrap') \
            .style('box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1)'):

            ui.button(icon='menu').props('flat color=white round')
            ui.button(text='海枫授权系统', on_click=lambda: ui.navigate('/')).classes('text-lg').props('flat color=white')

            ui.space()

            # 主题切换
            with ui.element().classes('max-[420px]:hidden').tooltip('主题切换'):
                ui.button(icon='dark_mode', on_click=lambda: dark_mode.set_value(None)) \
                    .props('flat fab-mini color=white').bind_visibility_from(dark_mode, 'value', value=True)
                ui.button(icon='light_mode', on_click=lambda: dark_mode.set_value(True)) \
                    .props('flat fab-mini color=white').bind_visibility_from(dark_mode, 'value', value=False)
                ui.button(icon='brightness_auto', on_click=lambda: dark_mode.set_value(False)) \
                    .props('flat fab-mini color=white').bind_visibility_from(dark_mode, 'value', lambda mode: mode is None)
            

        # 构建注册账号对话框
        with ui.dialog() as signup, ui.card().style('width: 90%; max-width: 500px'):
            ui.button(icon='gpp_good').props('outline round').classes('mx-auto w-auto shadow-sm w-fill')
            ui.label('注册账号').classes('text-h5 w-full text-center')

            with ui.scroll_area().classes('w-full'):
                signup_nickname = ui.input('昵称').on('keydown.enter').classes('block w-full text-gray-900')
                with ui.row(align_items='center').classes('w-full'):
                    signup_username = ui.input('电子邮箱').on('keydown.enter').classes('w-1/2 flex-grow')
                    ui.button('发送验证码', on_click= lambda: sendRegEmail()).classes('w-auto flex-grow')
                signup_code = ui.input('验证码').classes('w-full')
                signup_password = ui.input('密码', password=True, password_toggle_button=True, 
                                        validation={'密码不能小于6位': lambda value: len(value) > 5, \
                                                    '密码不能超过12位': lambda value: len(value) < 13}) \
                                    .on('keydown.enter').classes('block w-full text-gray-900')
                signup_password2 = ui.input('再次输入密码', password=True, password_toggle_button=True).classes('w-full')
                signup_qq = ui.input('QQ号').on('keydown.enter').classes('block w-full text-gray-900')
                refCode = ui.input('邀请码（选填）').on('keydown.enter').classes('block w-full text-gray-900')

            ui.button("注册", on_click=register) \
                .classes('items-center w-full').props('rounded')
            ui.button("返回", on_click=signup.close).classes('w-full').props('flat rounded')
        
        # 构建找回密码对话框
        with ui.dialog() as forget, ui.card().style('width: 90%; max-width: 500px'):
            ui.button(icon='lock').props('outline round').classes('mx-auto w-auto shadow-sm w-fill')
            ui.label('忘记密码').classes('text-h5 w-full text-center')

            with ui.scroll_area().classes('w-full'):
                with ui.row(align_items='center').classes('w-full'):
                    forget_username = ui.input('电子邮箱').on('keydown.enter').classes('w-1/2 flex-grow')
                    ui.button('发送验证码', on_click=lambda: (asyncio.run(sendforgetEmail()))).classes('w-auto flex-grow')
                forget_code = ui.input('验证码').classes('w-full')
                forget_password = ui.input('密码', password=True, password_toggle_button=True, 
                                        validation={'密码不能小于6位': lambda value: len(value) > 5, \
                                                    '密码不能超过12位': lambda value: len(value) < 13}) \
                                    .on('keydown.enter').classes('block w-full text-gray-900')
                forget_password2 = ui.input('再次输入密码', password=True, password_toggle_button=True).classes('w-full')
            
            ui.button("确认找回密码", on_click=fogetPassword) \
                .classes('items-center w-full').props('rounded')
            ui.button("返回", on_click=forget.close).classes('w-full').props('flat rounded')

        # 创建一个绝对中心的登录卡片
        with ui.card().classes('absolute-center round-lg').style('width: 70%; max-width: 500px'):
            # 登录标签
            ui.button(icon='lock').props('outline round').classes('mx-auto w-auto shadow-sm w-fill')
            ui.label('登录 ' + await db.getSiteName()).classes('text-h5 w-full text-center')
            # 用户名/密码框
            username = ui.input('电子邮箱').on('keydown.enter', try_login) \
                .classes('block w-full text-gray-900').props('rounded outlined')
            password = ui.input('密码', password=True, password_toggle_button=True) \
                .on('keydown.enter', try_login).classes('block w-full text-gray-900').props('rounded outlined')
            
            # 按钮布局
            ui.button('登录', on_click=try_login).classes('items-center w-full').props('rounded')
            with ui.row(align_items='center').classes('w-full'):
                ui.button('忘记密码', on_click=forget.open).props('flat')
                ui.space()
                ui.button('注册账号', on_click=signup.open).props('flat')
        
        # 底部文本
        with ui.card().classes('bottom').classes('absolute bottom-5'):
            ui.label(text=await db.getSetting('bottom_text')).classes('select-none')

if __name__ == '__main__':
    print("不支持单测，请使用main.py启动")
    exit(1)