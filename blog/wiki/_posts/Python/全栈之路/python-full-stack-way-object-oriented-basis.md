---
title: Python 全栈之路系列之面向对象基础
toc: true
date: 2020-05-23 18:21:46
tags:
- 编码
- 面向对象
---

## 面向对象基本介绍

**Python 编程方式：**

1. 面向过程编程
2. 面向函数编程
3. 面向对象编程

**名称定义：**

1. 如果函数没有在类中称之为`函数`
2. 如果函数在类中称之为`方法`

创建类

```python
# 创建一个类，类名是Class_basis
class Class_basis:
    # 在类里面创建了一个方法ret，类里面的方法必须加一个self关键字
    def ret(self):
        # 当调用方法的时候输出ret
        print("ret")
```

使用类

```python
# 通过Class_basis类创建一个对象obj(创建一个Class_basis实例)，类名后面加括号
obj = Class_basis()

# 通过对象调用类中的ret方法
obj.ret()
```

类的内存地址对应关系

![object-oriented-basis-01](https://blog.ansheng.me/images/2016/12/1483020680.png)

## 面向对象之 self

```python
#!/usr/bin/env python
# _*_ coding:utf-8 _*_

# 创建一个类，类名是Class_basis
class Class_basis:
    # 在类里面创建了一个方法ret
    def ret(self,):
        # 输出self的内存地址
        print("方法ret的self内存地址", id(self))

# 创建一个对象obj，类名后面加括号
obj = Class_basis()

# 输出对象obj的内存地址
print("obj对象内存地址", id(obj))

# 通过对象调用类中的ret方法
obj.ret()
``` 

执行结果

```python
C:\Python35\python.exe F:/Python_code/sublime/Week06/Day02/class_01.py
obj对象内存地址 2420760156536
方法ret的self内存地址 2420760156536

Process finished with exit code 0
```

通过上面的测试可以很清楚的看到`obj`对象和类的方法中`self`内存地址是一样的，那么方法中的`self`就等于`obj`

如图

![object-oriented-basis-02](https://blog.ansheng.me/images/2016/12/1483020708.png)

`self`是形式参数，有 Python 自行传递。

## 面向对象之封装

封装就是将内容封装到某个地方，以后再去调用被封装在某处的内容，在使用面向对象的封装特性时，需要：

1. 将内容封装到某处
2. 从某处调用被封装的内容

```bash
class Foo:
    def ret(self):
        # 输出backend变量的内容
        print(self.backend)

obj = Foo()
# 在对象中创建一个backend变量
obj.backend = "as"
obj.ret()
```

执行结果

```python
C:\Python35\python.exe F:/Python_code/sublime/Week06/Day02/class_01.py
as

Process finished with exit code 0
```

上面的封装是一种非主流的封装方式，下面的`__init__构造方法`封装方式是主流的封装方式。

```python
class Foo:
	
	# 进入类的时候首先执行__init__方法
    def __init__(self, name):
        
        """
        __init__称之为构造方法
        :param name: Foo传递过来的参数
        """

        # 在类中创建一个成员Name，它的值是传过来的形参name
        self.Name = name

    # 类的方法
    def user(self):
    	# 输出Name的值
        print(self.Name)

# 创建对象，并且将"Ansheng"封装到对象中，类+括号的时候会自动执行__init__方法
obj = Foo("Ansheng")

# 执行user方法
obj.user()
```

执行结果

```python
C:\Python35\python.exe F:/Python_code/sublime/Week06/Day02/class_01.py
Ansheng

Process finished with exit code 0
```

> \__del__ 解释器销毁对象时候自动调用，特殊的名：析构方法

封装的应用场景之一就是当同一类型的方法具有相同参数时，直接封装到对象即可。

### 实例

通过用户输入年龄和姓名输出用户的个人信息

```python
#!/usr/bin/env python
# _*_ coding:utf-8 _*_

class Foo:
    def __init__(self, name, age):
        self.Name = name
        self.Age = age

    def info(self):
        print("""
            My name is: %s
            My age is: %d
        """ % (self.Name, self.Age))

ansheng = Foo("Ansheng", 18)
ansheng.info()

xiaoming = Foo("xiaoming", 30)
xiaoming.info()
```

执行结果

```python
C:\Python35\python.exe F:/Python_code/sublime/Week06/Day02/class_01.py

            My name is: Ansheng
            My age is: 18
        

            My name is: xiaoming
            My age is: 30
        

Process finished with exit code 0
```

封装的应用场景之二就是把类当作模块，创建多个对象(对象内封装的数据可以不一样)

## 面向对象之继承基础

继承，面向对象中的继承和现实生活中的继承相同，即：子可以继承父的内容。

实例

创建一个`人`信息相关的类，比如说人拥有`四肢`、`头发`、`眼`、`耳朵`等信息，在创建一个中国人和外国人的类，中国人的语言是中文，皮肤是黄色，外国人的语言是英文，皮肤是黑色。

```python
#!/usr/bin/env python
# _*_ coding:utf-8 _*_

class People:
    def __init__(self):
        print("""
        你的通用特征有：四肢、头发、眼、耳朵
        """)

class China(People):
    def info(self):
        print("""
        你是中国人，你的语言是中文，皮肤是黄色
        """)

class Us(People):
    def info(self):
        print("""
        你是美国人，你的语言是英文，皮肤是黑色
        """)

c = China()
c.info()

m = Us()
m.info()
```

执行结果

```python
C:\Python35\python.exe F:/Python_code/sublime/Week06/Day02/class_01.py

        你的通用特征有：四肢、头发、眼、耳朵
        

        你是中国人，你的语言是中文，皮肤是黄色
        

        你的通用特征有：四肢、头发、眼、耳朵
        

        你是美国人，你的语言是英文，皮肤是黑色
        

Process finished with exit code 0
```

`People` --> `父类` or `基类`

`China` and `Us` --> `子类` or `派生类`

1. 派生类可以集成基类中所有的功能
2. 派生类和积累同时存在，优先找派生类
3. Python 类可以同时继承多个类

## 面向对象之继承之多继承(新式类)

多继承就是在`class My(China, Us):`括号内放入多个父类名。

多继承顺序

当`My(China, Us)`时，因为`My`类中有`info`这个方法，所以输出的结果是`我就是我`

```python
#!/usr/bin/env python
# _*_ coding:utf-8 _*_

class China:
    def info(self):
        print("你是中国人")

class Us:
    def info(self):
        print("你是美国人")

class My(China, Us):
    def info(self):
        print("我就是我")

c = My()
c.info()
```

执行结果

```python
C:\Python35\python.exe F:/Python_code/sublime/Week06/Day02/class_01.py
我就是我

Process finished with exit code 0
```


当`My(China, Us)`时，`My`类中没有`info`这个方法，输出的结果是`你是中国人`，默认括号内左边的类优先

```python
#!/usr/bin/env python
# _*_ coding:utf-8 _*_

class China:
    def info(self):
        print("你是中国人")

class Us:
    def info(self):
        print("你是美国人")

class My(China, Us):
    pass

c = My()
c.info()
```

执行结果

```python
C:\Python35\python.exe F:/Python_code/sublime/Week06/Day02/class_01.py
你是中国人

Process finished with exit code 0
```

当`My(China, Us)`时，`My`类中没有`info`这个方法，`China`类中也没有`info`这个方法，输出的结果是`你是美国人`

```python
#!/usr/bin/env python
# _*_ coding:utf-8 _*_

class China:
    pass

class Us:
    def info(self):
        print("你是美国人")

class My(China, Us):
    pass

c = My()
c.info()
```

执行结果

```python
C:\Python35\python.exe F:/Python_code/sublime/Week06/Day02/class_01.py
你是美国人

Process finished with exit code 0
```

## 面向对象之继承之多继承时的查找顺序

- **顶层两个类没有父类的情况**

![object-oriented-basis-03](https://blog.ansheng.me/images/2016/12/1483020761.png)

- **顶层两个类有父类的情况**

![object-oriented-basis-04](https://blog.ansheng.me/images/2016/12/1483020781.png)