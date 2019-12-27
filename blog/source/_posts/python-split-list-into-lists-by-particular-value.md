---
title: 🐍PyTricks | Python 中如何把一个列表切分成指定大小的子列表
date: 2019-12-27 14:32:54
tags:
- Python
- TODO
categories:
- 🐍PyTricks
---

## 自己写的

```python
import math

def split_list(alist, split_len):   # TODO: 是否有改进之处
    """
    按照每4个一组进行划分
    :param alist:
    :param split_len:
    :return:
    """
    b = []
    start_split_index = 0
    length = int(math.ceil(len(alist) / float(split_len)))
    while length > 0:
        a = []
        end_index = start_split_index + split_len
        for i in alist[start_split_index:end_index]:
            a.append(i)

        start_split_index += split_len

        length -= 1
        b.append(a)

    return b
```

## 网上看到的

```python
def list_of_groups(init_list, children_list_len):
    list_of_group = zip(*(iter(init_list),) * children_list_len)
    end_list = [list(i) for i in list_of_group]
    count = len(init_list) % children_list_len
    end_list.append(init_list[-count:]) if count != 0 else end_list
    return end_list
```
## CookBook
```python

def slice_list(seq, size):
    return [seq[i:i + size] for i in range(0, len(seq), size)]
    
def zip_iter(seq, size): # TODO:没看懂，这个方法当 seq 太小时，会返回空；e.g.zip_iter(list(range(2)),4)
    return list(zip(*[iter(seq)] * size))
```
## 执行结果

```python
if __name__ == '__main__':
    a = list(range(24))
    num = 4
    t1 = split_list(a, num)
    t2 = list_of_groups(a, num)
    t3 = slice_list(a, num)
    t4 = zip_iter(a, num)
    print(t1)
    print(t2)
    print(t3)
    print(t4)
# [[0, 1, 2, 3], [4, 5, 6, 7], [8, 9, 10, 11], [12, 13, 14, 15], [16, 17, 18, 19], [20, 21, 22, 23]]
# [[0, 1, 2, 3], [4, 5, 6, 7], [8, 9, 10, 11], [12, 13, 14, 15], [16, 17, 18, 19], [20, 21, 22, 23]]
# [[0, 1, 2, 3], [4, 5, 6, 7], [8, 9, 10, 11], [12, 13, 14, 15], [16, 17, 18, 19], [20, 21, 22, 23]]
# [(0, 1, 2, 3), (4, 5, 6, 7), (8, 9, 10, 11), (12, 13, 14, 15), (16, 17, 18, 19), (20, 21, 22, 23)]
```
## 更多阅读

- [**Splitting A Python List Into Sublists**](https://www.garyrobinson.net/2008/04/splitting-a-pyt.html)
- [**split a list into roughly equal-sized pieces (python recipe)**](http://code.activestate.com/recipes/425397/)
- [Python | Split list into lists by particular value](https://www.geeksforgeeks.org/python-split-list-into-lists-by-particular-value/)