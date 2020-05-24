---
title: 安装 Python3 提示找不到 _ctypes 模块
date: 2019-11-12 10:26:18
tags:
- Python
---
今天在虚拟机安装 Python3 的时候遇到下面的报错：
```sh
File "/usr/local/lib/python3.7/multiprocessing/sharedctypes.py", line 10, in <
module>
   import ctypes
   File "/usr/local/lib/python3.7/ctypes/__init__.py", line 7, in <module>
      from _ctypes import Union, Structure, Array
ImportError: No module named '_ctypes'
```
## 解决方案

```shell
# RHEL/Fedora/CentOS
sudo yum install libffi-devel
---
# Debian/Ubuntu:
sudo apt-get install libffi-dev
```
## 参考链接
[ImportError: No module named '_ctypes'](https://stackoverflow.com/questions/27022373/python3-importerror-no-module-named-ctypes-when-using-value-from-module-mul)