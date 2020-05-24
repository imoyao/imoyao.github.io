---
title: Python 全栈之路系列之面向对象成员修饰符
toc: true
date: 2020-05-23 18:21:46
tags:
- 编码
top: 3
---

成员修饰符就是设置类的成员有些是公开的有些是私有的，公开的是在外部通过对象或者类可以调用，但是私有的只能通过类的内部才可以调用。

- 静态字段修饰

```Python
#!/usr/bin/env python
# _*_coding:utf-8 _*_

class Foo:
    # 公有的静态字段
    ClassMembers = "公开的"
    # 私有的静态字段
    __ClassMembers = "私有的"

# 执行公有的静态字段
print(Foo.ClassMembers)

# 执行私有的静态字段
print(Foo.__ClassMembers)
```

```Python
/usr/bin/python3.5 /home/ansheng/文档/Python_code/sublime/Week06/Day04/s2.py
公开的
Traceback (most recent call last):
  File "/home/ansheng/文档/Python_code/sublime/Week06/Day04/s2.py", line 14, in <module>
    print(Foo.__ClassMembers)
AttributeError: type object 'Foo' has no attribute '__ClassMembers'

Process finished with exit code 1
```
私有的是不能够直接调用的，需要在类中进行调用，如下：
```Python
#!/usr/bin/env python
# _*_coding:utf-8 _*_

class Foo:

    # 私有的静态字段
    __ClassMembers = "私有的"

    # 通过类中的方法调用私有的静态字段进行输出
    def Members(self):
        print(Foo.__ClassMembers)

# 创建一个对象
obj = Foo()

# 执行类中的Members方法
obj.Members()
```
执行结果
```Python
/usr/bin/python3.5 /home/ansheng/文档/Python_code/sublime/Week06/Day04/s2.py
私有的

Process finished with exit code 0
```

普通字段修饰

```Python
#!/usr/bin/env python
# _*_coding:utf-8 _*_

class Foo:

    # 类的构造方法
    def __init__(self, url):

        # 普通字段
        self.url = url

        # 私有普通字段
        self.__Blog = url

# 创建一个对象，传入一个值
obj = Foo("http://ansheng.me")

# 普通字段
print(obj.url)

# 私有的普通字段
print(obj.__Blog)
```
输出
```Python
/usr/bin/python3.5 /home/ansheng/文档/Python_code/sublime/Week06/Day04/s2.py
http://ansheng.me
Traceback (most recent call last):
  File "/home/ansheng/文档/Python_code/sublime/Week06/Day04/s2.py", line 22, in <module>
    print(obj.__Blog)
AttributeError: 'Foo' object has no attribute '__Blog'

Process finished with exit code 1
```
若要输出私有的普通字段，需要在类中调用私有的普通字段进行输出
```Python
#!/usr/bin/env python
# _*_coding:utf-8 _*_

class Foo:

    # 类的构造方法
    def __init__(self, url):

        # 私有普通字段
        self.__Blog = url

        # 直接在狗仔方法没输出传入的URL
        print(self.__Blog)

# 创建一个对象，传入一个值
obj = Foo("http://ansheng.me")
```
输出结果
```bash
ansheng@Darker:~$ python3 /home/ansheng/文档/Python_code/sublime/Week06/Day04/s2.py
http://ansheng.me
```
对于私有的成员，只能够在类中进行访问，即使是继承关系也不可以，测试如下:
```Python
#!/usr/bin/env python
# _*_coding:utf-8 _*_

class Foo:

    # 父类的构造方法
    def __init__(self):

        # 私有普通字段
        self.__Blog = "http://ansheng.me"

# Bar继承了Foo类，
class Bar(Foo):

    # 由于Bar类没有构造方法，所以会执行他父类的构造方法

    # 创建一个类方法fetch
    def fetch(self):
        # 输出self.__Blog
        print(self.__Blog)

# 创建一个对象
obj = Bar()

# 执行类中的fetch方法
obj.fetch()
```
输出
```bash
ansheng@Darker:~$ python3 /home/ansheng/文档/Python_code/sublime/Week06/Day04/s2.py
Traceback (most recent call last):
  File "/home/ansheng/文档/Python_code/sublime/Week06/Day04/s2.py", line 26, in <module>
    obj.fetch()
  File "/home/ansheng/文档/Python_code/sublime/Week06/Day04/s2.py", line 20, in fetch
    print(self.__Blog)
AttributeError: 'Bar' object has no attribute '_Bar__Blog'
```

对于普通方法、静态方法类方法也是如此，只要成员前面加两个下划线就代表是私有的，即外部不能够访问，只有内部才可以访问。

## 通过特殊的方法去访问类中的私有成员

```Python
#!/usr/bin/env python
# _*_coding:utf-8 _*_

class Foo:

    # 父类的构造方法
    def __init__(self):

        # 私有普通字段
        self.__Blog = "http://ansheng.me"

# 创建一个对象
obj = Foo()

# 通过特殊的方法访问
print(obj._Foo__Blog)
# 一个下划线，一个类名，私有的变量名
```
输出
```bash
ansheng@Darker:~$ python3 /home/ansheng/文档/Python_code/sublime/Week06/Day04/s2.py
http://ansheng.me
```