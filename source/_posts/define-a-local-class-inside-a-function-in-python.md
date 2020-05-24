---
title: 在 Python 中定义本地类是什么操作？
date: 2019-12-10 11:39:22
tags:
- Python
---
## 缘起

今天在看 ceph（mgr-dashboard）源码的时候看到下面的代码，产生了一点疑惑，这里简单整理一下。代码详见`src/pybind/mgr/dashboard/module.py:502`
```python
import cherrypy

class StandbyModule(MgrStandbyModule, CherryPyConfig):
    def __init__(self, *args, **kwargs):
        super(StandbyModule, self).__init__(*args, **kwargs)
        pass

    def serve(self):        # here
        pass

        class Root(object):
            @cherrypy.expose
            def index(self):
                pass

        cherrypy.tree.mount(Root(), "{}/".format(self.url_prefix), {})
        pass

    def shutdown(self):
        pass
```
## 理解
```python

def some_funky_data_structure(bar_data=None):
    class FunkyClass:

        def __init__(self):
            self.data = 'This is dunder init innner of FunkyClass'

        def get_funky(self, inner_data):
            print('The inner_data of inner get_funky() is {inner_data}, outer of inner data is {bar_data}.'.format(
                inner_data=inner_data, bar_data=bar_data))

    return FunkyClass
    
    
if __name__ == '__main__':
    foo = some_funky_data_structure('foo')
    foo_bar = some_funky_data_structure('foo_bar')
    print(foo().get_funky('baz'), foo_bar().get_funky('baz'))

    f1 = some_funky_data_structure()()
    f2 = some_funky_data_structure()()
    # 类型看起来相同但实际不同
    print(type(f1))
    print(type(f2))
    print(type(f1) is type(f2))     # False
    print(isinstance(f1, type(f2)))     # False
```
初次遇到这种代码看起来会有点奇怪或者感到困惑。但是同时由于封装的实现，可以防止外部访问函数的实现。那么这究竟是一个好的实践还是糟糕的实现呢？
1. 无法进行类型检查，因为内部类对外部是隐藏的，你无法使用`isinstance(foo,FunkyClass)`语句检查类型，多次实例化之后两者类型虽然看起来相同，但实际不是一个类型，甚至在 Python2 中打印到的类型是`<type 'instance'>`
2. 实现`map()`函数的静态调用
```python
# 注：此处不知是我理解有误还是说的就是这个意思，这种写法还是尽量避免吧

class _FunkyClass:

    def __init__(self, *args, **kwargs):
        print(f'args is {args},kwargs is {kwargs}.')
        self.data = 'This is dunder init innner of FunkyClass'
        self.bar_data = kwargs.get('bar_data', None)

    def get_funky(self, inner_data):
        print('The inner_data of inner get_funky() is {inner_data}, outer of inner data is {bar_data}.'.format(
            inner_data=inner_data, bar_data=self.bar_data))
            
if __name__ == '__main__':
    # see also: https://stackoverflow.com/questions/16874244/python-map-and-arguments-unpacking            
    for i in map(lambda x: _FunkyClass.get_funky(x[1], x[0]),
                 [('foo', _FunkyClass(bar_data='foo_bar')), ('bar', _FunkyClass(bar_data='bar_foo'))]):
        pass
```

参阅[Python best practice: class definition inside function?](https://stackoverflow.com/questions/34034644/python-best-practice-class-definition-inside-function)

## 总结

- 优点：
    1. 使类局部性。该类不会以你不期望的方式在函数外部被执行使用；
    2. 性能。查找局部变量要比查找全局变量快得多。如果您创建了大量实例，这可能会提高使用全局类的性能。然而，通过默认参数/局部变量来抵消这种优势是**及其**容易的。
- 缺点：
    1. 可读性。除非类非常容易，否则函数将不可避免地增长变得非常长，会使代码丧失可读性。此外由于`Python`中使用缩进，如果你的外部函数某处嵌套循环，则会影响可读性；
    2. 性能。类在每一次函数调用时都将被重新编译。虽然不会很耗时，但还是会花一点时间。如果你原来的`function`很快，那么这个（引入本地类）成本可能有点高。

## 建议

定义全局的类，如果你想定义成私有的，使用下划线即可，例如`_MyClass()`，因为我们知道这是`Python`中约定好的。
```python
# python3

class _FunkyClass:

    def __init__(self, *args, **kwargs):
        print(f'args is {args},kwargs is {kwargs}.')
        self.data = 'This is dunder init innner of FunkyClass'
        self.bar_data = kwargs.get('bar_data', None)

    def get_funky(self, inner_data):
        print('The inner_data of inner get_funky() is {inner_data}, outer of inner data is {bar_data}.'.format(
            inner_data=inner_data, bar_data=self.bar_data))


def normal_some_funky_data_structure(bar_data=None):
    pass
    return _FunkyClass(bar_data=bar_data)


def call_normal_some_funky_data_structure():
    pass
    return _FunkyClass
    
    
if __name__ == '__main__':  
    foo = normal_some_funky_data_structure('foo')
    foo_bar = normal_some_funky_data_structure('foo_bar')
    foo.get_funky('baz')
    foo_bar.get_funky('baz')
    print(isinstance(foo, _FunkyClass))     # True

    c_foo = call_normal_some_funky_data_structure()(bar_data='foo')
    c_fb = call_normal_some_funky_data_structure()(bar_data='foo_bar')
    c_foo.get_funky('baz')
    c_fb.get_funky('baz')
    print(isinstance(c_foo, _FunkyClass))   # True
```

我们使用下面的代码做一个简单的性能测试：
```python
# python3

import timeit


class _Out:
    def test(self, _try_time=10):
        for i in range(_try_time):
            pass


def function_out(n, try_time):
    for _ in range(n):
        _Out().test(try_time)


def function_in(n, try_time):
    class Inner:
        def test(self, _try_time=10):
            for i in range(_try_time):
                pass

    for _ in range(n):
        Inner().test(try_time)


def function_mixed(n, try_time, cls=_Out):
    for _ in range(n):
        cls().test(try_time)


if __name__ == '__main__':
    m, test_try_time = 1, 10
    '''
    time of function_out is 0.0009663160890340805.
    time of function_in is 0.009836168959736824.    # 相差一个数量级
    time of function_mixed is 0.0009927581995725632.
    '''
    # m, test_try_time = 1000, 10
    '''
    time of function_out is 0.7052748203277588.
    time of function_in is 0.7609770204871893.
    time of function_mixed is 0.7371664671227336.
    '''
    # m, test_try_time = 10000, 10
    '''
    time of function_out is 6.49063076544553.
    time of function_in is 6.0502378745004535.
    time of function_mixed is 6.159397796727717.
    '''
    t1 = timeit.timeit(stmt="function_out(m, test_try_time)",
                       setup="from __main__ import function_out, m,test_try_time", number=1000)
    t2 = timeit.timeit(stmt="function_in(m, test_try_time)", setup="from __main__ import function_in, m,test_try_time",
                       number=1000)
    t3 = timeit.timeit(stmt="function_mixed(m, test_try_time)",
                       setup="from __main__ import function_mixed, m,test_try_time", number=1000)

    print(f'time of function_out is {t1}.')
    print(f'time of function_in is {t2}.')
    print(f'time of function_mixed is {t3}.')
```

## 参考链接
- [Is it a bad idea to define a local class inside a function in python?](https://stackoverflow.com/questions/22497985/is-it-a-bad-idea-to-define-a-local-class-inside-a-function-in-python)
- [Inner Classes in Python](https://www.datacamp.com/community/tutorials/inner-classes-python)
### TODO
- [Creating a class within a function and access a function defined in the containing function's scope](https://stackoverflow.com/questions/4296677/creating-a-class-within-a-function-and-access-a-function-defined-in-the-containi)
- [How references to variables are resolved in Python](https://stackoverflow.com/questions/20246523/how-references-to-variables-are-resolved-in-python)
