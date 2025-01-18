'''
Author: 于小丘 海枫
Date: 2024-08-06 09:52:15
LastEditors: Yuerchu admin@yuxiaoqiu.cn
LastEditTime: 2024-12-13 13:13:38
FilePath: /HeyAuth/pkg/database.py
Description: 海枫授权系统 数据库组件 `核心中间件`

Copyright (c) 2018-2024 by 于小丘Yuerchu, All Rights Reserved. 
'''

# 二开强烈建议配合VSCode的Python-string-sql插件使用: https://marketplace.visualstudio.com/items?itemName=ptweir.python-string-sql

import aiosqlite
from rich import print as printx
from typing import Literal, Optional, List, Dict, Any
from datetime import datetime, timedelta
import logging
try:
    from pkg.tool import *
    import pkg.log as log
except: pass

DatabaseConn = None

class database():
    async def __get_connection(self) -> aiosqlite.Connection:
        """
        获得数据库连接 Get database connection
        ~~~
        用法：
        ---
            >>> conn = await self.__get_connection()
            await conn.execute(sqlcode, params)
            await conn.commit()
        """
        global DatabaseConn
        if DatabaseConn is None:
            DatabaseConn = await aiosqlite.connect(database='data.db')
        return DatabaseConn

    async def init(self) -> None:
        '''
        初始化数据库
        ~~~
        如果数据库不存在或者数据库异常将会执行初始化操作，初始化将会在终端中打印账号与密码，请注意保存。
        '''
        conn = await self.__get_connection()
        try:
            await conn.execute("SELECT value FROM heyauth_settings WHERE name = 'version'")
            log.debug('Database already exist, skip init')
        except:
            log.info('Database not exist, start init')

            log.debug('Creating heyauth_auth_b ...')
            # B端授权表
            await conn.execute("""
                                --sql
                                CREATE TABLE IF NOT EXISTS "heyauth_auth_b" (
                                "id"	        INTEGER NOT NULL UNIQUE ,   -- 授权ID
                                "user_id"	    BIGINT,                     -- 授权用户ID
                                "product_id"	BIGINT ,                    -- 产品ID
                                "active"	    TEXT ,                      -- 激活状态
                                "domain"        TEXT ,                      -- 授权域名
                                "auth_key"	    TEXT ,                      -- 授权码
                                "time"          TEXT ,                      -- 授权有效期
                                "create_at"	    DATETIME ,                  -- 创建时间
                                "delete_at"	    DATETIME ,                  -- 删除/异常时间
                                "banReason"	    TEXT ,                      -- 封禁原因
                                PRIMARY KEY("id" AUTOINCREMENT)
                                );""")
            log.debug('Done')
            
            log.debug('Creating heyauth_auth_c ...')
            # C端授权表
            await conn.execute("""
                                --sql
                                CREATE TABLE IF NOT EXISTS "heyauth_auth_c" (
                                "id"	        INTEGER NOT NULL UNIQUE ,   -- 授权ID
                                "user_id"	    BIGINT,                     -- 授权用户ID
                                "product_id"	BIGINT ,                    -- 产品ID
                                "active"    	TEXT ,                      -- 激活状态
                                "cilent_info"   TEXT ,                      -- 客户端信息
                                "auth_key"	    TEXT ,                      -- 授权码
                                "time"          TEXT ,                      -- 授权有效期
                                "create_at"	    DATETIME ,                  -- 创建时间
                                "delete_at"	    DATETIME ,                  -- 删除/异常时间
                                PRIMARY KEY("id" AUTOINCREMENT)
                                );""")
            
            log.debug('Creating heyauth_pirated_b ...')
            # 盗版B端表
            await conn.execute("""
                                --sql
                                CREATE TABLE IF NOT EXISTS "heyauth_pirated_b" (
                                "id"	        INTEGER NOT NULL UNIQUE ,   -- 盗版ID
                                "domain"	    TEXT ,                      -- 盗版域名
                                "ip"	        TEXT ,                      -- 盗版IP
                                "db_name"	    TEXT ,                      -- 盗版数据库名
                                "db_user"	    TEXT ,                      -- 盗版数据库用户
                                "db_pwd"        TEXT ,                      -- 盗版数据库密码
                                "find_at"	    DATETIME ,                  -- 发现时间
                                "freq"          INTEGER ,                   -- 激活次数
                                PRIMARY KEY("id" AUTOINCREMENT)
                                );""")
            
            log.debug('Creating heyauth_pirated_c ...')
            # 盗版C端表
            await conn.execute("""
                                --sql
                                CREATE TABLE IF NOT EXISTS "heyauth_pirated_c" (
                                "id"	        INTEGER NOT NULL UNIQUE ,   -- 盗版ID
                                "domain"	    TEXT ,                      -- 盗版域名
                                "cilent_info"   TEXT ,                      -- 客户端信息
                                "find_at"	    DATETIME ,                  -- 发现时间
                                "freq"          INTEGER ,                   -- 激活次数
                                PRIMARY KEY("id" AUTOINCREMENT)
                                );""")

            log.debug('Creating heyauth_product_b ...')
            # B端产品表
            await conn.execute("""
                                --sql
                                CREATE TABLE IF NOT EXISTS "heyauth_product_b" (
                                "id"	        INTEGER NOT NULL UNIQUE ,   -- '产品ID'
                                "name"	        TEXT ,                      -- '产品名称'
                                "create_at"	    DATETIME ,                  -- '创建时间'
                                "delete_at"	    DATETIME ,                  -- '删除时间'
                                "price_month"	TEXT ,                      -- '产品月度价格'
                                "price_quarter"	TEXT ,                      -- '产品季度价格'
                                "price_year"	TEXT ,                      -- '产品年度价格'
                                "price_life"	TEXT ,                      -- '产品终身价格'
                                "number"	    INTEGER ,                   -- '产品数量'
                                "change"        INTEGER ,                   -- '变更次数'
                                "content"       TEXT ,                      -- '商品介绍页'
                                "paied_info"    TEXT ,                      -- '支付后的信息'
                                PRIMARY KEY("id" AUTOINCREMENT)
                                );""")
            
            log.debug('Creating heyauth_order ...')
            # 用户订单表
            await conn.execute("""
                                --sql
                                CREATE TABLE IF NOT EXISTS "heyauth_order" (
                                "id"	        INTEGER NOT NULL UNIQUE ,   -- '订单ID',
                                "order_id"	    TEXT  ,                     -- '订单号'
                                "user_id"	    INTEGER ,                   --  '用户ID'
                                "product_id"	INTEGER ,                   -- '产品ID'
                                "auth"	        INTEGER ,                   -- '授权次数'
                                "change_auth"	INTEGER ,                   -- '更换授权次数'
                                "order_name"    TEXT ,                      -- '商品名称'
                                "price"         TEXT,                       -- '价格'
                                "create_at"	    DATETIME ,                  --  '下单日期'
                                "status"    	TEXT,                       -- '订单状态'
                                "pay_method"	TEXT ,                      -- '支付方式'
                                "delete_at"     TEXT ,                      -- '到期时间'
                                PRIMARY KEY("id" AUTOINCREMENT)
                                );""")
            
            log.debug('Creating heyauth_aut_lst ...')
            # 授权变更表
            await conn.execute("""
                                --sql
                                CREATE TABLE IF NOT EXISTS "heyauth_aut_lst" (
                                "id"	        INTEGER NOT NULL UNIQUE ,   -- '日志ID'
                                "user_id"	    INTEGER ,                   -- '用户ID'
                                "product_id"	INTEGER ,                   -- '产品ID'
                                "total_auth"	INTEGER ,                   -- '总授权次数'
                                "remain_auth"	INTEGER ,                   -- '剩余授权次数'
                                "changeX_auth"  INTEGER ,                   -- '总变更授权次数'
                                "change_auth"   INTEGER ,                   -- '剩余授权次数'
                                "operate_time"  DATETIME ,                  -- '操作时间'
                                "expired_time"  DATETIME ,                  -- '到期时间'
                                PRIMARY KEY("id" AUTOINCREMENT)
                                );""")
            
            log.debug('Creating heyauth_aut_log ...')
            # 操作日志日志表
            await conn.execute("""
                                --sql
                                CREATE TABLE IF NOT EXISTS "heyauth_aut_log" (
                                "id"	        INTEGER NOT NULL UNIQUE ,   -- '日志ID'
                                "product_id"	INTEGER ,                   -- '产品ID'
                                "status"        TEXT ,                      -- '状态'
                                "operate_time"  DATETIME ,                  -- '操作时间'
                                PRIMARY KEY("id" AUTOINCREMENT)
                                );""")
            
            log.debug('Creating heyauth_cardmom ...')
            # 卡密表
            await conn.execute("""
                                --sql
                                CREATE TABLE IF NOT EXISTS "heyauth_cardamom" (
                                "id"	        INTEGER NOT NULL UNIQUE ,   -- '卡密ID'
                                "card"	        TEXT ,                      -- '卡密'
                                "product_id"	INTEGER ,                   -- '产品ID'
                                "status"	    TEXT ,                      -- '卡密状态'
                                "auth"          INTEGER ,                   -- '授权次数'
                                "change"        INTEGER ,                   -- '变更次数'
                                "create_at"	    DATETIME ,                  -- '创建时间'
                                "delete_at"	    DATETIME ,                  -- '删除时间'
                                PRIMARY KEY("id" AUTOINCREMENT)
                                );""")
            
            log.debug('Creating heyauth_tickets ...')
            # 工单表
            await conn.execute("""
                                --sql
                                CREATE TABLE IF NOT EXISTS "heyauth_tickets" (
                                "id"	        INTEGER NOT NULL UNIQUE ,   -- '工单ID'
                                "user_id"	    INTEGER ,                   -- '用户ID'
                                "product_id"	INTEGER ,                   -- '产品ID'
                                "status"	    TEXT ,                      -- '工单状态'
                                "content"	    TEXT ,                      -- '工单内容'
                                "create_at"	    DATETIME ,                  -- '创建时间'
                                "update_at"	    DATETIME ,                  -- '更新时间'
                                PRIMARY KEY("id" AUTOINCREMENT)
                                );""")
            
            log.debug('Creating heyauth_settings ...')
            # 系统设置表
            await conn.execute("""
                                --sql
                                CREATE TABLE IF NOT EXISTS "heyauth_settings" (
                                "type"	        TEXT,
                                "name"	        TEXT,
                                "value"	        TEXT
                                );""")
            
            log.debug('Creating heyauth_user ...')
            # 用户表
            await conn.execute("""
                                --sql
                                CREATE TABLE IF NOT EXISTS "heyauth_user" (
                                "id"	        INTEGER NOT NULL UNIQUE ,   -- '用户ID'
                                "status"	    TEXT ,                      -- '用户状态'
                                "name"	        TEXT ,                      -- '用户昵称'
                                "account"	    TEXT UNIQUE ,               -- '账号'
                                "password"	    TEXT ,                      -- '密码'
                                "QQ"            TEXT ,                      -- 'QQ'
                                "token"	        TEXT ,                      -- Token
                                "code"          TEXT ,                      -- '验证码'
                                "code_time"     TEXT ,                      -- '验证码有效期'
                                "inviter"       TEXT ,                      -- '邀请者'
                                "signup_at"	    DATETIME ,                  -- '注册日期'
                                "balance"        REAL ,                     -- '余额'
                                PRIMARY KEY("id" AUTOINCREMENT)
                                );""")
            log.info('Generating admin account ...')
            password = generate_password(8)
            password_code = hash_password(password)
            now = datetime.now()
            now = now.strftime("%Y-%m-%d %H:%M:%S")
            log.debug('Saving HeyAuth info ...')
            # 写入管理员账号信息
            await conn.execute("""
                                --sql
                                INSERT INTO heyauth_user (status, account, password, signup_at)
                                VALUES ('ok', '{}', '{}', '{}');""".format(
                                "admin@yuxiaoqiu.cn", password_code, now))
            
            # 初始化海枫授权系统默认配置
            await conn.execute("""
                                --sql
                                INSERT INTO heyauth_settings (type, name, value)
                                VALUES ('TEXT', 'version', '1.0.0');""")
            await conn.execute("""
                                --sql
                                INSERT INTO heyauth_settings (type, name, value)
                                VALUES ('TEXT', 'site_name', '海枫授权系统');""")
            await conn.execute("""--sql
                                INSERT INTO heyauth_settings (type, name, value)
                                VALUES ('TEXT', 'bottom_text', 'Copyright © 2018-至今 于小丘Yuerchu 版权所有.');""")
            __storage_secret = generate_password(32)
            await conn.execute("""
                                --sql
                                INSERT INTO heyauth_settings (type, name, value)
                                VALUES ('TEXT', 'storage_secret', '{}');""".format(
                                __storage_secret))
            await conn.execute("""
                                --sql
                                INSERT INTO heyauth_settings (type, name, value)
                                VALUES ('TEXT', 'mainPage_title', '海枫筑梦计划');""")
            await conn.execute("""
                                --sql
                                INSERT INTO heyauth_settings (type, name, value)
                                VALUES ('TEXT', 'mainPage_subtitle', '多应用授权系统');""")
            await conn.execute("""
                                --sql
                                INSERT INTO heyauth_settings (type, name, value)
                                VALUES ('TEXT', 'mainPage_description', '海枫授权系统旨在为个人开发者或者中小企业提供一种高效便捷的程序管理方案。通过海枫授权系统，您可以随时随地的面向您的B端或是C端用户管理授权。此外还可以通过简单的配置实现程序的在线下载与更新、盗版程序的追踪打击。');""")
            await conn.execute("""
                                --sql
                                INSERT INTO heyauth_settings (type, name, value)
                                VALUES ('TEXT', 'siteIcon', '🚀');""")
            await conn.execute("""
                                --sql
                                INSERT INTO heyauth_settings (type, name, value)
                                VALUES ('TEXT', 'icp_beian', '');""")
            await conn.execute("""
                                --sql
                                INSERT INTO heyauth_settings (type, name, value)
                                VALUES ('TEXT', 'ga_beian', '');""")
            await conn.commit()
            printx(f'Admin account：[bold]admin@yuxiaoqiu.cn[/bold]')
            printx('Admin password：[bold]{}[/bold]'.format(password))
            printx('storage_secret：[bold]' + str(__storage_secret) + '[/bold]')
            log.warning('Warning: The account and password nolonger '
                        'display after the program exits. Please save them in time.')
            log.info('Model init done.')
    
    async def addLicenseB(
            self, 
            user_id: int, 
            product_id: int, 
            domain: str, 
            expiredTime: str, 
            key: str = None, 
            usingNumber: bool = True) -> None:
        """
        添加B端授权信息。

        :param user_id: 用户ID
        :type user_id: int
        :param product_id: 产品ID
        :type product_id: int
        :param domain : 授权域名（IP也行）
        :type domain: str
        :param expiredTime : 授权到期时间 格式：2024-07-28 21:40:00
        :type expiredTime: str
        :param key: 授权码(可选) 不传入则调用tool.generate_code(32)方法自动生成
        :type key: str
        """
        if key is None: key = generate_password(32)

        now = datetime.now()
        now = now.strftime("%Y-%m-%d %H:%M:%S")

        if usingNumber == True:
            sqlcode = """
                    --sql
                    SELECT *
                    FROM heyauth_aut_lst
                    WHERE user_id = ?
                    AND product_id = ?"""

        sqlcode = """
                    --sql
                    INSERT INTO heyauth_auth_b (user_id, product_id, domain, auth_key, create_at, active, time)
                    VALUES (?, ?, ?, ?, ?, 'ok', ?);
                    """
        params = (user_id, product_id, domain, key, now, expiredTime)

        conn = await self.__get_connection()
        await conn.execute(sqlcode, params)
        await conn.commit()

    async def addLine(self, product_id, user_id, number, change):
        """
        添加授权额度信息。如果找到则更新，否则添加。
        
        :param product_id: 产品ID
        :type product_id: int
        :param user_id: 用户ID
        :type user_id: int
        :param number: 授权次数
        :type number: int
        :param change: 更换次数
        :type change: int
        """
        now = datetime.now()
        now = now.strftime("%Y-%m-%d %H:%M:%S")

        sqlcode = """
                    --sql
                    SELECT * FROM heyauth_aut_lst
                    WHERE user_id = ?
                    AND product_id = ?;
                    """
        params = (user_id, product_id)

        conn = await self.__get_connection()
        line = await conn.execute(sqlcode, params)
        line = await line.fetchone()

        if line:
            total_auth = int(line[3]) + number
            remain_auth = int(line[4]) + number
            changeX_auth = int(line[5]) + change
            change_auth = int(line[6]) + change

            now = datetime.now()
            now = now.strftime("%Y-%m-%d %H:%M:%S")

            sqlcode = """
                --sql
                UPDATE heyauth_aut_lst
                SET total_auth = ?,
                remain_auth = ?,
                changeX_auth = ?,
                change_auth = ?,
                operate_time = ?
                WHERE user_id = ?
                AND product_id = ?;
                """,
            params = (total_auth, remain_auth, changeX_auth, change_auth, now, user_id, product_id)
            await conn.execute(sqlcode, params)

        else:
            await conn.execute(
                """
                --sql
                INSERT INTO heyauth_aut_lst (user_id, product_id, total_auth, remain_auth, changeX_auth, change_auth, operate_time)
                VALUES (?, ?, ?, ?, ?, ?, ?);
                """,
            (user_id, product_id, number, number, change, change, now))
        await conn.commit()
    
    async def addOrder(self, user_id: int, product_id: int, product_name: str, price: float, payType: str, order_id: str, pay_status: str = 'paying', auth= 0, change_auth=0) -> None:
        '''
        添加订单信息。支付状态默认为`Paying`, 即支付中，若要修改请传入`pay_status`参数。

        :param user_id: 用户ID
        :type user_id: int
        :param product_id: 产品ID
        :type product_id: int
        :param product_name: 产品名称
        :type product_name: str
        :param price: 价格
        :type price: float
        :param payType: 支付方式
        :type payType: str
        :param order_id: 订单号
        :type order_id: str
        :param pay_status: 支付状态
        :type pay_status: str
        :param auth: 授权次数
        :type auth: int
        :param change_auth: 更换次数
        :type change_auth: int
        '''
        now = datetime.now()
        now = now.strftime("%Y-%m-%d %H:%M:%S")

        #TODO: 填充授权次数与更换次数
        sqlcode = """
                    --sql
                    INSERT INTO heyauth_order (user_id, product_id, order_name, price, pay_method, pay_time, order_id, create_at, Status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
                    """
        params = (user_id, product_id, product_name, price, payType, None, order_id, now, pay_status)

        conn = await self.__get_connection()
        await conn.execute(sqlcode, params)
        await conn.commit()
    
    async def addProduct(self, name: str, price_month: str, price_quarter: str, price_year: str, price_life: str, auth: str, change_auth: str) -> None:
        '''
        添加产品信息。
        '''
        now = datetime.now()
        now = now.strftime("%Y-%m-%d %H:%M:%S")

        sqlcode = """
                    --sql
                    INSERT INTO heyauth_product_b (name, create_at, price_month, price_quarter, price_year, price_life, number, change)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?);
                    """
        params = (name, now, price_month, price_quarter, price_year, price_life, auth, change_auth)

        conn = await self.__get_connection()
        await conn.execute(sqlcode, params)
        await conn.commit()

    async def addPirate(self, domain: str, ip: str, db_name: str, db_user: str, db_pwd: str) -> bool:
        '''
        添加盗版信息。
        '''
        # 检查是否有同样的盗版信息，如用则freq+1且不动find_at，没有则添上
        try:
            conn = await self.__get_connection()
            pirate = await conn.execute(
                """
                --sql
                SELECT * FROM heyauth_pirated_b
                WHERE domain = ?
                AND db_name = ?
                AND db_user = ?
                AND db_pwd = ?;
                """, 
            (domain, db_name, db_user, db_pwd))
            pirate = await pirate.fetchone()
            if pirate:
                freq = pirate[7] + 1
                await conn.execute(
                    """
                    --sql
                    UPDATE heyauth_pirated_b
                    SET freq = ?
                    WHERE domain = ?
                    AND db_name = ?
                    AND db_user = ?
                    AND db_pwd = ?;
                    """, 
                (freq, domain, db_name, db_user, db_pwd))
            else:
                now = datetime.now()
                now = now.strftime("%Y-%m-%d %H:%M:%S")
                await conn.execute(
                    """
                    --sql
                    INSERT INTO heyauth_pirated_b (domain, ip, db_name, db_user, db_pwd, find_at, freq)
                    VALUES (?, ?, ?, ?, ?, ?, 1);
                    """, 
                (domain, ip, db_name, db_user, db_pwd, now))
            await conn.commit()
        except Exception as e:
            log.error('添加盗版信息失败：' + str(e))
            raise e
        else:
            return True
    
    async def addUser(self, account: str, password: str = None, code: int = None, force: bool = False) -> None:
        '''
        <p>注册用户</p>
        ---
        ### 字段 Param
        - `account` : 账号
        - `password` : 密码
        - `code` : 验证码
        '''
        now = datetime.now()
        time = now + timedelta(minutes=5)
        time = time.strftime("%Y-%m-%d %H:%M:%S")

        sqlcode = """
                    --sql
                    INSERT INTO heyauth_user (status, account, code, code_time, signup_at)
                    VALUES (?, ?, ?, ?, ?);
                    """
        if force != True:
            params = ('verify', account, code, time, now)
        else:
            params = ('ok', account, None, None, now)

        conn = await self.__get_connection()
        await conn.execute(sqlcode, params)
        await conn.commit()
    
    async def banLicenseB(self, id, reason) -> None:
        '''
        封禁授权。
        '''
        now = datetime.now()
        now = now.strftime("%Y-%m-%d %H:%M:%S")
        sqlcode = """
                    --sql
                    UPDATE heyauth_auth_b
                    SET active = 'ban', banReason = ?, delete_at = ?
                    WHERE id = ?;
                    """
        params = (reason, now, id)

        conn = await self.__get_connection()
        await conn.execute(sqlcode, params)
        await conn.commit()

    async def checkAuth(self, product_id, domain, key = None) -> list[str] | None:
        '''
        检查授权是否存在。
        '''
        if key != None:
            sqlcode = ("""
                    --sql
                    SELECT * FROM heyauth_auth_b
                    WHERE product_id = ?
                    AND domain = ?
                    AND auth_key = ?;
                    """)
            params = (product_id, domain, key)
        else:
            sqlcode = ("""
                    --sql
                    SELECT * FROM heyauth_auth_b
                    WHERE product_id = ?
                    AND domain = ?;
                    """)
            params = (product_id, domain)

        conn = await self.__get_connection()
        auth = await conn.execute(sqlcode, params)
        auth = await auth.fetchone()

        if auth != None:
            log.debug('授权信息：' + str(auth))
            return auth
        else:
            return None
            

    async def getAllProduct(self) -> list[str] | None:
        '''
        获取所有产品信息
        '''
        sqlcode = """
                    --sql
                    SELECT name
                    FROM heyauth_product_b;
                    """

        conn = await self.__get_connection()
        products = await conn.execute(sqlcode)
        products = await products.fetchall()
        if products != None:
            products = [product[0] for product in products]
            return products
        else:
            return None
    
    async def getActiveExpiredTimes(self) -> list[str]:
        '''
        获取授权管理授权到期时间的列。
        '''
        sqlcode = """
                    --sql
                    SELECT time
                    FROM heyauth_auth_b;
                    """

        conn = await self.__get_connection()
        cursor = await conn.execute(sqlcode)
        times = await cursor.fetchall()
        times = [time[0] for time in times]
        return times
    
    async def getActiveNum(self) -> int:
        '''
        获取激活的产品的数量。
        '''
        sqlcode = """
                    --sql
                    SELECT id
                    FROM heyauth_auth_b;
                    """

        conn = await self.__get_connection()
        num = await conn.execute(sqlcode)
        num = await num.fetchall()
        num = len(num)
        return num
    
    async def getActiveIds(self) -> list[int]:
        '''
        获取授权管理授权id的列。
        '''
        sqlcode = """
                    --sql
                    SELECT id
                    FROM heyauth_auth_b;
                    """


        conn = await self.__get_connection()
        ids = await conn.execute(sqlcode)
        ids = await ids.fetchall()
        ids = [id[0] for id in ids]
        return ids
    
    async def getActiveUsers(self) -> list[int]:
        '''
        获取授权管理授权用户的列。
        '''
        sqlcode = """
                    --sql
                    SELECT user_id
                    FROM heyauth_auth_b;
                    """


        conn = await self.__get_connection()
        users = await conn.execute(sqlcode)
        users = await users.fetchall()
        users = [user[0] for user in users]
        return users
    
    async def getActiveProducts(self) -> list[int]:
        '''
        获取授权管理产品的列。
        '''
        sqlcode = """
                    --sql
                    SELECT product_id
                    FROM heyauth_auth_b;
                    """


        conn = await self.__get_connection()
        products = await conn.execute(sqlcode)
        products = await products.fetchall()
        products = [product[0] for product in products]
        return products
    
    async def getActiveDomains(self) -> list[str]:
        '''
        获取授权管理域名的列。
        '''
        sqlcode = """
                    --sql
                    SELECT domain
                    FROM heyauth_auth_b;
                    """


        conn = await self.__get_connection()
        domains = await conn.execute(sqlcode)
        domains = await domains.fetchall()
        domains = [domain[0] for domain in domains]
        return domains
    
    async def getActiveKeys(self) -> list[str]:
        '''
        获取授权管理授权码的列。
        '''
        sqlcode = """
                    --sql
                    SELECT auth_key
                    FROM heyauth_auth_b;
                    """


        conn = await self.__get_connection()
        keys = await conn.execute(sqlcode)
        keys = await keys.fetchall()
        keys = [key[0] for key in keys]
        return keys
    
    async def getActiveStatuses(self) -> list[str]:
        '''
        获取授权管理激活状态的列。
        '''
        sqlcode = """
                    --sql
                    SELECT active
                    FROM heyauth_auth_b;
                    """


        conn = await self.__get_connection()
        statuses = await conn.execute(sqlcode)
        statuses = await statuses.fetchall()
        statuses = [status[0] for status in statuses]
        return statuses
    
    async def getActiveTimes(self) -> list[str]:
        '''
        获取授权管理创建时间的列。
        '''
        sqlcode = """
                    --sql
                    SELECT create_at
                    FROM heyauth_auth_b;
                    """


        conn = await self.__get_connection()
        times = await conn.execute(sqlcode)
        times = await times.fetchall()
        times = [time[0] for time in times]
        return times
    
    async def getAuthTime(self, key) -> str:
        '''
        获取指定授权的到期时间。
        '''
        sqlcode = """
                    --sql
                    SELECT time
                    FROM heyauth_auth_b
                    WHERE auth_key = ?;
                    """
        param = (key)

        conn = await self.__get_connection()
        time = await conn.execute(sqlcode, param)
        time = await time.fetchone()[0]
        return time
    
    async def getCardamomNum(self) -> int:
        '''
        获取卡密的数量。
        '''
        sqlcode = """
                    --sql
                    SELECT id
                    FROM heyauth_cardamom;
                    """


        conn = await self.__get_connection()
        num = await conn.execute(sqlcode)
        num = await num.fetchall()
        num = len(num)
        return num
    
    async def getLegal(self, product_id, domain):
        '''
        正版查询
        '''

        sqlcode = """
                    --sql
                    SELECT * FROM heyauth_auth_b
                    WHERE product_id = ?
                    AND domain = ?;
                    """
        param = (product_id, domain)

        conn = await self.__get_connection()
        legal = await conn.execute(sqlcode, param)
        legal = await legal.fetchone()
        return legal
    
    async def getBLine(self, user_id = None, product_id = None):
        """
        获得B端授权额度信息。
        """
        conn = await self.__get_connection()

        sqlcode = """
                    --sql
                    SELECT * FROM heyauth_aut_lst
                    """
        if user_id or product_id:
            sqlcode = sqlcode + " WHERE "
            if user_id and not product_id:
                sqlcode = sqlcode + "user_id = ?"
                param = (user_id,)
                line = await conn.execute(sqlcode, param)
            if product_id and not user_id:
                sqlcode = sqlcode + "product_id = ?"
                param = (product_id,)
                line = await conn.execute(sqlcode, param)
            if user_id and product_id:
                sqlcode = sqlcode + "user_id = ? AND product_id = ?"
                params = (user_id, product_id)
                line = await conn.execute(sqlcode, params)
        else:
            line = await conn.execute(sqlcode)

        line = await line.fetchall()
        return line
    
    async def getOrderInfo(self, order_id):
        '''
        获取订单的信息。
        '''
        sqlcode = """
                    --sql
                    SELECT * FROM heyauth_order
                    WHERE order_id = ?;
                    """
        param = (order_id,)

        conn = await self.__get_connection()
        order = await conn.execute(sqlcode, param)
        order = await order.fetchone()
        try:
            return order[0]
        except:
            return order
    
    async def getPirateNum(self) -> int:
        '''
        获取盗版的产品的数量。
        '''
        sqlcode = """
        --sql
        SELECT id
        FROM heyauth_pirated_b;
        """

        conn = await self.__get_connection()
        num = await conn.execute(sqlcode)
        num = await num.fetchall()
        num = len(num)
        return num
    
    async def getProductCreateTimes(self) -> list[str]:
        '''
        获取产品创建时间的列。
        '''
        sqlcode = """
        --sql
        SELECT create_at
        FROM heyauth_product_b;
        """


        conn = await self.__get_connection()
        times = await conn.execute(sqlcode)
        times = await times.fetchall()
        times = [time[0] for time in times]
        return times
    
    async def getProductDeleteTimes(self) -> list[str]:
        '''
        获取产品停售时间的列。
        '''
        sqlcode = """
        --sql
        SELECT delete_at
        FROM heyauth_product_b;
        """


        conn = await self.__get_connection()
        times = await conn.execute(sqlcode)
        times = await times.fetchall()
        times = [time[0] for time in times]
        return times
    
    async def getProductId(self, name: str) -> int:
        '''
        获取产品id。
        '''
        sqlcode = """
        --sql
        SELECT id
        FROM heyauth_product_b
        WHERE name = ?;
        """
        param = (name,)

        conn = await self.__get_connection()
        ids = await conn.execute(sqlcode, param)
        ids = await ids.fetchall()
        if ids != []:
            return ids[0][0]
        else:
            return None
    
    async def getProductIds(self) -> list[int]:
        '''
        获取产品id的列。
        '''
        sqlcode = """
        --sql
        SELECT id
        FROM heyauth_product_b;
        """  


        conn = await self.__get_connection()
        ids = await conn.execute(sqlcode)
        ids = await ids.fetchall()
        ids = [id[0] for id in ids]
        return ids
    
    async def getProductInfo(self, product_id: int):
        '''
        获取产品信息。
        '''
        sqlcode = """
        --sql
        SELECT * FROM heyauth_product_b
        WHERE id = ?;
        """
        param = (product_id,)

        conn = await self.__get_connection()
        product = await conn.execute(sqlcode, param)
        product = await product.fetchone()
        return product
    
    async def getProductName(self, product_id: int) -> str:
        '''
        获取产品名称。
        '''
        sqlcode = """
        --sql
        SELECT name
        FROM heyauth_product_b
        WHERE id = ?;
        """
        param = (product_id,)

        conn = await self.__get_connection()
        name = await conn.execute(sqlcode, param)
        name = await name.fetchone()
        return name
    
    async def getProductNames(self) -> list[str]:
        '''
        以字典的形式获取产品id和产品名。
        '''
        try:
            conn = await self.__get_connection()
            products = await conn.execute(
                """
                --sql
                SELECT id, name
                FROM heyauth_product_b;
                """)
            products = await products.fetchall()
            # 将查询结果转换为字典
            product_dict = {product[0]: product[1] for product in products}
            return product_dict
        except Exception as e:
            log.error('获取产品名称失败：' + str(e))
            raise e
    
    async def getProductNumberChange(self, product_id: int) -> list[int]:
        '''
        获取产品变更次数的列。
        '''
        sqlcode = """
        --sql
        SELECT number, change
        FROM heyauth_product_b
        WHERE id = ?;
        """
        param = (product_id,)

        conn = await self.__get_connection()
        change = await conn.execute(sqlcode, param)
        change = await change.fetchone()
        return change
    
    async def getProductPrice(self, product_id,  time: Optional[Literal['month', 'quarter', 'year', 'life', 'all']] = 'all') -> list[str]:
        '''
        获取产品价格的列。
        '''
        sqlcode_dict = {
            'month': """
                        --sql
                        SELECT price_month
                        FROM heyauth_product_b
                        WHERE id = ?;
                    """,
            'quarter': """
                        --sql
                        SELECT price_quarter
                        FROM heyauth_product_b
                        WHERE id = ?;
                    """,
            'year': """
                        --sql
                        SELECT price_year
                        FROM heyauth_product_b
                        WHERE id = ?;
                    """,
            'life': """
                        --sql
                        SELECT price_life
                        FROM heyauth_product_b
                        WHERE id = ?;
                    """,
            'all': """
                        --sql
                        SELECT price_month, price_quarter, price_year, price_life
                        FROM heyauth_product_b
                        WHERE id = ?;
                    """
        }

        sqlcode = sqlcode_dict.get(time)
        param = (product_id,)
        if sqlcode is None:
            raise ValueError('时间参数错误')

        conn = await self.__get_connection()
        price = await conn.execute(sqlcode, param)
        price = await price.fetchone()
        return price
    
    async def getProductPrices(self, time: Optional[Literal['month', 'quarter', 'year', 'life', 'all']] = 'all') -> list[str]:
        '''
        获取产品价格的列。
        '''
        sqlcode_dict = {
            'month': """
                        --sql
                        SELECT price_month
                        FROM heyauth_product_b;
                    """,
            'quarter': """
                        --sql
                        SELECT price_quarter
                        FROM heyauth_product_b;
                    """,
            'year': """
                        --sql
                        SELECT price_year
                        FROM heyauth_product_b;
                    """,
            'life': """
                        --sql
                        SELECT price_life
                        FROM heyauth_product_b;
                    """,
            'all': """
                        --sql
                        SELECT price_month, price_quarter, price_year, price_life
                        FROM heyauth_product_b;
                    """
        }

        sqlcode = sqlcode_dict.get(time)
        if sqlcode is None:
            raise ValueError('时间参数错误')


        conn = await self.__get_connection()
        prices = await conn.execute(sqlcode)
        prices = await prices.fetchall()
        return prices
    
    async def getSetting(self, name) -> list[str]:
        '''
        获取指定设置的值。

        如果设置的值为单个，请自行调用[0][0]来获取
        '''
        sqlcode = """
                --sql
                SELECT value
                FROM heyauth_settings
                WHERE name = ?;
                """
        param = (name,)

        conn = await self.__get_connection()
        value = await conn.execute(sqlcode, param)
        value = await value.fetchall()
        return value
    
    async def getSiteName(self) -> str:
        '''
        获取站点名称。
        '''
        sqlcode = """
        --sql
        SELECT value
        FROM heyauth_settings
        WHERE name = 'site_name';
        """

        conn = await self.__get_connection()
        value = await conn.execute(sqlcode)
        value = await value.fetchone()
        if value:
            #TODO:这里有个Bug，不论怎么读取始终会输出[('站点名称'),]仅用临时解决方案
            return str(value[0]).replace("(","").replace(")","").replace(",","").replace("'","")
        else:
            return None
    
    async def getSiteNotice(self) -> str:
        '''
        获取站点公告。
        '''
        sqlcode = """
        --sql
        SELECT value
        FROM heyauth_settings
        WHERE name = 'site_notice';
        """        

        conn = await self.__get_connection()
        value = await conn.execute(sqlcode)
        value = await value.fetchone()
        if value:
            return str(value[0])
        else:
            return ''
    async def getStrorageSecret(self) -> str:
        '''
        获取存储密钥。
        '''
        sqlcode = """
        --sql
        SELECT value
        FROM heyauth_settings
        WHERE name = 'storage_secret';
        """

        conn = await self.__get_connection()
        value = await conn.execute(sqlcode)
        value = await value.fetchone()
        if value:
            return str(value[0])
        else:
            return ''

    
    async def getTicketNum(self) -> int:
        '''
        获取工单的数量。
        '''
        sqlcode = """
        --sql
        SELECT id
        FROM heyauth_tickets;
        """


        conn = await self.__get_connection()
        num = await conn.execute(sqlcode)
        num = await num.fetchall()
        num = len(num)
        return num
    
    async def getUserAccounts(self) -> list[str]:
        '''
        获取用户账号的列。
        '''
        sqlcode = """
        --sql
        SELECT account
        FROM heyauth_user
        ORDER BY id;
        """

        conn = await self.__get_connection()
        accounts = await conn.execute(sqlcode)
        accounts = await accounts.fetchall()
        accounts = [account[0] for account in accounts]
        return accounts
    
    async def getUserAuthsB(self, id: int = None, qq: str = None) -> list[str] | None:
        '''
        获取某个用户的所有B端产品许可证。
        '''
        conn = await self.__get_connection()
        if id != None and qq != None:
            raise TypeError('id和qq只能传入一个')
        elif id == None and qq == None:
            raise TypeError('id和qq必须传入一个')
        elif qq != None:
            sqlcode = """
            --sql
            SELECT id FROM heyauth_user
            WHERE qq = ?;
            """
            param = (qq,)
            id = await conn.execute(sqlcode, param)
            id = await id.fetchone()
            try:
                id = id[0]
            except:
                return None

        sqlcode = """
            --sql
            SELECT * FROM heyauth_auth_b
            WHERE user_id = ?;
            """
        param = (id,)
        UserAuth = await conn.execute(sqlcode, param)
        UserAuth = await UserAuth.fetchall()
        return UserAuth
    
    async def getUserCode(self, account: str) -> int:
        """
        获取用户的验证码。
        """
        sqlcode = '''
                    --sql
                    SELECT code
                    FROM heyauth_user
                    WHERE account = ?;
                    '''
        param = (account,)

        conn = await self.__get_connection()
        code = await conn.execute(sqlcode, param)
        code = await code.fetchone()
        print(int(code[0]))
        return int(code[0])

    async def getUserCount(self) -> int:
        '''
        获取用户数量。
        '''
        sqlcode = """
        --sql
        SELECT id
        FROM heyauth_user;
        """


        conn = await self.__get_connection()
        userConut = await conn.execute(sqlcode)
        userConut = await userConut.fetchall()
        count = len(userConut)
        return count
    
    async def getUserEmail(self, user_id) -> str:
        '''
        获取用户的邮箱。
        '''
        sqlcode = """
        --sql
        SELECT account
        FROM heyauth_user
        WHERE id = ?;
        """
        param = (user_id,)

        conn = await self.__get_connection()
        email = await conn.execute(sqlcode, param)
        email = await email.fetchall()
        return email[0][0]
    
    async def getUserExist(self, account) -> list[str] | None:
        """
        检查用户是否存在。
        """
        sqlcode = """
        --sql
        SELECT * FROM heyauth_user
        WHERE account = ?;
        """
        param = (account,)

        conn = await self.__get_connection()
        user = await conn.execute(sqlcode, param)
        user = await user.fetchone()
        return user

    async def getUserId(self, username) -> int:
        """
        获得用户ID，需要传入用户名。

        参数:username(在Bootstrap中使用app.storage.user["username"]方法获取)
        """
        sqlcode = """
        --sql
        SELECT id
        FROM heyauth_user
        WHERE account = ?;
        """
        param = (username,)

        conn = await self.__get_connection()
        account = await conn.execute(sqlcode, param)
        account = await account.fetchone()
        user_id = account[0]
        return user_id
    
    async def getUserIds(self) -> list[int]:
        '''
        获取用户id的列。
        '''
        sqlcode = """
        --sql
        SELECT id
        FROM heyauth_user;
        """


        conn = await self.__get_connection()
        ids = await conn.execute(sqlcode)
        ids = await ids.fetchall()
        ids = [id[0] for id in ids]
        return ids
    
    async def getUserNickName(self, id) -> str:
        """
        获得指定用户的昵称。
        """
        sqlcode = """
        --sql
        SELECT name
        FROM heyauth_user
        WHERE id = ?;
        """
        param = (id,)

        conn = await self.__get_connection()
        name = await conn.execute(sqlcode, param)
        name = await name.fetchall()
        if name != None:
            return name
        else:
            return ""
    
    async def getUserNickNames(self) -> list[str]:
        '''
        获取用户昵称的列。
        '''
        sqlcode = """
        --sql
        SELECT name
        FROM heyauth_user;
        """


        conn = await self.__get_connection()
        names = await conn.execute(sqlcode)
        names = await names.fetchall()
        names = [name[0] for name in names]
        return names
    
    async def getUserQQ(self, id: int) -> str:
        '''
        获取指定用户的QQ.
        '''
        sqlcode = """
        --sql
        SELECT QQ
        FROM heyauth_user
        WHERE id = ?;
        """

        conn = await self.__get_connection()
        param = (id,)
        QQ = await conn.execute(sqlcode, param)
        QQ = await QQ.fetchone()
        try:
            return QQ[0]
        except:
            return None

    
    async def getUserQQs(self) -> list[str]:
        '''
        获取用户QQ的列。
        '''
        sqlcode = """
        --sql
        SELECT QQ
        FROM heyauth_user;
        """

        conn = await self.__get_connection()
        QQs = await conn.execute(sqlcode)
        QQs = await QQs.fetchall()
        QQs = [QQ[0] for QQ in QQs]
        return QQs
    
    async def getUserSignUpAts(self) -> list[str]:
        '''
        获取用户注册时间的列。
        '''
        sqlcode = """
        --sql
        SELECT signup_at
        FROM heyauth_user;
        """ 

        conn = await self.__get_connection()
        times = await conn.execute(sqlcode)
        times = await times.fetchall()
        times = [time[0] for time in times]
        return times

    
    async def getUserStatus(self, id: int = None, account: str = None) -> str:
        """
        获得指定用户的账号状态。
        """
        if id != None and account != None:
            raise TypeError('id和account只能传入一个')
        elif id != None:
            sqlcode = """
            --sql
            SELECT status
            FROM heyauth_user
            WHERE id = ?;
            """
            param = (id,)
        elif account != None:
            sqlcode = """
            --sql
            SELECT status
            FROM heyauth_user
            WHERE account = ?;
            """
            param = (account,)
        conn = await self.__get_connection()
        status = await conn.execute(sqlcode, param)
        status = await status.fetchone()
        status = status[0]
        log.debug('getUserStatus方法：获取用户' + str(id) + '的状态：' + status)
        return status
    
    async def getUserStatuses(self) -> list[str]:
        '''
        获取用户状态的列。
        '''
        sqlcode = """
        --sql
        SELECT status
        FROM heyauth_user;
        """

        conn = await self.__get_connection()
        statuses = await conn.execute(sqlcode)
        statuses = await statuses.fetchall()
        statuses = [status[0] for status in statuses]
        return statuses

    async def getUserPassword(self, account: str='') -> str:
        """
        根据用户名获得指定用户的密码。
        """

        sqlcode = """
        --sql
        SELECT password
        FROM heyauth_user
        WHERE account = ?;
        """
        params = (account,)

        conn = await self.__get_connection()
        result = await conn.execute(sqlcode, params)
        result = await result.fetchone()
        if result:
            return str(result[0])
        else:
            return None
    
    async def resetAdminPassword(self) -> None:
        '''
        重置管理员密码，请注意终端输出的密码。
        '''
        password = generate_password(8)
        password_code = hash_password(password)
        # 将id为1的用户的密码重置为新密码
        sqlcode = """
                    --sql
                    UPDATE heyauth_user
                    SET password = ?
                    WHERE id = 1;
                    """
        conn = await self.__get_connection()
        await conn.execute(sqlcode, (password_code))
        await conn.commit()
        printx('管理员密码：[bold]{}[/bold]'.format(password))
        log.warning('请注意，管理员账号密码仅在本次显示，请注意保存！')
        log.info('管理员密码重置成功')
    
    async def setCode(self, user_name: int, code: int) -> None:
        """
        设置用户的验证码。
        """
        sqlcode = """
        --sql
        UPDATE heyauth_user
        SET code = ?
        WHERE account = ?;
        """
        param = (code, user_name)
        conn = await self.__get_connection()
        await conn.execute(sqlcode, param)
        await conn.commit()
    
    async def setOrderStatus(self, order_id: str, status: str) -> List[Dict[str, Any]]:
        '''
        设置订单状态。
        '''
        sqlcode = """
        --sql
        UPDATE heyauth_order
        SET Status = ?
        WHERE order_id = ?;
        """
        param = (status, order_id)

        conn = await self.__get_connection()
        await conn.execute(sqlcode, param)
        await conn.commit()

        sqlcode = """
        --sql
        SELECT user_id, product_id, create_at
        FROM heyauth_order
        WHERE order_id = ?;
        """
        param = (order_id,)

        conn = await self.__get_connection()
        order = await conn.execute(sqlcode, param)
        order = await order.fetchone()
        user_id = order[0]
        product_id = order[1]
        create_at = order[2]

        return {"user_id": user_id, 'product_id': product_id, 'create_at': create_at}

    async def setSetting(self, name, value):
        '''
        设置某项的值，没有则创建。
        '''
        conn = await self.__get_connection()

        log.debug('在表heyauth_settings中查找是否有名称为{}的项……'.format(name))
        sqlcode = """
                    --sql
                    SELECT * FROM heyauth_settings
                    WHERE name = ?;
                    """
        params = (name,)

        o_value = await conn.execute(sqlcode, params)
        o_value = await o_value.fetchall()
        log.debug('\n查询结果：\no_value = ' + str(o_value) + '\nvalue = ' + str(value))
        if o_value == None or o_value == []:
            log.debug('没有找到，创建新项……')
            sqlcode = """--sql
                            INSERT INTO heyauth_settings (type, name, value)
                            VALUES ('TEXT', ?, ?);
                            """
            params = (name, value)

            
            await conn.execute(sqlcode, params)
            await conn.commit()
        elif value == "":
            log.debug('找到了，删除值……')
            sqlcode = """
                        --sql
                        UPDATE heyauth_settings
                        SET value = ""
                        WHERE name = ?;
                        """
            params = (name,)

            await conn.execute(sqlcode, params)
            await conn.commit()
        elif o_value[0][2] == value[0][0]:
            log.debug("原值和新值相同，不进行操作")
            pass
        else:
            log.debug('找到了，更新值……')

            sqlcode = """
                        --sql
                        UPDATE heyauth_settings
                        SET value = ?
                        WHERE name = ?;
                        """
            if isinstance(value, list):
                if len(value) == 1:
                    value = str(value[0])
                else:
                    value = ','.join(map(str, value))
            params = (value, name)
            log.debug('SQL代码：' + str(params))
            await conn.execute(sqlcode, params)
            await conn.commit()
    
    async def setUserAccount(self, id, account) -> None:
        '''
        设置用户的账号。
        '''
        sqlcode = """
        --sql
        UPDATE heyauth_user
        SET account = ?
        WHERE id = ?;
        """
        params = (account, id)

        conn = await self.__get_connection()
        await conn.execute(sqlcode, params)
        await conn.commit()
    
    async def setUserNickName(self, id: int, nickname: str) -> None:
        '''
        设置用户的个人信息。

        参数:O_username(在Bootstrap中使用app.storage.user["username"]方法获取)
        '''
        sqlcode = """
        --sql
        UPDATE heyauth_user
        SET nickname = ?
        WHERE id = ?;
        """
        params = (nickname, id)

        conn = await self.__get_connection()
        await conn.execute(sqlcode, params)
        await conn.commit()
    async def setUserPassVerify(self, account: str, password: str, nickName = "", qq = "") -> None:
        """
        设置用户通过邮箱验证。
        """
        conn = await self.__get_connection()

        # 检查数据库中QQ是否重复
        selectQQ = await conn.execute("SELECT * FROM heyauth_user WHERE QQ = ?", (qq,))
        selectQQ = await selectQQ.fetchall()
        if selectQQ != None or selectQQ != []:
            raise ValueError("QQ已存在")

        sqlcode = """
        --sql
        UPDATE heyauth_user
        SET status = 'ok' , password = ? , name = ? , QQ = ?
        WHERE account = ?;
        """
        param = (password, account, nickName, qq)

        await conn.execute(sqlcode, param)
        await conn.commit()

    async def setUserPassword(self, id, password) -> None:
        '''
        设置用户的密码。
        '''
        sqlcode = """
        --sql
        UPDATE heyauth_user
        SET password = ?
        WHERE id = ?;
        """
        params = (password, id)

        conn = await self.__get_connection()
        await conn.execute(sqlcode, params)
        await conn.commit()
    
    async def signUpUser(self, account, password) -> None:
        """
        注册新用户。请在用户注册时调用。
        """
        sqlcode = """
        --sql
        INSERT INTO heyauth_user (status, account, password)
        VALUES ('ok', ?, ?);
        """
        params = (account, password)

        conn = await self.__get_connection()
        await conn.execute(sqlcode, params)
        await conn.commit()

    async def unbanLicenseB(self, id) -> None:
        '''
        解封授权。
        '''
        sqlcode = """
                    --sql
                    UPDATE heyauth_auth_b
                    SET active = 'ok', banReason = ''
                    WHERE id = ?;
                    """
        params = (id,)

        conn = await self.__get_connection()
        await conn.execute(sqlcode, params)
        await conn.commit()
    async def forceDisconnect(self):
        '''
        强制断开连接。
        '''
        conn = self.__get_connection()
        conn.close()