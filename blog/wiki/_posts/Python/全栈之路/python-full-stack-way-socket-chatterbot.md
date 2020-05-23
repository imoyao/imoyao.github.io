---
title: Python 全栈之路系列之基于 socket 实现聊天机器人
toc: true
date: 2020-05-23 18:21:46
tags:
- 编码
- socket
---

通过 socket 实现局域网内的聊天工具。

service.py 文件如下：

```Python
#!/usr/bin/env python
# _*_ coding:utf-8 _*_

import socket

# 创建一个socket对象
sk = socket.socket()

# 绑定允许连接的IP地址和端口
sk.bind(('127.0.0.1', 6053, ))

# 服务端允许起来之后，限制客户端连接的数量，如果超过五个连接，第六个连接来的时候直接断开第六个。
sk.listen(5)

while True:
    # 会一直阻塞，等待接收客户端的请求，如果有客户端连接会获取两个值，conn=创建的连接，address=客户端的IP和端口
    conn, address = sk.accept()

    # 当用户连接过来的时候就给用户发送一条信息，在Python3里面需要把发送的内容转换为字节
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
```

---

client.py 文件内容如下：

```Python
#!/usr/bin/env python
# _*_ coding:utf-8 _*_

import socket

# 创建一个socket对象
obj = socket.socket()

# 制定服务端的IP地址和端口
obj.connect(('127.0.0.1', 6053, ))

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

执行结果

![socket-02](https://blog.ansheng.me/images/2016/12/1483021707.png)