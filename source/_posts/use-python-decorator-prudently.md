---
title: "三思而后行：谨慎使用你的装饰器"
date: 2020-09-03 21:27:50
tags:
- TODO
- Python
- 装饰器
- decorator
categories:
- Python
subtitle: 使用新的语法特性时，请注意不要过度使用。
cover: /images/rzdf/Snipaste_2020-09-07_00-03-21.png
---
在学会使用装饰器之后，我们可能时不时地在心理暗示下使用它，下面是我个人总结的一些代码实践中遇到的问题，主要参考 [这一篇](https://stackoverflow.com/questions/739654/how-to-make-a-chain-of-function-decorators/1594484#1594484) 中关于装饰器链式调用中讨论的问题。

> **最佳实践**
- Decorators were introduced in Python 2.4, so be sure your code will be run on >= 2.4.
- Decorators slow down the function call. Keep that in mind.
- You cannot un-decorate a function. (There are hacks to create decorators that can be removed, but nobody uses them.) So once a function is decorated, it’s decorated for all the code.
- Decorators wrap functions, which can make them hard to debug. (This gets better from Python >= 2.5; see below.)

{% note info %}
以下演示基于 Python3.7 讨论，测试代码时请检查你的 Python 版本。
{% endnote %}

## 请神容易送神难
装饰器一旦被使用，就很难调用没有装饰器的原函数。
### 改善建议
1. 在[9.3 解除一个装饰器 | Python-cookbook](https://python3-cookbook.readthedocs.io/zh_CN/latest/c09/p03_unwrapping_decorator.html)，源码（[dabeaz/python-cookbook](https://github.com/dabeaz/python-cookbook/blob/master/src/9/unwrapping_a_decorator/example.py)）中，作者提到一个方法：
```python
from functools import wraps


def deco_it(func):
    """
    定义装饰器
    :param func:
    :return:
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        print('----inner of wrapper before func----')
        ret = func(*args, **kwargs)
        print('----inner of wrapper after func--')
        return ret

    return wrapper


@deco_it
def foo():
    print('Hello,World!')


if __name__ == '__main__':
    foo()       # 被装饰的调用
    foo.__wrapped__()       # 解除装饰的调用
```
```plain
----inner of wrapper before func----
Hello,World!
----inner of wrapper after func--
# 原函数
Hello,World!
```
需要注意的是，这种方法有两个缺陷：
 1. 装饰器函数内部必须被`functools.wraps`装饰或者直接设置了`__wrapped__`属性；
 2. 多个装饰器时，返回结果是不可预知的；请看下例：
```python

def another_deco_it(func):
    """
    定义另一个装饰器
    :param func:
    :return:
    """
    print('This is another deco.')

    @wraps(func)
    def wrapper(*args, **kwargs):
        ret = func(*args, **kwargs)
        return ret

    return wrapper


@another_deco_it
@deco_it
def foo():
    print('Hello,World!')


if __name__ == '__main__':
    foo()
    print('origin func under below.')
    foo.__wrapped__()
```
返回结果：
```plain
This is another deco.
----inner of wrapper before func----
Hello,World!
----inner of wrapper after func--
origin func under below.
# 原函数定义（实际上，此时并没有解除掉@deco_it装饰器）
----inner of wrapper before func----
Hello,World!
----inner of wrapper after func--
```
甚至，如果我们调换装饰器的位置
```python
@deco_it
@another_deco_it
def foo():
    print('Hello,World!')
```
返回的结果又是符合我们预期的😯：
```plain
This is another deco.
----inner of wrapper before func----
Hello,World!
----inner of wrapper after func--
origin func under below.
# 原函数定义
Hello,World!
```
2. 鉴于上面说到的缺陷，我们尝试使用 [这里](https://wiki.python.org/moin/PythonDecoratorLibrary#Enable.2FDisable_Decorators) 提到的方式继续改善；
我们说`Python中一切都是对象`，所以可以将我们的装饰器是否使用通过 flag 传递给调用函数名：
```python


def enable_deco(func):
    """
    使能装饰器
    :param func:
    :return:
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        print('----inner of wrapper before func----')
        ret = func(*args, **kwargs)
        print('----inner of wrapper after func--')
        return ret

    return wrapper


def disable_deco(func):
    """
    禁用装饰器
    :param func:
    :return:
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        ret = func(*args, **kwargs)
        return ret

    return wrapper


GLOBAL_ENABLE_FLAG = True
depend_with_flag = enable_deco if GLOBAL_ENABLE_FLAG else disable_deco


@depend_with_flag
def foo():
    print('Hello,World!')

```
我们通过`GLOBAL_ENABLE_FLAG`分别定义的`bool`值可以将装饰器启用或者禁用。这个方式也适用于多个装饰器的时候，只不过我们需要定义更多的 bool 变量来控制而已。

## 凡有导入，必留痕迹
调用被装饰函数会导致装饰器函数外部逻辑的执行。示例代码如下：
我们在第一个模块中编写一个装饰器`deco`：
```python
# deco_module
import time
from functools import wraps


def deco(func):
    print('out of real wrapper.')

    @wraps(func)
    def wrapper(*args, **kwargs):
        print('-----inner of wrapper.----')
        time.sleep(5)
        ret = func(*args, **kwargs)
        time.sleep(3)
        return ret

    return wrapper


@deco
def do_func():
    print('hello world')
    return 0

```
在第二个模块中，我们导入`deco_module`：
```python
# foo
from deco_module import do_func


def invoke_deco_func():
    do_func()
    do_other()
    return 0


def do_other():
    pass


def do_foo():
    pass


if __name__ == '__main__':
    do_foo()

```
此时，不管我们是否真正调用被装饰的函数`do_func`，装饰器`deco`中`wrapper`外面的函数都会被调用①。假如它是一个耗时的操作呢？😕
第三个模块中，我们导入`foo`模块：
```plain
# main.py
from foo import do_foo


def main():
    do_foo()


if __name__ == '__main__':
    main()
```
同样地，只要我们从`foo`中进行导入，不管我们是否在`main`中调用`invoke_deco_func`，上面提到的消耗①都会被执行。😣
{% note primary no-icon %}
有同学会举手发言了：嗳，你这装饰器写的不对啊，我所看到装饰器的逻辑都是写在`wrapper`函数里面的呀！陈独秀同学请坐，你在第一层，我在第二层。
有时候，我们为了装饰器更加灵活，既需要它可以不传参数，又需要它可以传递参数，这个时候就需要使用偏函数的定义。
请看下面的链接：
 1. [Python decorator best practice, using a class vs a function - Stack Overflow](https://stackoverflow.com/questions/10294014/python-decorator-best-practice-using-a-class-vs-a-function)
 2. [9.6 定义带可选参数的装饰器 | Python-cookbook](https://github.com/dabeaz/python-cookbook/blob/master/src/9/defining_a_decorator_that_takes_an_optional_argument/example.py)
 3. [9.7 利用装饰器强制函数上的类型检查 | Python-cookbook](https://github.com/dabeaz/python-cookbook/blob/master/src/9/enforcing_type_checking_on_a_function_using_a_decorator/example.py)

当然，我们都在期许第五层的老师能给我们指导释疑。
{% endnote %}

### 改善建议
1. 装饰器`wrapper`外面不要写函数；如果非要写，应该是很小的操作。一个函数一旦被装饰，它就不是`出走半生归来仍是少年`的模样了。所以，尽量不要把这种含有`wrapper`外做逻辑处理的装饰器到处导入。
2. 写进类里面；
 如果你类装饰器写得比较少，可以参考下面的链接：
 1. [9.8 将装饰器定义为类的一部分 — python3-cookbook 3.0.0 文档](https://python3-cookbook.readthedocs.io/zh_CN/latest/c09/p08_define_decorators_as_part_of_class.html)；参考 [源码](https://github.com/dabeaz/python-cookbook/tree/master/src/9/defining_decorators_as_part_of_a_class)
 2. [9.9 将装饰器定义为类](https://python3-cookbook.readthedocs.io/zh_CN/latest/c09/p09_define_decorators_as_classes.html) ；参考 [源码](https://github.com/dabeaz/python-cookbook/tree/master/src/9/defining_decorators_as_classes)
```python
# deco_module
class Deco:
    def __init__(self, func):
        self.func = func

    def __call__(self, *args, **kwargs):
        print('out of real wrapper.')

        ret = self.func(*args, **kwargs)
        return ret


@Deco
def do_func():
    print('hello world')
    return 0
```
此时我们在装饰器定义模块中执行返回:
```plain
out of real wrapper.
hello world

```
在不包含装饰器的模块中导入上述模块:
```python
from deco_module import do_bar


def do_foo():
    pass


if __name__ == '__main__':
    do_foo()
```
此时，如果不调用被装饰函数，则可以避免其被连带导入；当然，如果你导入它，那肯定还是会执行。🤓

## 执行顺序和调用顺序不一样

调用时从上到下，逻辑执行时从下到上。参考此文：[Python decorator order](https://gist.github.com/kirsle/bf24622fc5f255256c6e)
```python
import sys
from functools import wraps


def check_has_set(func):
    """
    是否进行了模块配置
    :param func:
    :return:
    """
    print(f'out of func: {sys._getframe().f_code.co_name}')

    @wraps(func)
    def wrapper(*args, **kwargs):
        print(f'inner of func check_has_set.')
        ret = func(*args, **kwargs)
        return ret

    return wrapper


def check_has_enable(func):
    """
    模块是否启用
    :param func:
    :return:
    """
    print(f'out of func: {sys._getframe().f_code.co_name}')

    @wraps(func)
    def wrapper(*args, **kwargs):
        print(f'inner of func check_has_enable.')
        ret = func(*args, **kwargs)
        return ret

    return wrapper


def check_has_execute(func):
    """
    模块是否执行，这是一个耗时操作，并且需要一定的条件才可以执行
    :param func:
    :return:
    """
    time.sleep(5)
    print(f'out of func: {sys._getframe().f_code.co_name}')

    @wraps(func)
    def wrapper(*args, **kwargs):
        print(f'inner of func check_has_execute.')
        ret = func(*args, **kwargs)
        return ret

    return wrapper


@check_has_execute
@check_has_enable
@check_has_set
def foo():
    print('I can do it only when has_set and has_enable and before has_execute')


def bar():
    pass


if __name__ == '__main__':
    # foo()
    bar()
```
我们执行上述函数，得到返回结果：
```plain
out of func: check_has_set
out of func: check_has_enable
out of func: check_has_execute
```
这个符合我们的预期，因为装饰器类似于这种写法：`check_has_execute(check_has_enable(check_has_set(foo)))`。

接下来，我们真正调用被装饰函数，即放开注释，将无关的调用`bar()`注释：
```python
out of func: check_has_set
out of func: check_has_enable
out of func: check_has_execute
inner of func check_has_execute.
inner of func check_has_enable.
inner of func check_has_set.
```
注意看返回结果中的前三行和后三行。此时先去执行了`check_has_execute`中的操作，而后才会执行`check_has_enable`和`check_has_set`！此时我们做的提前返回的限制就无效了。
### 改善建议
如果只是调用顺序导致的问题，底层函数不会有特别耗时的操作，我们可以按照条件的先后去装饰`foo()`函数，让其按照预定的顺序检查:
即`if check_has_set` >> `if check_has_enable` >> `if not check_has_execute`，只有条件都满足采取真正执行。
```plain
@check_has_set
@check_has_enable
@check_has_execute
def foo():
    pass
```
局限性：`check_has_execute`中长耗时会执行，此时会拖慢你的程序！如此处[Python decorator best practice, using a class vs a function - Stack Overflow](https://stackoverflow.com/questions/10294014/python-decorator-best-practice-using-a-class-vs-a-function)2018 update 章节处所示的写法。

## 总结
To be continue.

## 推荐阅读
[PythonDecorators - Python Wiki](https://wiki.python.org/moin/PythonDecorators)
[Python Decorators: A Step-By-Step Introduction – dbader.org](https://dbader.org/blog/python-decorators)
[Primer on Python Decorators – Real Python](https://realpython.com/primer-on-python-decorators/)
[Python decorators vs inheritance - Anselmos Blog](http://witkowskibartosz.com/blog/python_decorators_vs_inheritance.html)
[python - How to make a chain of function decorators? - Stack Overflow](https://stackoverflow.com/questions/739654/how-to-make-a-chain-of-function-decorators)
[第九章：元编程 — python3-cookbook 3.0.0 文档](https://python3-cookbook.readthedocs.io/zh_CN/latest/chapters/p09_meta_programming.html)