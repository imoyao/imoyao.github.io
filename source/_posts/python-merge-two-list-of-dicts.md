---
title: 🐍PyTricks | Python 中如何合并一个内字典列表？
date: 2020-04-19 10:19:44
tags:
- dict
- Python
categories: 🐍PyTricks
cover: /images/Python/Python-snake.jpg
subtitle: 内字典列表，是我自命名的一种非官方叫法，形如 [{'foo':'bar'}]，一般多见于后端返回给前端的 json 数据。
---
## 需求

有如下列表，要将他们按照 id 合并成一个列表。
```python
l1 = [{'id': 9, 'av': 4}, {'id': 10, 'av': 0}, {'id': 8, 'av': 0}]
l2 = [{'id': 9, 'nv': 45}, {'id': 10, 'nv': 0}, {'id': 8, 'nv': 30}]
```

##  解决方案

1.  初级版
将两个列表按照 id 分组，分别放置到新列表中，然后遍历其中一个列表，并按照 key 将数据更新，代码如下：
```python

l3 = {x['id']: {'av': x['av']} for x in l1}

l4 = {x['id']: {'nv': x['nv']} for x in l2}

{key: value.update(l4[key]) for key, value in l3.items()}

>> {9: {'av': 4, 'nv': 45}, 10: {'av': 0, 'nv': 0}, 8: {'av': 0, 'nv': 30}}

```
我们很容易发现里面的 l4 的是多余的，重复 for 循环会降低代码的效率。所以

2.  第一版改进
```python

l3 = {x['id']: {'av': x['av']} for x in l1}

for item in l2:

    l3[item['id']].update(nv=item['nv'])

```

3. 第二版代码
使用字典的[pop](https://docs.python.org/3/library/stdtypes.html#dict.pop)方法将 id 取出来，因为我们只关心 id，而不需要关注字典中的其他 key
```python
l3 = {_.pop('id'): _ for _ in l1}

for item in l2:

  l3[item.pop('id')].update(item)

```
但是这种办法有一个缺陷：我们会对所有输入的字典进行更新，为了消除这个影响，我们从一个空字典开始，更新每一个键，当然也包括 id，之后弹出额外的键，可以使用[defaultdict](https://docs.python.org/3/library/collections.html#collections.defaultdict):
简单介绍参考：[James Tauber : Evolution of Default Dictionaries in Python](https://jtauber.com/blog/2008/02/27/evolution_of_default_dictionaries_in_python/)
4.  第三版代码
```python
from collections import defaultdict


result = defaultdict(dict)
for sequence in (l1, l2):
   for dictionary in sequence:
       result[dictionary['id']].update(dictionary)
for dictionary in result.values():
   dictionary.pop('id')
```
如果我们要合并的内字典列表多于两个呢？用这种方法是很容易扩展的，定义一个方法：

5. 终极版代码
```python
import itertools
from collections import defaultdict


def merge_iterables_of_dict(shared_key, *iterables):
   result = defaultdict(dict)
   for dictionary in itertools.chain.from_iterable(iterables):
       result[dictionary[shared_key]].update(dictionary)
   for dictionary in result.values():
       dictionary.pop(shared_key)
   return result
```
使用这个函数：`merge_iterables_of_dict('id',l1,l2)`，注意，li 和 l2 的顺序会影响返回结果，更“靠谱”的数据应该放到 iterables 后方（参考字典`update`方法的更新逻辑）。

## 参考链接

[python - Merge two list of dicts with same key - Code Review Stack Exchange](https://codereview.stackexchange.com/questions/209202/merge-two-list-of-dicts-with-same-key)

## 推荐阅读

如果只是合并两个字典，请参阅：[dictionary - How do I merge two dictionaries in a single expression in Python? - Stack Overflow](https://stackoverflow.com/questions/38987/how-do-i-merge-two-dictionaries-in-a-single-expression-in-python/26853961)和[list - merging Python dictionaries - Stack Overflow](https://stackoverflow.com/questions/2365921/merging-python-dictionaries)