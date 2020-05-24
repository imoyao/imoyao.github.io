---
title: Python 全栈之路系列之元组数据类型
toc: true
date: 2020-05-23 18:21:46
tags:
- 编码
- 元组
top: 6
---

元组(tuple)和列表的唯一区别就是列表可以更改，元组不可以更改，其他功能与列表一样

创建元组的两种方法

第一种

```python
ages = (11, 22, 33, 44, 55)
```

第二种

```python
ages = tuple((11, 22, 33, 44, 55))
```

如果元祖内只有一个元素，那么需要加上一个逗号，否则就变成字符串了。

```python
In [1]: t = (1)

In [2]: t
Out[2]: 1

In [3]: type(t)
Out[3]: int

In [4]: t = (1,)

In [5]: t
Out[5]: (1,)

In [6]: type(t)
Out[6]: tuple
```

## 元组所具备的方法

查看列表中元素出现的次数

> count(self, value):

|属性|描述|
|:--|:--|
|value|元素的值|

```python
>>> ages = tuple((11, 22, 33, 44, 55))
>>> ages
(11, 22, 33, 44, 55)
>>> ages.count(11)
1
```

查找元素在元组中的位置

> index(self, value, start=None, stop=None):

|属性|描述|
|:--|:--|
|value|元素的值|
|start|开始的位置|
|stop|结束的位置|

```python
>>> ages = tuple((11, 22, 33, 44, 55))
>>> ages.index(11)
0
>>> ages.index(44)
3
```

列表嵌套

```python
>>> T = (1,2,3,4,5)
>>> (x * 2 for x in T)
<generator object <genexpr> at 0x102a3e360>
>>> T1 = (x * 2 for x in T)
>>> T1
<generator object <genexpr> at 0x102a3e410>
>>> for t in T1: print(t)
... 
2
4
6
8
10
```

## 元组嵌套修改

元组的元素是不可更改的，但是元组的元素的元素就可能是可以更改的

```python
>>> tup=("tup",["list",{"name":"ansheng"}])
>>> tup
('tup', ['list', {'name': 'ansheng'}])
>>> tup[1]
['list', {'name': 'ansheng'}]
>>> tup[1].append("list_a")
>>> tup[1]
['list', {'name': 'ansheng'}, 'list_a']
```

元组的元素本身是不可修改的，但是如果元组的元素是个列表或者字典那么就可以被修改

## 切片原地修改不可变类型

```python
>>> T = (1,2,3)
>>> T = T[:2] + (4,)
>>> T
(1, 2, 4)
```