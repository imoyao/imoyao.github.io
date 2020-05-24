---
title: Python 标准库系列之 sys 模块
toc: true
date: 2020-05-23 18:21:46
tags:
- 编码
- 面向对象
top: 3

---

> This module provides access to some variables used or maintained by the interpreter and to functions that interact strongly with the interpreter. It is always available.

`sys`模块用于提供对解释器相关的操作

|模块方法|解释说明|
|:--|:--|
|sys.argv|传递到 Python 脚本的命令行参数列表，第一个元素是程序本身路径|
|sys.executable|返回 Python 解释器在当前系统中的绝对路径|
|sys.exit([arg])|程序中间的退出，arg=0 为正常退出|
|sys.path|返回模块的搜索路径，初始化时使用 PYTHONPATH 环境变量的值|
|sys.platform|返回操作系统平台名称，Linux 是`linux2`，Windows 是`win32`|
|sys.stdout.write(str)|输出的时候把换行符`\n`去掉|
|val = sys.stdin.readline()[:-1]|拿到的值去掉`\n`换行符|
|sys.version|获取 Python 解释程序的版本信息|


- 位置参数

```bash
[root@ansheng ~]# cat scripts.py    
#!/usr/bin/env python
import sys
print(sys.argv[0])
print(sys.argv[1])
print(sys.argv[2])
[root@ansheng ~]# python scripts.py canshu1 canshu2  
scripts.py
canshu1
canshu2
```

> sys.argv[0]代表脚本本身，如果用相对路径执行则会显示脚本的名称，如果是绝对路径则会显示脚本名称；

- 程序中途退出

python 在默认执行脚本的时候会由头执行到尾，然后自动退出，但是如果需要中途退出程序, 你可以调用`sys.exit`函数，它带有一个可选的整数参数返回给调用它的程序. 这意味着你可以在主程序中捕获对`sys.exit`的调用。（注：0 是正常退出，其他为不正常，可抛异常事件供捕获!）

原脚本和输出的结果：
```bash
[root@iZ28i253je0Z sys]# cat sys-03.py 
#!/usr/bin/python
# _*_ coding:utf-8 _*_

import sys

print "hello word!"
print "your is pythoner"
[root@iZ28i253je0Z sys]# python sys-03.py 
hello word!
your is pythoner
```

执行脚本之后会输出，下面这两段内容：
```text
hello word!
your is pythoner
```

然后我们在`print "hello word！"`之后让程序退出不执行`print "your is pythoner"`

```bash
[root@iZ28i253je0Z sys]# cat sys-03.py 
#!/usr/bin/python
# _*_ coding:utf-8 _*_

import sys

print "hello word!"
sys.exit()
print "your is pythoner"
[root@iZ28i253je0Z sys]# python sys-03.py 
hello word!
```

> **PS：**sys.exit 从 python 程序中退出，将会产生一个 systemExit 异常，可以为此做些清除除理的工作。这个可选参数默认正常退出状态是 0，以数值为参数的范围为：0-127。其他的数值为非正常退出，还有另一种类型，在这里展现的是 strings 对象类型。


- 获取模块路径

在使用 Python 中用`import`、`_import_`导入模块的时候，那 Python 是怎么判断有没有这个模块的呢?
其实就是根据`sys.path`的路径来搜索你导入模块的名称。

```python
 >>> for i in sys.path:
 ...  print(i)
 ...

C:\Python35\lib\site-packages\pip-8.1.1-py3.5.egg
C:\Python35\python35.zip
C:\Python35\DLLs
C:\Python35\lib
C:\Python35
C:\Python35\lib\site-packages
```

- 获取当前系统平台

**Linux**

```python
 >>> import sys
 >>> sys.platform
'linux2'
```

**Windows**

```python
 >>> import sys
 >>> sys.platform
'win32'
```