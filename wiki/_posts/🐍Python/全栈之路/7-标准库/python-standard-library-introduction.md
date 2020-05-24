---
title: Python 标准库系列之模块介绍
toc: true
date: 2020-05-23 18:21:46
tags:
- 编码
- 面向对象
top: 1

---

# Python 标准库系列之模块介绍

Python 的模块其实就是封装了一个或者多个功能的代码集合，以便于重用，模块可以是一个`文件`也可以是一个`目录`，目录的形式称作`包`。

## 模块分类

**内置模块**

内置模块可以理解成当你安装好 python 环境之后，直接可以使用`import`导入的就是内置模块，默认模块路径为：`C:\Python35\lib`，你也可以通过以下方式获取内置模块的路径：

```python
 # 导入sys模块
 >>> import sys
 # 最后一个目录就是内置模块的路径
 >>> for n in sys.path:
 ...  print(n)
 ...

C:\Python35\lib\site-packages\pip-8.1.1-py3.5.egg
C:\Python35\python35.zip
C:\Python35\DLLs
C:\Python35\lib
C:\Python35
C:\Python35\lib\site-packages
```

**第三方模块**

第三方模块通常是开发者自己编写的模块，然后提交到 python 官方的库中，这样我们就可以下载安装使用了，默认安装目录为`C:\Python35\lib\site-packages`，

**自定义模块**

自己编写的模块

## 模块的导入方式

把一个模块当做成一个整体来进行导入

```python
import sys
```

从一个模块中导入特定的变量或者是方法

```python
from sys import path
```

调用的时候直接使用方法名`path`

```python
>>> path
['', 'C:\\Python35\\lib\\site-packages\\pip-8.1.1-py3.5.egg', 'C:\\Python35\\python35.zip', 'C:\\Python35\\DLLs', 'C:\\Python35\\lib', 'C:\\Python35', 'C:\\Python35\\lib\\site-packages']
```

给导入的模块或者方法起一个别名

```python
from sys import path as path_alias
```

调用的时候使用别名`path_alias`

```python
>>> path_alias
['', 'C:\\Python35\\lib\\site-packages\\pip-8.1.1-py3.5.egg', 'C:\\Python35\\python35.zip', 'C:\\Python35\\DLLs', 'C:\\Python35\\lib', 'C:\\Python35', 'C:\\Python35\\lib\\site-packages']
```

添加默认的环境变量,当前生效

```python
sys.path.append("PATH_NAME")
```

可以使用`imp`模块中的`reload`方法重新载入某个模块的方法，例如下面的实例：

```bash
$ cat simple.py 
#!/use/bin/env python

print('Hello, World!')
spam = 1
```
```python
>>> import simple
Hello, World!
>>> simple.spam
1
>>> simple.spam += 1
>>> import simple
>>> simple.spam
2
>>> import imp
>>> imp.reload(simple)
Hello, World!
<module 'simple' from '/Users/ansheng/simple.py'>
>>> simple.spam
1
```

## 模块导入顺序

1. 先在当前脚本目录寻找有没有与导入模块名称相同的文件，如果有就把这个文件当作模块导入（据不完全统计，这是个坑，测试`re`模块没有问题，但是测试`sys`模块就有问题了）
2. 查找模块路径下面有没有对应的模块名
3. 如果没有找到模块名就报错

## import 是如何工作的

模块在被导入的时候会执行以下三个步骤：

1. 通过环境变量找到模块文件；
2. 编译成字节码文件，如果有字节码文件则导入字节码文件；
3. 执行模块中的代码来创建所定义的对象；

以上的三个步骤只有在程序运行时，模块被第一次导入时才会进行。如果已经导入了这个模块然后再次导入的时候会跳过上面的三个步骤，它会直接提取内存中已经加载的模块对象。Python 已经导入的模块会保存在`sys.modules`字典中。

## \_X 与\_\_all__

在模块中的所有变量以`_`开头的都不会被`from *`所导入

```bash
$ cat simple.py 
#!/use/bin/env python

_spam1 = 1
spam2 = 1
```

```python
>>> from simple import *
>>> dir()
# _spam1没有被导入
['__builtins__', '__doc__', '__name__', '__package__', 'spam2']
```

相反的`__all__`列表里面的变量则会被`from *`所导入，没有在`__all__`列表里面的变量则不会被导入

```bash
$ cat simple.py
#!/use/bin/env python

__all__ = ['spam2']

spam1 = 1
spam2 = 1
```

```python
>>> from simple import *
>>> dir()
# spam1没有被导入
['__builtins__', '__doc__', '__name__', '__package__', 'spam2']
```

## 注意事项

据不完全统计，如果导入的模块的名称在当前目录下有这个文件，那么只会把当前目录下的这个文件当作模块，如下演示：

创建一个脚本文件，名称为 scripts

```bash
[root@iZ28i253je0Z ~]# touch scripts.py
```

内容为

```python
#!/usr/bin/env python
# _*_ coding:utf-8 _*_
# 导入一个模块re
import re
# 输出匹配到的字符串abc
print(re.match('\w+',"abc").group())
```

执行脚本

```bash
[root@iZ28i253je0Z ~]# python scripts.py 
# 把匹配到的结果abc输出出来
abc
```

创建一个`.py`文件，名称为`re.py`

```bash
[root@iZ28i253je0Z ~]# touch re.py
```

内容为

```python
#!/usr/bin/env python
# _*_ coding:utf-8 _*_
# 输出内容modus
print("Hello Word")
```

再次执行`scripts.py`脚本

```python
[root@iZ28i253je0Z ~]# python scripts.py 
# 先输出Hello Word
Hello Word
# 然后再报错没有match这个方法
Traceback (most recent call last):
  File "scripts.py", line 6, in <module>
    print(re.match('\w+',"abc").group())
AttributeError: 'module' object has no attribute 'match'
```

这是为什么呢？因为`python`把`re.py`当成模块`re`了，继续往下看：

更改`scripts.py`文件内容如下

```python
[root@iZ28i253je0Z ~]# cat scripts.py 
#!/usr/bin/env python
# _*_ coding:utf-8 _*_

import re
```

`re.py`文件内容不变，然后我们在执行脚本`scripts.py`

```python
[root@iZ28i253je0Z ~]# python scripts.py 
Hello Word
```

看到了吧，他会把`re.py`文件内的代码拿到`scripts.py`文件中去执行，这是个坑，最好别踩。

## 导入当前目录下子目录下的文件

```bash
[root@ansheng ~]# tree ./
./
├── modules
│   ├── __init__.py
│   ├── lib01.py
│   └── lib02.py
└── scripts.py

1 directory, 4 files
[root@ansheng ~]# cat scripts.py 
#!/usr/bin/env python
# 导入modules包下面的lib01模块
from modules import lib01
# 导入modules包下面的lib02模块
from modules import lib02
[root@ansheng ~]# cat modules/__init__.py 
#!/usr/bin/env python
[root@ansheng ~]# cat modules/lib01.py 
#!/usr/bin/env python
# lib01.py文件会输出"Hello lib01"
print("Hello lib01")
[root@ansheng ~]# cat modules/lib02.py  
#!/usr/bin/env python
# lib02.py文件会输出"Hello lib02"
print("Hello lib02")
```

执行结果

```python
[root@ansheng ~]# python scripts.py
# 会执行modules/lib02.py与modules/lib01.py文件内容
Hello lib01
Hello lib02
```

> 包含目录下的文件时需要在目录下声明一个`__init__.py`文件，即使这个文件是空的也可以。

## 如何安装 Python 第三方模块

Python 官方为我们提供了第三方库，那么如何安装这些库呢？

安装第三方库有两种方式：

1. 第一种就是使用 python 自带的仓库 pip 进安装
2. 第二种就是使用源码进行安装

## PIP 方式安装

首先用 yum 安装`python-pip`软件包

```bash
[root@ansheng ~]# yum  install python-pip
```

安装完成之后可以使用`pip -V`查看安装版本

```bash
[root@ansheng ~]# pip -V
pip 7.1.0 from /usr/lib/python2.6/site-packages (python 2.6)
```

这次就以`requests`模块为例把，先查看当前系统有没有安装`requests`模块

```bash
[root@ansheng ~]# python
Python 2.6.6 (r266:84292, Jul 23 2015, 15:22:56) 
[GCC 4.4.7 20120313 (Red Hat 4.4.7-11)] on linux2
Type "help", "copyright", "credits" or "license" for more information.
# 如果没有安装在导入的时候就会报错
>>> import requests
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
ImportError: No module named requests
>>> exit()
```

用`pip`的方式安装`requests`模块

```bash
[root@ansheng ~]# pip install requests
```

安装完成之后进入`python`解释器导入`requests`模块，看看能不能导入成功

```bash
[root@ansheng ~]# python
Python 2.6.6 (r266:84292, Jul 23 2015, 15:22:56) 
[GCC 4.4.7 20120313 (Red Hat 4.4.7-11)] on linux2
Type "help", "copyright", "credits" or "license" for more information.
>>> import requests
```

安装成功。

卸载执行`pip uninstall`加模块名

```bash
[root@ansheng ~]# pip uninstall requests
```

## 源码包方式安装

下载模块`requests`的源码包

```bash
[root@ansheng ~]# git clone git://github.com/kennethreitz/requests.git
Initialized empty Git repository in /root/requests/.git/
remote: Counting objects: 17546, done.
remote: Compressing objects: 100% (2/2), done.
remote: Total 17546 (delta 0), reused 0 (delta 0), pack-reused 17544
Receiving objects: 100% (17546/17546), 5.04 MiB | 46 KiB/s, done.
Resolving deltas: 100% (11232/11232), done.
```

查看下载下来的文件

```bash
[root@ansheng ~]# cd requests/
[root@ansheng requests]# ls
AUTHORS.rst      docs  HISTORY.rst  Makefile     NOTICE      requests                    requirements.txt  tests
CONTRIBUTING.md  ext   LICENSE      MANIFEST.in  README.rst  requirements-to-freeze.txt  setup.py
```

执行`python setup.py install`进行编译安装

```bash
[root@ansheng requests]# python setup.py install
```

验证是否安装成功

```bash
[root@ansheng requests]# python
Python 2.6.6 (r266:84292, Jul 23 2015, 15:22:56) 
[GCC 4.4.7 20120313 (Red Hat 4.4.7-11)] on linux2
Type "help", "copyright", "credits" or "license" for more information.
>>> import requests
```

安装成功，以上就是`Python`第三方模块的两种安装方式。