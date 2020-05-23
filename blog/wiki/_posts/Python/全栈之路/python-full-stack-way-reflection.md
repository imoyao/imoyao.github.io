---
title: Python 全栈之路系列之反射
toc: true
date: 2020-05-23 18:21:46
tags:
- 编码
---

## 反射的定义

根据字符串的形式去某个对象中操作成员

1. 根据字符串的形式去一个对象中寻找成员
2. 根据字符串的形式去一个对象中设置成员
3. 根据字符串的形式去一个对象中删除成员
4. 根据字符串的形式去一个对象中判断成员是否存在

## 初始反射

通过字符串的形式，导入模块

根据用户输入的模块名称，导入对应的模块并执行模块中的方法

```bash
# Python使用的是3.5.1
[root@ansheng ~]# python -V
Python 3.5.1
# commons.py为模块文件
[root@ansheng ~]# ls
commons.py  reflection.py
# commons.py文件内容
[root@ansheng ~]# cat commons.py 
#!/usr/bin/env python
# 定义了连个函数，f1和f2
def f1():
    return "F1"

def f2():
    return "F2"
[root@ansheng ~]# cat reflection.py 
#!/usr/bin/env python
# _*_ coding:utf-8 _*_
# 输入模块的名称
mod_name = input("请输入模块名称>>> ")
# 查看输入的内容及数据类型
print(mod_name, type(mod_name))
# 通过__import__的方式导入模块，并赋值给dd
dd = __import__(mod_name)
# 执行f1()函数
ret = dd.f1()
# 输出函数的返回值
print(ret)
# 执行reflection.py 
[root@ansheng ~]# python reflection.py 
# 输入模块名称
请输入模块名称>>> commons
# 返回输入的内容及数据类型
commons <class 'str'>
# 执行F1函数
F1
```

通过字符串的形式，去模块中寻找指定函数，并执行

用户输入模块名称和函数名称，执行指定模块内的函数 or 方法

```bash
[root@ansheng ~]# cat commons.py 
#!/usr/bin/env python

def f1():
    return "F1"

def f2():
    return "F2"
[root@ansheng ~]# cat reflection.py 
#!/usr/bin/env python
# _*_ coding:utf-8 _*_

# 输入模块的名称
mod_name = input("请输入模块名称>>>")

# 输入函数or方法的名称
func_name = input("请输入函数名称>>>")

# 导入模块
dd = __import__(mod_name)

# 导入模块中的方法
target_func = getattr(dd, func_name)

# 查看target_func和dd.f1的内存地址
print(id(target_func), id(dd.f1))

# 执行target_func()函数
result = target_func()

# 输出结果
print(result)
[root@ansheng ~]# python reflection.py
# 输入模块名称commons
请输入模块名称>>>commons
# 输入函数名称f1
请输入函数名称>>>f1
# 返回内存地址
139844714989224 139844714989224
# 执行的函数返回结果
F1
```

## 反射相关的函数

**getattr(object, name[, default])**

根据字符串的形式去一个对象中寻找成员

```bash
# 自定义模块的内容
[root@ansheng ~]# cat commons.py 
#!/usr/bin/env python

Blog_Url = "https://blog.ansheng.me"

def f1():
    return "F1"

def f2():
    return "F2"
```

```python
>>> import commons
>>> getattr(commons, "f1")
<function f1 at 0x7fbce5774598>
>>> getattr(commons, "f1f1f1")
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
AttributeError: module 'commons' has no attribute 'f1f1f1'
```

执行获取到的函数

```python
>>> target_func = getattr(commons, "f1")
>>> target_func
<function f1 at 0x7fbce5774598>
>>> target_func() 
'F1'
```

通过设置默认值可以避免获取不到方法时报错

```python
# 设置一个默认值为None
>>> target_func = getattr(commons, "f1f1f1", None)
>>> target_func
>>> 
```

通过 getattr 获取模块中的全局变量

```python
>>> import commons
>>> getattr(commons, "Blog_Url", None)
'https://blog.ansheng.me'
```

- setattr(object, name, value)

根据字符串的形式去一个对象中设置成员

设置全局变量

```python
# 获取commons内的Name变量
>>> getattr(commons, "Name", None)
# 在commons模块中设置一个全局变量Name，值为Ansheng
>>> setattr(commons, "Name", "Ansheng")
# 获取commons内的Name变量
>>> getattr(commons, "Name", None)
'Ansheng'
```

getattr 结合 lambda 表达式设置一个函数

```python
>>> setattr(commons, "as", lambda : print("as"))
>>> getattr(commons, "as")
<function <lambda> at 0x000001FD3E51FD90>
>>> aa = getattr(commons, "as")
>>> aa()
as
```

- delattr(object, name)

根据字符串的形式去一个对象中删除成员

```python
>>> getattr(commons, "Name")
'Ansheng'
>>> delattr(commons, "Name")
# 获取不到就报错
>>> getattr(commons, "Name")
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
AttributeError: module 'commons' has no attribute 'Name'
```

## hasattr(object, name)

根据字符串的形式去一个对象中判断成员是否存在

```python
# 如果不存在就返回False
>>> hasattr(commons, "Name")
False
>>> setattr(commons, "Name", "Ansheng")
# 如果存在就返回True
>>> hasattr(commons, "Name")
True
```

## (双下划线)import(双下划线)方式导入多层模块

```python
>>> m = __import__("lib.commons")     
>>> m
# 返回的路径是`lib`
<module 'lib' (namespace)>
>>> m = __import__("lib.commons", fromlist=True)
>>> m
# 返回的路径是`lib.commons`
<module 'lib.commons' from '/root/lib/commons.py'>
```

## 基于反射模拟 Web 框架路由系统

`find_index.py`文件内容

```python
#!/usr/bin/env python
# _*_ coding:utf-8 _*_

url = input("请输入url: ")
target_module, target_func = url.split('/')

m = __import__("lib." + target_module, fromlist=True)

if hasattr(m, target_func):
    target_func = getattr(m, target_func)
    r = target_func()
    print(r)
else:
    print("404")
```

目录结构及文件内容

```bash
[root@ansheng ~]# tree ./
./
├── find_index.py
└── lib
    ├── account.py
    └── commons.py

1 directory, 3 files
[root@ansheng ~]# cat lib/commons.py 
#!/usr/bin/env python

Blog_Url = "https://blog.ansheng.me"

def f1():
    return "F1"

def f2():
    return "F2"
[root@ansheng ~]# cat lib/account.py 
#!/usr/bin/env python
# _*_ coding:utf-8 _*_

def login():
    return "login"

def logout():
    return "logout"
```

执行

```bash
[root@ansheng ~]# python find_index.py 
请输入url: account/login
login
[root@ansheng ~]# python find_index.py 
请输入url: account/logout
logout
[root@ansheng ~]# python find_index.py 
请输入url: commons/f1
F1
[root@ansheng ~]# python find_index.py 
请输入url: commons/f2
F2
[root@ansheng ~]# python find_index.py 
请输入url: commons/asdasd
404
```