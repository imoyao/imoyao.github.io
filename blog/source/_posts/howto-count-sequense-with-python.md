---
title: 使用Python进行计数统计
date: 2017-11-21 11:29:44
tags:
- Python
- HOWTO
- 编程
categories:
- Python
---
## 使用常规`for`循环
```python

In [53]: test_seq = 'asfsdgfads'

In [54]: count_dict = dict()

In [55]: for item in test_seq:
    ...:     if item in count_dict:
    ...:         count_dict[item] += 1
    ...:     else:
    ...:         count_dict[item] = 0
    ...:

In [56]: count_dict
Out[56]: {'a': 1, 'd': 1, 'f': 1, 'g': 0, 's': 2}
```
## 使用`collections`库中的`defaultdict`
```python
In [57]: from collections import defaultdict

In [58]: cd_dict = defaultdict()

In [59]: cd_dict = defaultdict(int)

In [60]: for item in test_seq:
    ...:     cd_dict[item] += 1
    ...:
In [62]: cd_dict
Out[62]: defaultdict(int, {'a': 2, 'd': 2, 'f': 2, 'g': 1, 's': 3})
In [63]: cd_dict.items()
Out[63]: [('a', 2), ('s', 3), ('d', 2), ('g', 1), ('f', 2)]
```

## 使用`collections`库中的`Counter`
```python
In [64]: from collections import Counter

In [65]: Counter(test_data)
Out[65]: Counter({'a': 1, 'd': 3, 'g': 3, 'h': 1, 's': 2})

In [84]: counter = Counter(test_seq)

In [85]: counter.items()
Out[85]: [('a', 2), ('s', 3), ('d', 2), ('g', 1), ('f', 2)]
```
## 参考书籍

- 《编写高质量代码：改善Python程序的91个建议》迷你书-建议 39：使用 Counter 进行计数统计