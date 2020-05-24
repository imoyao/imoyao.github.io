---
title: Python 全栈之路系列之面向对象特殊成员
toc: true
date: 2020-05-23 18:21:46
tags:
- 编码
- 面向对象
top: 4
---

## 类的特殊成员之 call

```Python
#!/usr/bin/env python
# _*_coding:utf-8 _*_

class SpecialMembers:

    # 类的构造方法
    def __init__(self):
        print("My Blog is Url: http://ansheng.me")

    # 对象的构造方法
    def __call__(self):
        print("My Name is: Ansheng")

# 创建一个对象，并且执行类的构造方法
obj = SpecialMembers()

# 执行对象的构造方法
obj()

# 先执行类的构造方法，然后在执行对象的构造方法
SpecialMembers()()
```

---

输出
```Python
ansheng@Darker:~$ python3 /home/ansheng/文档/Python_code/sublime/Week06/Day04/s2.py
My Blog is Url: http://ansheng.me
My Name is: Ansheng
My Blog is Url: http://ansheng.me
My Name is: Ansheng
```

## 类的特殊成员之 getitem、setitem、delitem

```Python
#!/usr/bin/env python
# _*_coding:utf-8 _*_

class SpecialMembers:

    # 当执行obj['value']的时候就会自动执行__getitem__方法，并且把对象括号内的值当做__getitem__的值
    def __getitem__(self, item):
        print(item)

    def __setitem__(self, key, value):
        print(key, value)

    def __delitem__(self, key):
        print(key)

# 创建一个对象
obj = SpecialMembers()

# 自动执行__getitem__方法
obj['value']

# 自动执行__setitem__方法
obj['k1'] = "values"

# 自动执行__delitem__方法
del obj['key']
```
输出
```bash
ansheng@Darker:~$ python3 /home/ansheng/文档/Python_code/sublime/Week06/Day04/s2.py
value
k1 values
key
```
特殊的
```Python
#!/usr/bin/env python
# _*_coding:utf-8 _*_

class SpecialMembers:

    # 当执行obj['value']的时候就会自动执行__getitem__方法，并且把对象括号内的值当做__getitem__的值
    def __getitem__(self, item):
        print(item, type(item), "__getitem__")

    def __setitem__(self, key, value):
        print(key, value)

    def __delitem__(self, key):
        print(key)

# 创建一个对象
obj = SpecialMembers()

# 自动执行__getitem__方法
obj[1:3]  # __getslice__/__getitem__

# 自动执行__setitem__方法
obj[1:3] = [11, 22, 33]  # __setslice__/__setitem__

# 自动执行__delitem__
del obj[1:3]  # __delslice__/__delitem__
```
输出
```bash
ansheng@Darker:~$ python3 /home/ansheng/文档/Python_code/sublime/Week06/Day04/s2.py
slice(1, 3, None) <class 'slice'> __getitem__
slice(1, 3, None) [11, 22, 33]
slice(1, 3, None)
```

## 类的特殊成员之 dict

获取类或对象中的所有成员

```Python
#!/usr/bin/env python
# _*_coding:utf-8 _*_

class SpecialMembers:
    """
    类的注释
    """

    def __init__(self):
        self.Name = "Ansheng"
        self.Blog = "https://blog.ansheng.me"

# 获取类中的成员
print(SpecialMembers.__dict__)

# 创建一个对象
obj = SpecialMembers()

# 获取对象中的成员
print(obj.__dict__)
```
输出
```bash
ansheng@Darker:~$ python3 /home/ansheng/文档/Python_code/sublime/Week06/Day04/s2.py
{'__weakref__': <attribute '__weakref__' of 'SpecialMembers' objects>, '__doc__': '\n    类的注释\n    ', '__module__': '__main__', '__dict__': <attribute '__dict__' of 'SpecialMembers' objects>, '__init__': <function SpecialMembers.__init__ at 0x7ff2af2d7598>}
{'Blog': 'https://blog.ansheng.me', 'Name': 'Ansheng'}
```

## 类的特殊成员之 iter

一个对象如果可以被`for`循环迭代时，说明对象中又`__iter__`方法，且方法中有`yield`值。

```Python
#!/usr/bin/env python
# _*_coding:utf-8 _*_

class SpecialMembers:

    def __iter__(self):
        yield 1
        yield 2
        yield 3

# 创建一个对象
obj = SpecialMembers()

# 如果执行for循环对象时，自动会执行对象的__iter__方法，此时的__iter__就是一个生成器
for i in obj:
    print(i)
```
输出
```bash
ansheng@Darker:~$ python3 /home/ansheng/文档/Python_code/sublime/Week06/Day04/s2.py
1
2
3
```