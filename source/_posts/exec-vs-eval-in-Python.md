---
title: Python 中 exec()和 eval()的区别
date: 2017-11-17 15:23:17
tags:
- Python
categories:
- Python
thumbnail:
---

Python 动态执行字符串代码片段（也可以是文件）， 一般会用到 exec,eval。那么这两个方法有什么区别呢？

<!-- more -->

## exec 方法

注意：`exec` 是一个语法声明，不是一个函数。也就是说和`if`、`for`一样。

官方文档对于 exec 的解释
> This statement supports dynamic execution of Python code.

exec 的第一个表达式可以是：

1. 代码字符串
2. 文件对象
3. 代码对象
4. tuple

前面三种情况差不多，第四种比较特殊最后讲

如果忽略后面的可选表达式,exec 后面代码将在当前域执行
```plain
>>> a=2
>>> exec "a=1"
>>> a
1

```
如果在表达式之后使用 in 选项指定一个`dict`，它将作为`global`和`local`变量作用域
```plain
>>> a=10 
>>> b=20 
>>> g={'a':6,'b':8} 
>>> exec "global a;print a,b" in g 
6 8 
```
如果`in`后详指定两个表达式，它们将分别用作`global`和`local`变量作用域
```plain
>>> a=10 
>>> b=20 
>>> c=20 
>>> g={'a':6,'b':8} 
>>> l={'b':9,'c':10} 
>>> exec "global a;print a,b,c" in g,l 
6 9 10
```
现在说下`tuple`的情况，这也是导致很多人误以为`exec`是一个函数的原因。

如果第一个表达式是`tuple`

```plain
exec(expr, globals) #它等效于 `exec expr in globals`

exec(expr, globals, locals) #它等效于  `exec expr in globals,locals`
```
## eval()方法

`eval`通常用来执行一个字符串表达式，并返回表达式的值。

```python
eval(expression[, globals[, locals]])
```

有三个参数，表达式字符串，globals 变量作用域，locals 变量作用域。 其中第二个和第三个参数是可选的。

如果忽略后面两个参数，则`eval`在当前作用域执行。

```plain
>>> a=1 
>>> eval("a+1") 
2
```
如果指定 globals 参数
```plain
>>> a=1 
>>> g={'a':10} 
>>> eval("a+1",g) 
11
```
如果指定`locals`参数
```plain
>>> a=10 
>>> b=20 
>>> c=20 
>>> g={'a':6,'b':8} 
>>> l={'b':9,'c':10} 
>>> eval("a+b+c",g,l) 
25
```
如果要严格限制`eval`执行，可以设置`globals`为`__builtins__`,这样 这个表达式只可以访问`__builtin__` module。

```pyhton
# coding=utf-8
exec 'print("hello")'   #支持str的表达式动态代码执行    >>hello
exec ('a = 3*4')
print a     # >>12
b = eval('3*4')     #不支持表达式 有返回值
print b     # >>12
```
参考来源：

[python 的 exec、eval 详解 - 疯狂奔跑的猪](http://www.coolpython.com/index.php?aid=12)