---
title: Python 中动态调用函数或类的方法
date: 2020-10-15 21:09:27
tags:
- Python
- 编程
- magic
- exec
categories:
- 🐍PyTricks
cover: /images/esther-jiao-FKZwWLWgGyM-unsplash.jpg
subtitle: "最佳实践：import importlib "
---
## 使用`exec()`方法
- 示例代码
```python
# module.py

class A:

    def foo(self):
        print('this is foo.')

    def bar(self):
        print('this is bar')


def baz():
    print('baz……')

```
在 main 中调用：
```python
# main.py
module_name = 'module'
exec('  '.join(['import', module_name]))
a = module.A()
a.foo()
a.bar()

module.baz()
```
- 结果
```plain
this is foo.
this is bar
baz……
```
- 解释
这里请参阅[exec() 官方文档](https://docs.python.org/zh-cn/3/library/functions.html#exec)，相当于使用`exec()`执行了一句`import module`语句，后面的也就不用解释了。
> 这个函数支持动态执行 Python 代码。object 必须是字符串或者代码对象。如果是字符串，那么该字符串将被解析为一系列 Python 语句并执行（除非发生语法错误）
值得注意的是，实际上对于 exec() 的正确使用是比较难的。
>
关于`exec()`的使用说明请阅读此处[如何正确使用`exec`方法](https://python3-cookbook.readthedocs.io/zh_CN/latest/c09/p23_executing_code_with_local_side_effects.html#id4)。
> 默认情况下，exec() 会在调用者局部和全局范围内执行代码。然而，在函数里面， 传递给 exec() 的局部范围是拷贝实际局部变量组成的一个字典。 因此，如果 exec() 如果执行了修改操作，这种修改后的结果对实际局部变量值是没有影响的。
```plain 
>>> def test1():
...     x = 0
...     exec('x += 1')
...     print(x)
...
>>> test1()
0
>>>
```

## 使用`__import__`魔法方法
单独使用__import__() 可以直接加载模块，但是当需要动态加载类、函数时，就需要配合 getattr 来实现。
实现步骤：

1. 获取模块名(module_name)
2. 使用__import__(module_name)导入 Python 模块
3. 使用 getattr(module_name, class_name/function_name)获取类、方法的对象

- 示例代码
```python
# module.py

class A:

    def foo(self):
        print('this is foo.')

    @staticmethod
    def static_method():
        print('this is static.')


def bar():
    print('bar……')


def baz():
    print('==baz==')
```
```python
# main.py

module_name = 'module'  # 模块名
class_name = 'A'  # 类名
class_method = 'foo'  # 类中方法名称
func_name = 'bar'  # 函数名
module_obj = __import__(module_name)
# 调用模块中的类
class_of_module_obj = getattr(module_obj, class_name)
# 实例化对象
instance_of_cmo = class_of_module_obj()
# 调用实例的方法
method_of_cmo = getattr(instance_of_cmo, class_method)
method_of_cmo()
instance_of_cmo.static_method()
# 调用模块的函数
func_of_mo = getattr(module_obj, func_name)
func_of_mo()
# 也可以直接调用（像真正import模块那样）
module_obj.baz()

```

## 使用 importlib
这种方式其实是`__import__()` 方式的扩展。`Python`官方文档推荐程序式地导入模块时应该使用 `import_module()` 而不是`__import__`。
这里我们继续使用上面定义好的`module.py`模块。
```python
# main.py

import importlib

module_name = 'module'

module_obj = importlib.import_module(module_name)
class_of_module_obj = module_obj.A()
class_of_module_obj.foo()
class_of_module_obj.static_method()
module_obj.bar()
```
文档参见此处：[importlib --- import 的实现 — Python 3.9.0 文档](https://docs.python.org/zh-cn/3/library/importlib.html)
> importlib 包的目的有两个。 
>
>第一个目的是在 Python 源代码中提供 import 语句的实现（并且因此而扩展 `__import__()` 函数）。 这提供了一个可移植到任何 Python 解释器的 import 实现。 相比使用 Python 以外的编程语言实现方式，这一实现更加易于理解。
>
> 第二个目的是实现 import 的部分被公开在这个包中，使得用户更容易创建他们自己的自定义对象 (通常被称为 importer) 来参与到导入过程中。

## 应用场景
我们在使用 redis 的时候，有时候需要添加一个代理类，示例如下：
```python
class RedisClient:
    def init_con(self, *args, **kwargs):
        # do init things
        # like connect redis
        pass

```
然后希望直接通过这个 RedisClient 执行 redis 相关操作, 比如 set, get, hget...
```python
rc = RedisClient()
rc.set(...)
rc.get(...)
...
```
这样调用的话, 就需要将 pyredis 中的所有函数都在 RedisClient 中写一遍, 那就有点得不偿失了。

这里实际就是希望能够做到动态调用, 将 RedisClient 中的操作, 根据操作名, 直接映射到实际的 pyredis 操作之上。

所以, 我们在 RedisClient 中：
```python
class RedisClient:
    

    def __getattr__(self, func_name):
        def func(*args, **kwargs):
            # 这里的 getattr 实际就相当于redis_con.<func_name>了
            return getattr(self.redis_conn, func_name)(*args, **args)

if __name__ == '__main__':
    redis_client = RedisClient()
    redis_client.init_con(...)
    redis_client.set('key_name', 'key_value')
```
这样，就实现动态调动 pyredis 的操作的目的了。

## 参考链接
[Python 动态加载模块、类、函数的几种方式 - Threezh1's blog](https://threezh1.com/2019/07/12/Python%E5%8A%A8%E6%80%81%E5%8A%A0%E8%BD%BD%E6%A8%A1%E5%9D%97%E7%9A%84%E5%87%A0%E7%A7%8D%E6%96%B9%E5%BC%8F/#1-exec)
[python 类方法的动态调用 - u3v3](https://www.u3v3.com/ar/1313)

## 推荐阅读
[8.20 通过字符串调用对象方法](https://python3-cookbook.readthedocs.io/zh_CN/latest/c08/p20_call_method_on_object_by_string_name.html)
[9.23 在局部变量域中执行代码](https://python3-cookbook.readthedocs.io/zh_CN/latest/c09/p23_executing_code_with_local_side_effects.html#id4)