---
title: Python 全栈之路系列之迭代器与生成器
toc: true
date: 2020-05-23 18:21:46
tags:
- 编码
- 迭代器
- 生成器
top: 6
---

## 生成器

仅仅拥有生成某种东西的能力，如果不用`__next__`方法是获取不到值得。

创建一个生成器函数

```python
>>> def scq():
...    print("11")
       # 当函数代码块中遇到yield关键字的时候，这个函数就是一个生成器函数
...    yield 1
...    print("22")
...    yield 2
...    print("33")
...    yield 3
...
```

把生成器赋值给一个对象

```python
>>> r = scq()
```

查看 r 的苏剧类型并且输出 r 的值

```python
>>> print(type(r),r)
<class 'generator'> <generator object scq at 0x000001F117D8DF10> 
```

当执行生成器的`__next__`的时候，代码会按照顺序去执行，当执行到`yield`时会返回并提出，`yield`后面的值就是返回值，然后记录代码执行的位置，并退出

```python
>>> ret = r.__next__()
11
```
第二次执行的时候会根据上次代码执行的位置继续往下执行

```python
>>> ret = r.__next__()
22
>>> ret = r.__next__()
33
```

如果`__next__`获取不到值的时候就会报`StopIteration`错误

```python
>>> ret = r.__next__()
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
StopIteration
```

利用生成器创建一个类似`xrange`的功能

代码

```python
# 创建一个生成器函数，函数名是range，n是传入的参数，也是输出的数的最大值
def range(n):
    # 默认从0开始
    start = 0
    # 进入while循环，如果最小值小于最大值就进入循环
    while start < n:
        # 第一次返回start，下面代码不执行
        yield start
        # 第二次进来的时候start = start + 1，然后进入下一次循环
        start += 1

# 停止的参数为5
obj = range(5)
# 第一个数赋值给n1
n1 = obj.__next__()
# 第二个数赋值给n2
n2 = obj.__next__()
# 第三个数赋值给n3
n3 = obj.__next__()
# 第四个数赋值给n4
n4 = obj.__next__()
# 第五个数赋值给n5
n5 = obj.__next__()

# 输出这五个数的值
print(n1,n2,n3,n4,n5)
```

执行结果

```python
C:\Python35\python.exe F:/Python_code/sublime/Week5/Day03/s1.py
0 1 2 3 4

Process finished with exit code 0
```

## 迭代器

具有访问生成器的能力，可以访问到生成器的值，类似于生成器的`__next__`方法，一个一个值一个值得去迭代，只能够按照顺序的去查找。

**特点：**

1. 访问者不需要关心迭代器内部的结构，仅需通过 next()方法不断去取下一个内容
2. 不能随机访问集合中的某个值 ，只能从头到尾依次访问
3. 访问到一半时不能往回退
4. 便于循环比较大的数据集合，节省内存

优化上面`range`或`xrange`的生成器

```python
def irange(start, stop, step=1):
    while start != stop:
        yield start
        start += step
    else:
        raise StopIteration


for n in irange(1, 10):
    """for循环只要遇到StopIteration就会停止"""
    print(n)

ret = irange(1, 20)
print(ret)  # 返回一个生成器，相当于只在内存中创建了一个值
print(list(ret))  # 如果想要得到全部的值，变成列表就可以
```

```python
/Library/Frameworks/Python.framework/Versions/3.5/bin/python3.5 /Users/ansheng/MyPythonCode/hello.py
1
2
3
4
5
6
7
8
9
<generator object irange at 0x1021df7d8>
[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]

Process finished with exit code 0
```