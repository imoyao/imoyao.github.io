---
title: "三思而后行：谨慎使用你的装饰器"
date: 2020-09-03 21:27:50
tags:
- Python
- 装饰器
- decorator
subtitle: 使用新的语法特性时，请注意不要过度使用。
---
在学会使用装饰器之后，我们可能时不时地心理暗示使用它，下面我总结一些代码使用中需要注意的问题，主要参考 [这一篇](https://stackoverflow.com/questions/739654/how-to-make-a-chain-of-function-decorators/1594484#1594484) 中关于装饰器链式调用中讨论的问题。

> **最佳实践**
- Decorators were introduced in Python 2.4, so be sure your code will be run on >= 2.4.
- Decorators slow down the function call. Keep that in mind.
- You cannot un-decorate a function. (There are hacks to create decorators that can be removed, but nobody uses them.) So once a function is decorated, it’s decorated for all the code.
- Decorators wrap functions, which can make them hard to debug. (This gets better from Python >= 2.5; see below.)

## 请神容易送神难
装饰器一旦用上了，就很难调用没有装饰器的原函数。
### 改善建议
[9.3 解除一个装饰器 — python3-cookbook 3.0.0 文档](https://python3-cookbook.readthedocs.io/zh_CN/latest/c09/p03_unwrapping_decorator.html)
```
>>> @somedecorator
>>> def add(x, y):
...     return x + y
...
>>> orig_add = add.__wrapped__
>>> orig_add(3, 4)
7
>>>
```
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
此时，不管我们是否真正调用被装饰的函数`do_func`，装饰器`deco`中`wrapper`外面的函数都会被调用①。加入它是一个耗时的操作呢？😕
第三个模块中，我们导入`foo`模块：
```
# main.py
from foo import do_foo


def main():
    do_foo()


if __name__ == '__main__':
    main()
```
此时，只要我们从`foo`中进行导入，不管我们是否在`main`中调用`invoke_deco_func`，上面提到的消耗①都会被执行。😣

### 改善建议
1. 装饰器`wrapper`外面不要写函数；如果非要写，应该是很小的操作。一个函数一旦被装饰，它就不是`出走半生归来仍是少年`的模样了。所以，尽量不要把这种含有`wrapper`外做逻辑处理的装饰器到处导入。

#### TODO
验证：被装饰函数不要暴露到模块外面（_foo()）。外面包一层，然后从其他模块导入外面的函数。

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
注意看返回结果中的前三行和后三行。此时先去执行了`check_has_execute`中的操作，而后才会执行`check_has_enable`和`check_has_set`！此时我们做的提前返回的限制无效了。
### 改善建议
如果只是调用顺序导致的问题，底层函数不会有特别耗时的操作，我们可以按照条件的先后去装饰`foo()`函数，让其按照预定的顺序检查:
即`if check_has_set` >> `if check_has_enable` >> `if not check_has_execute`，只有条件都满足采取真正执行。
```
@check_has_set
@check_has_enable
@check_has_execute
def foo():
    pass
```
局限性:`check_has_execute`中长耗时会执行，此时会拖慢你的程序！如此处[Python decorator best practice, using a class vs a function - Stack Overflow](https://stackoverflow.com/questions/10294014/python-decorator-best-practice-using-a-class-vs-a-function)2018 update处
