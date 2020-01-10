---
title: 🐍PyTricks | Python 中如何实现列表的行列互转？
date: 2020-01-10 14:39:11
tags:
- 🐍PyTricks
- Python
categories:
- 🐍PyTricks
cover: /images/Python/Python-snake.jpg
---
## 笨方法
```python
def make_row_to_column(a):
    b = []
    for item in range(len(a[0])):
        r = []
        for j in range(len(a)):
            r.append(a[j][item])
        b.append(r)
    return b
```
## 🐍PyTricks

```python
def row_2_column(row_list):
    return map(list,zip(*row_list))


if __name__ == '__main__':
    nest_list = [[_ for _ in range(5)] for i in range(4)] 
    print(row_2_column(nest_list)) 
    # [[0, 0, 0, 0], [1, 1, 1, 1], [2, 2, 2, 2], [3, 3, 3, 3], [4, 4, 4, 4]]
```
注意在`Python3`中返回的是一个`<map object at 0x000002674CC62688>`，需要再用`list()` 方法转一下。

## 参考

- [如何用python实现行列互换？ - 知乎](https://www.zhihu.com/question/39660985)
