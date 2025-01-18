'''
## 海枫授权系统 日志组件 V0.2.1

提供了日志记录功能，支持记录到文件和控制台，支持error、info、success、warning、debug级别的日志记录。
'''

'''
- 作者 Author                 : 于小丘 海枫
- 网址 url                    : xiaoqiu.in
- 制作日期 MakeDate           : 2024-08-29
LastEditTime: 2024-12-01 18:40:23
- 邮箱 Email                 : admin@yuxiaoqiu.cn
- 项目名 Project             : 海枫授权系统
- 介绍 Description          : 一款针对B+C端的应用授权系统
- 请阅读 Read me            : 感谢您使用海枫授权系统，程序源码有详细的注释，支持二次开发。
- 注意 Remind              : 使用盗版海枫授权系统会存在各种未知风险。支持正版，从我做起！
'''

from rich import print
from rich.console import Console
from rich.markdown import Markdown
from configparser import ConfigParser
from typing import Literal, Optional
import time
import inspect

LogLevel = 'info'

def log(level: str = 'debug', message: str = ''):
    """
    输出日志
    ---
    通过传入的`level`和`message`参数，输出不同级别的日志信息。<br>
    `level`参数为日志级别，支持`红色error`、`紫色info`、`绿色success`、`黄色warning`、`淡蓝色debug`。<br>
    `message`参数为日志信息。<br>
    """
    
    lc = {
        'debug': '[bold cyan][ Debug ][/bold cyan]',
        'info': '[bold blue][ Info ][/bold blue]',
        'warn': '[bold yellow][ Warn ][/bold yellow]',
        'error': '[bold red][ Error ][/bold red]',
        'success': '[bold green][ Success ][/bold green]'
    }
    
    lv = lc.get(level, '[bold magenta][ Unknown ][/bold magenta]')

    global LogLevel
    if LogLevel == 'debug':
        print(f"{lv}\t{time.strftime('%Y/%m/%d %H:%M:%S %p', time.localtime())} [bold]From {inspect.currentframe().f_back.f_back.f_code.co_filename}, line {inspect.currentframe().f_back.f_back.f_lineno}[/bold] {message}")
    elif LogLevel == 'info' and level != 'debug':
        print(f"{lv}\t{time.strftime('%Y/%m/%d %H:%M:%S %p', time.localtime())} [bold]From {inspect.currentframe().f_back.f_back.f_code.co_filename}, line {inspect.currentframe().f_back.f_back.f_lineno}[/bold] {message}")
    elif LogLevel == 'warning' and level != 'debug' or level != 'info':
        print(f"{lv}\t{time.strftime('%Y/%m/%d %H:%M:%S %p', time.localtime())} [bold]From {inspect.currentframe().f_back.f_back.f_code.co_filename}, line {inspect.currentframe().f_back.f_back.f_lineno}[/bold] {message}")
    elif LogLevel == 'error' and level == 'error':
        print(f"{lv}\t{time.strftime('%Y/%m/%d %H:%M:%S %p', time.localtime())} [bold]From {inspect.currentframe().f_back.f_back.f_code.co_filename}, line {inspect.currentframe().f_back.f_back.f_lineno}[/bold] {message}")

debug = lambda message: log('debug', message)
info = lambda message: log('info', message)
warning = lambda message: log('warn', message)
error = lambda message: log('error', message)
success = lambda message: log('success', message)

def title(title: str = '海枫授权系统 HeyAuth', size: Optional[Literal['h1', 'h2', 'h3', 'h4', 'h5']] = 'h1'):
    """
    输出标题
    ---
    通过传入的`title`参数，输出一个整行的标题。<br>
    `title`参数为标题内容。<br>
    """
    console = Console()
    markdown_sizes = {
        'h1': '# ',
        'h2': '## ',
        'h3': '### ',
        'h4': '#### ',
        'h5': '##### '
    }
    
    markdown_tag = markdown_sizes.get(size)
    if markdown_tag:
        console.print(Markdown(markdown_tag + title))
    del console

if __name__ == '__main__':
    title('海枫授权系统 日志组件测试', 'h1')
    title('测试h2标题', 'h2')
    title('测试h3标题', 'h3')
    title('测试h4标题', 'h4')
    title('测试h5标题', 'h5')
    debug('这是一个debug日志')
    info('这是一个info日志')
    warning('这是一个warning日志')
    error('这是一个error日志')
    success('这是一个success日志')