---
title: 关于 Python 中的下划线用法的记录
date: 2018-04-28 17:23:18
tags:
- Python
categories:
- Python
thumbnail:
---
## Py乙己

孔乙己自己知道不能和架构师谈天，便只好向实习生说话。

有一回对我说道，“你写过`Python`么？”我略略点一点头。

他说，“写过代码，……我便考你一考。`Python`中的下划线，怎样用的？”

我想，搬砖一样的人，也配考我么？便回过脸去，不再理会。

孔乙己等了许久，很恳切的说道，“不能写罢？……我教给你，记着！这些用法应该记着。将来做面试官的时候要用。”

我暗想我和面试官的等级还很远呢，而且我们面试官也从不将这些问题拿来考应聘者；又好笑，又不耐烦，懒懒的答他道，“谁要你教，不就是命名变量，增加代码的可读性吗？”

孔乙己显出极高兴的样子，将两个指头的长指甲敲着键盘，点头说，“对呀对呀！……下划线有四种写法，你知道么？”

我愈不耐烦了，努着嘴走远。孔乙己刚用纸巾擦了擦键盘上的咖啡渍，想在`IDE`里写代码，见我毫不热心，便又叹一口气，显出极惋惜的样子。
<!--more-->

## 正文

- 在交互式解释器中获取上一个语句执行的结果；

```python
>>> 1+1
2
>>> _
2
>>> _ * 5
10
```

- 用来在函数、模块、包、变量名中分隔单词，增加可读性；

```python
var_foo_bar = 'hello,world!'
```

- 内部使用的变量、属性、方法、函数、类或模块，（约定）又称为内部实现；

```python
# 假定存在foo.py中定义变量：
_var = 9527
# 在bar.py中导入
from foo import *   # 不会导入以下划线开头的对象
print(_var)
# 返回：
NameError: name '_var' is not defined
当然也可以强制导入（不推荐）
from foo import _var        # Access to a protected member _var of a module
print(_var)
# 返回：
9527
```

- 避免与 `Python` 保留的关键字冲突（约定）；

```python
Tkinter.Toplevel(master, class_='ClassName')        # 注意class为Python內建名称
```

- 在类内的私有变量（`private`），类外部无法直接使用原名称访问，需要通过`instance._ClassName__var`的形式访问（`name mangling`）；

```python
class Person(object):

    __say_hello = 'Hello,world'

    def __init__(self, name, age):
        self.name = name
        self.age = age

    def get_name(self):
        return self.name

    def get_age(self):
        return self.age


if __name__ == '__main__':
    pi = Person('Peter', 26)
    # print(pi.__say_hello)       # AttributeError: 'Person' object has no attribute '__say_hello'
    print(pi._Person__say_hello)
    print(pi.get_age())
```

我们可以使用`dir(pi)`看一下对象中的中的属性和方法：

```shell
['_Person__say_hello', '__class__', '__delattr__', '__dict__', '__doc__', '__format__', '__getattribute__', '__hash__', '__init__', '__module__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__', '__weakref__', 'age', 'get_age', 'get_name', 'name']
```

这里 `Python` 解释器触发名称修饰，它这样做是为了防止变量在子类中被重写。

```python
# 新建一个集成Person的AI类

class AI(Person):

    __say_hello = 'ALL in AI'

    pass


if __name__ == '__main__':

    ai_attr = ['ALL in AI']*3
    ai = AI(*ai_attr)
    print(dir(ai))
```

我们可以看到继承关系：

```Python
# 返回
['_AI__say_hello', '_Person__gender', '_Person__say_hello', '__class__', '__delattr__', '__dict__', '__doc__', '__format__', '__getattribute__', '__hash__', '__init__', '__module__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__', '__weakref__', '_age', 'name']
```

这点在 `《Python Cookbook》- 8.5 在类中封装属性名` 中对于单下划线和双下划线的使用场景也有提及和解释：

> 大多数而言，你应该让你的非公共名称以单下划线开头。但是，如果你清楚你的代码会涉及到子类，并且有些内部属性应该在子类中隐藏起来，那么才考虑使用双下划线方案。

- 在类内的保护变量（这一条存疑）；

```python
_var_
```

- `Python` 内置的“魔法”方法或属性，你也可以自己定义，但强烈 **不推荐**。比如：

```python
__init__, __file__, __main__
```

- 作为内部使用的一次性变量；

```python
通常在循环里使用,比如：
foo_list = [_ for _ in range(10)]
或是用作占位，不实际使用的变量,比如：
for _, a in [(1,2),(3,4)]:
    print a
```

- `i18n` 里作为 `gettext()` 的缩写；

```python
_()
```

- 用来分隔数值以增加可读性（`Python 3.6` 新增）；

```python
>>> num = 1_000_000 
>>> num
1000000
1_000_000
```
### 参考来源

1. [PEP 8 -- Style Guide for Python Code](http://pep8.org/#descriptive-naming-styles)

2. [Python basic cheatsheet](https://www.pythonsheets.com/notes/python-basic.html#python-naming-rule)

3. [The Meaning of Underscores in Python – dbader.org](https://dbader.org/blog/meaning-of-underscores-in-python)

4. [Python中的下划线_有多少个意思？- 知乎](https://www.zhihu.com/question/268940585/answer/344852737)

## 派森多一点

`Python`中的`dunder`

参见[这里](https://nedbatchelder.com/blog/200605/dunder.html)

> 关于`Python` 编程的一个尴尬的事情是：有很多种双下划线。 例如，语法糖下面的标准方法名称具有 `__getattr__` 这样的名称，构造函数是 `__init__` ，内置运算符可以用 `__add__` 重载，等等。 在 `Django` 框架中（至少在他们整合了 `magic-removal` 分支之前），对象关系映射器使用了名为 `user__id__exact` 的关键字参数。

> 双下划线的问题是很难向别人描述。 你怎么读 `__init__` ？ “下划线下划线 `init` 下划线下划线”？ “双下划线 `init` 双下划线”？ 简单的 “`init`” 似乎漏掉了一些重要的东西。

> 我有一个解决方案：双下划线应该发音为 “`dunder`” 。 所以 `__init__` 念成“`dunder init dunder`”，或者也可以简读为 “`dunder init`” 。

> 现在我期待某个人定义一下 “`dunderhead`” 是什么意思，haha……

