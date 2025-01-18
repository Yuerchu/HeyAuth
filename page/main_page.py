'''
Author: 于小丘 海枫
Date: 2024-10-02 15:23:34
LastEditors: Yuerchu admin@yuxiaoqiu.cn
LastEditTime: 2024-12-05 00:08:51
FilePath: /HeyAuth/page/main_page.py
Description: 海枫授权系统 首页 Main_Page

Copyright (c) 2018-2024 by 于小丘Yuerchu, All Rights Reserved. 
'''

# 防止被独立启动
if __name__ == '__main__':
    print("不支持单测，请使用Main.py启动")
    exit(1)

from nicegui import ui, app
from pkg.model import database as database
from fastapi import Request
from pkg.tool import *
import pkg.log as log


async def dbgetter(param: str) -> str:
    db = database()
    result = await db.getSetting(param)
    res = str(result[0][0])
    return res

def create() -> None:
    @ui.page('/')
    async def main_page(request: Request, ref="") -> None:
        await echoLog()
        siteDomain = request.base_url.hostname
            
        dark_mode = ui.dark_mode(value=app.storage.browser.get('dark_mode'), on_change=lambda e: ui.run_javascript(f'''
                                fetch('/dark_mode', {{
                                    method: 'POST',
                                    headers: {{'Content-Type': 'application/json'}},
                                    body: JSON.stringify({{value: {e.value}}}),
                                }});
                            '''))
        with ui.header() \
            .classes('items-center duration-300 py-2 px-5 no-wrap') \
            .style('box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1)'):

            ui.button(icon='menu').props('flat color=white round')
            siteName = await dbgetter('site_name')
            if siteDomain == "127.0.0.1" or siteDomain == "localhost":
                ui.button(text=siteName+" (本地模式)").classes('text-lg').props('flat color=white')
            else:
                ui.button(text=siteName).classes('text-lg').props('flat color=white')

            ui.space()

            # 语言切换
            with ui.dropdown_button('简体中文', auto_close=True).props('flat color=white'):
                ui.item('简体中文', on_click=lambda: ui.run_javascript('window.location.href = "/?lang=zh-CN"'))
                ui.item('繁體中文', on_click=lambda: ui.run_javascript('window.location.href = "/?lang=zh-TW"'))
                ui.item('English', on_click=lambda: ui.run_javascript('window.location.href = "/?lang=en-US"'))

            # 主题切换
            with ui.element().tooltip('主题切换'):
                ui.button(icon='dark_mode', on_click=lambda: dark_mode.set_value(None)) \
                    .props('flat fab-mini color=white').bind_visibility_from(dark_mode, 'value', value=True)
                ui.button(icon='light_mode', on_click=lambda: dark_mode.set_value(True)) \
                    .props('flat fab-mini color=white').bind_visibility_from(dark_mode, 'value', value=False)
                ui.button(icon='brightness_auto', on_click=lambda: dark_mode.set_value(False)) \
                    .props('flat fab-mini color=white').bind_visibility_from(dark_mode, 'value', lambda mode: mode is None)

        with ui.column().classes('mx-auto py-16').style('width: 70%; max-width: 800px'):
            ui.label(await dbgetter(param='mainPage_title')) \
                .classes('mx-auto text-4xl sm:text-5xl md:text-6xl font-bold fancy-em')
            ui.label(await dbgetter(param='mainPage_subtitle')) \
                .classes('mx-auto bg-clip-text text-transparent bg-gradient-to-r from-pink-500 to-violet-500 text-4xl sm:text-5xl md:text-6xl font-bold fancy-em')
            ui.label(await dbgetter(param='mainPage_description')) \
                .classes('mt-6 text-lg text-center leading-8 text-gray-600')
            if not app.storage.user.get('authenticated', False):
                ui.button('登录/注册', on_click=lambda: (ui.navigate.to('/login'))).classes('mx-auto')
            else:
                with ui.row(align_items='center').classes('mx-auto'):
                    ui.button('开始使用', on_click=lambda: (ui.navigate.to('/dash'))).classes('mx-auto')
                    with ui.button(text='购买授权', 
                              on_click=lambda: (ui.run_javascript('window.open("https://xiaoqiu.in/product/heyuth/")'))):
                        ui.badge('限时折扣', color='red').props('floating')
                ui.button(text='查看文档', icon='arrow_forward', 
                          on_click=lambda: (ui.run_javascript('window.open("https://heyauth.yxqi.cn/")'))) \
                    .classes('mx-auto').props('flat')
        
        with ui.column().classes('w-full p-8 lg:p-16 bold-links arrow-links max-w-[1600px] mx-auto'):
            link_target('features', '-50px')
            section_heading('满足你的任何需求', '稳定、安全、可信的产品和服务')
            with ui.row().classes('w-full text-lg leading-tight grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-8'):
                features('badge', '双端授权', [
                    '支持3种接口B端授权',
                    '支持2种接口C端授权',
                    '授权后无二次收费，可放心使用',
                    '授权系统本身支持3种启动方式',
                ])
                features('apps', '功能完善', [
                    '包含授权系统常用的所有功能',
                    '拥有众多原创功能及众多模板',
                    '分钟级授权密钥自动切换',
                    '可关闭自带前端以Core模式运行',
                ])
                features('devices', '多端支持', [
                    '前端Material Design设计，美观优雅',
                    '后端基于FastAPI，性能可与Golang媲美',
                    '响应式设计，从手机到电脑均可完美显示',
                    '支持绝大多数现代浏览器',
                ])
                features('thumb_up_alt', '上手容易', [
                    '完善的在线教学文档，有详细的[官方对接文档](https://heyauth.yxqi.cn/)',
                    '提供授权用户专属技术服务群',
                    '三行代码即可完成*HeyAuth*的部署',
                    '(远期规划)支持与其他授权系统互相迁移授权数据',
                ])
                features('price_check', '低成本', [
                    '帮您省去了产品、设计等人员的工作',
                    '一次永久授权，小版本终身免费更新，大版本成本价更新',
                    '2h2G3M的服务器也可轻松运行',
                    '证明是*在校初中/高中/大学生*可享受9折优惠',
                ])
                features('engineering', '售后保障', [
                    '标准版与开源版独立售后群',
                    '完善的售后保障，5x8小时服务',
                    '版本持续更新，满足大众需求',
                    '针对当前大版本的所有支持',
                ])
        
        ui.label("我们的合作伙伴").classes('mx-auto text-lg font-bold fancy-em py-0')
        ui.label('排名不分先后').classes('mx-auto fancy-em text-zinc-700 py-0')
        with ui.row(align_items='center').classes('mx-auto'):
            ui.button('于小丘Blog', on_click=lambda: ui.navigate.to('https://www.yxqi.cn', new_tab=True)).classes('transition ease-in-out delay-150 hover:-translate-y-1 hover:scale-110 duration-300').props('flat')
            ui.button('初一小盏', on_click=lambda: ui.navigate.to('https://www.vxras.com', new_tab=True)).classes('transition ease-in-out delay-150 hover:-translate-y-1 hover:scale-110 duration-300').props('flat')
            ui.button('子比主题', on_click=lambda: ui.navigate.to('https://www.zibll.com/?ref=35922', new_tab=True)).classes('transition ease-in-out delay-150 hover:-translate-y-1 hover:scale-110 duration-300').props('flat')
            ui.button('苏晨博客网', on_click=lambda: ui.navigate.to('https://www.scbkw.com', new_tab=True)).classes('transition ease-in-out delay-150 hover:-translate-y-1 hover:scale-110 duration-300').props('flat')
            ui.button('炙焰技术网', on_click=lambda: ui.navigate.to('https://aut.zhiyanx.cn', new_tab=True)).classes('transition ease-in-out delay-150 hover:-translate-y-1 hover:scale-110 duration-300').props('flat')
            ui.button('泽汐阁', on_click=lambda: ui.navigate.to('https://www.zexige.com/', new_tab=True)).classes('transition ease-in-out delay-150 hover:-translate-y-1 hover:scale-110 duration-300').props('flat')
            ui.button('允梦网络', on_click=lambda: ui.navigate.to('https://www.mengdo.cn', new_tab=True)).classes('transition ease-in-out delay-150 hover:-translate-y-1 hover:scale-110 duration-300').props('flat')
            ui.button('星辰解忧工作室', on_click=lambda: ui.navigate.to('https://xcjygzs.cn', new_tab=True)).classes('transition ease-in-out delay-150 hover:-translate-y-1 hover:scale-110 duration-300').props('flat')
        
        with ui.card().classes('mx-auto'):
            with ui.row():
                ui.link(text=await dbgetter(param='icp_beian'), target='https://beian.miit.gov.cn/').classes('text-zinc-700 text-h7')
                ui.link(text=await dbgetter(param='ga_beian'), target='https://beian.mps.gov.cn/#/').classes('text-zinc-700 text-h7')