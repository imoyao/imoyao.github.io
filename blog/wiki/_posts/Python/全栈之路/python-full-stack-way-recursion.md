---
title: Python 全栈之路系列之递归
toc: true
date: 2020-05-23 18:21:46
tags:
- 编码
- 递归
---

所谓递归其实就是函数本身调用函数，直到满足指定条件之后一层层退出函数， 例如

从前有座山，山里有座庙，庙里有个老和尚，正在给小和尚讲故事呢！故事是什么呢？“从前有座山，山里有座庙，庙里有个老和尚，正在给小和尚讲故事呢！故事是什么呢？‘从前有座山，山里有座庙，庙里有个老和尚，正在给小和尚讲故事呢！故事是什么呢？……’”

- 利用函数编写一个斐波那契数列

`0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233，377，610，987，1597，2584，4181，6765，10946，17711，28657，46368`

> 斐波那契数列就是前面给两个数相加得到后面一个数，依次往后

代码如下

```python
#!/usr/bin/env python
# _*_ coding: utf-8 _*_

def Counter(n1, n2):
    if n1 > 10000:  # 当要计算的值大于10000就退出
        return
    print("Counter：", n1)  # 输出当前计算到那个值了
    n3 = n1 + n2  # 第一个值加上第一个值等于第三个值
    Counter(n2, n3)  # 调用计数器函数，此时第一个值是调用函数传过来的最后一个值，而第二个值是计算出来的第三个值


Counter(0, 1)  # 调用计数器函数
```

输出结果

```python
/usr/bin/python3.5 /home/ansheng/Documents/PycharmProjects/blogcodes/斐波那契.py
Counter： 0
Counter： 1
Counter： 1
Counter： 2
Counter： 3
Counter： 5
Counter： 8
Counter： 13
Counter： 21
Counter： 34
Counter： 55
Counter： 89
Counter： 144
Counter： 233
Counter： 377
Counter： 610
Counter： 987
Counter： 1597
Counter： 2584
Counter： 4181
Counter： 6765

Process finished with exit code 0
```

- 利用递归获取斐波那契数列中的第 10 个数，并将该值返回给调用者

代码：

```python
#!/usr/bin/env python
# _*_ coding: utf-8 _*_

def Counter(Index, Start, End):
    print("第%d次计算，第一个数字是%d，第二个数字是%d" % (Index, Start, End))
    if Index == 10:  # 如果要计算的值是10就退出
        return Start
    N = Start + End  # N等于第一个数加上第二个数
    Number = Counter(Index + 1, End, N)  # 继续调用计数器函数，End相当与传给函数的第一个数，N是传给函数的第二个数
    return Number


result = Counter(1, 0, 1)
print("得出的数字是：", result)
```

输出结果

```python
/usr/bin/python3.5 /home/ansheng/Documents/PycharmProjects/blogcodes/递归.py
第1次计算，第一个数字是0，第二个数字是1
第2次计算，第一个数字是1，第二个数字是1
第3次计算，第一个数字是1，第二个数字是2
第4次计算，第一个数字是2，第二个数字是3
第5次计算，第一个数字是3，第二个数字是5
第6次计算，第一个数字是5，第二个数字是8
第7次计算，第一个数字是8，第二个数字是13
第8次计算，第一个数字是13，第二个数字是21
第9次计算，第一个数字是21，第二个数字是34
第10次计算，第一个数字是34，第二个数字是55
得出的数字是： 34

Process finished with exit code 0
```