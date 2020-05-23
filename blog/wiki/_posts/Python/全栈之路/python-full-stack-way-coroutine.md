---
title: Python 全栈之路系列之协程
toc: true
date: 2020-05-23 18:21:46
tags:
- 编码
- 协程
---

## What is the association

与子例程一样，协程也是一种程序组件。 相对子例程而言，协程更为一般和灵活，但在实践中使用没有子例程那样广泛。 协程源自 Simula 和 Modula-2 语言，但也有其他语言支持。 协程更适合于用来实现彼此熟悉的程序组件，如合作式多任务，迭代器，无限列表和管道。

> 来自维基百科 https://zh.wikipedia.org/wiki/协程

协程拥有自己的寄存器上下文和栈，协程调度切换时，将寄存器上下文和栈保存到其他地方，在切回来的时候，恢复先前保存的寄存器上下文和栈。因此：协程能保留上一次调用时的状态（即所有局部状态的一个特定组合），每次过程重入时，就相当于进入上一次调用的状态，换种说法：进入上一次离开时所处逻辑流的位置。

协程的优缺点：

优点

1. 无需线程上下文切换的开销
2. 无需原子操作锁定及同步的开销(更改一个变量)
3. 方便切换控制流，简化编程模型
4. 高并发+高扩展性+低成本：一个 CPU 支持上万的协程都不是问题。所以很适合用于高并发处理。

缺点：

1. 无法利用多核资源：协程的本质是个单线程,它不能多核，协程需要和进程配合才能运行在多 CPU 上，当然我们日常所编写的绝大部分应用都没有这个必要，除非是 CPU 密集型应用。
2. 进行阻塞（Blocking）操作（如 IO 时）会阻塞掉整个程序

### 实现协程实例

yield

```python
def consumer(name):
    print("--->starting eating baozi...")
    while True:
        new_baozi = yield  # 直接返回
        print("[%s] is eating baozi %s" % (name, new_baozi))

def producer():
    r = con.__next__()
    r = con2.__next__()
    n = 0
    while n < 5:
        n += 1
        con.send(n)  # 唤醒生成器的同时传入一个参数
        con2.send(n)
        print("\033[32;1m[producer]\033[0m is making baozi %s" % n)

if __name__ == '__main__':
    con = consumer("c1")
    con2 = consumer("c2")
    p = producer()
```

Greenlet

安装 greenlet

```bash
pip3 install greenlet
```

```python
# -*- coding:utf-8 -*-
from greenlet import greenlet

def func1():
    print(12)
    gr2.switch()
    print(34)
    gr2.switch()

def func2():
    print(56)
    gr1.switch()
    print(78)

# 创建两个携程
gr1 = greenlet(func1)
gr2 = greenlet(func2)
gr1.switch()  # 手动切换
```

Gevent 

Gevent 可以实现并发同步或异步编程，在 gevent 中用到的主要模式是 Greenlet， 它是以 C 扩展模块形式接入 Python 的轻量级协程，Greenlet 全部运行在主程序操作系统进程的内部，但它们被协作式地调度。

安装 Gevent

```bash
pip3 install gevent
```

```python
import gevent

def foo():
    print('Running in foo')
    gevent.sleep(2)
    print('Explicit context switch to foo again')

def bar():
    print('Explicit context to bar')
    gevent.sleep(3)
    print('Implicit context switch back to bar')

# 自动切换
gevent.joinall([
    gevent.spawn(foo),  # 启动一个协程
    gevent.spawn(bar),
])
```

页面抓取

```python
from urllib import request
from gevent import monkey
import gevent
import time

monkey.patch_all()  # 当前程序中只要设置到IO操作的都做上标记

def wget(url):
    print('GET: %s' % url)
    resp = request.urlopen(url)
    data = resp.read()
    print('%d bytes received from %s.' % (len(data), url))

urls = [
    'https://www.python.org/',
    'https://www.python.org/',
    'https://github.com/',
    'https://blog.ansheng.me/',
]

# 串行抓取
start_time = time.time()
for n in urls:
    wget(n)
print("串行抓取使用时间：", time.time() - start_time)

# 并行抓取
ctrip_time = time.time()
gevent.joinall([
    gevent.spawn(wget, 'https://www.python.org/'),
    gevent.spawn(wget, 'https://www.python.org/'),
    gevent.spawn(wget, 'https://github.com/'),
    gevent.spawn(wget, 'https://blog.ansheng.me/'),
])
print("并行抓取使用时间：", time.time() - ctrip_time)
```

输出
```python
C:\Python\Python35\python.exe E:/MyCodeProjects/协程/s4.py
GET: https://www.python.org/
47424 bytes received from https://www.python.org/.
GET: https://www.python.org/
47424 bytes received from https://www.python.org/.
GET: https://github.com/
25735 bytes received from https://github.com/.
GET: https://blog.ansheng.me/
82693 bytes received from https://blog.ansheng.me/.
串行抓取使用时间： 15.143015384674072
GET: https://www.python.org/
GET: https://www.python.org/
GET: https://github.com/
GET: https://blog.ansheng.me/
25736 bytes received from https://github.com/.
47424 bytes received from https://www.python.org/.
82693 bytes received from https://blog.ansheng.me/.
47424 bytes received from https://www.python.org/.
并行抓取使用时间： 3.781306266784668

Process finished with exit code 0
```