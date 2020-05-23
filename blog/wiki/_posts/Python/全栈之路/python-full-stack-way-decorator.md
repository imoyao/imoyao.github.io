---
title: Python 全栈之路系列之装饰器
toc: true
date: 2020-05-23 18:21:46
tags:
- 编码
- 装饰器
---

装饰器是由函数去生成的，用于装饰某个函数或者方法或者类，他可以让这个函数在执行之前或者执行之后做一些操作。

## 实例

先定义一个函数`func`

```python
#!/usr/bin/env python
# _*_ coding: utf-8 _*_

def func(arg):  # 接受一个参数arg
    print(arg)  # 输出这个参数

func("Hello World!")  # 调用脚本并且传入参数
```

执行脚本，输出的结果为：

```python
C:\Python35\python.exe F:/Python_code/Note/装饰器.py
func

Process finished with exit code 0
```

现要在执行`func`这个函数前后执行一些操作，就可以创建一个装饰器来实现：

```python
#!/usr/bin/env python
# _*_ coding: utf-8 _*_

def decorator(func):  # 创建一个装饰器函数，接受的参数arg参数就是func函数名

    def inner(*args, **kwargs):
        print("执行函数之前")
        ret = func(*args, **kwargs)
        print("执行函数之后")
        return ret

    return inner

@decorator  # 如果要让某个函数使用装饰器，只需要在这个函数上面加上@+装饰器名
def func(arg):
    print(arg)

func("Hello World!")
```

输出结果为：

```python
/usr/bin/python3.5 /home/ansheng/Documents/PycharmProjects/blogcodes/装饰器.py
执行函数之前
Hello World!
执行函数之后

Process finished with exit code 0
```

## 多个装饰器装饰同一个函数

```python
#!/usr/bin/env python
# _*_ coding: utf-8 _*_

def decorator1(func):
    def inner():
        print("开始之前执行装饰器01")
        ret = func()
        print("结束之后执行装饰器01")
        return ret

    return inner


def decorator2(func):
    def inner():
        print("decorator2>>>Start...")
        ret = func()
        print("decorator2>>>End...")
        return ret

    return inner


@decorator1
@decorator2
def index():
    print("执行函数...")

index()
```

输出结果：

```python
/usr/bin/python3.5 /home/ansheng/Documents/PycharmProjects/blogcodes/装饰器.py
开始之前执行装饰器01
decorator2>>>Start...
执行函数...
decorator2>>>End...
结束之后执行装饰器01

Process finished with exit code 0
```

## 更多实例

```python
#!/usr/bin/env python
# _*_ coding:utf-8 _*_

# Created by 安生 on 2017/2/9

"""
函数装饰器
"""


def decorator(func):
    def wrapped(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapped


@decorator
def func(a, b):
    return a + b


print(func(1, 2))
"""
类装饰器
"""


class decorator:
    def __init__(self, func):
        self.func = func

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)


@decorator
def func(a, b):
    return a + b


print(func(1, 2))
"""
带参数的函数装饰器
"""


def parameter(a, b):
    print(a, b)

    def decorator(func):
        def wrapped(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapped

    return decorator


@parameter(1, 2)
def func(a, b):
    return a + b


print(func(10, 20))
"""
带参数的类装饰器
"""


def parameter(a, b):
    print(a + b)

    class decorator:
        def __init__(self, func):
            self.func = func

        def __call__(self, *args, **kwargs):
            return self.func(*args, **kwargs)

    return decorator


@parameter(1, 2)
def func(a, b):
    return a + b


print(func(10, 20))

"""
带参数的类装饰器
"""


def parameter(a, b):
    print(a, b)

    def decorator(cls):
        class wrapped:
            def __init__(self, *args, **kwargs):
                self.cls = cls(*args, **kwargs)

            def __getattr__(self, item):
                return getattr(self.cls, item)

        return wrapped

    return decorator


@parameter(1, 2)
class CLS:
    def __init__(self):
        self.a = 'a'

    def P(self, v):
        print(v)


obj = CLS()
print(obj.a)
obj.P('Hello,')

"""
为函数中和类中的方法添加装饰器
"""


def Call(aClass):
    calls = 0

    def onCall(*args, **kwargs):
        nonlocal calls
        calls += 1
        print('call %s to %s' % (calls, func.__name__))
        return aClass(*args, **kwargs)

    return onCall


@Call
def func(a, b):
    return a + b


print(func(1, 2))


class CLS:
    def __init__(self):
        self.a = 'a'

    @Call
    def b(self):
        return self.a


obj = CLS()
print(obj.b())
```