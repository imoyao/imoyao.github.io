---
title: Python 全栈之路系列之 IO 多路复用
toc: true
date: 2020-05-23 18:21:46
tags:
- 编码
- IO 多路复用
top: 3
---

![io-multiplexing-01](https://blog.ansheng.me/images/2016/12/1483022063.png)

## What is IO Multiplexing

IO 多路复用是指内核一旦发现进程指定的一个或者多个 IO 条件准备读取，它就通知该进程。

举例说明

你是一名老师(线程)，上课了(启动线程)，这节课是自习课，学生都在自习，你也在教室里面坐着，只看着这帮学生，什么也不干(休眠状态)，课程进行到一半时，A 同学(socket)突然拉肚子，举手说：老湿我要上厕所(read)，然后你就让他去了，过了一会，B 同学(socket)在自习的过程中有个问题不太懂，就请你过去帮她解答下(write)，然后你就过去帮他解答了。

上述这种情况就是 IO 多路复用，你就是一个 IO，那么你解决了 A 同学的问题和 B 同学的问题，这就是复用，多路网络连接复用一个 io 线程。

与多进程和多线程技术相比，I/O 多路复用技术的最大优势是系统开销小，系统不必创建进程/线程，也不必维护这些进程/线程，从而大大减小了系统的开销。

目前常见支持 I/O 多路复用的系统调用有 select，poll，epoll，I/O 多路复用就是通过一种机制，一个进程可以监视多个描述符，一旦某个描述符就绪（一般是读就绪或者写就绪），能够通知程序进行相应的读写操作

## What is a select

select 监视的文件描述符分 3 类，分别是 writefds、readfds 和 exceptfds，程序启动后 select 函数会阻塞，直到有描述符就绪（有数据 可读、可写、或者有 except），或者超时（timeout 指定等待时间，如果立即返回设为 null 即可），函数返回，当 select 函数返回后，可以通过遍历 fdset，来找到就绪的描述符。

- 特点

1. select 最大的缺陷就是单个进程所打开的 FD 是有一定限制的，它由 FD_SETSIZE 设置，默认值是 1024；
2. 对 socket 进行扫描时是线性扫描，即采用轮询的方法，效率较低；
3. 需要维护一个用来存放大量 fd 的数据结构，这样会使得用户空间和内核空间在传递该结构时复制开销大；

Python 实现 select 模型代码

```Python
#!/usr/bin/env python
# _*_coding:utf-8 _*_

import select
import socket

sk1 = socket.socket()
sk1.bind(('127.0.0.1', 8002, ))
sk1.listen()

demo_li = [sk1]
outputs = []
message_dict = {}

while True:
    r_list, w_list, e_list = select.select(sk1, outputs, [], 1)

    print(len(demo_li),r_list)

    for sk1_or_conn in r_list:

        if sk1_or_conn == sk1:
            conn, address = sk1_or_conn.accept()
            demo_li.append(conn)
            message_dict[conn] = []
        else:
            try:
                data_bytes = sk1_or_conn.recv(1024)
                # data_str = str(data_bytes, encoding="utf-8")
                # print(data_str)
                # sk1_or_conn.sendall(bytes(data_str+"good", encoding="utf-8"))
            except Exception as e:
                demo_li.remove(sk1_or_conn)
            else:
                data_str = str(data_bytes, encoding="utf-8")
                message_dict[sk1_or_conn].append(data_str)
                outputs.append(sk1_or_conn)

    for conn in w_list:
        recv_str = message_dict[conn][0]
        del message_dict[conn][0]
        conn.sendall(bytes(recv_str+"Good", encoding="utf-8"))
        outputs.remove(conn)
```

## What is a poll

**基本原理：**

poll 本质上和 select 没有区别，它将用户传入的数组拷贝到内核空间，然后查询每个 fd 对应的设备状态，如果设备就绪则在设备等待队列中加入一项并继续遍历，如果遍历完所有 fd 后没有发现就绪设备，则挂起当前进程，直到设备就绪或者主动超时，被唤醒后它又要再次遍历 fd。这个过程经历了多次无谓的遍历。

它没有最大连接数的限制，原因是它是基于链表来存储的，但是同样有一个缺点：

1. 大量的 fd 的数组被整体复制于用户态和内核地址空间之间，而不管这样的复制是不是有意义。
2. poll 还有一个特点是“水平触发”，如果报告了 fd 后，没有被处理，那么下次 poll 时会再次报告该 fd。

## What is a epoll

poll 是在 2.6 内核中提出的，是之前的 select 和 poll 的增强版本。相对于 select 和 poll 来说，epoll 更加灵活，没有描述符限制。epoll 使用一个文件描述符管理多个描述符，将用户关系的文件描述符的事件存放到内核的一个事件表中，这样在用户空间和内核空间的 copy 只需一次。

**基本原理：**

epoll 支持水平触发和边缘触发，最大的特点在于边缘触发，它只告诉进程哪些 fd 刚刚变为就绪态，并且只会通知一次。还有一个特点是，epoll 使用“事件”的就绪通知方式，通过 epoll_ctl 注册 fd，一旦该 fd 就绪，内核就会采用类似 callback 的回调机制来激活该 fd，epoll_wait 便可以收到通知。

**epoll 的优点：**

1. 没有最大并发连接的限制，能打开的 FD 的上限远大于 1024（1G 的内存上能监听约 10 万个端口）。
2. 效率提升，不是轮询的方式，不会随着 FD 数目的增加效率下降。只有活跃可用的 FD 才会调用 callback 函数；即 Epoll 最大的优点就在于它只管你“活跃”的连接，而跟连接总数无关，因此在实际的网络环境中，Epoll 的效率就会远远高于 select 和 poll。
3. 内存拷贝，利用 mmap()文件映射内存加速与内核空间的消息传递；即 epoll 使用 mmap 减少复制开销。

epoll 对文件描述符的操作有两种模式：LT（level trigger）和 ET（edge trigger）。LT 模式是默认模式，LT 模式与 ET 模式的区别如下：

**LT 模式：**当 epoll_wait 检测到描述符事件发生并将此事件通知应用程序，应用程序可以不立即处理该事件。下次调用 epoll_wait 时，会再次响应应用程序并通知此事件。

**ET 模式：**当 epoll_wait 检测到描述符事件发生并将此事件通知应用程序，应用程序必须立即处理该事件。如果不处理，下次调用 epoll_wait 时，不会再次响应应用程序并通知此事件。

**LT 模式**
LT(level triggered)是缺省的工作方式，并且同时支持 block 和 no-block socket。在这种做法中，内核告诉你一个文件描述符是否就绪了，然后你可以对这个就绪的 fd 进行 IO 操作。如果你不作任何操作，内核还是会继续通知你的。

**ET 模式**
ET(edge-triggered)是高速工作方式，只支持 no-block socket。在这种模式下，当描述符从未就绪变为就绪时，内核通过 epoll 告诉你。然后它会假设你知道文件描述符已经就绪，并且不会再为那个文件描述符发送更多的就绪通知，直到你做了某些操作导致那个文件描述符不再为就绪状态了(比如，你在发送，接收或者接收请求，或者发送接收的数据少于一定量时导致了一个 EWOULDBLOCK 错误）。但是请注意，如果一直不对这个 fd 作 IO 操作(从而导致它再次变成未就绪)，内核不会发送更多的通知(only once)。ET 模式在很大程度上减少了 epoll 事件被重复触发的次数，因此效率要比 LT 模式高。epoll 工作在 ET 模式的时候，必须使用非阻塞套接口，以避免由于一个文件句柄的阻塞读/阻塞写操作把处理多个文件描述符的任务饿死。

在 select/poll 中，进程只有在调用一定的方法后，内核才对所有监视的文件描述符进行扫描，而 epoll 事先通过 epoll_ctl()来注册一个文件描述符，一旦基于某个文件描述符就绪时，内核会采用类似 callback 的回调机制，迅速激活这个文件描述符，当进程调用 epoll_wait()时便得到通知。(此处去掉了遍历文件描述符，而是通过监听回调的的机制。这正是 epoll 的魅力所在。)