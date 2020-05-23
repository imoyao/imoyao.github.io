---
title: Python 全栈之路系列之文件操作
toc: true
date: 2020-05-23 18:21:46
tags:
- 编码
- 文件操作
---

Python 可以对文件进行查看、创建等功能，可以对文件内容进行添加、修改、删除，且所使用到的函数在 Python3.5.x 为`open`，在 Python2.7.x 同时支持`file`和`open`，但是在 3.5.x 系列移除了`file`函数。

## Python 文件打开方式

```python
文件句柄 = open('文件路径','打开模式')
```

> **Ps：**文件句柄相当于于变量名，文件路径可以写为绝对路径也可以写为相对路径。

## Python 打开文件的模式

基本的模式

|模式|说明|注意事项|
|:--:|:--|:--|
|r|只读模式|文件必须存在|
|w|只写模式|文件不存在则创建文件，文件存在则清空文件内容|
|x|只写模式|文件不可读，文件不存在则创建，存在则报错|
|a|追加模式|文件不存在创建文件，文件存在则在文件末尾添加内容|

带`+`的模式

|模式|说明|
|:--:|:--|
|r+|读写|
|w+|写读|
|x+|写读|
|a+|写读|

带`b`的模式

|模式|说明|
|:--:|:--|
|rb|二进制读模式|
|wb|二进制写模式|
|xb|二进制只写模式|
|ab|二进制追加模式|

> **提示：**以 b 方式打开时，读取到的内容是字节类型，写入时也需要提供字节类型

带`+`带`b`的模式

|模式|说明|
|:--:|:--|
|rb+|二进制读写模式|
|wb+|二进制读写模式|
|xb+|二进制只写模式|
|ab+|二进制读写模式|

## Python 文件读取方式

|模式|说明|
|:--|:--|
|read([size])|读取文件全部内容，如果设置了 size，那么久读取 size 字节|
|readline([size])|一行一行的读取|
|readlines()|读取到的每一行内容作为列表中的一个元素|

测试的文件名是`hello.tx"`，文件内容为：

```text
Hello Word!
123
abc
456
abc
789
abc
```

**read**

代码：

```python
# 以只读的方式打开文件hello.txt
f = open("hello.txt","r")
# 读取文件内容赋值给变量c
c = f.read()
# 关闭文件
f.close()
# 输出c的值
print(c)
```

输出结果：

```powershell
C:\Python35\python.exe F:/Python_code/sublime/Day06/file.py
Hello Word!
123
abc
456
abc
789
abc
```

**readline**

代码：

```python
# 以只读模式打开文件hello.txt
f = open("hello.txt","r")
# 读取第一行
c1 = f.readline()
# 读取第二行
c2 = f.readline()
# 读取第三行
c3 = f.readline()
# 关闭文件
f.close()
# 输出读取文件第一行内容
print(c1)
# 输出读取文件第二行内容
print(c2)
# 输出读取文件第三行内容
print(c3)
```

输出结果：

```powershell
C:\Python35\python.exe F:/Python_code/sublime/Day06/file.py
Hello Word!

123

abc
```

**readlines**

```python
# 以只读的方式打开文件hello.txt
f = open("hello.txt","r")
# 将文件所有内容赋值给c
c = f.readlines()
# 查看数据类型
print(type(c))
# 关闭文件
f.close()
# 遍历输出文件内容
for n in c:
    print(n)
```

结果

```powershell
C:\Python35\python.exe F:/Python_code/sublime/Day06/file.py
# 输出的数据类型
<class 'list'>
Hello Word!

123

abc

456

abc

789

abc
```

## Python 文件写入方式

|方法|说明|
|:--|:--|
|write(str)|将字符串写入文件|
|writelines(sequence or strings)|写多行到文件，参数可以是一个可迭代的对象，列表、元组等|

**write**

代码：

```python
# 以只读的模式打开文件write.txt，没有则创建，有则覆盖内容
file = open("write.txt","w")
# 在文件内容中写入字符串test write
file.write("test write")
# 关闭文件
file.close()
```

`write.txt`文件内容为：

```python
test write
```

**writelines**

代码：

```python
# 以只读模式打开一个不存在的文件wr_lines.txt
f = open("wr_lines.txt","w",encoding="utf-8")
# 写入一个列表
f.writelines(["11","22","33"])
# 关闭文件
f.close()
```

`wr_lines.txt`文件内容：

```python
112233
```

## Python 文件操作所提供的方法

**close(self):**

关闭已经打开的文件

```python
f.close()
```

**fileno(self):**

文件描述符

```python
 f = open("hello.txt","r")
ret = f.fileno()
f.close()
print(ret)
```

执行结果：

```python
3
```

**flush(self):**

刷新缓冲区的内容到硬盘中

```python
f.flush()
```

**isatty(self):**

判断文件是否是 tty 设备，如果是 tty 设备则返回`True`，否则返回`False`

```python
f = open("hello.txt","r")
ret = f.isatty()
f.close()
print(ret)
```

返回结果：

```python
C:\Python35\python.exe F:/Python_code/sublime/Day06/file.py
False
```

**readable(self):**

是否可读，如果可读返回`True`，否则返回`False`

```python
f = open("hello.txt","r")
ret = f.readable()
f.close()
print(ret)
```

返回结果：

```python
C:\Python35\python.exe F:/Python_code/sublime/Day06/file.py
True
```

**readline(self, limit=-1):**

每次仅读取一行数据

```python
f = open("hello.txt","r")
print(f.readline())
print(f.readline())
f.close()
```

返回结果：

```python
C:\Python35\python.exe F:/Python_code/sublime/Day06/file.py
Hello Word!

123
```

**readlines(self, hint=-1):**

把每一行内容当作列表中的一个元素

```python
f = open("hello.txt","r")
print(f.readlines())
f.close()
```

返回结果：

```python
C:\Python35\python.exe F:/Python_code/sublime/Day06/file.py
['Hello Word!\n', '123\n', 'abc\n', '456\n', 'abc\n', '789\n', 'abc']
```

- tell(self):

获取指针位置

```python
f = open("hello.txt","r")
print(f.tell())
f.close()
```

返回结果:

```python
C:\Python35\python.exe F:/Python_code/sublime/Day06/file.py
0
```

**seek(self, offset, whence=io.SEEK_SET):**

指定文件中指针位置

```python
f = open("hello.txt","r")
print(f.tell())
f.seek(3)
print(f.tell())
f.close()
```

执行结果

```python
C:\Python35\python.exe F:/Python_code/sublime/Day06/file.py
0
3
```

**seekable(self):**

指针是否可操作

```python
f = open("hello.txt","r")
print(f.seekable())
f.close()
```

执行结果

```python
C:\Python35\python.exe F:/Python_code/sublime/Day06/file.py
True
```

**writable(self):**

是否可写

```python
f = open("hello.txt","r")
print(f.writable())
f.close()
```

执行结果

```python
C:\Python35\python.exe F:/Python_code/sublime/Day06/file.py
False
```

**writelines(self, lines):**

写入文件的字符串序列，序列可以是任何迭代的对象字符串生产，通常是一个`字符串列表`。

```python
f = open("wr_lines.txt","w")
f.writelines(["11","22","33"])
f.close()
```

执行结果

```python
112233
```

**read(self, n=None):**

读取指定字节数据，后面不加参数默认读取全部

```python
f = open("wr_lines.txt","r")
print(f.read(3))
f.seek(0)
print(f.read())
f.close()
```

执行结果

```python
C:\Python35\python.exe F:/Python_code/sublime/Day06/file.py
112
112233
```

**write(self, s):**

往文件里面写内容

```python
f = open("wr_lines.txt","w")
f.write("abcabcabc")
f.close()
```

文件内容

```python
abcabcabc
```

## 同时打开多个文件

为了避免打开文件后忘记关闭，可以通过管理上下文，即：

```python
with open('log','r') as f:
 代码块
```

如此方式，当 with 代码块执行完毕时，内部会自动关闭并释放文件资源。

在 Python 2.7 及以后，with 又支持同时对多个文件的上下文进行管理，即：

```python
with open('log1') as obj1, open('log2') as obj2:
    pass
```