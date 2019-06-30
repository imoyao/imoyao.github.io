---
title: 浅析 Python 中的延迟绑定问题
date: 2018-04-10 15:41:35
tags:
- Python
- 延迟绑定
- 生成器
toc: true
---
# 延迟绑定(`late binding`)闭包
`Python` 使用中一个常见的困惑是 `Python` 在闭包(或在周围全局作用域（`surrounding global scope`）)中绑定变量的方式。
<!--more-->
你所写的函数：
```python
def multi_expression():
    return [lambda n: n*i for i in range(5)]
```
你所期望的：
```python
if __name__ == '__main__':
    print([mult(10) for mult in multi_expression()])
```
一个包含五个函数返回值的列表，每个函数有它们自己的封闭变量 `i` 乘以它们的参数，得到:
```python
[0, 10, 20, 30, 40]
```
而实际结果是：
```python
[40, 40, 40, 40, 40]
```
创建了五个函数，它们全都是 `4` 乘以 `n` 。
`Python` 的闭包是*迟绑定* 。这意味着闭包中用到的变量的值是在内部函数被调用时查询得到的。
在这里, 每当调用*任何*函数返回时, `i` 的值是调用时在周围作用域（ `surrounding scope`）中查询到的。到那个时候，循环已经完成， `i` 的值最终变成 `4` 。
关于这个陷阱有一个普遍严重的误解，它很容易被甩锅给 `Python` 的 [lambda](http://docs.python.org/reference/expressions.html#lambda)表达式。实际上， `lambda` 表达式是被冤枉滴。我们尝试把它改写成普通函数：
```python

def multi_func():
    foo = []

    for i in range(5):
        def func(n):
            return n * i
        foo.append(func)

    return foo
```
## 为了实现目标，你应该这样
1. 最一般的解决方案可以说是有点取巧（ `hack` ）。由于 `Python` 拥有在前文提到的为函数默认参数赋值的行为（参见 [可变默认参数](http://docs.python-guide.org/en/latest/writing/gotchas/#default-args) ）,你可以像下面这样创建一个立即绑定参数的闭包：

```python
def multi_expression_hack():
    return [lambda n, i=i: n * i for i in range(5)]     # 此处用法参见《Python Cookbook》7.7 匿名函数捕获变量值


if __name__ == '__main__':
    print([func(10) for func in multi_expression_hack()])
```

2. 或者，你可以使用 `functools.partial` 函数（偏函数）：

```python
from functools import partial
from operator import mul


def partial_func():
    return [partial(mul, i) for i in range(5)]


if __name__ == '__main__':
    print([func(10) for func in partial_func()])
```

3. 优雅的写法，直接用生成器推导式：

```python
def gen_expression():
    return (lambda n: n * i for i in range(5))


if __name__ == '__main__':
    print([gen(10) for gen in gen_expression()])
```

4. 利用 `yield` 的惰性求值思想编写生成器函数：

```python
def gen_func():
    for i in range(5):
        yield lambda n: i * n


if __name__ == '__main__':
    print([gen(10) for gen in gen_func()])
```

## 当陷阱不是一个陷阱

有时, 你预期闭包是这样的（迟绑定的表现形式）。延迟绑定在多数情况下是正常的。不幸的是, 循环创建独特的函数可能会导致未知的小问题。

## 派森多一点

关于生成器的惰性求值，我们可以看点简单的例子：

```python
# coding=utf-8


def add(a, b):
    return a + b


def gen(n):
    for i in range(n):
        yield i


def main(m_num, m_gen_num):
    base = gen(m_gen_num)
    for n in range(m_num):
        base = (add(i, n) for i in base)
    return base


if __name__ == '__main__':
    num = 5
    gen_num = 10
    print(list(main(num, gen_num)))
```

返回结果：

```Python
[90, 91, 92]
```

如果我们对之前改写的`multi_func()`函数再稍微改写一下，让内部函数传值`*args`会怎么样？

```Python
def multi_func_starred():
    foo = []

    for i in range(5):
        def func(*n):
            return n * i
        foo.append(func)

    return foo

if __name__ == '__main__':
    print([func(10) for func in multi_func_starred()])
```

返回结果：

```Python
[(10, 10, 10, 10), (10, 10, 10, 10), (10, 10, 10, 10), (10, 10, 10, 10), (10, 10, 10, 10)]
```

实际上，`*args`相当于一个生成器推导式，这点很容易验证：

```Python
def multi_expression_starred():
    # print(type(lambda *n: n*i for i in range(5)))     # 去掉注释 >>>: <class 'generator'>
    return [lambda *n: n * i for i in range(5)]


if __name__ == '__main__':
    print([func(10) for func in multi_expression_starred()])
```
