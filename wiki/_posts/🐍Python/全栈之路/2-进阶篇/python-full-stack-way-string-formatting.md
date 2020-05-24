---
title: Python 全栈之路系列之字符串格式化
toc: true
date: 2020-05-23 18:21:46
tags:
- 编码
- 字符串格式化
top: 5
---

> This PEP proposes a new system for built-in string formatting operations, intended as a replacement for the existing '%' string formatting operator.

Python 目前提供的字符串格式化方式有两种：

- 百分号方式
- format 方式

这两种方式在`Python2`和`Python3`中都适用，百分号方式是 Python 一直内置存在的，`format`方式为近期才出来的。

## 旧式%格式化

- 参数格式

```python
%[(name)][flags][width].[precision]typecode
```

- **[(name)]**

可选，用于选择指定的 key

- **[flags]** 

可选，可供选择的值有:

|值|说明|
|:--:|:--|
|+|右对齐；正数前加正好，负数前加负号|
|-|左对齐；正数前无符号，负数前加负号|
|space|右对齐；正数前加空格，负数前加负号|
|0|右对齐；正数前无符号，负数前加负号；用 0 填充空白处|

- **[width]**

可选，占有宽度

- **.[precision]**

可选，小数点后保留的位数

- **typecode**

必选，参数如下：

|值|说明|
|:--:|:--|
|s|获取传入对象的\__str__方法的返回值，并将其格式化到指定位置|
|r|获取传入对象的\__repr__方法的返回值，并将其格式化到指定位置|
|c|整数：将数字转换成其 unicode 对应的值，10 进制范围为 0 <= i <= 1114111（py27 则只支持 0-255）；字符：将字符添加到指定位置|
|o|将整数转换成 八  进制表示，并将其格式化到指定位置|
|x|将整数转换成十六进制表示，并将其格式化到指定位置|
|d|将整数、浮点数转换成十进制表示，并将其格式化到指定位置|
|e|将整数、浮点数转换成科学计数法，并将其格式化到指定位置（小写 e）|
|E|将整数、浮点数转换成科学计数法，并将其格式化到指定位置（大写 E）|
|f| 将整数、浮点数转换成浮点数表示，并将其格式化到指定位置（默认保留小数点后 6 位）|
|F|同上|
|g|自动调整将整数、浮点数转换成 浮点型或科学计数法表示（超过 6 位数用科学计数法），并将其格式化到指定位置（如果是科学计数则是 e；）|
|G|自动调整将整数、浮点数转换成 浮点型或科学计数法表示（超过 6 位数用科学计数法），并将其格式化到指定位置（如果是科学计数则是 E；）|
|%|当字符串中存在格式化标志时，需要用 %%表示一个百分号|
</b>
> **注：**Python中百分号格式化是不存在自动将整数转换成二进制表示的方式

### 格式化实例

- 常用字符串格式化方式

```python
 # %s 代表字符串
 >>> string = "My name is: %s" % ("ansheng")
 >>> string
'My name is: ansheng'
```

- 字符串中出现`%`号的次数要与`%`之后所提供的数据项个数相同，如果需要插入多个数据，则需要将他们封装进一个元组。

```python
 # %s是姓名，%d是年龄，必须是一个整数，不然会报错
 >>> string = "My name is: %s, I am %d years old" % ("anshen", 20)
 >>> string
'My name is: anshen, I am 20 years old'
```

- 给参数起一个名字，后面传值的时候必须是一个字典

```python
 # %(name)s是姓名，%(age)d是年龄，必须是一个整数，传入的值是一个字典格式
 >>> string = "My name is: %(name)s, I am %(age)d years old" % {"name":"anshen", "age":20}
 >>> string
'My name is: anshen, I am 20 years old'
```

- 去浮点数后面的位数

```python
 # %.2f小数后面只取两位
 >>> string = "percent %.2f" % 99.97623
 >>> string
'percent 99.98'
```

- 给浮点数起一个名字(key)

```python
 >>> string = "percent %(pp).2f" % {"pp":99.97623}
 >>> string
'percent 99.98'
```

- 两个百分号代表一个百分号

```python
 >>> string = "percent %(pp).2f%%" % {"pp":99.97623}
 >>> string
'percent 99.98%'
```

## 使用{}和 format 的新格式化

```python
[[fill]align][sign][#][0][width][,][.precision][type]
```

- **[fill]**

可选，空白处填充的字符

- **align**

可选，对齐方式（需配合 width 使用）

|参数|说明|
|:--:|:--|
|<|强制内容左对齐|
|>|强制内容右对齐(默认)|
|＝|强制内容右对齐，将符号放置在填充字符的左侧，且只对数字类型有效。 即使：符号+填充物+数字|
|^|强制内容居中|

- **[sign]**

可选，有无符号数字

|参数|说明|
|:--:|:--|
|+|正号加正，负号加负|
|-|正号不变，负号加负|
|space|正号空格，负号加负|

- **[#]**

可选，对于二进制、八进制、十六进制，如果加上#，会显示 0b/0o/0x，否则不显示

- **[,]**

可选，为数字添加分隔符，如：1,000,000

- **[width]**

可选，格式化位所占宽度

- **[.precision]**

可选，小数位保留精度

- **[type]**

可选，格式化类型

* 传入” 字符串类型 “的参数

|参数|说明|
|:--:|:--|
|s|格式化字符串类型数据|
|空白|未指定类型，则默认是 None，同 s|

* 传入“ 整数类型 ”的参数

|参数|说明|
|:--:|:--|
|b|将 10 进制整数自动转换成 2 进制表示然后格式化|
|c|将 10 进制整数自动转换为其对应的 unicode 字符|
|d|十进制整数|
|o|将 10 进制整数自动转换成 8 进制表示然后格式化；|
|x|将 10 进制整数自动转换成 16 进制表示然后格式化（小写 x）|
|X|将 10 进制整数自动转换成 16 进制表示然后格式化（大写 X）|

* 传入“ 浮点型或小数类型 ”的参数

|参数|说明|
|:--:|:--|
|e| 转换为科学计数法（小写 e）表示，然后格式化；|
|E| 转换为科学计数法（大写 E）表示，然后格式化;|
|f|转换为浮点型（默认小数点后保留 6 位）表示，然后格式化；|
|F| 转换为浮点型（默认小数点后保留 6 位）表示，然后格式化；|
|g| 自动在 e 和 f 中切换|
|G| 自动在 E 和 F 中切换|
|%|显示百分比（默认显示小数点后 6 位）|

### format 格式化实例

- 第一种基本 format 格式化方式

```python
 >>> string = "My name is: {}, I am {} years old, {} Engineer".format("ansheng",20,"Python")
 >>> string
'My name is: ansheng, I am 20 years old, Python Engineer'
```

- 第二种基本 format 格式化方式

```python
 >>> string = "My name is: {}, I am {} years old, {} Engineer".format(*["ansheng",20,"Python"])
 >>> string
'My name is: ansheng, I am 20 years old, Python Engineer'
```

- 给传入的参数加一个索引

```python
 >>> string = "My name is: {0}, I am {1} years old, {0} Engineer".format(*["ansheng",20,"Python"])
 >>> string
'My name is: ansheng, I am 20 years old, ansheng Engineer'
```

- 给参数起一个名字(key)

```python
>>> string = "My name is: {name}, I am {age} years old, {job} Engineer".format(name="ansheng",age=20,job="Python")
>>> string
'My name is: ansheng, I am 20 years old, Python Engineer'
```

- 字典的方式

```python
 >>> string = "My name is: {name}, I am {age} years old, {job} Engineer".format(**{"name":"ansheng","age":20,"job":"Python"})
 >>> string
'My name is: ansheng, I am 20 years old, Python Engineer'
```

- 索引内的索引

```python
 >>> string = "My name is: {0[0]}, I am {0[1]} years old, {0[2]} Engineer".format(["Ansheng",20,"Python"],["An",11,"IT"])
 >>> string
'My name is: Ansheng, I am 20 years old, Python Engineer'
```

- 制定参数类型

```python
 >>> string = "My name is: {:s}, I am {:d} years old, {:f} wage".format("Ansheng",20,66666.55)
 >>> string
'My name is: Ansheng, I am 20 years old, 66666.550000 wage'
```

- 制定名称(key)的值类型

```python
 >>> string = "My name is: {name:s}, I am {age:d} years old".format(name="Ansheng",age=20)
 >>> string
'My name is: Ansheng, I am 20 years old'
```

- 异类实例

```python
 >>> string = "numbers: {:b},{:o},{:d},{:x},{:X}, {:%}".format(15, 15, 15, 15, 15, 15.87623, 2)
 >>> string
'numbers: 1111,17,15,f,F, 1587.623000%'
```

- 索引

```python
 >>> string = "numbers: {0:b},{0:o},{0:d},{0:x},{0:X}, {0:%}".format(15)
 >>> string
'numbers: 1111,17,15,f,F, 1500.000000%'
```