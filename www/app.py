# -*- coding:utf-8 -*-

'''
主要思路：
　　理解 asyncio、aiohttp 基本应用
　　使用 asyncio 异步 IO 模块创建服务协程，监听相应端口
　　使用 aiohttp 异步 Web 开发框架，处理 HTTP 请求，构建并返回 HTTP 响应
'''

import logging;logging.basicConfig(level=logging.INFO)   # 指定log日志的级别为INFO，其他还有debug、warning、error级别
import asyncio, os, json, time   # asyncio 异步IO模块
from datetime import datetime
from aiohttp import web     # 异步 Web开发框架

# 处理函数，参数包含了所有浏览器发送过来的HTTP协议里面的信息，一般不用自己构造
def index(request):
    # 请求的返回内容
    return web.Response(body='<h1>您好！欢迎您的光临！</h1>', content_type='text/html', charset='utf-8')

# #这里用的时coroutine...yield from
# @asyncio.coroutine
# def init(loop):
#     app = web.Application(loop=loop)
#     app.router.add_route('GET', '/', index)
#     srv = yield from loop.create_server(app.make_handler(),'127.0.0.1', 9000)
#     logging.info('server started at http://127.0.0.1:9000...')
#     return srv

async def init(loop):
    # 创建Web服务器实例app，也就是aiohttp.web.Application类的实例，该实例的作用是处理URL、HTTP协议
    # 使用app时，首先要将URLs注册进router，再用aiohttp.RequestHandlerFactory 作为协议簇创建套接字
    app = web.Application(loop=loop)
    # add_route将处理函数（这里是index）与对应的URL（HTTP方法method，URL路径path）绑定，浏览器敲击URL时返回处理函数的内容
    app.router.add_route('GET', '/', index)
    # 用协程创建监听服务，其中loop为传入函数的协程，调用其类方法创建一个监听服务
    # await 返回一个创建好的，绑定IP、端口、HTTP协议簇的监听服务的协程。
    # await 的作用是使srv的行为模式和 loop.create_server()一致
    # make_handle() 创建aiohttp.RequestHandlerFactory
    srv = await loop.create_server(app.make_handler(),'127.0.0.1', 9000)
    # 输出info级别日志
    logging.info('server started at http://127.0.0.1:9000...')
    return srv

# 创建协程
loop = asyncio.get_event_loop()
# 运行协程，直到完成
loop.run_until_complete(init(loop))
# 运行协程，直到调用 stop()
loop.run_forever()




