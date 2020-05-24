---
title: Python 全栈之路系列之面向对象类成员特性
toc: true
date: 2020-05-23 18:21:46
tags:
- 编码
top: 5
---

特性的存在就是将方法伪装成字段。

property

把类方法当做普通字段去调用，即用对象调用的时候后面不用加括号

```Python
#!/usr/bin/env python
# _*_coding:utf-8 _*_

class Foo:

    @property
    def Characteristic(self):
        print("类方法的特性")

# 创建一个对象
obj = Foo()
# 调用类方法的时候方法后面不用加括号
obj.Characteristic
```
输出
```Python
/usr/bin/python3.5 /home/ansheng/文档/Python_code/sublime/Week06/Day04/s2.py
类方法的特性

Process finished with exit code 0
```

setter

设置类方法的值
```Python
#!/usr/bin/env python
# _*_coding:utf-8 _*_

class Foo:

    # 获取Characteristic值
    @property
    def Characteristic(self):
        return "获取Characteristic值"

    # 意思是下面的Characteristic函数用来给上面的Characteristic函数设置值
    @Characteristic.setter
    def Characteristic(self, value):
        return "设置Characteristic的值"

# 创建一个对象
obj = Foo()

# 获取Characteristic的值
print(obj.Characteristic)

# 设置Characteristic的值
obj.Characteristic = 123
```
输出
```Python
/usr/bin/python3.5 /home/ansheng/文档/Python_code/sublime/Week06/Day04/s2.py
获取Characteristic值

Process finished with exit code 0
```

deleter

```Python
class Foo:

    # 特殊字段
    @property
    def pp(self):
        # 调用特殊字段的时候输出aaa
        print("property")

    @pp.setter
    def pp(self, value):
        # 调用设置方法的时候输出value的值
        print(value)

    @pp.deleter
    def pp(self):
        # 调用删除方法的时候输出del
        print("deleter")

# 创建一个对象obj
obj = Foo()

# 自动执行@property
obj.pp

# 自动执行@pp.setter
obj.pp = 999

# 自动执行@pp.deleter
del obj.pp
```
输出
```bash
ansheng@Darker:~$ python3 /home/ansheng/文档/Python_code/sublime/Week07/s1.py
property
999
deleter
```

## 另一种调用特殊属性的方法

```Python
class Foo:

    def f1(self):
        print("f1")

    def f2(self, value):
        print("f2")

    def f3(self):
        print("f3")

    SpecialFields = property(fget=f1, fset=f2, fdel=f3, doc="我是注释")

# 创建一个对象
obj = Foo()

# 调用类的f1方法
obj.SpecialFields

# 调用类的f2方法
obj.SpecialFields = 123

# 调用类的发方法
del obj.SpecialFields

# 调用类的doc，这里只能通过类去访问，对象无法访问
print(Foo.SpecialFields.__doc__)
```
输出结果
```bash
ansheng@Darker:~$ python3 /home/ansheng/文档/Python_code/sublime/Week07/s1.py
f1
f2
f3
我是注释
```