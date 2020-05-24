---
title: Python 全栈之路系列之正则表达式 re 模块
toc: true
date: 2020-05-23 18:21:46
tags:
- 编码
- 正则表达式
top: 4
---

正则表达式并不是 Python 的一部分。正则表达式是用于处理字符串的强大工具，拥有自己独特的语法以及一个独立的处理引擎，效率上可能不如 str 自带的方法，但功能十分强大。得益于这一点，在提供了正则表达式的语言里，正则表达式的语法都是一样的，区别只在于不同的编程语言实现支持的语法数量不同；但不用担心，不被支持的语法通常是不常用的部分。如果已经在其他语言里使用过正则表达式，只需要简单看一看就可以上手了。

## 正则表达式概念

1. 使用单个字符串来描述匹配一系列符合某个句法规则的字符串
2. 是对字符串操作的一种逻辑公式
3. 应用场景：处理文本和数据
4. 正则表示是过程：依次拿出表达式和文本中的字符比较，如果每一个字符都能匹配，则匹配成功；否则匹配失败

## 字符匹配

|字符|描述|
|:--:|:--|
|.|匹配任意一个字符（除了\n）|
|\d \D|数字/非数字|
|\s \S|空白/非空白字符|
|\w \W|单词字符[a-zA-Z0-9]/非单词字符|
|\b \B|单词边界，一个\w 与\W 之间的范围，顺序可逆/非单词边界|

- 匹配任意一个字符

```python
 # 匹配字符串abc，.代表b
 >>> re.match('a.c','abc').group()
'abc'
```

- 数字与非数字

```python
 # 匹配任意一数字
 >>> re.match('\d','1').group()
'1'
 # 匹配任意一个非数字
 >>> re.match('\D','a').group()
'a'
```

- 空白与非空白字符

```python
 # 匹配任意一个空白字符
 >>> re.match("\s"," ").group()
' '
 # 匹配任意一个非空白字符
 >>> re.match("\S","1").group()
'1'
 >>> re.match("\S","a").group()
'a'
```

- 单词字符与非单词字符

> 单词字符即代表[a-zA-Z0-9]

```python
 # 匹配任意一个单词字符
 >>> re.match("\w","a").group()
'a'
 >>> re.match("\w","1").group()
'1'
 # 匹配任意一个非单词字符
 >>> re.match("\W"," ").group()
' '
```

## 次数匹配

|字符|匹配|
|:--|:--|
|*|匹配前一个字符 0 次或者无限次|
|+|匹配前一个字符 1 次或者无限次|
|?|匹配前一个字符 0 次或者 1 次|
|{m}/{m,n}|匹配前一个字符 m 次或者 N 次|
|*?/+?/??|匹配模式变为贪婪模式（尽可能少匹配字符）|

- 介绍

|字符|匹配|
|:--|:--|
|prev?|0 个或 1 个 prev|
|prev*|0 个或多个 prev，尽可能多地匹配|
|prev*?|0 个或多个 prev，尽可能少地匹配|
|prev+|1 个或多个 prev，尽可能多地匹配|
|prev+?|1 个或多个 prev，尽可能少地匹配|
|prev{m}|m 个连续的 prev|
|prev{m,n}|m 到 n 个连续的 prev，尽可能多地匹配|
|prev{m,n}?|m 到 n 个连续的 prev，尽可能少地匹配|
|[abc]|a 或 b 或 c|
|[^abc]|非(a 或 b 或 c)|


- 匹配前一个字符 0 次或者无限次

```python
 >>> re.match('[A-Z][a-z]*','Aaa').group()
'Aaa'
 >>> re.match('[A-Z][a-z]*','Aa').group()
'Aa'
 >>> re.match('[A-Z][a-z]*','A').group()
'A'
```

- 匹配前一个字符 1 次或者无限次

```python
 # 匹配前一个字符至少一次，如果一次都没有就会报错
 >>> re.match('[A-Z][a-z]+','A').group()
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
AttributeError: 'NoneType' object has no attribute 'group'
```
```python
 >>> re.match('[A-Z][a-z]+','Aa').group()
'Aa'
 >>> re.match('[A-Z][a-z]+','Aaaaaaa').group()
'Aaaaaaa'
```

- 匹配前一个字符 0 次或者 1 次

```python
 >>> re.match('[A-Z][a-z]?','A').group()
'A'
 # 只匹配出一个a
 >>> re.match('[A-Z][a-z]?','Aaaa').group()
'Aa'
```

- 匹配前一个字符 m 次或者 N 次

```python
 #匹配前一个字符至少5次
 >>> re.match('\w{5}','asd234').group()
'asd23'
 # 匹配前面的字符6-10次
 >>> re.match('\w{6,10}','asd234').group()
'asd234'
 # 超过的字符就匹配不出来
 >>> re.match('\w{6,10}','asd2313qeadsd4').group()
'asd2313qea'

```

- 匹配模式变为贪婪模式

```python
 >>> re.match(r'[0-9][a-z]*','1bc').group()
'1bc'
 # *?匹配0次或者多次
 >>> re.match(r'[0-9][a-z]*?','1bc').group()
'1'
 # +?匹配一次或者多次，但是只匹配了一次
 >>> re.match(r'[0-9][a-z]+?','1bc').group()
'1b'
 # ??匹配0次或者一次
 >>> re.match(r'[0-9][a-z]??','1bc').group()
'1'
```

> 贪婪匹配和非贪婪匹配


## 边界匹配

|字符|匹配|
|:--|:--|
|^|匹配字符串开头|
|$|匹配字符串结尾|
|\A \Z|指定的字符串必须出现在开头/结尾|

- 匹配字符串开头

```python
 # 必须以指定的字符串开头，结尾必须是@163.com
 >>> re.match('^[\w]{4,6}@163.com$','asdasd@163.com').group()
'asdasd@163.com'
```

- 匹配字符串结尾

```python
 # 必须以.me结尾
 >>> re.match('[\w]{1,20}.me$','ansheng.me').group()
'ansheng.me'
```

- 指定的字符串必须出现在开头/结尾

```python
 >>> re.match(r'\Awww[\w]*\me','wwwanshengme').group()
'wwwanshengme'
```

## 正则表达式分组匹配

- | 匹配左右任意一个表达式

```python
 >>> re.match("www|me","www").group()
'www'
 >>> re.match("www|me","me").group()
'me'
```

- (ab) 括号中表达式作为一个分组 

```python
# 匹配163或者126的邮箱
 >>> re.match(r'[\w]{4,6}@(163|126).com','asdasd@163.com').group()
'asdasd@163.com'
 >>> re.match(r'[\w]{4,6}@(163|126).com','asdasd@126.com').group()
'asdasd@126.com'
```

- (?P<name>)  分组起一个别名 

```python
 >>> re.search("(?P<zimu>abc)(?P<shuzi>123)","abc123").groups()
('abc', '123')
```
- 引用别名为 name 的分组匹配字符串 

```python
 >>> res.group("shuzi")
'123'
 >>> res.group("zimu")
'abc'
```


## re 模块常用的方法

- re.match()

**语法格式：**

```python
match(pattern, string, flags=0)
```

**释意：**

> Try to apply the pattern at the start of the string, returning a match object, or None if no match was found.

**实例：**

```python
 # 从头开始匹配，匹配成功则返回匹配的对象
 >>> re.match("abc","abc123def").group()
'abc'
 # 从头开始匹配，如果没有匹配到对应的字符串就报错
 >>> re.match("\d","abc123def").group()
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
AttributeError: 'NoneType' object has no attribute 'group'
```

- re.search()

**语法格式：**

```python
search(pattern, string, flags=0)
```

**释意：**

> Scan through string looking for a match to the pattern, returning a match object, or None if no match was found.

**实例：**

```python
 # 匹配整个字符串，匹配到第一个的时候就返回匹配到的对象
 >>> re.search("\d","abc1123def").group()
'1'
```

- re.findall()

**语法格式：**

```python
findall(pattern, string, flags=0)
```

**释意：**

> Return a list of all non-overlapping matches in the string.

**实例：**

```python
 # 匹配字符串所有的内容，把匹配到的字符串以列表的形式返回
 >>> re.findall("\d","abc123def456")
['1', '2', '3', '4', '5', '6']
```

- re.split

**语法格式：**

```python
split(pattern, string, maxsplit=0)
```

**释意：**

> Split the source string by the occurrences of the pattern, returning a list containing the resulting substrings.

**实例：**

```python
 # 指定以数字进行分割，返回的是一个列表对象
 >>> re.split("\d+","abc123def4+-*/56")
['abc', 'def', '+-*/', '']
 # 以多个字符进行分割
 >>> re.split("[\d,]","a,b1c")
['a', 'b', 'c']
```

- re.sub()

**语法格式：**

```python
sub(pattern, repl, string, count=0)
```

**释意：**

> Return the string obtained by replacing the leftmost non-overlapping occurrences of the pattern in string by the replacement repl.  repl can be either a string or a callable;
if a string, backslash escapes in it are processed.  If it is a callable, it's passed the match object and must return a replacement string to be used.

**实例：**

```python
 # 把abc替换成def
 >>> re.sub("abc","def","abc123abc")
'def123def'
 # 只替换查找到的第一个字符串
 >>> re.sub("abc","def","abc123abc",count=1)
'def123abc'
```

## 实例

string 方法包含了一百个可打印的 ASCII 字符，大小写字母、数字、空格以及标点符号

```python
 >>> import string
 >>> printable = string.printable
 >>> printable
'0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~ \t\n\r\x0b\x0c'
```

```python
 >>> import re
 # 定义的字符串
 >>> source = '''I wish I may, I wish I migth
... Hava a dish of fish tonight.'''
 # 在字符串中检索wish
 >>> re.findall('wish',source)
['wish', 'wish']
 # 对源字符串任意位置查询wish或者fish
 >>> re.findall('wish|fish',source)
['wish', 'wish', 'fish']
 # 从字符串开头开始匹配wish
 >>> re.findall('^wish',source)    
[]
 # 从字符串开头匹配I wish
 >>> re.findall('^I wish',source)
['I wish']
 # 从字符串结尾匹配fish
 >>> re.findall('fish$',source)   
[]
 # 从字符串结尾匹配fish tonight.
 >>> re.findall('fish tonight.$',source)
['fish tonight.']
 # 查询以w或f开头,后面紧跟着ish的匹配
 >>> re.findall('[wf]ish',source)
['wish', 'wish', 'fish']
 # 查询以若干个w\s\h组合的匹配
 >>> re.findall('[wsh]+',source) 
['w', 'sh', 'w', 'sh', 'h', 'sh', 'sh', 'h']
 # 查询以ght开头，后面紧跟着一个非数字和字母的匹配
 >>> re.findall('ght\W',source)
['ght.']
 # 查询已以I开头，后面紧跟着wish的匹配
 >>> re.findall('I (?=wish)',source)
['I ', 'I ']
 # 最后查询以wish结尾,前面为I的匹配（I出现次数尽量少）
 >>> re.findall('(?<=I) wish',source)
[' wish', ' wish']
```

- 匹配时不区分大小写

```python
 >>> re.match('a','Abc',re.I).group()
'A'
```

- r 源字符串，转义，如果要转义要加两个\\n

```python
 >>> import re
 >>> pa = re.compile(r'ansheng')
 >>> pa.match("ansheng.me")
<_sre.SRE_Match object; span=(0, 7), match='ansheng'>
 >>> ma = pa.match("ansheng.me")
 >>> ma
<_sre.SRE_Match object; span=(0, 7), match='ansheng'>
 # 匹配到的值存到group内
 >>> ma.group()
'ansheng'
 # 返回字符串的所有位置
 >>> ma.span()
(0, 7)
 # 匹配的字符串会被放到string中
 >>> ma.string
'ansheng.me'
 # 实例放在re中
 >>> ma.re
re.compile('ansheng')
```