---
title: Python 全栈之路系列之列表数据类型
toc: true
date: 2020-05-23 18:21:46
tags:
- 编码
- 列表
---

列表(list)同字符串一样都是有序的，因为他们都可以通过切片和索引进行数据访问，且列表是可变的。

## 创建列表的几种方法

第一种

```python
name_list = ['Python', 'PHP', 'JAVA']
```

第二种

```python
name_list ＝ list(['Python', 'PHP', 'JAVA'])
```

创建一个空列表

```python
>>> li = list() 
>>> type(li)
<class 'list'>
```

把一个字符串转换成一个列表

```python
>>> var="abc"
>>> li = list(var)
>>> li
['a', 'b', 'c']
```

list 在把字符串转换成列表的时候，会把字符串用 for 循环迭代一下，然后把每个值当作 list 的一个元素。

把一个元组转换成列表

```python
>>> tup=("a","b","c")
>>> li=list(tup)
>>> type(li)
<class 'list'>
>>> li
['a', 'b', 'c']
```

把字典转换成列表

```python
>>> dic={"k1":"a","k2":"b","k3":"c"}
>>> li=list(dic)
>>> type(li)
<class 'list'>
>>> li
['k3', 'k1', 'k2']
```

字典默认循环的时候就是 key，所以会把 key 当作列表的元素

```python
>>> dic={"k1":"a","k2":"b","k3":"c"}
>>> li=list(dic.values())
>>> li
['c', 'a', 'b']
```

如果指定循环的是 values，那么就会把 values 当作列表的元素

## 列表所提供的方法

在列表末尾添加新的对象

> append(self, p_object): 

```python
>>> name_list = ['Python', 'PHP', 'JAVA']
>>> name_list.append("C#")
>>> name_list
['Python', 'PHP', 'JAVA', 'C#']
```

统计某个元素在列表中出现的次数

> count(self, value): 

|属性|描述|
|:--|:--|
|obj|列表中统计的对象|

```python
>>> name_list = ['Python', 'PHP', 'PHP']
>>> name_list.count("PHP")
2
```

用于在列表末尾一次性追加另一个序列中的多个值

> extend(self, iterable): 

|属性|描述|
|:--|:--|
|seq|元素列表|

```python
>>> name_list = ['Python', 'PHP', 'Python']
>>> name_OS = ['Windows', 'Linux', 'Unix']
>>> name_list
['Python', 'PHP', 'Python']
>>> name_OS
['Windows', 'Linux', 'Unix']
# 把列表`name_OS`中的内容添加到`name_list`的尾部
>>> name_list.extend(name_OS)
# 输出的结果
>>> name_list
['Python', 'PHP', 'Python', 'Windows', 'Linux', 'Unix']
```

从列表中找出某个值第一个匹配项的索引位置

> index(self, value, start=None, stop=None): 

|属性|描述|
|:--|:--|
|value|列表中统计的对象|

```python
# 查找对象所在的位置
>>> name_list = ['Python', 'PHP', 'JAVA']
>>> name_list.index("PHP")
1
```

将指定对象插入列表

> insert(self, index, p_object): 

|属性|描述|
|:--|:--|
|index|对象 obj 需要插入的索引位置|
|obj|要出入列表中的对象|

```python
>>> name_list = ['Python', 'PHP', 'JAVA']
# 把位置`1`的内容换成`C`，后面的自动退格一个位置
>>> name_list.insert(1,"C")
>>> name_list
['Python', 'C', 'PHP', 'JAVA']
```

移除列表中的一个元素，并且返回该元素的值

> pop(self, index=None):

|属性|描述|
|:--|:--|
|index|可选参数，要移除列表元素的位置|

```python
>>> name_list = ['Python', 'PHP', 'JAVA']
# 删除位置1上面的内容，并且返回删除的字符串
>>> name_list.pop(1)
'PHP'
>>> name_list
['Python', 'JAVA']
```

移除列表中某个值的第一个匹配项

> remove(self, value): 

|属性|描述|
|:--|:--|
|value|列表中要移除的对象|

```python
>>> name_list = ['Python', 'PHP', 'JAVA', 'Python']
# 每次删除的时候只会把第一次匹配到的值删除，第二个值不会被删除
>>> name_list.remove("Python")
>>> name_list
['PHP', 'JAVA', 'Python']
>>> name_list.remove("Python")
>>> name_list
['PHP', 'JAVA']
```

当然删除元素还可以直接使用`del`进行删除：

```python
>>> L = [1,2,3]
>>> del L[1]
>>> L
[1, 3]
```

又或者使用切片赋值进行元素删除

```python
>>> L = [1,2,3]
>>> L[1:2] = []
>>> L
[1, 3]
```

反向输出列表中的元素

> reverse(self):

```python
>>> name_list = ['Python', 'PHP', 'JAVA']
>>> name_list
['Python', 'PHP', 'JAVA']
>>> name_list.reverse()
>>> name_list
['JAVA', 'PHP', 'Python']
```

对原列表进行排序，如果指定参数，则使用比较函数指定的比较函数

> sort(self, cmp=None, key=None, reverse=False):

```python
>>> name_list = ['Python', 'PHP', 'JAVA']
>>> name_list
['Python', 'PHP', 'JAVA']
>>> name_list.sort()
>>> name_list
['JAVA', 'PHP', 'Python']
```

清除列表内所有元素

```python
>>> li
['Ansheng']
>>> li.clear()
>>> li
[]
```

同字符串一样，列表也支持解析，称为列表解析

```python
>>> li = [x for x in range(1,20)]
>>> li
[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]
```
