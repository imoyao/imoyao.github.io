---
title: Python 全栈之路系列之函数
toc: true
date: 2020-05-23 18:21:46
tags:
- 编码
- 函数
---

## 函数

函数是`Python`为了代码最大程度的重用和最小化代码冗余而提供的最基本的程序结构。

1. 函数式：将某功能代码封装到函数中，日后便无需重复编写，仅调用函数即可
2. 面向对象：对函数进行分类和封装，让开发“更快更好更强...”

函数式编程最重要的是增强代码的重用性和可读性

创建的函数语法

```python
def 函数名(参数):
    ...
    函数体
    ...
    返回值
```

简单的实例

```python
# x为函数的参数
>>> def num(x):
...  print(x)
...
# 123456等于x
>>> num("123456")
123456
```

## 函数的返回值

函数的返回值需要使用到`return`这个关键字，返回值主要是用来接受函数的执行结果

```python
>>> def re():
...   if 1==1:
...     return True
...   else:
...     return False
...
>>> re()
True
```

函数 return 后面是什么值，re 就返回什么值，如果没有指定 return 返回值，那么会返回一个默认的参数`None`

在函数中，当`return`执行完成之后，`return`后面的代码是不会被执行的

```python
>>> def ret():
...  print("123")
...  return True
...  print("abc")
...
>>> ret()
123
True
```

## 位置参数

传入参数的值是按照顺序依次赋值过去的。

代码

```python
# x==形式参数，形式参数有几个，那么实际参数就要传几个，默认参数除外
def ret(x):
    print(x)
# "Hello Word"实际参数
print(ret("Hello Word"))
```

执行结果

```python
Hello Word
```

如图所示:
![Python-Day04-04](https://blog.ansheng.me/images/2016/12/1483016903.png)

ret 小括号内的值会被传入到函数 ret 里面都能做 x 的值，结果差不多就是`print("Hello Word")`

### 函数的普通参数实例：发送邮件

```python
def email(mail):
    import smtplib
    from email.mime.text import MIMEText
    from email.utils import formataddr

    msg = MIMEText('邮件内容', 'plain', 'utf-8')
    msg['From'] = formataddr(["测试",'asdasd@126.com'])
    msg['To'] = formataddr(["走人",'asdasdasd@163.com'])
    msg['Subject'] = "主题"

    server = smtplib.SMTP("smtp.126.com", 25)
    server.login("wdfgfghfgh@126.com", "123456")
    server.sendmail('asdasdas@126.com', [mail,], msg.as_string())
    server.quit()

email("6087414@qq.com")
```

当执行这个脚本的时候会给邮箱`6087414@qq.com`发送邮件。

**注：**上面的邮箱地址等都是随便写的，请自行更改

## 指定参数

```python
>>> def ret(a,b,c):
...  print(a,"a")
...  print(b,"b")
...  print(c,"c")
...
>>> ret(b="bbb",a="aaa",c="ccc")
aaa a
bbb b
ccc c
```

默认情况在函数 ret 括号内如果要输入函数参数的值，是要按照顺序来的，但是如果在 ret 括号内制定的参数的值，那么就不需要按照顺序来了。

## 默认参数

如果我们在创建函数的时候给函数定义了值，那么在调用函数的时候如果不填写值程序就会报错：

```python
>>> def ret(x):
...  print(x)
...
>>> ret()
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
TypeError: ret() missing 1 required positional argument: 'x'
```

如果要解决这个问题就可以给函数的值指定一个默认值，指定函数的默认值需要在`def`这一行指定，制定之后，当调用这个函数的时候就不需要输入函数值了。

```python
>>> def ret(x="Hello Word"):
...  print(x)
...
>>> ret()
Hello Word
# 如果值指定默认值，那么实际参数替换掉形式参数
>>> ret("Pythoner")
Pythoner
```

如果给函数创建了默认值，那么有默认值的这个参数必须在最后面定义，不能够在没有默认参数的值的前面。

## 动态参数

动态参数把接收过来的实际参数当作一个元组，每一个参数都是元组中的一个元素。

**第一种动态参数**

定义第一种动态参数需要在参数前面加上一个`*`号

```python
>>> def ret(*args):
...  print(args,type(args))
...
>>> ret(11,22,33)
(11, 22, 33) <class 'tuple'>
```

**第二种动态参数**

定义第二种动态参数需要在参数前面加上两个`*`号，给参数传参的时候是一个 key 对应一个 value 的，相当于一个字典的键值对，而且返回的类型就是字典类型。

使用两个星号可以将参数收集到一个字典中，参数的名字是字典的键，对应参数的值是字典的值。

```python
>>> def ret(**kwargs):
...  print(kwargs,type(kwargs))
...
>>> ret(k1=123,k2=456)
{'k1': 123, 'k2': 456} <class 'dict'>
```

**第三种动态参数**

第三种又称为万能的动态参数，如下实例：

```python
>>> def ret(*args,**kwargs):
...  print(args,type(args))
...  print(kwargs,type(kwargs))
...
>>> ret(11,222,333,k1=111,k2=222)
(11, 222, 333) <class 'tuple'>
{'k1': 111, 'k2': 222} <class 'dict'>
```

字典小例子：

```python
>>> def arg(**kwargs):
...  print(kwargs,type(kwargs))
...
>>> dic = {"k1":123,"k2":456}
>>> arg(k1=dic)
{'k1': {'k1': 123, 'k2': 456}} <class 'dict'>
>>> arg(**dic)
{'k1': 123, 'k2': 456} <class 'dict'>
```

## 避免可变参数的修改

如果不想在函数内部修改参数值而影响到外部对象的值，我们可以使用切片的方式进行参数的传递：

```python
#!/use/bin/env python

L = ['a', 'b']
def changer(L):
    L[0] = 0
print(L)
changer(L)
"""
['a', 'b']
[0, 'b']
"""
# changer(L[:])
"""
['a', 'b']
['a', 'b']
"""
print(L)
```

## 参数解包

```python
In [2]: def f(a, b, c, d): print(a, b, c, d)

In [3]: args = (1, 2)

In [4]: args += (3, 4)

In [5]: f(*args)
1 2 3 4
```

又或者使用

```python
def f(a, b, c, d): print(a, b, c, d)
args = {'a': 1, 'b': 2, 'c': 3, 'd': 4}
f(**args)
```

## 参数书写位置

**在函数调用中：** 位置参数 --》 关键字参数 --》元组形式--》字典形式
**在函数头部：** 一般参数--》默认参数--》元组形式--》字典形式

```python
def func(name, age=None, *args, **kwargs):
    print(name, age, args, kwargs)

func('ansheng', 18, *(1, 2, 3), **{'blog': 'blog.ansheng.me'})
```

## 全局变量和局部变量

简单的理解全局变量和变量，全局变量可以理解为在当前这个文件内定义的变量，局部变量则是在函数内定义的变量，如下例：

```python
# qa
# 全局变量
n1 = 1
def num():
	# 局部变量
    n2 = 2
    print(n1)
    print(n2)
num()
```

输出的结果

```python
C:\Python35\python.exe F:/Python_code/sublime/Day05/def.py
1
2
```

定义的全局变量都可以在函数内调用，但是不能再函数内修改，局部变量在也不能够直接调用，如果要在函数内修改全局变量，那么就需要用到关键字

```python
n1 = 1
def num():
    n2 = 2
    global n1
    n1 = 3
    print(n1)
    print(n2)
num()
```
执行结果
```python
C:\Python35\python.exe F:/Python_code/sublime/Day05/def.py
3
2
```

## nonlocal 语句

`nonlocal`是用来修改嵌套作用域中的变量，类似于`global`一样，只需要在嵌套函数中声明变量名即可，但是这个变量名是必须已经存在的否则就会报错，如果要修改的变量在作用域中查找不到，那么不会继续到全局或内置作用域中查找。

```python
In [1]: def func1(arg1):
   ...:     n = arg1
   ...:     print(n)
   ...:     def func2():
   ...:         nonlocal n
   ...:         n += 1
   ...:     func2()
   ...:     print(n)
   ...:     

In [2]: func1(10)
10
11
```

## Lambda 表达式

Lambda（Lambda expressions）表达式是用 lambda 关键字创建的匿名函数，Lambda 函数可以用于任何需要函数对象的地方，在语法上，它们被局限于只能有一个单独的表达式。

使用`Lambda`表达式创建函数

```python
>>> f = lambda x,y : x + y
>>> f(1,2)
3
```

使用 def 创建函数

```python
>>> def f(x,y):
...  return x + y
...
>>> f(1,2)
3
```

对于比较简单的函数我们就可以通过 lambda 来创建，它的的好处是缩短行数。

lambda 创建的函数和 def 创建的函数对应关系如图所示：

![Python-Day05-01](https://blog.ansheng.me/images/2016/12/1483017178.png)

### 嵌套 lambda 和作用域

```python
def action(x):
    return (lambda y: x + y)

act = action(99)
print(act)
result = act(2)
print(result)
```

输出为：

```python
<function action.<locals>.<lambda> at 0x1021e6400>
101
```

`lambda`也能够获取到任意上层`lambda`中的变量名：

```python
action = lambda x: (lambda y: x + y)
act = action(99)
print(act)
result = act(3)
print(result)
```

输出为：

```bash
<function <lambda>.<locals>.<lambda> at 0x1029e6400>
102
```

## 测试题

### 第一题

**简述普通参数、指定参数、默认参数、动态参数的区别**

普通参数即是用户在调用函数是填入的参数，且参数位置必须与参数保持一致。

指定参数即在用户调用函数的时候不需要按照函数中参数的位置中所填写，指定参数是需要制定参数对应的值。

默认参数可以写在定义参数的后面，如果用户调用函数是没有制定参数，那么就会用默认参数，如果用户指定了参数，那么用户指定的参数就会代替默认参数。

动态参数可以接受用户输入的任何参数，包括字典、列表、元组等数据类型。

### 第二题

计算传入字符串中数字、字母、空格以及其他的个数

```python
def var(s):
    all_num = 0
    spance_num = 0
    digit_num = 0
    others_num = 0
    for i in s:
        # 检测数字
        if i.isdigit():
            digit_num += 1
        # 检测空格
        elif i.isspace():
            spance_num += 1
        # 检测字母
        elif i.isalpha():
            all_num += 1
        else:
            # 其他
            others_num += 1
    return ("字母：",all_num,"空格：",spance_num,"数字",digit_num,"其他字符",others_num)
num = var("21323 asd*%^*^% &*213asdasdasda sdasdasd")
print(num)
```
执行结果
```python
C:\Python35\python.exe F:/Python_code/sublime/operation/Day05/c.py
('字母：', 21, '空格：', 3, '数字', 8, '其他字符', 8)
```

### 第三题

写函数，判断用户传入的对象（字符串、列表、元组）长度是否大于 5，如果大于 5 就返回 True，如果小于 5 就返回 False

```python
# 定义一个函数num
def num(x):
    # 判断函数的值如果长度大于5就返回True
    if len(x) > 5:
        return True
    # 否则就返回False
    else:
        return False

ret = num(["asd","asdasd","asdasd","asdasd"])
print(ret)
ret = num("asdasdasd")
print(ret)
```

### 第四题

写函数，检查用户传入的对象（字符串、列表、元组）的每一个元素是否含有空内容，如果有空就返回 False

```python
# 定义一个函数num
def num(x):
    # 循环输出num内的所有内容
    for n in x:
        # 数据类型转换为字符串
        n = str(n)
        # 如果有空格就返回False
        if n.isspace():
            return False

ret = num(" ")
print(ret)

ret = num("asdasd")
print(ret)

ret = num(["asd","312",123," "])
print(ret)
```

### 第五题

写函数，检查传入列表的长度，如果大于 2，那么仅保留前两个长度的内容，并将新内容返回给调用者。

```python
def num(x):
    # 如果列表中的长度大于2,那么就输出列表前两个内容，否则就返回一个空
    if len(x) > 2:
        return x[:2]
    else:
        return ""
print(num(["11","22","33"]))

print(num(["33"]))
```

### 第六题

写函数，检查获取传入列表或元组对象的所有奇数位索引对应的元素，并将其作为新列表返回给调用者。

```python
def num(x):
    # 定义一个空列表用于接收奇数位的元素
    resule = []
    # 循环输出列表中的所有元素值
    for n in range(len(x)):
        # 如果列表中的位置为奇数就把值添加到resule列表中
        if n % 2 == 1:
            resule.append(x[n])
    # 然会resule列表中的内容
    return resule

ret = num([11,22,33,44,55,66])
print(ret)
```

### 第七题

写函数，检查传入字典的每一个 value 的长度,如果大于 2，那么仅保留前两个长度的内容，并将新内容返回给调用者。

```python
dic = {"k1": "v1v1", "k2": [1111,22,33,44]}
```

PS:字典中的 value 只能是字符串或列表

代码

```python
def dictt(x):
    # 循环字典中所有的key
    for k in x.keys():
        # 如果字典中k对应的元素是字符串类型就下面的判断
        if type(x[k]) == str:
            # 如果元素的长度大于2
            if len(x[k]) > 2:
                # 那么就让这个元素重新赋值，新的值只保留原来值的前两个
                x[k]=x[k][0:2]
        # 如果字典中k对应的元素类型是列表，就进入下面的判断
        elif type(x[k]) == list:
            # 先把列表中的值全部for循环
            for i in x[k]:
                # 把元素转换为字符串
                string = str(i)
                # 如果元素的长度大于2
                if len(string) > 2:
                    # 获取元素的索引值
                    num = x[k].index(i)
                    # 先把这个元素给删除
                    x[k].pop(x[k].index(i))
                    # 然后再添加一个新的元素，新元素的只保留原来元素的前两个
                    x[k].insert(num,string[:2])
    # 把结果return出来
    return dic
ret = dictt(dic)
print(ret)
```

- 执行结果

```python
C:\Python35\python.exe F:/Python_code/sublime/operation/Day05/h.py
{'k1': 'v1', 'k2': ['11', 22, 33, 44]}
```