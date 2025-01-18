'''
Author: 于小丘 海枫
Date: 2024-10-02 15:23:34
LastEditors: Yuerchu admin@yuxiaoqiu.cn
LastEditTime: 2024-12-28 16:53:26
FilePath: /HeyAuth/page/admin.py
Description: 海枫授权系统 管理员页 Admin

Copyright (c) 2018-2024 by 于小丘Yuerchu, All Rights Reserved. 
'''

# 防止被独立启动
if __name__ == '__main__':
    print("不支持单测，请使用main.py启动"); exit(1)

from nicegui import ui, app, __version__
from pkg.model import database as database
from typing import Dict
from fastapi import HTTPException, Request
import traceback
import asyncio
import pkg.version
import pkg.tool as tool
import pkg.smsSender as smsSender
import requests
import datetime
import time
import pkg.emailer as emailer
import pkg.log as log
from pkg.tool import echoLog

def create() -> None:
    # 添加跳转，防止出现404
    @ui.page('/admin')
    async def jumpToAdmin():
        ui.run_javascript('window.location.href="/admin/home"')
    
    @ui.page('/admin/{page}')
    async def admin(request: Request, page: str = 'home'):

        # 防止非管理员进入后台
        if app.storage.user['id'] != 1:
            log.warning('ID为' + str(app.storage.user['id']) + '的用户尝试进入后台，准备阻止')
            raise HTTPException(status_code=404, detail="Not Found")
        else:
            log.info('管理员尝试进入后台')

        # 将整个页面包在try...except...里面，防止页面构建出现异常时导致无法获取错误原因
        try:
            await echoLog()
            
            # 开始构建页面
            ui.page_title('HeyAuth 仪表盘')
        
            # 添加无刷新修改URL的Javascript函数
            ui.add_head_html(r'''
                <script>
                async function setURL(url) {
                    window.history.pushState({}, '', url);
                }
                </script>
            ''')

            db = database()

            await ui.context.client.connected()

            # 进度条dialog
            with ui.dialog().props('persistent') as loading, ui.card():
                with ui.row(align_items='center'):
                    ui.spinner(size='lg')
                    ui.label('数据加载中...')

            # 进入Tab时的页面显示
            async def jumpPage(pageName: str, pageUrl: str, appBar_Name: str = '') -> None:
                tabs.set_value(pageName)
                appBarName.set_text(appBar_Name if appBar_Name != '' else 'HeyAuth 仪表盘')
                await ui.run_javascript('setURL("{}")'.format(pageUrl))
            
            # 表格列的显示隐藏开关
            def tableToggle(column: Dict, visible: bool, table) -> None:
                column['classes'] = '' if visible else 'hidden'
                column['headerClasses'] = '' if visible else 'hidden'
                table.update()
        
            
            # 构建添加卡密对话框
            with ui.dialog() as addCardamomDialog, ui.card().style('width: 70%; max-width: 500px'):
                ui.label('添加卡密').classes('text-h5')
        
                ui.radio(['由系统自动生成', '导入卡密'], value='由系统自动生成')

                ui.textarea(label='输入卡密', placeholder='一行一个(选择“由系统自动生成”时填写无效)')
        
                with ui.row():
                    ui.button("添加", on_click=lambda: (ui.notify('功能暂未开放', color='negative')))
                    ui.button("返回", on_click=addCardamomDialog.close)

            dark_mode = ui.dark_mode(value=app.storage.browser.get('dark_mode'), on_change=lambda e: ui.run_javascript(f'''
                                fetch('/dark_mode', {{
                                    method: 'POST',
                                    headers: {{'Content-Type': 'application/json'}},
                                    body: JSON.stringify({{value: {e.value}}}),
                                }});
                            '''))

            # 页面布局
            with ui.header() \
            .classes('items-center duration-300 py-2 px-5 no-wrap') \
            .style('box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1)'):
                with ui.tabs(value=page) as tabs:
                    ui.button(on_click=lambda: left_drawer.toggle(), icon='menu').props('flat color=white round')
                    appBarName = ui.label('HeyAuth 仪表盘').classes('text-lg px-4').props('flat color=white')
                
                ui.space()
            
                # 主题切换
                with ui.element().tooltip('主题切换'):
                    ui.button(icon='dark_mode', on_click=lambda: dark_mode.set_value(None)) \
                        .props('flat fab-mini color=white').bind_visibility_from(dark_mode, 'value', value=True)
                    ui.button(icon='light_mode', on_click=lambda: dark_mode.set_value(True)) \
                        .props('flat fab-mini color=white').bind_visibility_from(dark_mode, 'value', value=False)
                    ui.button(icon='brightness_auto', on_click=lambda: dark_mode.set_value(False)) \
                        .props('flat fab-mini color=white').bind_visibility_from(dark_mode, 'value', lambda mode: mode is None)
                    
                ui.button(icon='home', on_click=lambda: (ui.navigate.to('/'))).tooltip('返回首页') \
                    .props('flat fab-mini color=white')
            
            siteDomain = request.base_url.hostname

            loading.open()
            await asyncio.sleep(1)

            # 侧边栏
            with ui.left_drawer() as left_drawer:
                ui.interactive_image('https://bing.img.run/1366x768.php').classes('w-full')
                ui.label('海枫授权系统').classes('text-2xl text-bold')

                if siteDomain == "127.0.0.1" or siteDomain == "localhost": ui.label("本地模式无需授权").classes('text-gray-600')
                else:
                    with ui.element('div').classes('p-2 bg-red-100 w-full'):
                            with ui.row(align_items='center'):
                                ui.icon('info').classes('text-red-500 text-2xl')
                                ui.label('请先激活 HeyAuth').classes('text-red-500')

                with ui.scroll_area().classes('h-full'):
                    with ui.expansion('站点一览', icon='space_dashboard').classes('w-full text-black'):
                        ui.button('仪表盘', icon='dashboard', on_click=lambda: jumpPage(pageName='home', pageUrl='/admin/home', appBar_Name='HeyAuth 仪表盘')) \
                            .classes('w-full').props('flat')
                        ui.button('收入统计', icon='trending_up', on_click=lambda: jumpPage(pageName='income', pageUrl='/admin/income', appBar_Name="HeyAuth 收入统计")) \
                            .classes('w-full').props('flat')
                        ui.button('授权日志', icon='history', on_click=lambda: jumpPage(pageName='autlog', pageUrl='/admin/autlog', appBar_Name="HeyAuth 授权日志")) \
                            .classes('w-full').props('flat')
                    
                    with ui.expansion('授权管理', icon='work').classes('w-full'):
                        ui.button('B端授权', on_click=lambda: jumpPage(pageName='blicense', pageUrl='/admin/blicense', appBar_Name="HeyAuth B端授权")) \
                                .classes('w-full').props('flat')
                        ui.button('C端授权', on_click=lambda: jumpPage(pageName='clicense', pageUrl='/admin/clicense', appBar_Name="HeyAuth C端授权")) \
                                .classes('w-full').props('flat')
                    
                    with ui.expansion('额度管理', icon='apps').classes('w-full'):
                        ui.button('B端额度', on_click=lambda: jumpPage(pageName='bquota', pageUrl='/admin/bquota', appBar_Name="HeyAuth B端额度")) \
                            .classes('w-full').props('flat')
                        ui.button('C端额度', on_click=lambda: jumpPage(pageName='cquota', pageUrl='/admin/cquota', appBar_Name="HeyAuth C端额度")) \
                            .classes('w-full').props('flat')
                    
                    with ui.expansion('产品管理', icon='apps').classes('w-full'):
                        ui.button('B端产品', on_click=lambda: jumpPage(pageName='bproduct', pageUrl='/admin/bproduct', appBar_Name="HeyAuth B端产品")) \
                            .classes('w-full').props('flat')
                        ui.button('C端产品', on_click=lambda: jumpPage(pageName='cproduct', pageUrl='/admin/cproduct', appBar_Name="HeyAuth C端产品")) \
                            .classes('w-full').props('flat')
                    
                    with ui.expansion('用户管理', icon='people').classes('w-full'):
                        ui.button('所有用户', on_click=lambda: jumpPage(pageName='user', pageUrl='/admin/user', appBar_Name="HeyAuth 用户管理")) \
                            .classes('w-full').props('flat')
                        ui.button('产品代理', on_click=lambda: jumpPage(pageName='user', pageUrl='/admin/proxy', appBar_Name="HeyAuth 产品代理")) \
                            .classes('w-full').props('flat')
                    
                    with ui.expansion('工单管理', icon='insert_comment').classes('w-full'):
                        ui.button('所有工单', on_click=lambda: jumpPage(pageName='ticket', pageUrl='/admin/ticket', appBar_Name="HeyAuth 工单管理")) \
                            .classes('w-full').props('flat')
                        
                    with ui.expansion('卡密管理', icon='confirmation_number').classes('w-full'):
                        ui.button('所有卡密', on_click=lambda: jumpPage(pageName='cardmom', pageUrl='/admin/cardmom', appBar_Name="HeyAuth 卡密管理")) \
                            .classes('w-full').props('flat')
                        
                    with ui.expansion('系统设置', icon='settings').classes('w-full'):
                        ui.button('全局设置', on_click=lambda: ui.navigate.to('/admin/settings#全局设置')).classes('w-full').props('flat')
                        ui.button('短信设置', on_click=lambda: ui.navigate.to('/admin/settings#短信设置')).classes('w-full').props('flat')
                        ui.button('邮件设置', on_click=lambda: ui.navigate.to('/admin/settings#邮件设置')).classes('w-full').props('flat')
                        ui.button('推送设置', on_click=lambda: ui.navigate.to('/admin/settings#推送设置')).classes('w-full').props('flat')
                        ui.button('支付设置', on_click=lambda: ui.navigate.to('/admin/settings#支付设置')).classes('w-full').props('flat')
                        ui.button('授权设置', on_click=lambda: ui.navigate.to('/admin/settings#授权设置')).classes('w-full').props('flat')
                        ui.button('系统更新', on_click=lambda: ui.navigate.to('/admin/settings#系统更新')).classes('w-full').props('flat')

            db = database()
            with ui.tab_panels(tabs, value='home').classes('w-full').props('vertical'):
                # 站点一览
                with ui.tab_panel('home'):
                    # 数据展示
                    with ui.row().classes('w-full justify-around'):
                        with ui.card().classes('w-full sm:w-1/3 lg:w-1/5 flex-grow'):
                            ui.label('应用数量')
                            ui.label(len(await db.getAllProduct())).classes('text-h5')
                            ui.label('用户公告： 0 条')
                        
                        with ui.card().classes('w-full sm:w-1/3 lg:w-1/5 flex-grow'):
                            ui.label('正版授权')
                            ui.label(await db.getActiveNum()).classes('text-h5')
                            ui.label('盗版数量： ' + str(await db.getPirateNum()) + " 条")
                        
                        with ui.card().classes('w-full sm:w-1/3 lg:w-1/5 flex-grow'):
                            ui.label('全站用户')
                            ui.label(await db.getUserCount()).classes('text-h5')
                            ui.label('会员用户： -')
                        
                        with ui.card().classes('w-full sm:w-1/3 lg:w-1/5 flex-grow'):
                            ui.label('卡密数量')
                            ui.label(await db.getCardamomNum()).classes('text-h5')
                            ui.label('已用卡密： -')
                    # 授权信息与公告
                    with ui.row().classes('w-full'):
                        with ui.card().classes('w-full lg:w-1/2 flex-grow'):
                            # 授权列表
                            home_columns = [
                                {'name': 'name', 'label': '系统名称', 'field': 'name'},
                                {'name': 'value', 'label': '海枫授权系统 HeyAuth', 'field': 'value'},
                            ]
                            home_rows = [
                                {'name': '系统作者', 'value': str(pkg.version.versionAuthor)},
                                {'name': '当前版本', 'value': "HeyAuth 版本: " + str(pkg.version.version) + " | NiceGUI版本: " + __version__},
                                {'name': '更新时间', 'value': str(pkg.version.versionDate)},
                            ]
                            ui.table(columns=home_columns, rows=home_rows, row_key="name", title="程序信息", column_defaults={'align': 'left', 'required': True}).classes('w-full').props('flat')
                
                
                # 收入统计
                with ui.tab_panel('income'):
                    ui.label("还在做")
                

                # 授权日志
                with ui.tab_panel('autlog'):
                    # 授权列表
                    authlog_columns = [
                        {'name': 'user_name', 'label': '用户ID', 'field': 'user_id'},
                        {'name': 'product_name', 'label': '授权产品', 'field': 'user_status'},
                        {'name': 'req_domain', 'label': '请求域名', 'field': 'user_nickname'},
                        {'name': 'req_ip', 'label': '请求IP', 'field': 'user_account'},
                        {'name': 'req_type', 'label': '请求类型', 'field': 'signup_at'},
                        {'name': 'req_result', 'label': '请求结果', 'field': 'signup_at'},
                        {'name': 'req_time', 'label': '请求时间', 'field': 'signup_at'},
                        {'name': 'req_time', 'label': '请求时间', 'field': 'signup_at'},
                    ]
        
                    authlog_rows = []
        
                    ui.table(columns=authlog_columns, rows=authlog_rows, row_key='user_name', pagination=10, column_defaults={'align': 'left', 'required': True, 'sortable': True}).classes('w-full')
        
                    ui.label('还在做')


                # B端授权
                with ui.tab_panel('blicense').classes('wh-full'):

                    # 添加授权函数
                    async def addLicense():
                        # 检查填写内容是否合理
                        if addLicense_user_id.value == '' \
                        or addLicense_product_id.value == '' \
                        or addLicense_domain.value == '' \
                        or addlicense_time.value == '':
                            ui.notify('请填写完整', color='negative')
                            return
                        elif addLicense_user_id.value.isdigit() == False \
                        or addLicense_product_id.value.isdigit() == False:
                            ui.notify('用户id和产品id必须为数字', color='negative')
                            return

                        if str(addlicense_time.value) == "forever":
                            log.debug('永久授权')
                            expiredTime = '9999-12-31 23:59:59'
                        else:
                            if addlicense_time.value.isdigit() == False:
                                ui.notify('授权时间必须为数字', color='negative')
                                return
                            expiredTime = datetime.datetime.now() + \
                                datetime.timedelta(days=int(addlicense_time.value))
                            expiredTime = expiredTime.strftime('%Y-%m-%d %H:%M:%S')
                            log.debug('授权时间：' + expiredTime)
                        await db.addLicenseB(
                            user_id=addLicense_user_id.value,
                            product_id=addLicense_product_id.value,
                            domain=addLicense_domain.value,
                            expiredTime=expiredTime)
                        shouquan_table.add_row({
                            'id': "刷新后显示",
                            'user_id': addLicense_user_id.value,
                            'product_name': productNameList[int(addLicense_product_id.value)],
                            'domain': addLicense_domain.value,
                            'key': "刷新后显示",
                            'status': "正常",
                            'time': time.strftime('%Y-%m-%d %H:%M:%S'),
                            'expired': "永久授权" if expiredTime == "9999-12-31 23:59:59" \
                                                else expiredTime
                        })
                        addLicenseDialogB.close()
                        await reloadShouquan(tips=False)
                        ui.notify('添加成功', color='positive')

                    # 封禁授权函数
                    async def banLicenseB():
                        await db.banLicenseB(shouquan_table.selected[0]['id'], banLicense_reason.value)
                        banLicenseDialogB.close()
                        await reloadShouquan(tips=False)
                        ui.notify('封禁成功', color='positive')
                    
                    # 解封授权函数
                    async def unbanLicenseB():
                        await db.unbanLicenseB(shouquan_table.selected[0]['id'])
                        unbanLicenseDialogB.close()
                        await reloadShouquan(tips=False)
                        ui.notify('解封成功', color='positive')

                    # 列表选择函数
                    async def shouquanTableOnClick():
                        try:
                            status = str(shouquan_table.selected[0]['status'])
                        except:
                            # 当授权列表未选中，显示添加授权按钮
                            banLicenseFAB.set_visibility(False)
                            unbanLicenseFAB.set_visibility(False)
                            addLicenseFAB.set_visibility(True)
                        try:
                            if status == "正常":
                                # 选中正常授权，显示封禁授权按钮
                                addLicenseFAB.set_visibility(False)
                                unbanLicenseFAB.set_visibility(False)
                                banLicenseFAB.set_visibility(True)
                            elif status == "被封禁":
                                # 选中封禁授权，显示解封授权按钮
                                addLicenseFAB.set_visibility(False)
                                banLicenseFAB.set_visibility(False)
                                unbanLicenseFAB.set_visibility(True)
                            else:
                                # 选中其他状态，隐藏所有按钮
                                addLicenseFAB.set_visibility(False)
                                banLicenseFAB.set_visibility(False)
                                unbanLicenseFAB.set_visibility(False)
                        except: pass
                            

                    # 添加授权对话框
                    with ui.dialog() as addLicenseDialogB, ui.card().style('width: 90%; max-width: 500px'):
                        ui.button(icon='add_circle').props('outline round').classes('mx-auto w-auto shadow-sm w-fill')
                        ui.label('添加授权').classes('w-full text-h5 text-center')
                
                        ui.label('请注意，在这里添加授权不占用用户剩余授权次数，即：'
                                '用户目前剩余3次授权，你添加了一次授权，用户剩余授权次数仍然为3次。')
                
                        addLicense_user_id = ui.input('用户id').classes('block w-full text-gray-900')
                        addLicense_product_id = ui.input('产品id').classes('block w-full text-gray-900')
                        addLicense_domain = ui.input('授权域名').classes('block w-full text-gray-900')
                        addlicense_time = ui.input('授权有效期(填写天数)').classes('block w-full text-gray-900')
                        with ui.button_group().classes('w-full').props('flat'):
                            ui.button("月度授权", on_click=lambda: (addlicense_time.set_value("31"))).props('flat')
                            ui.button("季度授权", on_click=lambda: (addlicense_time.set_value("93"))).props('flat')
                            ui.button("年度授权", on_click=lambda: (addlicense_time.set_value("366"))).props('flat')
                            ui.button("永久授权", on_click=lambda: (addlicense_time.set_value("forever"))).props('flat')
                
                        ui.button("添加", on_click=lambda: (addLicense())) \
                                .classes('items-center w-full').props('rounded')
                        ui.button("返回", on_click=addLicenseDialogB.close) \
                                .classes('w-full').props('flat rounded')

                    # 封禁授权对话框
                    with ui.dialog() as banLicenseDialogB, ui.card().style('width: 90%; max-width: 500px'):
                        ui.button(icon='gpp_bad', color='red').props('outline round').classes('mx-auto w-auto shadow-sm w-fill')
                        ui.label('封禁授权').classes('w-full text-h5 text-center')
                        
                        ui.label('确定要封禁这个授权吗？')
                        banLicense_reason = ui.input('封禁原因 (选填)') \
                            .classes('block w-full text-gray-900')
                        ui.button("封禁", color='red', on_click=lambda: (banLicenseB())) \
                            .classes('items-center w-full').props('rounded')
                        ui.button("返回", on_click=banLicenseDialogB.close) \
                            .classes('w-full').props('flat rounded')

                    # 解封授权对话框
                    with ui.dialog() as unbanLicenseDialogB, ui.card().style('width: 90%; max-width: 500px'):
                        ui.button(icon='remove_moderator').props('outline round').classes('mx-auto w-auto shadow-sm w-fill')
                        ui.label('解封B端产品').classes('w-full text-h5 text-center')
                        
                        ui.label('确定要解封这个授权吗？')

                        ui.button("确认解封", on_click=lambda: (unbanLicenseB())) \
                        .classes('items-center w-full').props('rounded')
                        ui.button("返回", on_click=unbanLicenseDialogB.close) \
                        .classes('w-full').props('flat rounded')

                    # 授权列表
                    shouquan_columns = [
                        {'name': 'id', 'label': '授权id', 'field': 'id', 'sortable': True},
                        {'name': 'user_id', 'label': '授权用户', 'field': 'user_id', 'sortable': True},
                        {'name': 'product_name', 'label': '产品名', 'field': 'product_name', 'sortable': True},
                        {'name': 'domain', 'label': '授权域名', 'field': 'domain'},
                        {'name': 'key', 'label': '授权码', 'field': 'key'},
                        {'name': 'status', 'label': '授权状态', 'field': 'status'},
                        {'name': 'time', 'label': '创建时间', 'field': 'time'},
                        {'name': 'expired', 'label': '过期时间', 'field': 'expired', 'required': True, 'align':'left'},
                    ]
                    
                    async def fetchShouquan():
                        ActiveIDs = await db.getActiveIds()
                        ActiveUsers = await db.getActiveUsers()
                        ActiveProducts = await db.getActiveProducts()
                        ActiveDomains = await db.getActiveDomains()
                        ActiveKeys = await db.getActiveKeys()
                        ActiveStatus = await db.getActiveStatuses()
                        ActiveTimes = await db.getActiveTimes()
                        ActiveExpireds = await db.getActiveExpiredTimes()
                        productNameList = await db.getProductNames()
                        status_mapping = {"ok": "正常", "ban": "被封禁", "lapse": "被更换或删除"}

                        shouquan_rows = [
                            {
                                'id': id_,
                                'user_id': user,
                                'product_name': productNameList[int(product)],
                                'domain': domain,
                                'key': key,
                                'status': status_mapping.get(status, status),
                                'time': time,
                                'expired': "永久授权" if expired == "9999-12-31 23:59:59" else expired
                            }
                            for id_, user, product, domain, key, status, time, expired in zip(
                                ActiveIDs, ActiveUsers, ActiveProducts, ActiveDomains,
                                ActiveKeys, ActiveStatus, ActiveTimes, ActiveExpireds)
                        ]

                        return shouquan_rows
                    
                    async def reloadShouquan(tips: bool = True):
                        loading.open()
                        shouquan_table.update_rows(await fetchShouquan())
                        loading.close()
                        if tips: ui.notify('刷新成功')

                    shouquan_rows = await fetchShouquan()
                    shouquan_table = ui.table(columns=shouquan_columns, rows=shouquan_rows, title='B端授权',
                                            row_key="id", pagination=10, selection='single', 
                                            on_select=lambda: shouquanTableOnClick(), 
                                            column_defaults={
                                                'align': 'left',
                                                'headerClasses': 'uppercase text-primary',
                                                'required': True,
                                            }) \
                                    .classes('w-full h-auto')

                    shouquan_table.add_slot('body-cell-status', '''
                        <q-td key="status" :props="props">
                            <q-badge :color="props.value === '正常' ? 'green' : 'red'">
                                {{ props.value }}
                            </q-badge>
                        </q-td>
                    ''')

                    with shouquan_table.add_slot('top-right'):
                        ui.input('搜索授权').classes('px-2').bind_value(shouquan_table, 'filter').props('rounded outlined dense clearable')
                        ui.button(icon='refresh', on_click=lambda: reloadShouquan()).classes('px-2').props('flat fab-mini')
                        with ui.button(icon='menu').props('flat fab-mini'):
                            with ui.menu(), ui.column().classes('gap-0 p-4'):
                                for column in shouquan_columns:
                                    ui.switch(column['label'], value=True, on_change=lambda e,
                                              column=column: tableToggle(column=column, visible=e.value, table=shouquan_table))
                    
                    # FAB按钮
                    with ui.page_sticky(x_offset=24, y_offset=24) as addLicenseFAB:
                        ui.button(icon='add', on_click=addLicenseDialogB.open) \
                            .props('fab')
                    with ui.page_sticky(x_offset=24, y_offset=24) as banLicenseFAB:
                        ui.button(icon='gpp_bad', on_click=banLicenseDialogB.open, color='red') \
                            .props('fab')
                        # 单独拉出来默认隐藏，防止无法再设置其显示
                    banLicenseFAB.set_visibility(False)
                    with ui.page_sticky(x_offset=24, y_offset=24) as unbanLicenseFAB:
                        ui.button(icon='remove_moderator', on_click=unbanLicenseDialogB.open) \
                            .props('fab')
                        # 单独拉出来默认隐藏，防止无法再设置其显示
                    unbanLicenseFAB.set_visibility(False)
                

                # C端授权
                with ui.tab_panel('clicense'):
                    ui.label('还在做')


                # B端额度
                with ui.tab_panel('bquota'):
                    
                    # 额度列表
                    bLine_columns = [
                        {'name': 'id', 'label': '内部id', 'field': 'id'},
                        {'name': 'user_id', 'label': '用户id', 'field': 'user_id'},
                        {'name': 'product_id', 'label': '产品id', 'field': 'product_id'},
                        {'name': 'total_auth', 'label': '总授权额度', 'field': 'total_auth'},
                        {'name': 'remain_auth', 'label': '剩余授权额度', 'field': 'remain_auth'},
                        {'name': 'change_auth', 'label': '总变更次数额度', 'field': 'change_auth'},
                        {'name': 'changeX_auth', 'label': '剩余变更次数额度', 'field': 'changeX_auth'},
                        {'name': 'oprate_time', 'label': '修改时间', 'field': 'oprate_time'},
                        {'name': 'expired_time', 'label': '过期时间', 'field': 'expired_time', 'required': True, 'align':'left'},
                    ]

                    bLineList = await db.getBLine()

                    bLineRows = []

                    for i in range(len(bLineList)):
                        bLineRows.append({
                            'id': bLineList[i][0], 
                            'user_id': bLineList[i][1],
                            'product_id': bLineList[i][2],
                            'total_auth': bLineList[i][3],
                            'remain_auth': bLineList[i][4],
                            'change_auth': bLineList[i][5],
                            'changeX_auth': bLineList[i][6],
                            'oprate_time': bLineList[i][7],
                            'expired_time': bLineList[i][8]
                        })

                    line_table = ui.table(columns=bLine_columns, rows=bLineRows, title='B端额度',
                                            row_key="id", pagination=10, selection='single', column_defaults={'align': 'left', 'required': True, 'sortable': True}).classes('w-full')
                    
                    with line_table.add_slot('top-right'):
                        ui.input('搜索额度').bind_value(line_table, 'filter').props('rounded outlined dense clearable')
                        
                    ui.label('还在做')

                    # FAB按钮
                    with ui.page_sticky(x_offset=24, y_offset=24) as addquotaB:
                        ui.button(icon='add').props('fab')

                    with ui.page_sticky(x_offset=24, y_offset=24) as deletequotaB:
                        ui.button(icon='gpp_bad', color='red').props('fab')

                        # 单独拉出来默认隐藏，防止无法再设置其显示
                    deletequotaB.set_visibility(False)
        

                # C端额度
                with ui.tab_panel('cquota'):
                    ui.label('还在做')


                # B端产品
                with ui.tab_panel('bproduct'):

                    async def adminProductBListTableOnClick():
                        try:
                            status = str(adminProductBList.selected[0]['delete_time'])
                        except:
                            # 当授权列表未选中，显示添加产品按钮
                            banProductBFAB.set_visibility(False)
                            addProductBFAB.set_visibility(True)
                        try:
                            if status == "" or status == None:
                                # 选中在售产品，显示下架产品按钮
                                banProductBFAB.set_visibility(False)
                                addProductBFAB.set_visibility(True)
                            else:
                                # 选中其他状态，显示添加产品按钮
                                banProductBFAB.set_visibility(False)
                                addProductBFAB.set_visibility(True)
                        except Exception as e:
                            log.error(str(e))
                            ui.notify('发生错误: ' + str(e), color='negative')

                    # 添加产品函数
                    async def addProductB():
                        # 判断是否填写完整
                        if addProductB_name.value == '' \
                        or addProductB_auth.value == '' \
                        or addProductB_change_auth.value == '':
                            ui.notify('请填写完整', color='negative')
                            return
                        # 判断是否存在同名商品
                        elif await db.getProductId(name=addProductB_name.value) != None:
                            ui.notify('商品已存在，请勿重复添加', color='negative')
                            return
                        # 判断内容是否符合填写要求
                        elif addProductB_price_month.value.isdigit() == False \
                        or addProductB_price_quarter.value.isdigit() == False \
                        or addProductB_price_year.value.isdigit() == False \
                        or addProductB_price_life.value.isdigit() == False:
                            ui.notify('价格必须为数字', color='negative')
                            return
                        # 判断授权数量和变更次数是否不小于0
                        elif int(addProductB_auth.value) < 0 \
                        or int(addProductB_change_auth.value) < 0 :
                            ui.notify('授权数量变或更次数不能为负数', color='negative')
                            return
                        elif float(addProductB_price_month.value) < 0 \
                        or float(addProductB_price_quarter.value) < 0 \
                        or float(addProductB_price_year.value) < 0 \
                        or float(addProductB_price_life.value) < 0:
                            ui.notify('价格不能为负数', color='negative')
                            return
                        await db.addProduct(
                            name = addProductB_name.value, 
                            price_month = addProductB_price_month.value, 
                            price_quarter = addProductB_price_quarter.value,
                            price_year = addProductB_price_year.value,
                            price_life = addProductB_price_life.value)
                        addProductDialogB.close()
                        ui.notify('添加成功', color='positive')

                    # 添加产品对话框
                    with ui.dialog() as addProductDialogB, ui.card().style('width: 70%; max-width: 500px'):
                        ui.label('添加B端产品').classes('text-h5')

                        ui.label("如果不需要按月授权或者季度授权或者年度授权，请将价格填写为0")

                        addProductB_name = ui.input('产品名').classes('block w-full text-gray-900')
                        addProductB_auth = ui.input('授权数', placeholder='单次购买后，默认获得的授权数量') \
                            .classes('block w-full text-gray-900')
                        addProductB_change_auth = ui.input('变更授权数', placeholder='单次购买后，默认可以修改授权的次数')  \
                            .classes('block w-full text-gray-900')
                        addProductB_price_month = ui.input('月卡价格') \
                            .classes('block w-full text-gray-900')
                        addProductB_price_quarter = ui.input('季卡价格') \
                            .classes('block w-full text-gray-900')
                        addProductB_price_year = ui.input('年卡价格') \
                            .classes('block w-full text-gray-900')
                        addProductB_price_life = ui.input('永久价格') \
                            .classes('block w-full text-gray-900')
                        # addProductB_Editor = ui.editor()
                
                        with ui.row():
                            ui.button("添加", on_click=lambda: (addProductB()))
                            ui.button("返回", on_click=addProductDialogB.close)

                    # 下架产品对话框
                    with ui.dialog() as removeProductDialogB, ui.card().style('width: 70%; max-width: 500px'):
                        ui.label('下架B端产品').classes('text-h5')

                        ui.label('下架后，该商品将无法再被购买，但用户已购买的商品不受影响，后续可以重新上架。')
                
                        hideProductB_id = ui.input('产品id').classes('block w-full text-gray-900')

                        with ui.row():
                            ui.button("下架", on_click=lambda: (ui.notify('功能暂未开放', color='negative')))
                            ui.button("返回", on_click=removeProductDialogB.close)

                    # 产品列表
                    product_columns = [
                        {'name': 'product_id', 'label': '产品id', 'field': 'product_id'},
                        {'name': 'product_name', 'label': '产品名', 'field': 'product_name'},
                        {'name': 'create_time', 'label': '创建日期', 'field': 'create_time'},
                        {'name': 'delete_time', 'label': '下架日期', 'field': 'delete_time'},
                        {'name': 'price_month', 'label': '月卡价格', 'field': 'price_month'},
                        {'name': 'price_quarter', 'label': '季卡价格', 'field': 'price_quarter'},
                        {'name': 'price_year', 'label': '年卡价格', 'field': 'price_year'},
                        {'name': 'price_life', 'label': '永久价格', 'field': 'price_life'},
                        {'name': 'original', 'label': '正版数量', 'field': 'original'},
                        {'name': 'piracy', 'label': '盗版数量', 'field': 'piracy'},
                    ]
        
                    ProductIDs = await db.getProductIds()
                    ProductCreateTimes = await db.getProductCreateTimes()
                    ProductDeleteTimes = await db.getProductDeleteTimes()
                    ProductPrices = await db.getProductPrices(time='all')
                    Product_rows = []
                    productNameList = await db.getProductNames()
        
                    for i in range(len(ProductIDs)):
                        prices = ProductPrices[i] if ProductPrices[i] is not None else ["", "", "", ""]
                        Product_rows.append({
                            'product_id': ProductIDs[i], 
                            'product_name': productNameList[int(ProductIDs[i])],
                            'create_time': ProductCreateTimes[i], 
                            'delete_time': ProductDeleteTimes[i],
                            'price_month': str(prices[0] if prices[0] is not None else ""), 
                            'price_quarter': str(prices[1] if prices[1] is not None else ""), 
                            'price_year': str(prices[2] if prices[2] is not None else ""), 
                            'price_life': str(prices[3] if prices[3] is not None else "")
                        })
        
                    adminProductBList = ui.table(columns=product_columns, rows=Product_rows, title='B端产品', row_key="product_id",
                                                pagination=10, selection='single', on_select=lambda: adminProductBListTableOnClick(),
                                                column_defaults={'sortable': True, 'align': 'left'}).classes('w-full')
                    # ui.label('还在做')

                    with adminProductBList.add_slot('top-right'):
                        ui.input('搜索产品').classes('px-2').bind_value(adminProductBList, 'filter').props('rounded outlined dense clearable')
                        ui.button(icon='refresh').classes('px-2').props('flat fab-mini')

                    # FAB按钮
                    with ui.page_sticky(x_offset=24, y_offset=24) as addProductBFAB:
                        ui.button(icon='add', on_click=addProductDialogB.open).props('fab')

                    with ui.page_sticky(x_offset=24, y_offset=24) as banProductBFAB:
                        ui.button(icon='gpp_bad', on_click=removeProductDialogB.open, color='red') \
                            .props('fab')
                        
                    # 单独拉出来默认隐藏，防止无法再设置其显示
                    banProductBFAB.set_visibility(False)


                # C端产品
                with ui.tab_panel('cproduct'):

                    # 构建添加C端产品对话框
                    with ui.dialog() as addProductDialogC, ui.card() \
                        .style('width: 70%; max-width: 500px'):
                        ui.label('添加C端产品').classes('text-h5')
                
                        addProductC_name = ui.input('产品名') \
                            .classes('block w-full text-gray-900')
                        addProductC_price = ui.input('价格') \
                            .classes('block w-full text-gray-900')
                
                        with ui.row():
                            # ui.button("添加", on_click=lambda: (addProductC()))
                            ui.button("返回", on_click=addProductDialogC.close)

                    ui.button('添加C端产品', on_click=addProductDialogC.open)
                    ui.label("还在做")


                # 所有用户
                with ui.tab_panel('user'):

                    # 添加用户函数
                    async def addUser():
                        if addUser_nickname.value == '' \
                        or addUser_account.value == '' \
                        or addUser_password.value == '' \
                        or addUser_qq.value == '':
                            ui.notify('请填写完整', color='negative')
                            return
                        await db.addUser(
                            account=addUser_account.value,
                            password=addUser_password.value,
                            force=True
                        )
                        addUserDialog.close()
                        ui.notify('添加成功', color='positive')

                    # 添加用户对话框
                    with ui.dialog() as addUserDialog, ui.card().style('width: 70%; max-width: 500px'):
                        ui.label('添加用户').classes('text-h5')
                
                        addUser_nickname = ui.input('昵称').classes('block w-full text-gray-900')
                        addUser_account = ui.input('账号').classes('block w-full text-gray-900')
                        addUser_password = ui.input('密码').classes('block w-full text-gray-900')
                        addUser_qq = ui.input('QQ').classes('block w-full text-gray-900')
                
                        with ui.row():
                            ui.button("添加", on_click=lambda: addUser())
                            ui.button("返回", on_click=addUserDialog.close)

                    # 界面
                    with ui.row():
                        ui.button('添加用户', on_click=addUserDialog.open)
                        ui.button('封禁用户')
                        ui.button('推送广告')
                    # 用户列表
                    user_columns = [
                        {'name': 'user_id', 'label': '用户id', 'field': 'user_id'},
                        {'name': 'user_status', 'label': '状态', 'field': 'user_status'},
                        {'name': 'user_nickname', 'label': '昵称', 'field': 'user_nickname'},
                        {'name': 'user_qq', 'label': 'QQ', 'field': 'user_qq'},
                        {'name': 'user_account', 'label': '账号', 'field': 'user_account'},
                        {'name': 'signup_at', 'label': '注册时间', 'field': 'signup_at'},
                    ]
        
                    user_ids = await db.getUserIds()
                    user_statuses = await db.getUserStatuses()
                    user_nicknames = await db.getUserNickNames()
                    user_accounts = await db.getUserAccounts()
                    user_signup_ats = await db.getUserSignUpAts()
                    user_qqs = await db.getUserQQs()
        
                    user_rows = []
                    for i in range(len(user_ids)):
                        user_rows.append({'user_id': user_ids[i], 'user_status': user_statuses[i], 'user_nickname': user_nicknames[i],
                                        'user_qq': user_qqs[i], 'user_account': user_accounts[i], 'signup_at': user_signup_ats[i]})
        
                    ui.table(columns=user_columns, rows=user_rows, row_key='user_id',selection='multiple', column_defaults={'sortable': True, 'align': 'left'}).classes('w-full')
        
                    ui.label('还在做')
        

                # 所有工单
                with ui.tab_panel('ticket'):
                    ui.label('还在做')
                

                # 卡密管理
                with ui.tab_panel('cardmom'):
                    with ui.row():
                        ui.button('添加卡密')
                        ui.button('删除卡密')
                    ui.label('还在做')


                # 系统设置
                with ui.tab_panel('settings'):

                    # 全局设置-保存
                    async def saveSiteSettings():
                        await db.setSetting('site_name', siteTitle.value)
                        await db.setSetting('bottom_text', siteCopyRight.value)
                        await db.setSetting('mainPage_title', main_page_title.value)
                        await db.setSetting('mainPage_subtitle', main_page_subtitle.value)
                        await db.setSetting('mainPage_description', main_page_description.value)
                        await db.setSetting('icp_beian', icp_beian.value)
                        await db.setSetting('ga_beian', ga_beian.value)
                        await db.setSetting('siteIcon', siteIcon.value)
                        ui.notify('保存成功', color='positive')

                    # 全局设置-页面
                    with ui.card().classes('w-full'):
                        tool.link_target('全局设置')
                        ui.label('全局设置').classes('text-h5')
                        with ui.element('div').classes('p-2 bg-blue-100 w-full'):
                            with ui.row(align_items='center'):
                                ui.icon('info').classes('text-blue-500 text-2xl')
                                ui.label('标有"*"的需要重新启动 HeyAuth 才能生效。')
                        
                        ui.label('站点配置').classes('text-h6')
                        siteTitle = ui.input('站点标题*', value=await db.getSetting('site_name')).classes('w-full')
                        siteCopyRight = ui.input('登录页底部版权', value=await db.getSetting('bottom_text')).classes('w-full')
                        main_page_title = ui.input('主页大标题', value=await db.getSetting('mainPage_title')).classes('w-full')
                        main_page_subtitle = ui.input('主页副标题', value=await db.getSetting('mainPage_subtitle')).classes('w-full')
                        main_page_description = ui.textarea('主页描述', value=await db.getSetting('mainPage_description'),
                                                            placeholder='建议不要写太多，否则移动端会显示异常').classes('w-full')
                        icp_beian = ui.input('网站ICP备案号', value=await db.getSetting('icp_beian')).classes('w-full')
                        ga_beian = ui.input('公安联网备案号', value=await db.getSetting('ga_beian')).classes('w-full')
                        ui.label('填写后将会在主页页脚显示，会自动链接到相关网页，没有请留空')
                        siteIcon = ui.input('favicon图标*(请填写一个Emoji)', value=await db.getSetting('siteIcon')).classes('w-full')

                        ui.label('首页SEO优化').classes('text-h6')
                        ui.input(label='SEO标题(title)', placeholder='自定义网站的SEO标题(title)').classes('w-full')
                        ui.input(label='SEO关键字(keywords)', placeholder='自定义网站的SEO关键字(keywords)').classes('w-full')
                        ui.input(label='SEO描述(description)', placeholder='自定义网站的SEO描述(description)').classes('w-full')

                        with ui.row():
                            ui.button('保存', on_click=lambda: (saveSiteSettings()))


                    # 短信设置-保存星耀短信设置
                    async def saveXinYaoSmsConfig():
                        await db.setSetting('xinYaoSmsURL', xinYaoSmsURL.value)
                        await db.setSetting('xinYaoSmsChannel', xinYaoSmsChannel.value)
                        await db.setSetting('xinYaoSmsusername', xinYaoSmsusername.value)
                        await db.setSetting('xinYaoSmsKey', xinYaoSmsKey.value)
                        ui.notify('星耀短信配置已保存', color='positive')
                    
                    # 短信设置-保存允梦短信配置
                    async def saveYunMenSmsConfig():
                        await db.setSetting('yunMenSmsChannel', yunMenSmsChannel.value)
                        await db.setSetting('yunMenSmsUsername', yunMenSmsusername.value)
                        await db.setSetting('yunMenSmsKey', yunMenSmsKey.value)
                        ui.notify('允梦短信配置已保存', color='positive')
                    
                    # 短信设置-测试星耀短信
                    async def testSendXinYaoMessager():
                        try:
                            if smsSender.sendXinYaoMessager(
                                phone=testSendXinYaoMessage_phone, 
                                content=testSendXinYaoMessage_content):
                                ui.notify('发送成功', color='positive')
                        except TypeError as e: ui.notify(message=str(e), color='negative')
                        except: ui.notify('发送失败，网络错误')
                    
                    # 短信设置-测试允梦短信
                    async def testSendYunMenMessager():
                        try:
                            if smsSender.SendYunMenMessager(
                                phone=testSendYunMenMessage_phone, 
                                content=testSendYunMenMessage_content):
                                ui.notify('发送成功', color='positive')
                        except TypeError as e: ui.notify(message=str(e), color='negative')
                        except: ui.notify('发送失败，网络错误')
                    
                    # 构建发送星耀短信对话框
                    with ui.dialog() as testSendXinYaoMessage, ui.card().style('width: 70%; max-width: 700px'):
                        ui.label('测试发送短信消息(星耀短信)').classes('text-h5')
                
                        testSendXinYaoMessage_phone = ui.input('手机号').classes('block w-full text-gray-900')
                        testSendXinYaoMessage_content = ui.input('短信内容').classes('block w-full text-gray-900')
                
                        with ui.row():
                            ui.button("确认提交", on_click=lambda: (testSendXinYaoMessager()))
                            ui.button("返回", on_click=testSendXinYaoMessage.close)
                    
                    # 构建发送允梦短信对话框
                    with ui.dialog() as testSendYunMenMessage, ui.card().style('width: 70%; max-width: 700px'):
                        ui.label('测试发送短信消息(允梦短信)').classes('text-h5')
                
                        testSendYunMenMessage_phone = ui.input('手机号').classes('block w-full text-gray-900')
                        testSendYunMenMessage_content = ui.input('短信内容').classes('block w-full text-gray-900')
                
                        with ui.row():
                            ui.button("确认提交", on_click=lambda: (testSendYunMenMessager()))
                            ui.button("返回", on_click=testSendYunMenMessage.close)

                    # 短信设置-页面
                    with ui.card().classes('w-full'):
                        tool.link_target('短信设置')
                        ui.label('短信设置').classes('text-h5')

                        with ui.element('div').classes('p-2 bg-blue-100 w-full'):
                            with ui.row(align_items='center'):
                                ui.icon('info').classes('text-blue-500 text-2xl')
                                # ui.label('此服务由第三方平台提供， 产生的任何纠纷与 海枫授权系统 开发者无关。')
                                ui.label('目前没什么用，海枫授权系统暂不支持绑定手机号。')

                        with ui.card().classes('w-full'):
                            ui.label("短信发送方式").classes('text-h6')
                            sendSMSChannel = ui.radio(["关闭短信发送", "星耀网络·企信通_EnterpriseSMS", "允梦短信"],
                                                    value="关闭短信发送").props('inline')
                            ui.label('短信签名')
                            ui.input("海枫筑梦计划").classes('w-full')
                            ui.button('保存', on_click=lambda: (ui.notify(sendSMSChannel.value, color='positive')))

                        with ui.card().classes('w-full'):
                            ui.label("星耀网络·企信通_EnterpriseSMS").classes('text-h6')
                            xinYaoSmsURL = ui.input('API地址', value=await db.getSetting('xinYaoSmsURL')).classes('w-full')
                            xinYaoSmsChannel = ui.input('发信通道ID（可选）', value=await db.getSetting('xinYaoSmsChannel')).classes('w-full')
                            xinYaoSmsusername = ui.input('username', value=await db.getSetting('xinYaoSmsusername')).classes('w-full')
                            xinYaoSmsKey = ui.input('Key', value=await db.getSetting('xinYaoSmsKey')).classes('w-full')
                            with ui.row():
                                ui.button('保存', on_click=saveXinYaoSmsConfig)
                                ui.button('测试（请先保存）', on_click=testSendXinYaoMessage.open)

                        with ui.card().classes('w-full'):
                            ui.label("允梦短信").classes('text-h6')
                            ui.link('允梦短信官网', 'https://sms.mengdo.cn/R/T7oOZELC')
                            yunMenSmsChannel = ui.input('发信通道ID（可选）', value=await db.getSetting('yunMenSmsChannel')).classes('w-full')
                            yunMenSmsusername = ui.input('username', value=await db.getSetting('yunMenSmsusername')).classes('w-full')
                            yunMenSmsKey = ui.input('Key', value=await db.getSetting('yunMenSmsKey')).classes('w-full')
                            with ui.row():
                                ui.button('保存', on_click=saveYunMenSmsConfig)
                                ui.button('测试（请先保存）', on_click=testSendYunMenMessage.open)

                        with ui.card().classes('w-full'):
                            ui.label("腾讯云短信").classes('text-h6')
                            ui.label("海枫授权系统的短信模板会传出两个参数，{1}是验证码，{2}是有效期，请注意在模板配置中修改。")
                            ui.label("推荐为：“【海枫筑梦计划】{1}是你的验证码，{2}分钟内有效，请勿告知他人。”")
                            ui.link('腾讯云短信控制台', 'https://console.cloud.tencent.com/smsv2')
                    
                            tencentSmsSdkAppId = ui.input('SDK AppID', value=await db.getSetting('tencentSmsSdkAppId')).classes('w-full')
                            tencentSmsTemplateID = ui.input('模板ID', value=await db.getSetting('tencentSmsTemplateID')).classes('w-full')
                            with ui.row():
                                ui.button('保存', on_click=saveYunMenSmsConfig)
                                ui.button('测试（请先保存）', on_click=testSendYunMenMessage.open)


                    # 邮件设置-保存邮件设置
                    async def saveEMailSettings():
                        try:
                            await db.setSetting('openEMail', openEMail.value)
                            await db.setSetting('emailSendName', emailSendName.value)
                            await db.setSetting('emailSenderMail', emailSenderMail.value)
                            await db.setSetting('emailSmtpServer', emailSmtpServer.value)
                            await db.setSetting('emailSmtpSeverPort', emailSmtpSeverPort.value)
                            await db.setSetting('emailSmtpUsername', emailSmtpUsername.value)
                            await db.setSetting('emailSmtpPassword', emailSmtpPassword.value)
                            await db.setSetting('emailFeedbackMail', emailFeedbackMail.value)
                            await db.setSetting('emailForceUsingSSL', True)
                            await db.setSetting('emailConnectTime', emailConnectTime.value)
                        except:
                            ui.notify('保存失败', color='negative')
                            log.error(str(traceback.format_exc()))
                        else: ui.notify('保存成功', color='positive')
                    
                    # 邮件设置-测试邮件发送设置
                    async def sendEmailTest():
                        if adminTestSendEmailTarget.value == None or adminTestSendEmailTarget.value == '':
                            ui.notify('请填写接收邮箱', color='negative')
                            return
                        response = await emailer.sendTestEmail(email=adminTestSendEmailTarget.value)
                        if response == None: ui.notify('发送成功', color='positive')
                        else: ui.notify('发送失败：' + str(response), color='negative')

                    # 邮件设置-构建发送测试邮件对话框
                    with ui.dialog() as sendEmailTestDialog, ui.card().style('width: 70%; max-width: 500px'):
                        ui.label('发送测试邮件').classes('text-h5')
                
                        adminTestSendEmailTarget = ui.input('接收邮箱').classes('block w-full text-gray-900')
                
                        with ui.row():
                            ui.button("发送", on_click=lambda: sendEmailTest())
                            ui.button("返回", on_click=sendEmailTestDialog.close)

                    # 邮件设置-页面
                    with ui.card().classes('w-full'):
                        tool.link_target('邮件设置')
                        ui.label('邮件设置').classes('text-h5')

                        openEMail = ui.switch('开启邮件服务', value=tool.checkingToF(await db.getSetting('openEMail'))).classes('w-full')
                        ui.label('若不开启，则所有用户随便填个邮箱即可完成注册，无需验证码。'
                                '下面没填写完整请不要开启，否则可能会出现不可预料的错误。')


                        emailSendName = ui.input('发件人名', value=await db.getSetting('emailSendName')) \
                            .classes('w-full md:w-1/2 lg:w-1/3')
                        ui.label('邮件中展示的发件人姓名').classes('w-full md:w-1/2 lg:w-1/3')

                        emailSenderMail = ui.input('发件人邮箱', value=await db.getSetting('emailSenderMail')) \
                            .classes('w-full md:w-1/2 lg:w-1/3')
                        ui.label('发件邮箱的地址').classes('w-full md:w-1/2 lg:w-1/3')

                        emailSmtpServer = ui.input('SMTP服务器', value=await db.getSetting('emailSmtpServer')) \
                            .classes('w-full md:w-1/2 lg:w-1/3')
                        ui.label('发件服务器地址，不包括端口号').classes('w-full md:w-1/2 lg:w-1/3')

                        emailSmtpSeverPort = ui.input('SMTP端口号', value=await db.getSetting('emailSmtpSeverPort')) \
                            .classes('w-full md:w-1/2 lg:w-1/3')
                        ui.label('发件服务器地址端口号').classes('w-full md:w-1/2 lg:w-1/3')

                        emailSmtpUsername = ui.input('SMTP用户名', value=await db.getSetting('emailSmtpUsername')) \
                            .classes('w-full md:w-1/2 lg:w-1/3')
                        ui.label('发信邮箱用户名，一般与邮箱地址相同').classes('w-full md:w-1/2 lg:w-1/3')

                        emailSmtpPassword = ui.input('SMTP密码', password=True, value=await db.getSetting('emailSmtpPassword')) \
                            .classes('w-full md:w-1/2 lg:w-1/3')
                        ui.label('发信邮箱密码').classes('w-full md:w-1/2 lg:w-1/3')

                        emailFeedbackMail = ui.input('回信邮箱', value=await db.getSetting('emailFeedbackMail')) \
                            .classes('w-full md:w-1/2 lg:w-1/3')
                        ui.label('用户回复系统发送的邮件时，用于接收回信的邮箱')

                        emailForceUsingSSL = ui.switch('强制使用SSL连接(暂时无法关闭)', value=True) \
                            .classes('w-full md:w-1/2 lg:w-1/3').disable()
                        ui.label('是否强制使用SSL加密连接。如果无法发送邮件，可以尝试关闭此选项，'
                                '海枫授权系统会尝试使用STARTTLS并决定是否使用加密连接').classes('w-full md:w-1/2 lg:w-1/3')

                        emailConnectTime = ui.input('SMTP连接有效期', value=await db.getSetting('emailConnectTime')) \
                            .classes('w-full md:w-1/2 lg:w-1/3')
                        ui.label('有效期内建立的SMTP连接会被新邮件发送请求复用').classes('w-full md:w-1/2 lg:w-1/3')

                        with ui.row():
                            ui.button('保存', on_click=lambda: (saveEMailSettings()))
                            ui.button('测试（请先保存）', on_click=sendEmailTestDialog.open)
                        
                    
                     # 推送设置


                    # 推送设置-页面
                    with ui.card().classes('w-full'):
                        tool.link_target('推送设置')
                        ui.label('推送设置').classes('text-h5')

                        with ui.element('div').classes('p-2 bg-blue-100 w-full'):
                            with ui.row(align_items='center'):
                                ui.icon('info').classes('text-blue-500 text-2xl')
                                ui.label('当用户购买某项产品时，系统会向用户发送购买详情。如果有新的盗版授权，系统会向管理员发送一条推送消息。')
                        
                        ui.label('还在做')


                    # 支付设置-页面
                    with ui.card().classes('w-full'):
                        tool.link_target('支付设置')
                        ui.label('支付设置').classes('text-h5')

                        with ui.element('div').classes('p-2 bg-blue-100 w-full'):
                            with ui.row(align_items='center'):
                                ui.icon('info').classes('text-blue-500 text-2xl')
                                ui.label('此服务由第三方平台提供， 产生的任何纠纷与 海枫授权系统 开发者无关。')
                        with ui.card().classes('w-full'):
                            # 支付宝当面付
                            with ui.row(align_items='center'):
                                ui.switch('启用支付宝当面付').classes('text-lg')
                                ui.link(text="支付宝应用管理平台", target='https://open.alipay.com/develop/manage', new_tab=True)
                                ui.link(text='开发文档参考：生成RSA密钥', target='https://opendocs.alipay.com/open/291/105971', new_tab=True)
                            aliDMPayAppID = ui.input('支付宝AppID', placeholder='当面付应用的App_ID').classes('w-full')
                            aliDMPayAppPrivateKey = ui.textarea('应用私钥', placeholder='当面付应用的 RSA2 (SHA256) 私钥，'
                                                                '一般是由您自己生成。').classes('w-full')
                            aliDMPayPublicKey = ui.textarea('支付宝公钥', placeholder='由支付宝提供，可在 应用管理 - 应用信息'
                                                            ' - 接口加签方式 中获取。').classes('w-full')
                            aliDMPayIsSandbox = ui.switch('使用沙箱环境')

                        with ui.card().classes('w-full'):
                        # 微信支付
                            with ui.row(align_items='center'):
                                ui.switch('启用微信支付(暂未开放，填了也没用)').classes('text-lg')
                                ui.link(text="微信支付商户平台", target='https://pay.weixin.qq.com/index.php/core/home/login', new_tab=True)
                                ui.link(text='开发文档参考：生成API密钥',
                                        target='https://pay.weixin.qq.com/wiki/doc/api/app/app.php?chapter=4_3', new_tab=True)

                        # 支付设置-保存易支付
                        async def saveEasyPayConfig():
                            await db.setSetting('easyPayUrl', easyPayUrl.value)
                            await db.setSetting('easyPayID', easyPayID.value)
                            await db.setSetting('easyPayKey', easyPayKey.value)
                            ui.notify('保存成功', color='positive') 

                        with ui.card().classes('w-full'):  
                            # 易支付渠道
                            with ui.row(align_items='center'):
                                ui.switch('启用彩虹聚合易支付渠道(目前仅支持彩虹易支付，不支持修改)', value=True).classes('text-lg').set_enabled(False)
                                #ui.link(text='开发文档参考：自定义支付渠道', target='about:blank', new_tab=True)
                            with ui.element('div').classes('p-2 bg-blue-100 w-full'):
                                with ui.row(align_items='center'):
                                    ui.icon('info').classes('text-blue-500 text-2xl')
                                    
                                    ui.label('目前仅支持V1接口（即MD5签名方式）。')
                            easyPayUrl = ui.input('支付接口URL(结尾不要带/)', placeholder='支付接口的URL，例如：https://pay.yxqi.cn', value=await db.getSetting('easyPayUrl')).classes('w-full')
                            easyPayID = ui.input('商户ID', placeholder='易支付商户ID', value=await db.getSetting('easyPayID')).classes('w-full')
                            easyPayKey = ui.input('商户密钥', placeholder='易支付商户密钥', value=await db.getSetting('easyPayKey')).classes('w-full')
                            saveEasyPayConfigButton = ui.button('保存', on_click=lambda: (saveEasyPayConfig()))
                        
                        # 自定义支付渠道
                        with ui.row(align_items='center'):
                            ui.switch('启用自定义支付渠道').classes('text-lg')
                            ui.link(text='开发文档参考：自定义支付渠道', target='about:blank', new_tab=True)
                        ui.input('支付渠道名称', placeholder='支付渠道的名称，例如：贝宝PayPal').classes('w-full')
                        ui.input('支付接口URL', placeholder='支付接口的URL，例如：https://pay.yourdomain.com/order').classes('w-full')
                        ui.textarea('支付私钥', placeholder='海枫授权系统 用于签名付款请求的RSA密钥').classes('w-full')

                        ui.button('保存', on_click=lambda: (ui.notify('功能暂未开放', color='negative')))

                        ui.label('还在做')
                        
                
                    # 授权设置
                    with ui.card().classes('w-full'):
                        tool.link_target('授权设置')
                        ui.label('授权设置').classes('text-h5')
                        
                        if siteDomain == "127.0.0.1" or siteDomain == "localhost":
                            with ui.element('div').classes('p-2 bg-orange-100 w-full'):
                                with ui.row(align_items='center'):
                                    ui.icon('favorite').classes('text-rose-500 text-2xl')
                                    ui.label('感谢您使用 海枫授权系统').classes('text-rose-500 text-bold')
                                with ui.column():
                                    ui.markdown('> 首次使用请在下方进行授权验证'
                                                '<br>'
                                                '海枫授权系统 是一款良心、厚道的好产品！创作不易，支持正版，从我做起！'
                                                '<br>'
                                                '如需在生产环境部署或者商用请前往 `auth.yxqi.cn` 购买正版'
                                                ).classes('text-rose-500')
                                    ui.markdown('- 海枫授权系统官网：[https://auth.yxqi.cn](https://auth.yxqi.cn)\n'
                                                '- 作者联系方式：QQ 2372526808\n'
                                                '- 管理我的授权：[https://auth.yxqi.cn/product/1](https://auth.yxqi.cn/product/1)\n'
                                                ).classes('text-rose-500')
                            ui.label('您正在进行本地调试，无需授权即可体验完整版海枫授权系统。').classes('text-rose-500 text-bold')
                        elif not await db.getSetting('License'):
                            with ui.element('div').classes('p-2 bg-orange-100 w-full'):
                                with ui.row(align_items='center'):
                                    ui.icon('favorite').classes('text-rose-500 text-2xl')
                                    ui.label('感谢您使用 海枫授权系统').classes('text-rose-500 text-bold')
                                with ui.column():
                                    ui.markdown('> 首次使用请在下方进行授权验证'
                                                '<br>'
                                                '海枫授权系统 是一款良心、厚道的好产品！创作不易，支持正版，从我做起！'
                                                '<br>'
                                                '请确认已在 海枫授权系统官网 已将本站域名 `{}` 添加授权'.format(request.base_url.hostname)
                                                ).classes('text-rose-500')
                                    ui.markdown('- 海枫授权系统官网：[https://auth.yxqi.cn](https://auth.yxqi.cn)\n'
                                                '- 作者联系方式：QQ 2372526808\n'
                                                '- 管理我的授权：[https://auth.yxqi.cn/product/1](https://auth.yxqi.cn/product/1)\n'
                                                ).classes('text-rose-500')
                            ui.label('当前未检测到授权，请前往海枫授权系统官网进行授权。').classes('text-rose-500 text-bold')
                            ui.button('刷新授权').classes('w-full').props('rounded')
                            #TODO:授权检测
                        else:
                            with ui.element('div').classes('p-2 bg-green-100 w-full'):
                                with ui.row(align_items='center'):
                                    ui.icon('verified').classes('text-green-500 text-2xl')
                                    ui.label('授权已通过').classes('text-green-500 text-bold')
                                with ui.column():
                                    ui.markdown('> 感谢您使用 海枫授权系统')
                                    ui.markdown('- 海枫授权系统官网：[https://auth.yxqi.cn](https://auth.yxqi.cn)\n'
                                                '- 作者联系方式：QQ 2372526808\n'
                                                '- 管理我的授权：[https://auth.yxqi.cn/product/1](https://auth.yxqi.cn/product/1)\n'
                                                ).classes('text-green-500')
                            ui.label('授权已通过，感谢您的支持！').classes('text-green-500 text-bold')
                            ui.button('刷新授权').classes('w-full').props('rounded')
                    

                    # 系统更新
                    with ui.card().classes('w-full'):
                        tool.link_target('系统更新')
                        ui.label('系统更新').classes('text-h5')
                

                # 等待客户端连接完成后跳转
                await ui.context.client.connected()
                if page == 'home':
                    tabs.set_value('home')
                elif page == 'income':
                    tabs.set_value('income')
                elif page == 'autlog':
                    tabs.set_value('autlog')
                elif page == 'blicense':
                    tabs.set_value('blicense')
                elif page == 'clicense':
                    tabs.set_value('clicense')
                elif page == 'addlicense':
                    tabs.set_value('addlicense')
                elif page == 'bquota':
                    tabs.set_value('bquota')
                elif page == 'cquota':
                    tabs.set_value('cquota')
                elif page == 'bproduct':
                    tabs.set_value('bproduct')
                elif page == 'cproduct':
                    tabs.set_value('cproduct')
                elif page == 'addproduct':
                    tabs.set_value('addproduct')
                elif page == 'user':
                    tabs.set_value('user')
                elif page == 'adduser':
                    tabs.set_value('adduser')
                elif page == 'ticket':
                    tabs.set_value('ticket')
                elif page == 'addticket':
                    tabs.set_value('addticket')
                elif page == 'cardmom':
                    tabs.set_value('cardmom')
                elif page == 'addcardmom':
                    tabs.set_value('addcardmom')
                elif page == 'addcardmom':
                    tabs.set_value('addcardmom')
                elif page == 'settings':
                    tabs.set_value('settings')
                else:
                    raise HTTPException(404, detail='Not Found')
        
            loading.close()

        except HTTPException:
            raise HTTPException(404, "Not Found")
        except:
            log.error(str(traceback.format_exc()))
            ui.run_javascript('alert("此站点遇到了致命错误，请根据程序终端命令进行排查，已使用红色[ ERROR ]标出。将退回至首页。")')
            ui.navigate.to('/')