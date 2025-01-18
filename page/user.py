'''
Author: 于小丘 海枫
Date: 2024-10-02 15:23:34
LastEditors: Yuerchu admin@yuxiaoqiu.cn
LastEditTime: 2024-11-11 21:07:37
FilePath: /HeyAuth/page/user.py
Description: 海枫授权系统 用户中心 User

Copyright (c) 2018-2024 by 于小丘Yuerchu, All Rights Reserved. 
'''

# 防止被独立启动
if __name__ == '__main__':
    print("不支持单测，请使用main.py启动")
    exit(1)

from nicegui import ui, app
from pkg.model import database as database
from pkg.tool import *

def create() -> None:
    @ui.page('/user')
    async def user_page() -> None:
        return
        await echoLog()
        ui.page_title('用户中心')
        # 创建一个包含绝对居中和项目中心的列
        with ui.card().classes('absolute-center').style('width: 70%; max-width: 500px'):
            # 添加标题
            with ui.row(align_items='center'):
                ui.button(icon='arrow_back', on_click=ui.navigate.back).props('flat color=black')
                ui.label('用户中心').classes('text-h5 text-center')

            with ui.list().classes('w-full').props('padding'):
                with ui.item(on_click=lambda: ui.notify('修改邮箱功能暂未实现')).classes('h-20'):
                    with ui.item_section().props('avatar'):
                        ui.icon('email', color='blue-400')
                    with ui.item_section():
                        ui.item_label('邮箱')
                        ui.item_label('admin@yuxiaoqiu.cn').props('caption')
                    with ui.item_section().props('side'):
                        ui.icon('edit')
                ui.separator()
                with ui.item(on_click=lambda: ui.notify('修改密码暂未实现，请退出登录后选择忘记密码来重置')).classes('h-20'):
                    with ui.item_section().props('avatar'):
                        ui.icon('key', color='pink-500')
                    with ui.item_section():
                        ui.item_label('密码')
                        ui.item_label('修改密码').props('caption')
                    with ui.item_section().props('side'):
                        ui.icon('edit')
                ui.separator()
                with ui.item(on_click=lambda: ui.notify('暂不支持自助注销，请联系管理员')).classes('h-20'):
                    with ui.item_section().props('avatar'):
                        ui.icon('delete_outline', color='red-500')
                    with ui.item_section():
                        ui.item_label('注销账号')
                        ui.item_label('危险操作').props('caption')
                    with ui.item_section().props('side'):
                        ui.icon('arrow_forward')