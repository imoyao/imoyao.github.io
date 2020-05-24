---
title: Python 全栈之路系列之字典数据类型
toc: true
date: 2020-05-23 18:21:46
tags:
- 编码
- 字典
top: 5
---

字典(dict)在基本的数据类型中使用频率也是相当高的，而且它的访问方式是通过键来获取到对应的值，当然存储的方式也是`键值`对了，属于可变类型。

其中字典的 Key 必须是不可变类型，比如字符串、数字、元组都可以作为字典的 Key。

## 创建字典的两种方式

第一种

```python
>>> dic = {"k1":"123","k2":"456"}
>>> dic
{'k1': '123', 'k2': '456'}
>>> type(dic)
<class 'dict'>
```

第二种

```python
>>> dic = dict({"k1":"123","k2":"456"})
>>> dic
{'k1': '123', 'k2': '456'}
>>> type(dic)
<class 'dict'>
```

在创建字典的时候，`__init__`初始化的时候还可以接受一个可迭代的变量作为值

```python
>>> li = ["a","b","c"]
>>> dic = dict(enumerate(li))
>>> dic
{0: 'a', 1: 'b', 2: 'c'}
```

默认 dict 在添加元素的时候会把 li 列表中的元素 for 循环一遍，添加的时候列表中的内容是字典的值，而键默认是没有的，可以通过 enumerate 方法给他加一个序列，也就是键。

与其变量不同的是，字典的键不仅仅支持字符串，而且还支持其他数据类型，譬如：

```python
# 数字
>>> D = {1:3}
>>> D[1]
3
# 元组
>>> D = {(1,2,3):3}
>>> D[(1,2,3)]
3
```

字典解析

```python
>>> D = {x: x*2 for x in range(10)}
>>> D
{0: 0, 1: 2, 2: 4, 3: 6, 4: 8, 5: 10, 6: 12, 7: 14, 8: 16, 9: 18}
# 可以使用zip
>>> D = {k:v for (k, v) in zip(['a','b','c'],[1,2,3])}
>>> D
{'a': 1, 'c': 3, 'b': 2}
```

## 字典所提供的常用方法

删除字典中的所有元素

> clear(self):

```python
>>> person = dict({"name": "ansheng", 'age': 18})
>>> person
{'age': 18, 'name': 'ansheng'}
>>> person.clear()
# 清空字典的内容之后字典会变成一个空字典
>>> person
{}
```

返回一个字典的浅复制

> copy(self): 

```python
>>> person = dict({"name": "ansheng", 'age': 18})
>>> person.copy()
{'age': 18, 'name': 'ansheng'}
```

创建一个新字典，以序列 seq 中元素做字典的键，value 为字典所有键对应的初始值

> fromkeys(S, v=None): 

|属性|描述|
|:--|:--|
|S|字典键值列表|
|v|可选参数, 设置键序列（seq）的值|

```python
>>> seq = ('name', 'age', 'sex')
>>> dict = dict.fromkeys(seq)
>>> dict
{'age': None, 'name': None, 'sex': None}
```

fromkeys 方法就是把一个字典的 key 更新到另外一个字典中，默认的值可以设置

```python
>>> dic={"k1":123,"k2":456,"k4":111}
>>> dic
{'k1': 123, 'k4': 111, 'k2': 456}
# 创建一个新的字典，默认值是`123`
>>> dic.fromkeys(["k1","k2","k3"],"123")
{'k1': '123', 'k3': '123', 'k2': '123'}
```

返回指定键的值，如果值不在字典中返回默认值

> get(self, k, d=None):

|属性|描述|
|:--|:--|
|key|字典中要查找的键|
|default|如果指定键的值不存在时，返回该默认值值|

```python
>>> person = {"name": "ansheng", 'age': 18}
>>> person.get("name")
'ansheng'
```

成员运算符 in 可以判断键是否存在于字典中，如果键在字典 dict 里返回 true，否则返回 false

```python
>>> person = {"name": "mr", 'age': 18}
>>> 'name' in person
True
>>> 'aname' in person
False
```

以列表返回可遍历的(键, 值)元组数组

> items(self):

```python
>>> person = {"name": "mr.wu", 'age': 18}
# 以元组的方式输出出来
>>> person.items()
[('age', 18), ('name', 'mr.wu')]
```

以列表的形式返回一个字典所有的键

> keys(self):

```python
>>> person = {"name": "ansheng", 'age': 18}
>>> person.keys()
['age', 'name']
```

删除指定给定键所对应的值，返回这个值并从字典中把它移除

> pop(self, k, d=None): 

```python
>>> person = {"name": "ansheng", 'age': 18}
>>> person
{'age': 18, 'name': 'ansheng'}
# 返回删除键对应的值
>>> person.pop("age")
18
>>> person
{'name': 'ansheng'}
```

随机返回并删除字典中的一对键和值，因为字典是无序的，没有所谓的"最后一项"或是其它顺序。

> popitem(self): 

```python
>>> person = {"name": "ansheng", 'age': 18}
# 随即删除并显示所删除的键和值
>>> person.popitem()
('age', 18)
>>> person
{'name': 'ansheng'}
```

如果 key 不存在，则创建，如果存在，则返回已存在的值且不修改

> setdefault(self, k, d=None): 

|属性|描述|
|:--|:--|
|key|查找的键值|
|default|键不存在时，设置的默认键值|

```python
>>> person = {"name": "ansheng", 'age': 18}
# 如果字典中有这个键，那么就输出这个键的值
>>> person.setdefault("name")
'ansheng'
# 如果没有则不输出，但是会创建一个键，值为默认的'None'，值是可以指定的
>>> person.setdefault("sex")
>>> person
{'age': 18, 'name': 'ansheng', 'sex': None}

```

把字典 dic2 的键/值对更新到 dic1 里

> update(self, E=None, **F): 

```python
>>> dic1 = {"name":"ansheng"}
>>> dic2 = {"age":"18"}
>>> dic1
{'name': 'ansheng'}
>>> dic2
{'age': '18'}
>>> dic1.update(dic2)
>>> dic1
{'age': '18', 'name': 'ansheng'}
```

显示字典中所有的值

> values(self): 

```python
>>> person = {"name": "ansheng", 'age': 18}
>>> person.values()
[18, 'ansheng']
```
