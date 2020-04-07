---
title: 🐍PyTricks | Python 字典排序
date: 2018-01-02 17:00:59
tags:
- Python
- sort
- dict
categories:
- 🐍PyTricks
cover: /images/Python/Python-snake.jpg
---
写出`Pythonic`的代码应该是每个 Pythonista 的毕生追求，本文主要记录在开发中遇到的一些有关`Python`技巧。

<!--more-->

## 排序

- `JSON`字典内按照某个键值排序

```python

In [15]: alist = [{'create': '2017-12-28 11:05:48', 'id': '0_1', 'path': 'foo.py', 'size': 0},
{'create': '2017-12-28 11:00:29', 'id': '0_2', 'path': 'bar.py', 'size': 0}, {'create': '2017-12-28 11:05:55', 'id': '0_3', 'path': 'baz.py', 'size': 0}]

In [16]: alist.sort(key=lambda x:x['create'])    # 按照创建时间排序 

In [17]: alist
Out[17]:
[{'create': '2017-12-28 11:00:29', 'id': '0_2', 'path': 'bar.py', 'size': 0},
 {'create': '2017-12-28 11:05:48', 'id': '0_1', 'path': 'foo.py', 'size': 0},
 {'create': '2017-12-28 11:05:55', 'id': '0_3', 'path': 'baz.py', 'size': 0}]
 
```

- 字典排序

```python

In [35]: languages = {'JAVA':15,'Python':12,'Go':13,'PHP':14}

In [35]: sorted(languages.items(),key=lambda x:x[0])        # 以key排序
Out[35]: [('Go', 13), ('JAVA', 15), ('PHP', 12), ('Python', 12)]

In [36]: sorted(languages.items(),key=lambda x:x[1])        # 以value排序
Out[36]: [('Python', 12), ('PHP', 12), ('Go', 13), ('JAVA', 15)]

In [37]: sorted(languages.items(),key=lambda x:-x[1])       # 以value倒序
Out[37]: [('JAVA', 15), ('Go', 13), ('Python', 12), ('PHP', 12)]

```

**注意**：`sort()`与`sorted()`的区别，前者直接修改列表，返回值为`None`；后者为内置函数，它会从一个可迭代对象构建一个新的排序列表。

## 参考阅读
- [排序指南 — Python 3.6.10 文档](https://docs.python.org/zh-cn/3.6/howto/sorting.html)

