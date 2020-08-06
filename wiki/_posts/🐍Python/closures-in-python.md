---
title: 关于 Python 闭包理解
toc: true
date: 2020-08-06 12:27:56
tags: 
- Python
- 闭包
---
## 前言

闭包这个概念在 JavaScript 中讨论和使用得比较多，不过在 Python 中却不是那么显而易见，之所以说“不是那么”，是因为即使用到了，也没用注意到而已，比如定义一个 Decorator 时，就已经用到闭包了。网上对闭包的各种解释，感觉非常晦涩，在这里谈谈我的浅显认识：要形成闭包，首先得有一个嵌套的函数，即函数中定义了另一个函数，闭包则是一个集合，它包括了外部函数的局部变量，这些局部变量在外部函数返回后也继续存在，并能被内部函数引用。

## 代码示例

这是个经常使用到的例子，定义一个函数 `generate_power_func`，它返回另一个函数，现在闭包形成的条件已经达到。
```python
def generate_power_func(n):
    print("id(n): %X" % id(n))
    def nth_power(x):
        return x**n
    print("id(nth_power): %X" % id(nth_power))
    return nth_power
```

对于内部函数 `nth_power`，它能引用到外部函数的局部变量 `n`，而且即使 `generate_power_func` 已经返回。把这种现象就称为闭包。具体使用一下。
```plain
>>> raised_to_4 = generate_power_func(4)
id(n): 246F770
id(nth_power): 2C090C8
>>> repr(raised_to_4)
'<function nth_power at 0x2c090c8>'
```
从结果可以看出，当 `generate_power_func(4)` 执行后, 创建和返回了 `nth_power` 这个函数对象，内存地址是 0x2C090C8,并且发现 `raised_to_4` 和它的内存地址相同，即 `raised_to_4` 只是这个函数对象的一个引用。先在全局命名空间中删除 `generate_power_func`，再试试会出现什么结果。
```plain
>>> del generate_power_func
>>> raised_to_4(2)
16
```
啊哈，居然没出现错误， `nth_power` 是怎么知道 `n` 的值是 4，而且现在 `generate_power_func` 甚至都不在这个命名空间了。对，这就是闭包的作用，外部函数的局部变量可以被内部函数引用，即使外部函数已经返回了。

## __closure__ 属性和 cell 对象

现在知道闭包是怎么一回事了，那就到看看闭包到底是怎么回事的时候了。Python 中函数也是对象，所以函数也有很多属性，和闭包相关的就是 `__closure__` 属性。`__closure__` 属性定义的是一个包含 cell 对象的元组，其中元组中的每一个 cell 对象用来保存作用域中变量的值。
```plain
>>> raised_to_4.__closure__
(<cell at 0x2bf4ec0: int object at 0x246f770>,)
>>> type(raised_to_4.__closure__[0])
<type 'cell'>
>>> raised_to_4.__closure__[0].cell_contents
4
```
就如刚才所说，在 `raised_to_4` 的 `__closure__` 属性中有外部函数变量 `n` 的引用，通过内存地址可以发现，引用的都是同一个 `n`。如果没用形成闭包，则 `__closure__` 属性为 `None`。对于 Python 具体是如何实现闭包的，可以查看 [Python 闭包详解](http://www.cnblogs.com/ChrisChen3121/p/3208119.html)，它通过分析 Python 字节码来讲述闭包的实现。

## 总结
闭包特性有着非常多的作用，不过都是需要时才会不经意的用上，不要像使用设计模式一样去硬套这些法则。这篇文章按照自己的理解翻译至 [Python Closures Explained](http://www.shutupandship.com/2012/01/python-closures-explained.html)，可能和原文有些不同之处，如有疑惑，请查看原文。附上一些参考资料。

## 参考链接
- [浅显理解 Python 闭包 - I'm SErHo](https://serholiu.com/python-closures)
- [闭包的概念、形式与应用](http://www.ibm.com/developerworks/cn/linux/l-cn-closure/): 可以从其中了解闭包的应用
- [Python 闭包详解](http://www.cnblogs.com/ChrisChen3121/p/3208119.html)：从字节码出发了解 Python 闭包的实现机制
- [理解 Javascript 的闭包](http://coolshell.cn/articles/6731.html): 从 Javascript 的闭包中了解一些闭包特性，可以和 Python 作下对比
- [Why aren't python nested functions called closures? - Stack Overflow](https://stackoverflow.com/questions/4020419/why-arent-python-nested-functions-called-closures)
