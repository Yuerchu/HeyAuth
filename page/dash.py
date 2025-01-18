'''
Author: 于小丘 海枫
Date: 2024-10-02 15:23:34
LastEditors: Yuerchu admin@yuxiaoqiu.cn
LastEditTime: 2024-12-24 10:15:48
FilePath: /HeyAuth/page/dash.py
Description: 海枫授权系统 用户端管理 Dash

Copyright (c) 2018-2024 by 于小丘Yuerchu, All Rights Reserved. 
'''

# 防止被独立启动
if __name__ == '__main__':
    print("不支持单测，请使用main.py启动")
    exit(1)

from nicegui import ui, app
from pkg.model import database as database
import pkg.log as log
import asyncio
from pkg.tool import *
from contextlib import contextmanager
from fastapi import Request
import uuid
import traceback
from pkg.easyPay import easyPay

def create() -> None:
    @ui.page('/dash')
    async def dash(request: Request) -> None:
        await echoLog()
        user_id = int(app.storage.user['id'])
        ui.page_title('我的授权')
        db = database()

        await ui.context.client.connected()

        # 构建拉起支付进度条dialog
        with ui.dialog().props('persistent') as loading, ui.card():
            with ui.row(align_items='center'):
                ui.spinner(size='lg')
                ui.label('数据加载中...')
        
        loading.open()

        productName = await db.getProductNames()
        productNameList = list(productName.values())
        productNameList.insert(0, '')

        async def getProductInfo(name: str ='选择需要购买的产品'):
            if name == '选择需要购买的产品':
                productLevelChooser.set_visibility(False)
                chooseProductTips.set_text('请先选择产品')
            # 如果用户已经购买过选择的产品，则提醒用户联系管理员手动添加次数
            elif str(rows).find(name):
                productLevelChooser.set_visibility(False)
                chooseProductTips.set_text('您已购买过该产品，如需继续购买请联系管理员。')
            else:
                productLevelChooser.set_visibility(True)
                # TODO: 产品值目前默认为2
                ProductNumberChange = await db.getProductNumberChange(await db.getProductId(name))
                chooseProductTips.set_text('该产品默认授权为 {} 个，可更换 {} 次授权。' \
                                           .format(ProductNumberChange[0], ProductNumberChange[1]))
                priceList = await db.getProductPrice(product_id=await db.getProductId(name=name))
                priceList = [str(i) for i in priceList]
                if priceList[0] == "None":
                    month_license.set_text('月度授权')
                    month_license.disable()
                else:
                    month_license.set_text('月度授权 ￥{}'.format(priceList[0]))
                    month_license.enable()
                if priceList[1] == "None":
                    quarter_license.set_text('季度授权')
                    quarter_license.disable()
                else:
                    quarter_license.set_text('季度授权 ￥{}'.format(priceList[1]))
                    quarter_license.enable()
                if priceList[2] == "None":
                    year_license.set_text('年度授权')
                    year_license.disable()
                else:
                    year_license.set_text('年度授权 ￥{}'.format(priceList[2]))
                    year_license.enable()
                if priceList[3] == "None":
                    lifetime_license.set_text('终身授权')
                    lifetime_license.disable()
                else:
                    lifetime_license.set_text('终身授权 ￥{}'.format(priceList[3]))
                    lifetime_license.enable()
        
        async def checkProduct(value):
            if product.value == '选择需要购买的产品':
                ui.notify('请选择需要购买的产品', color='negative')
            else:
                priceList = await db.getProductPrice(product_id=await db.getProductId(name=product.value))
                priceList = [str(i) for i in priceList]
                paypriceNum.set_text(priceList[int(value)])
                buystepper.next()
        
# 定义一个异步函数jumpToPay，用于跳转到支付页面
        async def jumpToPay():
        # 打开支付页面
            preparePay.open()
            await asyncio.sleep(1)
            try:
        # 获取商品价格列表
                product_id = await db.getProductId(name=product.value)
                priceList = await db.getProductPrice(product_id=product_id)
        # 将价格列表中的元素转换为字符串
                priceList = [str(i) for i in priceList]
        # 获取支付金额
                price = int(paypriceNum.text)
        # 提交支付请求
                payURL = await easyPay.submitPay_v1(
                    user_id = app.storage.user['id'], 
                    product_id = await db.getProductId(name=product.value), 
                    out_trade_no = str(uuid.uuid4()).replace('-', ''),
                    notify_url = "https://" + str(request.base_url.hostname) + '/api/pay/easypay/b_return', 
                    return_url = "https://" + str(request.base_url.hostname) + '/api/pay/easypay/f_return', 
                    name = product.value, 
                    money = price
                    )
                # 跳转到支付页面
                ui.navigate.to(payURL)
            except Exception as e:
                # 打印错误信息
                log.error(f"支付失败：{str(e)}")
                log.error(str(traceback.format_exc()))
                # 关闭支付页面
                preparePay.close()
                # 提示支付失败
                ui.notify('支付失败，请联系管理员', color='negative')
            

        # 构建拉起支付进度条dialog
        with ui.dialog() as preparePay, ui.card():
                with ui.row(align_items='center'):
                    ui.spinner(size='lg')
                    ui.label('拉起支付中...')

        async def selectLegal():
            product_id = await db.getProductId(name=legalSelectProduct.value)
            findLegal = await db.getLegal(product_id=product_id, domain=legalSelectDomain.value)
            
            if findLegal: ui.notify('该域名是正版授权')
            else: ui.notify('该域名不是正版授权，建议立即举报')

        # 添加授权
        with ui.dialog() as addLicense, ui.card() \
            .style('width: 90%; max-width: 500px'):
            # 添加标题
            ui.button(icon='add_circle').props('outline round').classes('mx-auto w-auto shadow-sm w-fill')
            ui.label('添加授权').classes('text-h5 w-full text-center')
            
            ui.label('我们会以您绑定的第一个域名为标准，判断用户是否遵守授权规范。')
            ui.label('每次绑定和更换授权都会在本站记录，一旦发现用户违反授权规范做封号处理。')
            ui.label('如果绑定失败，请准备相关截图及待更换的域名与管理员联系。')
            
            ui.select(productNameList, value="").classes('w-full')

            selectDomain = ui.input('添加域名').classes('block w-full text-gray-900')

            ui.button('确认提交', on_click=lambda: (ui.notify('功能尚未开发，请联系管理员手动授权', color='negative'))) \
                .classes('items-center w-full').props('rounded')
            ui.button('返回', on_click=addLicense.delete).classes('w-full').props('flat rounded')


        # 更换授权
        with ui.dialog() as changeLicense, ui.card().style('width: 90%; max-width: 500px'):
            # 添加标题
            ui.button(icon='change_circle').props('outline round').classes('mx-auto w-auto shadow-sm w-fill')
            ui.label('更换授权').classes('text-h5 w-full text-center')
            
            ui.label('更换前域名和新域名所有人为同一人。')
            ui.label('或者更换前域名和新域名备案人为同一人。')
            ui.label('如果系统自动审核失败，请准备相关截图及待更换的域名与管理员联系。')
            
            ui.select(productNameList, value="").classes('w-full')

            selectDomain = ui.input('添加域名').classes('block w-full text-gray-900')

            ui.button('确认提交', on_click=lambda: (ui.notify('功能尚未开发，请联系管理员手动更换', color='negative'))) \
                .classes('items-center w-full').props('rounded')
            ui.button('返回', on_click=changeLicense.delete).classes('w-full').props('flat rounded')


        # 购买新授权
        with ui.dialog() as buyLicense, ui.card().style('width: 90%; max-width: 700px'):
            # 添加标题
            with ui.row(align_items='center'):
                ui.button(icon='arrow_back', on_click=ui.navigate.back).props('flat round')
                ui.label('购买新授权').classes('text-h5 text-center')
            '''ui.label('购买前请阅读下面的购买条款：')
            ui.label('代码类商品属于数字化商品，一旦支付不支持退款；')
            ui.label('授权程序仅供购买者使用，请勿分享源代码、程序；')
            ui.label('捐助版可在不二次分发的情况下自由进行二次开发及扩展；')
            ui.label('禁止将本产品用于含诈骗、赌博、色情、木马、病毒等违法违规业务；')'''
            
            # ui.label('目前我们不支持在线支付购买授权。请联系管理员购买。')

            # 获取所有在售产品
            productName = await db.getAllProduct()
            productName.insert(0, '选择需要购买的产品')

            #ui.select(productName, value="选择需要购买的产品")

            #ui.label('该产品默认授权为 {} 次，可更换 {} 个授权额度。'.format('1', '1'))

            with ui.stepper().props('vertical flat').classes('w-full') as buystepper:
                with ui.step('购买前必读'):
                    ui.label('代码类商品属于数字化商品，一旦支付不支持退款；')
                    ui.label('授权程序仅供购买者使用，请勿分享源代码、程序；')
                    ui.label('捐助版可在不二次分发的情况下自由进行二次开发及扩展；')
                    ui.label('禁止将本产品用于含诈骗、赌博、色情、木马、病毒等违法违规业务。')
                    with ui.stepper_navigation():
                        ui.button('我已阅读并同意，继续', on_click=buystepper.next)
                with ui.step('选择产品'):
                    product = ui.select(productName, value="选择需要购买的产品", on_change=lambda e: (getProductInfo(e.sender.value)))
                    chooseProductTips = ui.label("请先选择产品")

                    with ui.row(align_items='center') as productLevelChooser:
                        month_license = ui.button('月度授权', on_click=lambda: (checkProduct(value=0))).props('outline')
                        quarter_license = ui.button('季度授权', on_click=lambda: (checkProduct(value=1))).props('outline')
                        year_license = ui.button('年度授权', on_click=lambda: (checkProduct(value=2))).props('outline')
                        lifetime_license = ui.button('终身授权', on_click=lambda: (checkProduct(value=3))).props('outline')
                    productLevelChooser.set_visibility(False)

                    with ui.stepper_navigation():
                        ui.button('重新阅读用户协议', on_click=buystepper.previous).props('flat')
                with ui.step('支付'):
                    # ui.label('目前我们不支持在线支付购买授权。请联系管理员购买。')
                    payProductName = ui.label()
                    payProductLevel = ui.label()
                    ui.label('请选择支付方式：')
                    ui.radio(['支付宝支付', '微信支付']).props('inline')
                    with ui.row(align_items='center'):
                        paypriceTips = ui.label("价格(不包含手续费)：")
                        paypriceNum = ui.label()
                    ui.label('可能会有手续费，请以实际支付金额为准。')
                    with ui.stepper_navigation():
                        ui.button(text='前往支付', icon='arrow_forward', on_click=lambda: (jumpToPay()))
                        ui.button('重新选择产品', on_click=buystepper.previous).props('flat')


        # 正版查询
        with ui.dialog() as legal, ui.card().style('width: 90%; max-width: 500px'):
            # 添加标题
            ui.button(icon='gpp_good').props('outline round').classes('mx-auto w-auto shadow-sm w-fill')
            ui.label('正版查询').classes('text-h5 w-full text-center')
            ui.label('输入需要查询正版的完整域名')
            ui.label('如若是盗版请立即举报，举报核实后将获得丰厚奖励')
            
            legalSelectProduct = ui.select(productNameList, value="").classes('w-full')

            legalSelectDomain = ui.input('查询域名').classes('block w-full text-gray-900')

            ui.button('确认提交', on_click=lambda: selectLegal()) \
                    .classes('items-center w-full').props('rounded')
            ui.button('返回', on_click=legal.delete).classes('w-full').props('flat rounded')
        

        # 盗版举报
        with ui.dialog() as pirate, ui.card().style('width: 90%; max-width: 500px'):
            # 添加标题
            ui.button(icon='warning').props('outline round').classes('mx-auto w-auto shadow-sm w-fill')
            ui.label('盗版举报').classes('text-h5 w-full text-center')

            ui.select(productNameList, value="").classes('w-full')

            selectDomain = ui.input('举报域名').classes('block w-full text-gray-900')

            ui.label('违规证据(2MB以内)：')
            ui.upload(
                max_file_size=2_000_000, 
                on_rejected=lambda: ui.notify('文件大小不得超过2MB')).classes('w-full').props("accept='.jpg, image/*'")

            ui.button('确认提交', on_click=lambda: (ui.notify('调用查询失败：数据库连接异常', color='negative'))) \
                .classes('items-center w-full').props('rounded')
            ui.button('返回', on_click=pirate.delete).classes('w-full').props('flat rounded')


        dark_mode = ui.dark_mode(value=app.storage.browser.get('dark_mode'), on_change=lambda e: ui.run_javascript(f'''
                                fetch('/dark_mode', {{
                                    method: 'POST',
                                    headers: {{'Content-Type': 'application/json'}},
                                    body: JSON.stringify({{value: {e.value}}}),
                                }});
                            '''))
        
        with ui.header() \
            .classes('items-center duration-300 mb-2 px-5 py-2 no-wrap') \
            .style('box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1)'):

            ui.button(icon='menu').props('flat color=white round')
            ui.button(text='控制台').classes('text-lg').props('flat color=white')

            ui.space()

            # 主题切换
            with ui.element().tooltip('主题切换'):
                ui.button(icon='dark_mode', on_click=lambda: dark_mode.set_value(None)) \
                    .props('flat fab-mini color=white').bind_visibility_from(dark_mode, 'value', value=True)
                ui.button(icon='light_mode', on_click=lambda: dark_mode.set_value(True)) \
                    .props('flat fab-mini color=white').bind_visibility_from(dark_mode, 'value', value=False)
                ui.button(icon='brightness_auto', on_click=lambda: dark_mode.set_value(False)) \
                    .props('flat fab-mini color=white').bind_visibility_from(dark_mode, 'value', lambda mode: mode is None)
            
            # 等待一秒，防止页面加载过快被扒
            await asyncio.sleep(1)

            # 菜单
            with ui.button().props('flat fab-mini'):
                with ui.avatar().classes('w-10 h-10'):
                    QQ_Code = app.storage.user['qq']
                    ui.image('http://q1.qlogo.cn/g?b=qq&nk={QQ_Code}&s=100'.format(QQ_Code=QQ_Code)).classes('w-10 h-10')
                with ui.menu().classes('w-60').props('auto-close'):
                    ui.menu_item('添加授权', on_click=addLicense.open).classes('items-center')
                    ui.menu_item('更换授权', on_click=changeLicense.open).classes('items-center')
                    ui.menu_item('购买新授权', on_click=buyLicense.open).classes('items-center')
                    ui.menu_item('用户中心', on_click=lambda: (ui.navigate.to('/user'))).classes('items-center')
                    ui.menu_item('工单管理', on_click=lambda: (myTicketsDialog.open)).classes('items-center')
                    ui.menu_item('正版查询', on_click=legal.open)
                    ui.menu_item('盗版举报', on_click=pirate.open)
                    try:
                        if user_id == 1:
                            ui.menu_item('后台管理', on_click=lambda: (ui.navigate.to('/admin'))).classes('items-center')
                    except:
                        pass
                    ui.menu_item('退出登录', on_click=lambda: (app.storage.user.clear(), ui.navigate.to('/login')))


        # 构建用户工单的Dialog
        with ui.dialog() as myTicketsDialog, ui.card().style('width: 90%; max-width: 500px'):
            ui.label('我的工单').classes('text-h5')

            with ui.row(align_items='center').classes('w-full'):
                ui.button('发起新工单')
                ui.space()
                ui.input(placeholder='搜索工单')
                ui.button('搜索')


            with ui.row():
                ui.button("添加")
                ui.button("返回", on_click=myTicketsDialog.close)

        def productNameListOnClick():
            if productSelecter.value == '':
                userDashProductTable.set_visibility(False)
                noProductSelected.set_visibility(True)
            else:
                noProductSelected.set_visibility(False)
                userDashProductTable.set_visibility(True)

        # 创建一个包含绝对居中和项目中心的列
        with ui.card().classes('mx-auto py-18').style('width: 90%; max-width: 1200px').props('flat'):
            with ui.row().classes('w-full'):
                with ui.card().classes("w-full lg:w-1/5 flex-grow"):
                    ui.label("选择产品").classes('text-h6')
                    productSelecter = ui.select(
                        productNameList, on_change=lambda: productNameListOnClick()).classes('w-full')

                
                with ui.card().classes("w-full lg:w-1/5 flex-grow"):
                    with ui.row(align_items='center').classes('w-full'):
                        ui.label("产品详情").classes('text-h6')
                        ui.space()
                        ui.button('查看购买项')

                    ui.label('剩余授权额度次数：{}'.format(0))
                    ui.label('剩余更换授权次数：{}'.format(0))
            
            # 创建一个卡片，用于没有选中产品时间显示“请先选择产品”
            with ui.card().classes('w-full') as noProductSelected:
                ui.label('正版授权').classes('text-h6')
                ui.label('请先选择产品').classes('w-full py-10 text-h5 text-center')

            # 授权列表
            columns = [
                {'name': 'product', 'label': '授权产品', 'field': 'product', 'sortable': True, 'align': 'left'},
                {'name': 'domain', 'label': '授权域名', 'field': 'domain', 'sortable': True, 'align': 'left'},
                {'name': 'status', 'label': '授权状态', 'field': 'status', 'sortable': True, 'align': 'left'},
                {'name': 'key', 'label': '授权码', 'field': 'key', 'sortable': True, 'align': 'left'},
                {'name': 'time', 'label': '授权有效期', 'field': 'time', 'sortable': True, 'align': 'left'},
            ]
            rows = []

            # 在数据库中查找该用户的授权
            UserAuth = await db.getUserAuthsB(id=user_id)

            for i in range(len(UserAuth)):
                rows.append({'product': productName[int(UserAuth[i][2])], 'domain': UserAuth[i][4], 'status': UserAuth[i][3], 
                             'key': UserAuth[i][5], 'time': UserAuth[i][7]})

            userDashProductTable = ui.table(
                columns=columns, 
                rows=rows, 
                row_key="name", 
                pagination=5, 
                title='正版授权').classes('w-full max-h-72')
            productSelecter.bind_value(userDashProductTable, 'filter')
            # 默认隐藏，因为没有选中产品
            userDashProductTable.set_visibility(False)

        loading.close()
        loading.delete()