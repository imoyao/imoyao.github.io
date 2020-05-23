---
title: Python 全栈之路系列之异常处理
toc: true
date: 2020-05-23 18:21:46
tags:
- 编码
- 异常处理
---

当程序出现错误的时候，进行捕捉，然后根据捕捉到的错误信息进行对应的处理

Even if a statement or expression is syntactically correct, it may cause an error when an attempt is made to execute it. Errors detected during execution are called exceptions and are not unconditionally fatal: you will soon learn how to handle them in Python programs.

## 初识异常处理

如下面的例子：

让用户进行输入，提示用户输入一个数字，如果输入的事一个数字那个就把输入的数字转换为`int`类型，然后输出用户输入的而数字，如果用户输入的不是一个数字，那么类型转换就会出错，如果出错，就提示用户"输入类型错误，你因该输入的是一个数字。"

```Python
#!/usr/bin/env python
# _*_coding:utf-8 _*_

try:
    n = int(input("请输出一个数字>>> "))
    print("你输入的数字是",n)
# e是Exception的对象，Exception是一个类
except Exception as e:
    print("输入类型错误，你因该输入的是一个数字。")
```
输出
```bash
ansheng@Darker:~$ python3 /home/ansheng/文档/Python_code/sublime/Week06/Day04/s2.py
请输出一个数字>>> 123
你输入的数字是 123
ansheng@Darker:~$ python3 /home/ansheng/文档/Python_code/sublime/Week06/Day04/s2.py
请输出一个数字>>> abc
输入类型错误，你因该输入的是一个数字。
```
## 异常分类

常用异常

|异常名|说明|
|:--:|:--|
|AttributeError|试图访问一个对象没有的树形，比如 foo.x，但是 foo 没有属性 x|
|IOError|输入/输出异常；基本上是无法打开文件|
|ImportError|无法引入模块或包；基本上是路径问题或名称错误|
|IndentationError|语法错误（的子类） ；代码没有正确对齐|
|IndexError|下标索引超出序列边界，比如当 x 只有三个元素，却试图访问 x[5]|
|KeyError|试图访问字典里不存在的键|
|KeyboardInterrupt|Ctrl+C 被按下|
|NameError|使用一个还未被赋予对象的变量|
|SyntaxError|Python 代码非法，代码不能编译(个人认为这是语法错误，写错了）|
|TypeError|传入对象类型与要求的不符合|
|UnboundLocalError|试图访问一个还未被设置的局部变量，基本上是由于另有一个同名的全局变量，导致你以为正在访问它|
|ValueError|传入一个调用者不期望的值，即使值的类型是正确的|

对不同的异常进行不同的处理

```Python
try:
    n = int(input("请输出一个数字>>> "))
except ValueError as e:
    print("ValueError错误")
except Exception as e:
    print("出现异常")
```
输出
```bash
ansheng@Darker:~$ python3 /home/ansheng/文档/Python_code/sublime/Week06/Day04/s2.py
请输出一个数字>>> 123
ansheng@Darker:~$ python3 /home/ansheng/文档/Python_code/sublime/Week06/Day04/s2.py
请输出一个数字>>> asd
ValueError错误
```

在处理异常时，如果出现错误，那么会首先匹配`ValueError`，然后在匹配`Exception`。

捕获多个错误

```python
try:
    raise IndexError('出错了')
except (IndexError, NameError) as e:  # 捕获括号内的错误，并把错误信息赋值给e
    print(e)
```

## 错误异常的基本结构

```Python
try:
    # 主代码块
    pass
except KeyError as e:
    # 异常时，执行该块
    pass
else:
    # 主代码块执行完，执行该块
    pass
finally:
    # 无论异常与否，最终执行该块
    pass
```

**执行流程：**

1. 如果出现错误，那么就执行`except`代码块，然后在执行`finally`
2. 如果没有出现错误，那么就执行`else`代码块，然后再执行`finally`
3. 不管有没有出现异常都会执行`finally`

## 主动出发异常

```Python
#!/usr/bin/env python
# _*_coding:utf-8 _*_

try:
    # raise表示主动出发异常，然后创建一个Exception对象，Exception括号内的值就是Exception对象的值
    raise Exception("主动出发的异常")
except Exception as e:
    # 输出Exception对象的值
    print(e)
```
输出
```bash
ansheng@Darker:~$ python3 /home/ansheng/文档/Python_code/sublime/Week06/Day04/s2.py
主动出发的异常
```

如果需要捕获和处理一个异常，又不希望异常在程序中死掉，一般都会利用 raise 传递异常

```python
>>> try:
...     raise IndexError('Index')
... except IndexError:
...     print('error')
...     raise
... 
error
Traceback (most recent call last):
  File "<stdin>", line 2, in <module>
IndexError: Index
```

## 断言

如果条件成立则成立，如果条件不成立则报错。

```Python
# assert关键字，后面的是条件
>>> assert 1 == 1
>>> assert 1 == 2
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
AssertionError
```

## 自定义异常

用户自定义的异常通过类编写，且通常需要继承`Exception`内置的异常类，基于类的异常允许脚本建立异常类型、继承行为以及附加状态信息。

```python
>>> class Bar(Exception):
...     pass
... 
>>> 
>>> def doomed():
...     raise Bar()
... 
>>> 
>>> try:
...     doomed()
... except Bar as e:
...     print('error')
... 
error
```

如果要自定义错误显示信息，我们只需要在类中定义字符串重载(`__str__`，`__repr__`)方法中的其中一个即可：

```python
>>> class MyError(Exception):
...     def __str__(self):
...         return '出错啦.'
... 
>>> try:
...     raise MyError()
... except MyError as e:
...     print(e)
... 
出错啦.
```