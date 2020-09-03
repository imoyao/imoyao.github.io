---
title: 浅析 Python 中的延迟绑定问题
date: 2018-04-10 15:41:35
tags:
- Python
- 延迟绑定
- 生成器
toc: true
---
`Python` 使用中一个常见的困惑是 `Python` 在闭包(或在周围全局作用域（`surrounding global scope`）)中绑定变量的方式。
<!--more-->
你所写的函数：
```python
def multi_expression():
    return [lambda n: n*i for i in range(5)]
    
    
if __name__ == '__main__':
    print([multi(10) for multi in multi_expression()])
```
你所期望的是：
一个包含 5 个函数返回值的列表，每个函数有它们自己的封闭变量 `i` 乘以它们的参数，得到:
```python
[0, 10, 20, 30, 40]
```
而实际返回结果是：
```python
[40, 40, 40, 40, 40]
```
创建了 5 个函数，它们全都是 `4` 乘以 `n` 。
`Python` 的闭包是*迟绑定* 。这意味着闭包中用到的变量的值是在内部函数被调用时查询得到的。
在这里, 每当调用*任何*函数返回时, `i` 的值是调用时在周围作用域（ `surrounding scope`）中查询到的。而到那个时候，循环已经完成， `i` 的值最终变成 `4` 。

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
1. 最一般的解决方案可以说是有点取巧（ `hack` ）。由于 `Python` 拥有在前文提到的为函数的默认参数赋值的行为（参见 [可变默认参数](http://docs.python-guide.org/en/latest/writing/gotchas/#default-args) ）,你可以像下面这样创建一个立即绑定参数的闭包：

 ```python
def multi_expression_hack():
    return [lambda n, i=i: n * i for i in range(5)]     # 此处用法参见《Python Cookbook》7.7 匿名函数捕获变量值


if __name__ == '__main__':
    print([func(10) for func in multi_expression_hack()])
 ```
 此处会在函数内部再次定义一个局部变量。

2. 或者，你可以使用 `functools.partial` 函数（偏函数）：

 ```python
    from functools import partial
    from operator import mul


    def partial_func():
        return [partial(mul, i) for i in range(5)]


    if __name__ == '__main__':
        print([func(10) for func in partial_func()])
 ```

3. 优雅的写法，直接用生成器表达式：

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

关于生成器的惰性求值，我们可以看个例子：

```python
# coding=utf-8


def add(a, b):      # ①
    return a + b


def gen(n):     # ②
    for i in range(n):
        yield i


def main(m_num, m_gen_num):
    base = gen(m_gen_num)
    for n in range(m_num):              # ③
        base = (add(i, n) for i in base)
    return base


if __name__ == '__main__':
    num = 10
    gen_num = 3
    print(list(main(num, gen_num)))
```

返回结果：

```Python
[90, 91, 92]
```
### 解释

看懂这个函数的关键是看懂 for 循环中的`base = (add(i, n) for i in base)`表达式，其中 add 的求和运算是和`for i in base`生成器中的元素（0,1,2）进行的，**而 n 在最终运算时实际上每次都是 9**。所以最终求值时相当于 9 和 `gen()` 求和之后再自己连续累加 10 次，最终得到值为（90,91,92）的生成器，而 list 就很简单了，只是一个简单的将生成器转换为列表的操作。

注意：此处代码不记得在哪里看的原文了，时隔两年再去看居然看不懂了。🤕如果读了上面看不懂的话可以参考此处 👉 [python 迭代器与生成器小结 - shomy - SegmentFault 思否](https://segmentfault.com/a/1190000004554823)

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

```plain
[(10, 10, 10, 10), (10, 10, 10, 10), (10, 10, 10, 10), (10, 10, 10, 10), (10, 10, 10, 10)]
```

实际上，`*args`相当于一个生成器表达式，这点很容易验证：

```python
def multi_expression_starred():
    # print(type(lambda *n: n*i for i in range(5)))     # 注释行打印 >>>: <class 'generator'>
    return [lambda *n: n * i for i in range(5)]


if __name__ == '__main__':
    print([func(10) for func in multi_expression_starred()])
```
