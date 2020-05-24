---
title: Python 标准库系列之模块默认全局变量
toc: true
date: 2020-05-23 18:21:46
tags:
- 编码
- 装饰器
top: 3
---
# Python 标准库系列之模块默认全局变量

当我们创建了一个自己写的模块后，那么这个模块本身就自带了好几个全局变量，这些全局变量在每个文件中都存在。

查看当前`py`文件的全局变量

```python
[root@ansheng ~]# echo 'print(vars())' > scripts.py      
[root@ansheng ~]# python scripts.py 
{'__builtins__': <module '__builtin__' (built-in)>, '__name__': '__main__', '__file__': 'scripts.py', '__doc__': None, '__package__': None}
```

## 默认全局变量

|变量名|说明|
|:--:|:--|
|\__doc__|py 文件的注释，是对文件的注释|
|\__file__|获取当前文件路径|
|\__package__ |返回导入的文件所在包，用`.`分隔，如果是当前文件则返回 None|
|\__cached__|返回导入的其他文件`pyc`文件路径,当前文件返回 None|
|\__name\__|如果是主文件则返回`__main__` 否则等于模块名|

> 没有列出来的就是没必要了解的


## 实例

返回`scripts`文件的注释及文件路径

```bash
[root@ansheng ~]# cat scripts.py 
#!/usr/bin/env pyton
# 文件的注释顶格写
"""  Python file comments """
# 输出文件注释
print("comments",__doc__)
# 输出文件路径
print("file path",__file__)
```

执行脚本

```python
[root@ansheng ~]# python scripts.py 
('comments', '  Python file comments ')
# 如果是当前文件则直接返回文件名
('file path', 'scripts.py')
```

`__name__`函数的应用

查看当前目录下面的文件及文件内容

```bash
[root@ansheng ~]# ls -l
total 8
drwxr-xr-x 2 root root 4096 May 24 21:36 lib
-rw-r--r-- 1 root root   80 May 24 21:37 scripts.py
[root@ansheng ~]# ls -l lib/
total 12
-rwxr-xr-x 1 root root  54 May 24 21:36 f1.py
-rw-r--r-- 1 root root   0 May 24 21:34 __init__.py
[root@ansheng ~]# cat lib/f1.py
#!/usr/bin/env python
def echo():
 print("lib/f1.py")
[root@ansheng ~]# cat scripts.py 
#!/usr/bin/env pyton
from lib import f1

if __name__ == "__main__":
  f1.echo()
```
```bash

执行`scripts.py`脚本，脚本会调用`lib/f1.py`文件，而`lib/f1.py`文件会输出`lib/f1.py`，所以执行`scripts.py`文件的时候自然也会输出`lib/f1.py`

```bash
[root@ansheng ~]# python scripts.py 
# 正如我们看到的，会输出下面的内容
lib/f1.py
```

这是我们再创建一个`scripts1.py`文件

```bash
[root@ansheng ~]# touch scripts1.py
```

`scripts1.py`文件内容如下

```bash
[root@ansheng ~]# cat scripts1.py 
#!/usr/bin/env pyton
import scripts
```

文件创建好后执行他，我们会发现什么也没有输出

```bash
[root@ansheng ~]# python scripts1.py
```

然后我们把`scripts.py`脚本文件内容改为如下

```bash
[root@ansheng ~]# cat scripts.py
#!/usr/bin/env pyton
from lib import f1
f1.echo()
```

再次执行`scripts1.py`脚本这是就会输出`lib/f1.py`

```bash
[root@ansheng ~]# python scripts1.py 
lib/f1.py
```

为什么会出现上面的情况呢？

因为原来的`scripts.py`文件加了 if 判断，其意思就是说如果`__name__`的值等于`"__main__"`，那么我就执行 f1.echo()方法，否则就什么也不做，当`scripts.py`文件被我们直接执行的时候的`__name__`返回结果是`"__main__"`，如果被别的文件调用了，那么`__name__`返回的结果是`"scripts"`。

自动把当前目录下面的`bin`目录添加到 python 的`PATH`变量中

目录结构及脚本内容如下

```bash
[root@ansheng ~]# tree /tmp/
/tmp/
├── bin
│   ├── f1.py
│   └── __init__.py
└── scripts.py

1 directory, 3 files
[root@ansheng ~]# cat /tmp/scripts.py 
#!/usr/bin/env pyton
import os
import sys

path = os.path.dirname(__file__)
mod_path = os.path.join(path,"bin")

sys.path.append(mod_path)
for n in sys.path:
    print(n)
```

执行结果

```bash
[root@ansheng ~]# python /tmp/scripts.py 
/tmp
/usr/lib64/python26.zip
/usr/lib64/python2.6
/usr/lib64/python2.6/plat-linux2
/usr/lib64/python2.6/lib-tk
/usr/lib64/python2.6/lib-old
/usr/lib64/python2.6/lib-dynload
/usr/lib64/python2.6/site-packages
/usr/lib64/python2.6/site-packages/gtk-2.0
/usr/lib/python2.6/site-packages
/usr/lib/python2.6/site-packages/setuptools-0.6c11-py2.6.egg-info
/tmp/bin
```