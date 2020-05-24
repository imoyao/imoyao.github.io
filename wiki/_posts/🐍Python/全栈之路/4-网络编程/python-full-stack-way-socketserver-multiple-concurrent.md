---
title: Python 全栈之路系列之 socketserver 实现多并发
toc: true
date: 2020-05-23 18:21:46
tags:
- 编码
top: 4
---

利用`socketserver`实现多并发，`socketserver`内部会调用`socket`模块进行功能上的实现

`client.py`客户端脚本文件内容

```Python
#!/usr/bin/env python
# _*_ coding:utf-8 _*_

import socket

# 创建一个socket对象
obj = socket.socket()

# 制定服务端的IP地址和端口
obj.connect(('127.0.0.1', 999, ))

# 阻塞，等待服务端发送内容，接受服务端发送过来的内容，最大接受1024字节
ret_bytes = obj.recv(1024)

# 因为服务端发送过来的是字节，所以我们需要把字节转换为字符串进行输出
ret_str = str(ret_bytes, encoding="utf-8")

# 输出内容
print(ret_str)

while True:
    # 当进入连接的时候，提示让用户输入内容
    inp = input("Client请输入要发送的内容>>> ")
    # 如果输出q则退出
    if inp == "q":
        # 把q发送给服务端
        obj.sendall(bytes(inp, encoding="utf-8"))
        # 退出当前while
        break
    else:
        # 否则就把用户输入的内容发送给用户
        obj.sendall(bytes(inp, encoding="utf-8"))
        # 等待服务端回答
        print("正在等待Server输入内容......")
        # 获取服务端发送过来的结果
        ret = str(obj.recv(1024), encoding="utf-8")
        # 输出结果
        print(ret)

# 连接完成之后关闭链接
obj.close()
```

`server.py`服务端脚本文件内容

```Python
#!/usr/bin/env python
# _*_ coding:utf-8 _*_

import socketserver

class MyServer(socketserver.BaseRequestHandler):

    def handle(self):

        conn = self.request

        conn.sendall(bytes("你好，欢迎登陆！", encoding="utf-8"))

        while True:
            # 输出等待客户端发送内容
            print("正在等待Client输入内容......")
            # 接收客户端发送过来的内容
            ret_bytes = conn.recv(1024)
            # 转换成字符串类型
            ret_str = str(ret_bytes, encoding="utf-8")
            # 输出用户发送过来的内容
            print(ret_str)

            # 如果用户输入的是q
            if ret_str == "q":
                # 则退出循环，等待下个用户输入
                break
            # 给客户端发送内容
            inp = input("Service请输入要发送的内容>>> ")
            conn.sendall(bytes(inp, encoding="utf-8"))

if __name__ == "__main__":
    server = socketserver.ThreadingTCPServer(('127.0.0.1', 999, ), MyServer)
    server.serve_forever()
```

效果图

![socker-04](https://blog.ansheng.me/images/2016/12/1483021949.png)

同时打开多个客户端，服务端也不会出现错误