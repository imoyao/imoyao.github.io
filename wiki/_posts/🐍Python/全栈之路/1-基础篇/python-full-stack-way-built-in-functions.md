---
title: Python 全栈之路系列之 Python3 内置函数
toc: true
date: 2020-05-23 18:21:46
tags:
- 编码
top: 12
---

The Python interpreter has a number of functions and types built into it that are always available. They are listed here in alphabetical order.

||||Built-in Functions||||
|:--:|:--:|:--:|:--:|:--:|:--:|:--:|
|abs()|dict()|help()|min()|setattr()|all()|dir()|
|hex()|next()|slice()|any()|divmod()|id()|object()|
|sorted()|ascii()|enumerate()|input()|oct()|staticmethod()|bin()|
|eval()|int()|open()|str()|bool()|exec()|isinstance()|
|ord()|sum()|bytearray()|filter()|issubclass()|pow()|super()|
|bytes()|float()|iter()|print()|tuple()|callable()|format()|
|len()|property()|type()|chr()|frozenset()|list()|range()|
|vars()|classmethod()|getattr()|locals()|repr()|zip()|compile()|
|globals()|map()|reversed()|\__import__()|complex()|hasattr()|max()|
|round()|delattr()|hash()|memoryview()|set()|

> 官方介绍：https://docs.python.org/3/library/functions.html

## 内置函数详解

abs(x)

> 返回数字的绝对值，参数可以是整数或浮点数，如果参数是复数，则返回其大小。

```python
# 如果参数是复数，则返回其大小。
 >>> abs(-25)
25
 >>> abs(25)
25
```

all(iterable)

> all()会循环括号内的每一个元素，如果括号内的所有元素都是真的，或者如果 iterable 为空，则返回`True`，如果有一个为假的那么就返回`False`

```python
>>> all([])
True
>>> all([1,2,3])
True
>>> all([1,2,""])
False
# 如果有一个为假，则都为假
>>> all([1,2,None])
False
```

假的参数有：`False`、`0`、`None`、`""`、`[]`、`()`、`{}`等，查看一个元素是否为假可以使用 bool 进行查看。

any(iterable)

> 循环元素，如果有一个元素为真，那么就返回 True，否则就返回 False

```python
 >>> any([0,1])
True
 >>> any([0])
False
```

ascii(object)

> 在对象的类中寻找`__repr__`方法，获取返回值

```python
 >>> class Foo:
 ...  def __repr_(self):
 ...     return "hello"
 ...
 >>> obj = Foo()
 >>> r = ascii(obj)
 >>> print(r)
# 返回的是一个可迭代的对象
<__main__.Foo object at 0x000001FDEE13D320>
```

bin(x)

将整数 x 转换为二进制字符串，如果 x 不为 Python 中 int 类型，x 必须包含方法`__index__()`并且返回值为`integer`

```python
# 返回一个整数的二进制
 >>> bin(999)
'0b1111100111'
```

```python
# 非整型的情况，必须包含__index__()方法切返回值为integer的类型
 >>> class myType:
 ...   def __index__(self):
 ...       return 35
 ...
 >>> myvar = myType()
 >>> bin(myvar)
'0b100011'
```

bool([x])

查看一个元素的布尔值，非真即假

```python
 >>> bool(0)
False
 >>> bool(1)
True
 >>> bool([1])
True
 >>> bool([10])
True
```

bytearray([source [, encoding [, errors]]])

> 返回一个 byte 数组，Bytearray 类型是一个可变的序列，并且序列中的元素的取值范围为 [0 ,255]。

source 参数：

1. 如果 source 为整数，则返回一个长度为 source 的初始化数组；
2. 如果 source 为字符串，则按照指定的 encoding 将字符串转换为字节序列；
3. 如果 source 为可迭代类型，则元素必须为[0 ,255]中的整数；
4. 如果 source 为与 buffer 接口一致的对象，则此对象也可以被用于初始化 bytearray.。

```python
 >>> bytearray(3)
bytearray(b'\x00\x00\x00')
```

bytes([source[, encoding[, errors]]])

```python
 >>> bytes("asdasd",encoding="utf-8")
b'asdasd'
```

callable(object)

> 返回一个对象是否可以被执行

```python
 >>> def func():
 ...  return 123
 ...
 >>> callable(func)
True
 >>> func = 123
 >>> callable(func)
False
```

chr(i)

> 返回一个数字在 ASCII 编码中对应的字符，取值范围 256 个

```python
 >>> chr(66)
'B'
 >>> chr(5)
'\x05'
 >>> chr(55)
'7'
 >>> chr(255)
'\xff'
 >>> chr(25)
'\x19'
 >>> chr(65)
'A'
```

classmethod(function)

> 返回函数的类方法

compile(source, filename, mode, flags=0, dont_inherit=False, optimize=-1)

> 把字符串编译成 python 可执行的代码

```python
 >>> str = "for i in range(0,10): print(i)"
 >>> c = compile(str,'','exec')
 >>> exec(c)
0
1
2
3
4
5
6
7
8
9
```

complex([real[, imag]])

> 创建一个值为 real + imag * j 的复数或者转化一个字符串或数为复数。如果第一个参数为字符串，则不需要指定第二个参数

```python
 >>> complex(1, 2)
(1+2j)
# 数字
 >>> complex(1)
(1+0j)
# 当做字符串处理
 >>> complex("1")
(1+0j)
# 注意：这个地方在“+”号两边不能有空格，也就是不能写成"1 + 2j"，应该是"1+2j"，否则会报错
 >>> complex("1+2j")
(1+2j)
```

delattr(object, name)

> 删除对象的属性值

```python
>>> class cls:
...   @classmethod
...   def echo(self):
...     print('CLS')
... 
>>> cls.echo()
CLS
>>> delattr(cls, 'echo')
>>> cls.echo()
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
AttributeError: type object 'cls' has no attribute 'echo'
```

dict(**kwarg)

> 创建一个数据类型为字典

```python
 >>> dic = dict({"k1":"123","k2":"456"})
 >>> dic
{'k1': '123', 'k2': '456'}
```

dir([object])

> 返回一个对象中中的所有方法

```python
 >>> dir(str)
['__add__', '__class__', '__contains__', '__delattr__', '__dir__', '__doc__', '__eq__', '__format__', '__ge__', '__getattribute__', '__getitem__', '__getnewargs__', '__gt__', '__hash__', '__init__', '__iter__', '__le__', '__len__', '__lt__', '__mod__', '__mul__', '__ne__', '__new__', '__reduce__', '__reduce\_ex__', '__repr__', '__rmod__', '__rmul__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__', 'capitalize', 'casefold', 'center', 'count', 'encode', 'endswith', 'expandtabs', 'find', 'format', 'format_map', 'index', 'isalnum', 'isalpha', 'isdecimal', 'isdigit', 'isidentifier', 'islower', 'isnumeric', 'isprintable', 'isspace', 'istitle', 'isupper', 'join', 'ljust', 'lower', 'lstrip', 'maketrans', 'partition', 'replace', 'rfind', 'rindex', 'rjust', 'rpartition', 'rsplit', 'rstrip', 'split', 'splitlines', 'startswith', 'strip', 'swapcase', 'title', 'translate', 'upper', 'zfill']
```

divmod(a, b)

> 返回的是 a//b（除法取整）以及 a 对 b 的余数，返回结果类型为 tuple

```python
 >>> divmod(10, 3)
(3, 1)
```

enumerate(iterable, start=0)

> 为元素生成下标

```python
 >>> li = ["a","b","c"]
 >>> for n,k in enumerate(li):
 ...  print(n,k)
 ...
0 a
1 b
2 c
```

eval(expression, globals=None, locals=None)

> 把一个字符串当作一个表达式去执行

```python
 >>> string = "1 + 3"
 >>> string
'1 + 3'
 >>> eval(string)
4
```

exec(object[, globals[, locals]])

> 把字符串当作 python 代码执行

```python
 >>> exec("for n in range(5): print(n)")
0
1
2
3
4
```

filter(function, iterable)

> 筛选过滤，循环可迭代的对象，把迭代的对象当作函数的参数，如果符合条件就返回`True`，否则就返回`False`

```python
 >>> def func(x):
 ...  if x == 11 or x == 22:
 ...    return True
 ...
 >>> ret = filter(func,[11,22,33,44])
 >>> for n in ret:
 ...  print(n)
 ...
11
22
```

```python
>>> list(filter((lambda x: x > 0),range(-5,5)))
[1, 2, 3, 4]
```

float([x])

> 将整数和字符串转换成浮点数

```python
 >>> float("124")
124.0
 >>> float("123.45")
123.45
 >>> float("-123.34")
-123.34
```

format(value[, format_spec])

> 字符串格式化

详键：https://blog.ansheng.me/article/python-full-stack-way-string-formatting/

frozenset([iterable])

> frozenset 是冻结的集合，它是不可变的，存在哈希值，好处是它可以作为字典的 key，也可以作为其它集合的元素。缺点是一旦创建便不能更改，没有 add，remove 方法。

getattr(object, name[, default])

> 返回对象的命名属性的值，`name`必须是字符串，如果字符串是对象属性之一的名称，则结果是该属性的值。

globals()

> 获取或修改当前文件内的全局变量

```ptyhon
>>> a = "12"
>>> bsd = "54asd"
>>> globals()
{'__doc__': None, 'a': '12', '__loader__': <class '_frozen_importlib.BuiltinImporter'>, 'bsd': '54asd', '__builtins__': <module 'builtins' (built-in)>, 'n': '__doc__', '__name__': '__main__', '__spec__': None, '__package__': None}
```

hasattr(object, name)

> 参数是一个对象和一个字符串，如果字符串是对象的某个属性的名称，则结果为 True，否则为 False。

hash(object)

> 返回一个对象的 hash 值

```python
 >>> a = "asdadasdwqeq234sdfdf"
 >>> hash(a)
5390438057823015497
```

help([object])

> 查看一个类的所有详细方法，或者查看某个方法的使用详细信息

```python
 >>> help(list)
Help on class list in module __builtin__:

class list(object)
 |  list() -> new empty list
 |  list(iterable) -> new list initialized from iterable's items
 |  
 |  Methods defined here:
 |  
 |  __add__(...)
 |      x.__add__(y) <==> x+y
 |  
 |  __contains__(...)
 |      x.__contains__(y) <==> y in x
 |  
 |  __delitem__(...)
 |      x.__delitem__(y) <==> del x[y]
 |  
 |  __delslice__(...)
 |      x.__delslice__(i, j) <==> del x[i:j]
 |      
 |      Use of negative indices is not supported.
..........
```

hex(x)

> 获取一个数的十六进制

```python
 >>> hex(13)
'0xd'
```

id(object)

> 返回一个对象的内存地址

```python
 >>> a = 123
 >>> id(a)
1835400816
```

input([prompt])

> 交互式输入

```python
 >>> name = input("Pless your name: ")
Pless your name: ansheng
 >>> print(name)
ansheng
```

int(x, base=10)

> 获取一个数的十进制

```python
 >>> int("31")
31
```

> 也可以作为进制转换

```python
 >>> int(10)
10
 >>> int('0b11',base=2)
3
 >>> int('11',base=8)
9
 >>> int('0xe',base=16)
14
```

isinstance(object, classinfo)

> 判断对象是否是这个类创建的

```python
>>> li = [11,22,33]
>>> isinstance(li,list)
True
```

issubclass(class, classinfo)

> 查看一个对象是否为子类

iter(object[, sentinel])

> 创建一个可迭代的对象

```python
 >>> obj = iter([11,22,33,44])
 >>> obj
<list_iterator object at 0x000002477DB25198>
 >>> for n in obj:
 ...  print(n)
 ...
11
22
33
44
```

len(s)

> 查看一个对象的长度

```python
 >>> url="ansheng.me"
 >>> len(url)
10
```

list([iterable])

> 创建一个数据类型为列表

```python
 >>> li = list([11,22,33,44])
 >>> li
[11, 22, 33, 44]
```

locals()

> 返回当前作用域的局部变量，以字典形式输出

```python
 >>> func()
 >>> def func():
 ...  name="ansheng"
 ...  print(locals())
 ...
 >>> func()
{'name': 'ansheng'}
```

map(function, iterable,  ...)

> 对一个序列中的每一个元素都传到函数中执行并返回

```python
>>> list(map((lambda x : x +10),[1,2,3,4]))
[11, 12, 13, 14]
```

max(iterable, *[, key, default])

max(arg1, arg2, *args[, key])

> 取一个对象中的最大值

```python
 >>> li = list([11,22,33,44])
 >>> li = [11,22,33,44]
 >>> max(li)
44
```

memoryview(obj)

> 返回对象 obj 的内存查看对象

```python
 >>> import struct
 >>> buf = struct.pack("i"*12, *list(range(12)))
 >>> x = memoryview(buf)
 >>> y = x.cast('i', shape=[2,2,3])
 >>> print(y.tolist())
[[[0, 1, 2], [3, 4, 5]], [[6, 7, 8], [9, 10, 11]]]
```

min(iterable, *[, key, default])

min(arg1, arg2, *args[, key])

> 取一个对象中的最小值

```python
 >>> li = list([11,22,33,44])
 >>> li = [11,22,33,44]
 >>> min(li)
11
```

next(iterator[, default])

> 每次只拿取可迭代对象的一个元素

```python
 >>> obj = iter([11,22,33,44])
 >>> next(obj)
11
 >>> next(obj)
22
 >>> next(obj)
33
 >>> next(obj)
44
 >>> next(obj)
 # 如果没有可迭代的元素了就会报错
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
StopIteration
```

object

> 返回一个新的无特征对象

oct(x)

> 获取一个字符串的八进制

```python
 >>> oct(13)
'0o15'
```

open(file, mode='r', buffering=-1, encoding=None, errors=None, newline=None, closefd=True, opener=None)

> 文件操作的函数，用来做文件操作的

```python
 # 打开一个文件
- >>> f = open("a.txt","r")
```

ord(c)

> 把一个字母转换为 ASCII 对对应表中的数字

```python
 >>> ord("a")
97
 >>> ord("t")
116
```

pow(x, y[, z])

> 返回一个数的 N 次方

```python
 >>> pow(2, 10)
1024
 >>> pow(2, 20)
1048576
```

print(*objects, sep=' ', end='\n', file=sys.stdout, flush=False)

> 打印输出

```python
 >>> print("hello word")
hello word
```

property(fget=None, fset=None, fdel=None, doc=None)

range(start, stop[, step])

> 生成一个序列

```python
 >>> range(10)
range(0, 10)
 >>> for n in range(5):
 ...  print(n)
 ...
0
1
2
3
4
```

repr(object)

> 返回一个包含对象的可打印表示的字符串

```python
>>> repr(111)
'111'
>>> repr(111.11)
'111.11'
```

reversed(seq)

> 对一个对象的元素进行反转

```python
 >>> li = [1, 2, 3, 4]
 >>> reversed(li)
<list_reverseiterator object at 0x000002CF0EF6A940>
 >>> for n in reversed(li):
 ...  print(n)
 ...
4
3
2
1
```

round(number[, ndigits])

> 四舍五入

```python
 >>> round(3.3)
3
 >>> round(3.7)
4
```

set([iterable])

> 创建一个数据类型为集合

```python
 >>> varss = set([11,222,333])
 >>> type(varss)
<class 'set'>
```

setattr(object, name, value)

> 为某个对象设置一个属性

slice(start, stop[, step])

> 元素的切片操作都是调用的这个方法

sorted(iterable[, key][, reverse])

> 为一个对象的元素进行排序

代码：
```python
#!/usr/bin/env python
# _*_ coding:utf-8 _*_

char=['赵',"123", "1", "25", "65","679999999999", "a","B","alex","c" ,"A", "_", "ᒲ",'a钱','孙','李',"余", '佘',"佗", "㽙", "铱", "钲钲㽙㽙㽙"]

new_chat = sorted(char)
print(new_chat)
for i in new_chat:
    print(bytes(i, encoding='utf-8'))
```

输出结果：

```python
C:\Python35\python.exe F:/Python_code/Note/soretd.py
['1', '123', '25', '65', '679999999999', 'A', 'B', '_', 'a', 'alex', 'a钱', 'c', 'ᒲ', '㽙', '佗', '佘', '余', '孙', '李', '赵', '钲钲㽙㽙㽙', '铱']
b'1'
b'123'
b'25'
b'65'
b'679999999999'
b'A'
b'B'
b'_'
b'a'
b'alex'
b'a\xe9\x92\xb1'
b'c'
b'\xe1\x92\xb2'
b'\xe3\xbd\x99'
b'\xe4\xbd\x97'
b'\xe4\xbd\x98'
b'\xe4\xbd\x99'
b'\xe5\xad\x99'
b'\xe6\x9d\x8e'
b'\xe8\xb5\xb5'
b'\xe9\x92\xb2\xe9\x92\xb2\xe3\xbd\x99\xe3\xbd\x99\xe3\xbd\x99'
b'\xe9\x93\xb1'

Process finished with exit code 0
```

staticmethod(function)

> 返回函数的静态方法

 str(object=b'', encoding='utf-8', errors='strict')

> 字符串

```python
 >>> a = str(111)
 >>> type(a)
<class 'str'>
```

sum(iterable[, start])

> 求和

```python
 >>> sum([11,22,33])
66
```

super([type[, object-or-type]])

> 执行父类的构造方法

tuple([iterable])

> 创建一个对象，数据类型为元组

```python
>>> tup = tuple([11,22,33,44])
>>> type(tup)
<class 'tuple'>
```

type(object)

> 查看一个对象的数据类型

```python
 >>> a = 1
 >>> type(a)
<class 'int'>
 >>> a = "str"
 >>> type(a)
<class 'str'>
```

vars([object])

查看一个对象里面有多少个变量

zip(*iterables)

> 将两个元素相同的序列转换为字典

```python
>>> li1 = ["k1","k2","k3"]
>>> li2 = ["a","b","c"]
>>> d = dict(zip(li1,li2))
>>> d
{'k1': 'a', 'k2': 'b', 'k3': 'c'}
```

\_\_import\_\_(name, globals=None, locals=None, fromlist=(), level=0)

> 导入模块，把导入的模块作为一个别名

## 生成随机验证码例子

生成一个六位的随机验证码，且包含数字，数字的位置随机

```python
# 导入random模块
import random
temp = ""
for i in range(6):
    num = random.randrange(0,4)
    if num == 3 or num == 1:
        rad2 = random.randrange(0,10)
        temp = temp + str(rad2)
    else:
        rad1 = random.randrange(65,91)
        c1 = chr(rad1)
        temp = temp + c1
print(temp)
```
输出结果
```python
C:\Python35\python.exe F:/Python_code/sublime/Day06/built_in.py
72TD11
```