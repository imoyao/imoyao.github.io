---
title: 装饰器
date: 2020-06-08 21:41:49
tags:
- 装饰器
- 设计模式
categories:
---
## 作用
> Adds behaviour to object without affecting its class.
Decorator模式用于动态地向对象添加新特性，而不更改其原来的代码实现。它与继承不同，新特性只绑定到特定对象，而不会添加到整个子类。

## 优缺点
### 优点
1. 你无需创建新子类即可扩展对象的行为。
2. 你可以在运行时添加或删除对象的功能。
3. 你可以用多个装饰封装对象来组合几种行为。
4. 单一职责原则。 你可以将实现了许多不同行为的一个大类拆分为多个较小的类。
### 缺点
1. 在封装器栈中删除特定封装器比较困难。
2. 实现行为不受装饰栈顺序影响的装饰比较困难。
3. 各层的初始化配置代码看上去可能会很糟糕。

## 代码

### 入门
- 函数运行时间记录
```python
import time

def time_it(func):
    def wrap_func(*args, **kwargs):
        start_time = time.time()
        ret_result = func(*args, **kwargs)
        end_time = time.time()
        print('The function **{0}** takes {1} time.'.format(func.__name__, end_time - start_time))
        return ret_result

    return wrap_func
    
@time_it
def foo():
    pass
```

### 进阶

- 装饰器带参数
```
def deco_with_args(name):
    def decorator(func):
        def wrapper(*args,**kwargs):
            if name=='foo':
                print('hello')
            else:
                print('Bonjour!')
            ret = func(*args,**kwargs)
            return ret
        return wrapper
    return decorator

@deco_with_args('foo')
def foo():
    print('this is foo')

@deco_with_args('bar')
def bar():
    print('this is bar')


foo()
print('---------------')
bar()
```
#### 类装饰器
- 不带参数
基于类装饰器的实现，必须实现 `__call__` 和 `__init__`两个内置函数。 其中`__init__` 用于接收被装饰函数， `__call__` 实现装饰逻辑。

