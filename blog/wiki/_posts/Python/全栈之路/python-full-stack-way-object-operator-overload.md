---
title: Python 全栈之路系列之面向对象运算符重载
toc: true
date: 2020-05-23 18:21:46
tags:
- 编码
---

运算符重载的概念如下：

1. 运算符重载让类拦截常规的 Python 运算；
2. 类可重载所有 Python 表达式运算符；
3. 类也可重载打印、函数调用、属性点号运算等内置运算；
4. 重载是类实例的行为想内置类型；
5. 重载是通过提供特殊名称的类方法来实现的；

## 常见的运算符重载方法

|方法|重载|调用|
|:--|:--|:--|
|`__init__`|构造函数|对象建立：X = Class(args)|
|`__del__`|解析函数|X 对象收回|
|`__add__`|运算符+|如果没有`__iadd__`,X+Y,X+=Y|
|`__or__`|运算符或|如果没有`__ior__`|
|`__repr__`,`__str__`|打印、转换|print(X)、repr(X)、str(X)|
|`__call__`|函数调用|X(*args, **kwargs)|
|`__getattr__`|点号运算|X.undefined|
|`__setattr__`|属性赋值语句|X.any = value|
|`__delattr__`|属性删除|del X.any|
|`__getattribute__`|属性获取|X.any
|`__getitem__`|索引运算|X[key]，X[i:j]，没`__iter__`时的 for 循环和其他迭代器|
|`__setitem__`|索引赋值语句|X[key]=value,X[i:k]=sequence|
|`__delitem__`|索引和分片删除|del X[key], del X[i:j]|
|`__len__`|长度|len(X)，如果没有`__bool__`，真值测试|
|`__bool__`|布尔测试|bool(X)，真测试|
|`__lt__`，`__gt__`，`__le__`，`__ge__`，`__eq__`，`__ne__`|特定的比较|X<Y，X>Y...|
|`__radd__`|右侧加法|Other + X|
|`__iadd__`|增强的加法|X += Y|
|`__iter__`，`__next__`|迭代环境|I=iter(X),next(I)|
|`__contains__`|成员关系测试|item in X(任何可迭代对象)|
|`__index__`|整数值|hex(X),bin(X),oct(X),o[X],O[X:]|
|`__enter__`,`__exit__`|环境管理器|with obj as var:|
|`__get__`,`__set__`,`__delete__`|描述符属性|X.attr，X.attr=Value,del X.attr|
|`__new__`|创建|在`__init__`之前创建对象|

所有重载方法的名称前后都有两个下划线字符，以便把同类中定义的变量名区别开来。

### 构造函数和表达式:`__init__`和`__sub__`

```python
>>> class Number:
...   def __init__(self, start):
...     self.data = start
...   def __sub__(self, other):
...     return Number(self.data - other)
... 
>>> X = Number(5)
>>> Y = X - 2
>>> Y
<__main__.Number object at 0x10224d550>
>>> Y.data
3
```

### 索引和分片: `__getitem__`和`__setitem__`

基本索引

```python
>>> class Index:
...     def __getitem__(self, item):
...         return item ** 2
... 
>>> 
>>> for i in range(5):
...     I = Index()
...     print(I[i], end=' ')
... 
0 1 4 9 16 
```

切片索引

```python
>>> class Index:
...   data = [5, 6, 7, 8, 9]
...   def __getitem__(self, item):
...     print('getitem: ', item)
...     return self.data[item]
...   def __setitem__(self, key, value):
...     self.data[key] = value
... 
>>> X = Index()
>>> print(X[1:4])
getitem:  slice(1, 4, None)
[6, 7, 8] 
>>> X[1:4] = (1, 1, 1)
>>> print(X[1:4])
getitem:  slice(1, 4, None)
[1, 1, 1]
```

### 索引迭代：`__getitem__`

如果重载了这个方法，for 循环每次循环时都会调用类的__getitem__方法；

```python
>>> class stepper:
...     def __getitem__(self, item):
...         return self.data[item].upper()
... 
>>> 
>>> X = stepper()
>>> X.data = 'ansheng'
>>> for item in X:
...     print(item)
... 
A
N
S
H
E
N
G
```

### 迭代器对象：`__iter__`和`__next__`

```python
>>> class Squares:
...   def __init__(self, start, stop):
...         self.value = start - 1
...         self.stop = stop
...   def __iter__(self):
...         return self
...   def __next__(self):
...         if self.value == self.stop:
...             raise StopIteration
...         self.value += 1
...         return self.value ** 2
... 
>>> for i in Squares(1, 5):
...   print(i)
... 
1
4
9
16
25
```

### 成员关系：`__contains__`、`__iter__`和`__getitem__`

```python
class Iters:
    def __init__(self, value):
        self.data = value

    def __getitem__(self, item):
        print('get[%s]' % item, end='')
        return self.data[item]

    def __iter__(self):
        print('iter>==', end='')
        self.ix = 0
        return self

    def __next__(self):
        print('next:', end='')
        if self.ix == len(self.data): raise StopIteration
        item = self.data[self.ix]
        self.ix += 1
        return item

    def __contains__(self, item):
        print('contains: ', end=' ')
        return item in self.data


X = Iters([1, 2, 3, 4, 5])
print(3 in X)
for i in X:
    print(i, end='|')

print([i ** 2 for i in X])
print(list(map(bin, X)))

I = iter(X)
while True:
    try:
        print(next(I), end=' @')
    except StopIteration as e:
        break
```

### 属性引用：`__getattr__`和`__setattr__`

当通过未定义的属性名称和实例通过点号进行访问时，就会用属性名称作为字符串调用这个方法，但如果类使用了继承，并且在超类中可以找到这个属性，那么就不会触发。

```python
>>> class empty:
...     def __getattr__(self, item):
...         if item == 'age':
...             return 40
...         else:
...             raise AttributeError(item)
... 
>>> 
>>> x = empty()
>>> print(x.age)
40
>>> print(x.name)
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "<stdin>", line 6, in __getattr__
AttributeError: name
```

```python
>>> class accesscontrol:
...     def __setattr__(self, key, value):
...         if key == 'age':
...             self.__dict__[key] = value
...         else:
...             raise AttributeError(key + ' not allowed')
... 
>>> 
>>> x = accesscontrol()
>>> x.age = 40
>>> print(x.age)
40
>>> x.name = 'Hello'
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "<stdin>", line 6, in __setattr__
AttributeError: name not allowed
```

### `__repr__`和`__str__`会返回字符串表达式

`__repr__`和`__str__`都是为了更友好的显示，具体来说，如果在终端下 print(Class)则会调用`__repr__`，非终端下会调用`__str__`方法，且这两个方法只能返回字符串；


```python
class adder:
    def __init__(self, value=0):
        self.data = value

    def __add__(self, other):
        self.data += other

    def __repr__(self):
        return 'addrepr(%s)' % self.data

    def __str__(self):
        return 'N: %s' % self.data


x = adder(2)
x + 1
print(x)
print((str(x), repr(x)))
```

### 右侧加法和原处加法: `__radd__`和`__iadd__`

只有当+右侧的对象是类实例，而左边对象不是类实例的时候，Python 才会调用`__radd__`

```python
class Commuter:
    def __init__(self, val):
        self.val = val

    def __add__(self, other):
        print('add', self.val, other)
        return self.val + other

    def __radd__(self, other):
        print('radd', self.val, other)
        return other + self.val


x = Commuter(88)
y = Commuter(99)
print(x + 1)
print('')
print(1 + y)
print('')
print(x + y)
```

使用`__iadd__`进行原处加法

```python
class Number:
    def __init__(self, val):
        self.val = val

    def __iadd__(self, other):
        self.val += other
        return self


x = Number(5)
x += 1
x += 1
print(x.val)


class Number:
    def __init__(self, val):
        self.val = val

    def __add__(self, other):
        return Number(self.val + other)


x = Number(5)
x += 1
x += 1
print(x.val)
```

### Call 表达式：`__call__`

当调用类实例时执行`__call__`方法

```python
class Callee:
    def __call__(self, *args, **kwargs):
        print('Callee:', args, kwargs)


C = Callee()
C(1, 2, 3)
C(1, 2, 3, x=1, y=2, z=3)


class Prod:
    def __init__(self, value):
        self.value = value

    def __call__(self, other):
        return self.value * other


x = Prod(3)
print(x(3))
print(x(4))
```

### 比较:`__lt__`,`__gt__`和其他方法

类可以定义方法来捕获所有的 6 种比较运算符：<、>、<=、>=、==和!=

```python
class C:
    data = 'spam'

    def __gt__(self, other):
        return self.data > other

    def __lt__(self, other):
        return self.data < other

x = C()
print(x > 'han')
print(x < 'han')
```

### 布尔值测试：__bool__和__len__

```python
class Truth:
    def __bool__(self):
        return True


X = Truth()
if X: print('yes')


class Truth:
    def __bool__(self):
        return False

X = Truth()
print(bool(X))
```

如果没有这个方法，Python 退而求其次的求长度，因为一个非空对象看作是真:

```python
>>> class Truth:
...   def __len__(self): return 0
... 
>>> X = Truth()
>>> if not X: print('no')
... 
no
```

如果两个方法都有，`__bool__`会胜过`__len__`：

```python
>>> class Truth:
...   def __bool__(self): return True
...   def __len__(self): return 0
... 
>>> X = Truth()
>>> bool(X)
True
```
如果两个方法都没有定义，对象毫无疑义的看作为真：
```python
>>> class Truth: pass
... 
>>> bool(Truth)
True
```

### 对象解析函数：`__del__`

每当实例产生时，就会调用__init__构造函数，每当实例空间被收回时，它的对立面`__del__`，也就是解析函数，就会自动执行；


```python
class Life:
    def __init__(self, name='unknown'):
        print('Hello, ', name)
        self.name = name

    def __del__(self):
        print('Goodbye', self.name)


brian = Life('Brian')
brian = 'loretta'
```