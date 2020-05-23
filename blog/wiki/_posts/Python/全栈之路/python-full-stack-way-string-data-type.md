---
title: Python 全栈之路系列之字符串数据类型
toc: true
date: 2020-05-23 18:21:46
tags:
- 编码
- 字符串
---

## 字符串(str)

字符串类型是 python 的序列类型，他的本质就是字符序列，而且 python 的字符串类型是不可以改变的，你无法将原字符串进行修改，但是可以将字符串的一部分复制到新的字符串中，来达到相同的修改效果。

创建字符串类型可以使用单引号或者双引号又或者三引号来创建，实例如下：

单引号

```python
>>> string = 'ansheng'
# type是查看一个变量的数据类型
>>> type(string)
<class 'str'>
```

双引号

```python
>>> string = "ansheng"
# type是查看一个变量的数据类型
>>> type(string) 
<class 'str'>
```

三引号

```python
>>> string = """ansheng"""
>>> type(string)
<class 'str'>
```

还可以指定类型

```python
>>> var=str("string")
>>> var
'string'
>>> type(var)
<class 'str'>
```

### 字符串方法

> 每个类的方法其实都是很多的，无论我们在学习的过程中个还是工作的时候，常用的其实没有多少，所以我们没必要去可以得记那么多，有些方法我们只需要对其有个印象就 ok 了，忘了的时候可以 google 一下。


首字母变大写

> capitalize(self):

```python
>>> name="ansheng"
>>> name.capitalize()
'Ansheng'
```

内容居中，width：字符串的总宽度；fillchar：填充字符，默认填充字符为空格。

> center(self, width, fillchar=None): 

```python
# 定义一个字符串变量，名为"string"，内容为"hello word"
>>> string="hello word"
# 输出这个字符串的长度，用len(value_name)
>>> len(string)
10
# 字符串的总宽度为10，填充的字符为"*"
>>> string.center(10,"*")
'hello word'
# 如果设置字符串的总产都为11，那么减去字符串长度10还剩下一个位置，这个位置就会被*所占用
>>> string.center(11,"*")
'*hello word'
# 是从左到右开始填充
>>> string.center(12,"*")
'*hello word*'
```

统计字符串里某个字符出现的次数,可选参数为在字符串搜索的开始与结束位置。

> count(self, sub, start=None, end=None): 

|参数|描述|
|:--|:--|
|sub|搜索的子字符串;|
|start|字符串开始搜索的位置。默认为第一个字符,第一个字符索引值为 0;|
|end|字符串中结束搜索的位置。字符中第一个字符的索引为 0。默认为字符串的最后一个位置;|

```python
>>> string="hello word"
# 默认搜索出来的"l"是出现过两次的
>>> string.count("l")
2
# 如果指定从第三个位置开始搜索，搜索到第六个位置，"l"则出现过一次
>>> string.count("l",3,6)
1
```

解码

> decode(self, encoding=None, errors=None): 

```python
# 定义一个变量内容为中文
temp = "中文"
# 把变量的字符集转化为UTF-8
temp_unicode = temp.decode("utf-8")
```

编码，针对 unicode

> encode(self, encoding=None, errors=None):

```python
# 定义一个变量内容为中文,字符集为UTF-8
temp = u"中文"
# 编码，需要指定要转换成什么编码
temp_gbk = temp_unicode.encode("gbk")
```

于判断字符串是否以指定后缀结尾，如果以指定后缀结尾返回 True，否则返回 False。

> endswith(self, suffix, start=None, end=None):

|参数|描述|
|:--|:--|
|suffix|后缀，可能是一个字符串，或者也可能是寻找后缀的 tuple|
|start|开始，切片从这里开始|
|end|结束，片到此为止|

```python
>>> string="hello word"
# 判断字符串中是否已"d"结尾，如果是则返回"True"
>>> string.endswith("d")
True
# 判断字符串中是否已"t"结尾，不是则返回"False"
>>> string.endswith("t")
False
# 制定搜索的位置，实则就是从字符串位置1到7来进行判断，如果第七个位置是"d"，则返回True，否则返回False
>>> string.endswith("d",1,7)
False
```

把字符串中的 tab 符号('\t')转为空格，tab 符号('\t')默认的空格数是 8。

> expandtabs(self, tabsize=None):

|参数|描述|
|:--|:--|
|tabsize|指定转换字符串中的 tab 符号('\t')转为空格的字符数|

```python
>>> string="hello       word"
# 输出变量"string"内容的时候会发现中间有一个"\t"，这个其实就是一个`tab`键
>>> string
'hello\tword'
# 把`tab`键换成一个空格
>>> string.expandtabs(1)
'hello word'
# 把`tab`键换成十个空格
>>> string.expandtabs(10)
'hello     word'
```

检测字符串中是否包含子字符串 str，如果指定 start(开始)和 end(结束)范围，则检查是否包含在指定范围内，如果包含子字符串返回开始的索引值，否则返回-1。

> find(self, sub, start=None, end=None):

|参数|描述|
|:--|:--|
|str|指定检索的字符串|
|start|开始索引，默认为 0|
|end|结束索引，默认为字符串的长度|

```python
>>> string="hello word"
# 返回`o`在当前字符串中的位置，如果找到第一个`o`之后就不会再继续往下面寻找了
>>> string.find("o")
4
# 从第五个位置开始搜索，返回`o`所在的位置
>>> string.find("o",5)
7
```

字符串格式，后续文章会提到。

> format(*args, **kwargs): 

检测字符串中是否包含子字符串 str ，如果指定 start（开始） 和 end（结束） 范围，则检查是否包含在指定范围内，该方法与 python find()方法一样，只不过如果 str 不在 string 中会报一个异常。

> index(self, sub, start=None, end=None):

|参数|描述|
|:--|:--|
|str|指定检索的字符串|
|start|开始索引，默认为 0|
|end|结束索引，默认为字符串的长度|

```python
>>> string="hello word"
# 返回字符串所在的位置
>>> string.index("o")
4
# 如果查找一个不存在的字符串那么就会报错
>>> string.index("a")
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
ValueError: substring not found
```

检测字符串是否由字母和数字组成，如果 string 至少有一个字符并且所有字符都是字母或数字则返回 True,否则返回 False

> isalnum(self): 

```python
>>> string="hes2323"
# 如果存在数字或字母就返回`True`，否则返回`False`
>>> string.isalnum()
True
# 中间有空格返回的就是False了
>>> string="hello word"
>>> string.isalnum()
False
```

检测字符串是否只由字母组成。

> isalpha(self): 

```python
# 如果全部都是字母就返回`True`
>>> string="helloword"
>>> string.isalpha()
True
# 否则就返回False
>>> string="hes2323"
>>> string.isalpha()
False
```

检测字符串是否只由数字组成

> isdigit(self):  

```python
# 如果变量里面都是数字就返回`True`，否则就返回`False`
>>> string="hes2323"
>>> string.isdigit()
False
>>> string="2323"
>>> string.isdigit()
True
```

检测字符串是否由小写字母组成

> islower(self): 

```python
# 如果变量内容全部都是小写字母就返回`True`，否则就返回`False`
>>> string="hesasdasd"
>>> string.islower()
True
>>> string="HelloWord"
>>> string.islower()
False
```

检测字符串是否只由空格组成

> isspace(self):  

```python
# 如果变量内容由空格来组成，那么就返回`True`否则就返回`False`
>>> string=" "
>>> string.isspace()
True
>>> string="a"
>>> string.isspace()
False
```

检测字符串中所有的单词拼写首字母是否为大写，且其他字母为小写。

> istitle(self):  

```python
# 如果变量的内容首字母是大写并且其他字母为小写，那么就返回`True`，否则会返回`False`
>>> string="Hello Word"
>>> string.istitle()
True
>>> string="Hello word"
>>> string.istitle()
False
```

检测字符串中所有的字母是否都为大写。

> isupper(self):

```python
# 如果变量值中所有的字母都是大写就返回`True`，否则就返回`False`
>>> string="hello word"
>>> string.isupper()
False
>>> string="HELLO WORD"
>>> string.isupper()
True
```

将序列中的元素以指定的字符连接生成一个新的字符串。

> join(self, iterable): 

```python
>>> string=("a","b","c")
>>> '-'.join(string)
'a-b-c'
```

返回一个原字符串左对齐,并使用空格填充至指定长度的新字符串。如果指定的长度小于原字符串的长度则返回原字符串。

> ljust(self, width, fillchar=None):

|参数|描述|
|:--|:--|
|width|指定字符串长度|
|fillchar|填充字符，默认为空格|

```python
>>> string="helo word"
>>> len(string)
9
# 定义的长度减去字符串的长度,剩下的就开始填充
>>> string.ljust(15,'*')
'helo word******'
```

转换字符串中所有大写字符为小写。

> lower(self):

```python
# 把变量里的大写全部转换成小写
>>> string="Hello WORD"
>>> string.lower()
'hello word'
```

截掉字符串左边的空格或指定字符

> lstrip(self, chars=None):

|参数|描述|
|:--|:--|
|chars|指定截取的字符|

```python
# 从左侧开始删除匹配的字符串
>>> string="hello word"
>>> string.lstrip("hello ")
'word'
```

用来根据指定的分隔符将字符串进行分割，如果字符串包含指定的分隔符，则返回一个 3 元的 tuple，第一个为分隔符左边的子串，第二个为分隔符本身，第三个为分隔符右边的子串。

> partition(self, sep):

|参数|描述|
|:--|:--|
|str|指定的分隔符|

```python
# 返回的是一个元组类型
>>> string="www.ansheng.me"
>>> string.partition("ansheng")
('www.', 'ansheng', '.me')
```

把字符串中的 old(旧字符串)替换成 new(新字符串)，如果指定第三个参数 max，则替换不超过 max 次

> replace(self, old, new, count=None):

|参数|描述|
|:--|:--|
|old|将被替换的子字符串|
|new|新字符串，用于替换 old 子字符串|
|count|可选字符串, 替换不超过 count 次|

```python
>>> string="www.ansheng.me"
# 把就字符串`www.`换成新字符串`https://`
>>> string.replace("www.","https://")
'https://ansheng.me'
# 就字符串`w`换成新字符串`a`只替换`2`次
>>> string.replace("w","a",2)
'aaw.ansheng.me'
```

返回字符串最后一次出现的位置，如果没有匹配项则返回-1。

> rfind(self, sub, start=None, end=None):

|参数|描述|
|:--|:--|
|str|查找的字符串|
|start|开始查找的位置，默认为 0|
|end|结束查找位置，默认为字符串的长度|

```python
>>> string="hello word"
# rfind其实就是反向查找
>>> string.rfind("o")
7
# 指定查找的范围
>>> string.rfind("o",0,6)
4
```

返回子字符串 str 在字符串中最后出现的位置，如果没有匹配的字符串会报异常，你可以指定可选参数`[start:end]`设置查找的区间。

> rindex(self, sub, start=None, end=None):

|参数|描述|
|:--|:--|
|str|查找的字符串|
|start|开始查找的位置，默认为 0|
|end|结束查找位置，默认为字符串的长度|

```python
>>> string="hello word"
# 反向查找索引
>>> string.rindex("o")
7
# 如果没有查找到就报错
>>> string.rindex("a")
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
ValueError: substring not found
```

返回一个原字符串右对齐,并使用空格填充至长度 width 的新字符串。如果指定的长度小于字符串的长度则返回原字符串。

> rjust(self, width, fillchar=None):

|参数|描述|
|:--|:--|
|width|指定填充指定字符后中字符串的总长度|
|fillchar|填充的字符，默认为空格|

```python
>>> string="hello word"
>>> len(string)
10
>>> string.rjust(10,"*")
'hello word'
>>> string.rjust(12,"*")
'**hello word'
```

从右到左通过指定分隔符对字符串进行切片,如果参数 num 有指定值，则仅分隔 num 个子字符串

> rsplit(self, sep=None, maxsplit=None):

|参数|描述|
|:--|:--|
|str|隔符，默认为空格|
|num|分割次数|

```python
>>> string="www.ansheng.me"
>>> string.rsplit(".",1)
['www.ansheng', 'me']
>>> string.rsplit(".",2)
['www', 'ansheng', 'me']
```

删除 string 字符串末尾的指定字符（默认为空格）.

> rstrip(self, chars=None):

|参数|描述|
|:--|:--|
|chars|指定删除的字符|

```python
# 从尾部开始匹配删除
>>> string="hello word"
>>> string.rstrip("d")
'hello wor'
```

从左到右通过指定分隔符对字符串进行切片,如果参数 num 有指定值，则仅分隔 num 个子字符串

> split(self, sep=None, maxsplit=None): 

|参数|描述|
|:--|:--|
|str|分隔符，默认为空格|
|num|分割次数|

```python
>>> string="www.ansheng.me"
# 指定切一次，以`.`来分割
>>> string.split(".",1)
['www', 'ansheng.me']
# 指定切二次，以`.`来分割
>>> string.split(".",2)
['www', 'ansheng', 'me']
```

按照行分隔，返回一个包含各行作为元素的列表，如果 num 指定则仅切片 num 个行.

> splitlines(self, keepends=False): 

|参数|描述|
|:--|:--|
|num|分割行的次数|

```python
# 定义一个有换行的变量，`\n`可以划行
>>> string="www\nansheng\nme"
# 输出内容
>>> print(string)
www
ansheng
me
# 把有行的转换成一个列表
>>> string.splitlines(1)
['www\n', 'ansheng\n', 'me']
```

检查字符串是否是以指定子字符串开头，如果是则返回 True，否则返回 False。如果参数 start 和 end 指定值，则在指定范围内检查。

> startswith(self, prefix, start=None, end=None):

|参数|描述|
|:--|:--|
|str|检测的字符串|
|start|可选参数用于设置字符串检测的起始位置|
|end|可选参数用于设置字符串检测的结束位置|

```python
>>> string="www.ansheng.me"
>>> string.startswith("www")
True
>>> string.startswith("www",3)
False
```

移除字符串头尾指定的字符（默认为空格）

> strip(self, chars=None):

|参数|描述|
|:--|:--|
|chars|移除字符串头尾指定的字符|

```python
>>> string=" www.ansheng.me "
>>> string
' www.ansheng.me '
# 删除空格
>>> string.strip()
'www.ansheng.me'
>>> string="_www.ansheng.me_"
# 指定要把左右两边的"_"删除掉
>>> string.strip("_")
'www.ansheng.me'
```

用于对字符串的大小写字母进行转换，大写变小写，小写变大写

> swapcase(self):

```python
>>> string="hello WORD"
>>> string.swapcase()
'HELLO word'
```

返回"标题化"的字符串,就是说所有单词都是以大写开始，其余字母均为小写。

> title(self):

```python
>>> string="hello word"
>>> string.title()
'Hello Word'
```

根据参数 table 给出的表(包含 256 个字符)转换字符串的字符, 要过滤掉的字符放到 del 参数中。

> translate(self, table, deletechars=None):

|参数|描述|
|:--|:--|
|table|翻译表，翻译表是通过 maketrans 方法转换而来|
|deletechars|字符串中要过滤的字符列表|

将字符串中的小写字母转为大写字母

> upper(self):

```python
>>> string="hello word"
>>> string.upper()
'HELLO WORD'
```

返回指定长度的字符串，原字符串右对齐，前面填充 0

> zfill(self, width):

|参数|描述|
|:--|:--|
|width|指定字符串的长度。原字符串右对齐，前面填充 0|

```python
>>> string="hello word"
>>> string.zfill(10)
'hello word'
>>> string.zfill(20)
'0000000000hello word'
```

## str 类型和 bytes 类型转换

以 UTF-8 编码的时候，一个汉字是三个字节，一个字节是八位

**3.5.x 实例**

代码如下：
```python
#!/usr/bin/env python
# _*_ coding:utf-8 _*_

var = "中文"
for n in var:
    print(n)

print("================")

var2 = "zhongwen"
for n in var2:
    print(n)
```
执行结果：
```python
C:\Python35\python.exe F:/Python_code/sublime/Day03/str.py
中
文
================
z
h
o
n
g
w
e
n
```

**2.7.x 实例**

代码如下：
```python
#!/usr/bin/env python
# _*_ coding:utf-8 _*_

var = "中文"
for n in var:
    print(n)

print("================")

var2 = "zhongwen"
for n in var2:
    print(n)
```

执行结果
```python
C:\Python27\python.exe F:/Python_code/sublime/Day03/str.py
�
�
�
�
�
�
================
z
h
o
n
g
w
e
n
```

通过上面的实例可以知道，`Python3.5.x`在输出中文或者英文的时候是按照一个字符一个字符来输出的，但是在`Python2.7.x`就不这样了，`Python2.7.x`是按照字节来进行输出的，可以看到在输出中文的时候是乱码的，而且还输出了六次，因为在 UTF-8 编码的情况下一个汉字是等于三个字节的，所以输出了六个乱码的字符。

在 Python3.5.x 里面是既可以输出汉字，也可以把输出字节的，利用 bytes 这个方法，bytes 可以将字符串转换为字节
```python
var="中文"
for n in var:
    print(n)
    bytes_list = bytes(n, encoding='utf-8')
    # 十六进制输出
    print(bytes_list)
    for x in bytes_list:
        # 十进制,bin(x)二进制
        print(x,bin(x))
```
输出的结果
```python
# 字符串
中
# 十六进制
b'\xe4\xb8\xad'
# 228=十进制，0b11100100=二进制
228 0b11100100
184 0b10111000
173 0b10101101
文
b'\xe6\x96\x87'
230 0b11100110
150 0b10010110
135 0b10000111
```

b 代表十六进制，\xe4 这样的是一个十六进制的字节

## 其他知识点

### 索引

索引是指某个值在列表或别的数据类型中的一个位置

定义一个列表，查看列表中`Linux`值对应在列表中的位置

```python
>>> list_os = ["Windows","Linux","Mac","Unix"]
>>> list_os.index("Linux")
1
>>> list_os[1]
'Linux'
```

### 使用`\`转义

Python 允许你对某些字符进行转义，以此来实现一些难以单纯用字符描述的效果

```python
# 常用的内容也转义也就是`\n`和`\t`了，`\n`是用来换行的，`\t`是用来代替一个`tab`键
>>> string="My \n Name  \t is"
>>> print(string)
My
 Name    is
 ```

### 使用`+`拼接

你可以使用`+`号将多个字符串或字符串变量拼接起来

```python
>>> a="my "
>>> b="name "
>>> c="is "
>>> d="ansheng"
>>> a+b+c+d
'my name is ansheng'
```

### 切片

切片操作符是序列名后跟一个方括号，方括号中有一对可选的数字，并用冒号分割。注意这与你使用的索引操作符十分相似。记住数是可选的，而冒号是必须的，切片操作符中的第一个数表示切片开始的位置，第二个数表示切片到哪里结束，第三个数表示切片间隔数。如果不指定第一个数，Python 就从序列首开始。如果没有指定第二个数，则 Python 会停止在序列尾。注意，返回的序列从开始位置开始 ，刚好在结束位置之前结束。即开始位置是包含在序列切片中的，而结束位置被排斥在切片外。

```python
>>> os="Linux"
>>> os
'Linux'
>>> os[0:2]
'Li'
>>> os[0:4:2]
'Ln'
```

更多实例如下

|切片符|说明|
|:--|:--|
|[:]|提取从开头到结尾的整个字符串|
|[start:]|从 start 到结尾的字符串|
|[:end]|从开头提取到 end - 1|
|[start:end]|从 start 提取到 end - 1|
|[start : end : setp]|从 start 提取到 end-1，每 setp 个字符提取一个|


索引和切片同时适用于字符串、列表与元组

1. 索引通常用于查找某一个字符串或值
2. 切片通常用于查找某一个范围内的字符串或值

实例：

```python
# 定义一个列表，列表内有三个元素
>>> var=["Linux","Win","Unix"]
# 通过索引取到了一个值
>>> var[0]
'Linux'
# 通过切片取到了多个值
>>> var[0:2]
['Linux', 'Win']
>>> var[1:3]
['Win', 'Unix']
```