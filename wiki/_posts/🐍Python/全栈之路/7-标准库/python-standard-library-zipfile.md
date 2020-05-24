---
title: Python 标准库系列之 zipfile 模块
toc: true
date: 2020-05-23 18:21:46
tags:
- 编码
- 面向对象
top: 11

---
# Python 标准库系列之 zipfile 模块

The ZIP file format is a common archive and compression standard. This module provides tools to create, read, write, append, and list a ZIP file. 

This module does not currently handle multi-disk ZIP files. It can handle ZIP files that use the ZIP64 extensions (that is ZIP files that are more than 4 GiB in size). It supports decryption of encrypted files in ZIP archives, but it currently cannot create an encrypted file. Decryption is extremely slow as it is implemented in native Python rather than C.

官方文档：https://docs.python.org/3.5/library/zipfile.html

打包

```python
>>> import zipfile
>>> import os
>>> os.system("ls -l")
总用量 0
0
# 以w的方式的时候是打开文件并清空，如果是a方式那么就是追加文件了
>>> z = zipfile.ZipFile('zip_file.zip', 'w')
# 把文件放入压缩包
>>> z.write('/tmp/folder/file.txt')
# 也可以是一个目录
>>> z.write('/tmp/folder/dir')         
# 关闭文件
>>> z.close()
# 查看已经打包的文件
>>> os.system("ls -l zip_file.zip")                     
-rw-rw-r-- 1 ansheng ansheng 238 5月  26 17:08 zip_file.zip
0
```

追加一个文件

```python
# 追加其实就是把模式w换成a
>>> z = zipfile.ZipFile('zip_file.zip', 'a')
>>> z.write('/tmp/folder/file.txt')         
# 关闭文件
>>> z.close()
# 查看包内的文件
>>> z.namelist()
['tmp/folder/sc.pyc', 'tmp/folder/dir/', 'tmp/folder/file.txt']
```

查看压缩包内的所有文件

```python
# z.namelist()获取压缩包内的所有文件，以列表形式返回
>>> z.namelist()
['tmp/folder/sc.pyc', 'tmp/folder/dir/', 'tmp/folder/file.txt']
```

解压

```python
>>> z = zipfile.ZipFile('zip_file.zip', 'r')
# extractall把所有的文件解压到当前目录
>>> z.extractall()
>>> os.system("tree tmp/")         
tmp/
└── folder
    ├── dir
    └── sc.pyc

2 directories, 1 file
0
```

解压一个单独的文件

```python
>>> z = zipfile.ZipFile('zip_file.zip', 'r')
# 返回文件所在路径
>>> z.extract("tmp/folder/sc.pyc")          
'/home/ansheng/tmp/folder/sc.pyc'
>>> os.system("tree tmp/")                  
tmp/
└── folder
    └── sc.pyc

1 directory, 1 file
0
```