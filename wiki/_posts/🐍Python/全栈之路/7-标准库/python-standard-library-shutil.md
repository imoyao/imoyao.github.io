---
title: Python 标准库系列之 shutil 模块
toc: true
date: 2020-05-23 18:21:46
tags:
- 编码
- 面向对象
top: 10

---

> The shutil module offers a number of high-level operations on files and collections of files. In particular, functions are provided which support file copying and removal. For operations on individual files, see also the os module.

对文件、文件夹、压缩包进行处理的模块。

官方文档：https://docs.python.org/3.5/library/shutil.html

## 文件和目录操作

**shutil.copyfileobj(fsrc, fdst[, length])**

将文件内容拷贝到另一个文件中

```python
>>> import shutil
# 循环读取old.txt文件内容并写入到new.txt文件当中
>>> shutil.copyfileobj(open('old.txt','r'), open('new.txt', 'w'))
>>> import os
# 查看复制过去的文件内容
>>> os.system("cat old.txt new.txt") 
old
old
0
```

**shutil.copyfile(src, dst, *, follow_symlinks=True)**

拷贝整个文件，没有第二个文件就创建，有就覆盖

```python
>>> os.system("cat old.txt new.txt")
old
new
0
>>> shutil.copyfile('old.txt', 'new.txt')
# 把第二个文件内容给覆盖了
>>> os.system("cat old.txt new.txt")     
old
old
0
```

**shutil.copymode(src, dst, *, follow_symlinks=True)**

仅拷贝文件权限，文件的内容、组、用户均不变

```python
>>> os.system("ls -l old.txt new.txt")    
-rw-rw-rw- 1 ansheng ansheng 4 5月  26 15:54 new.txt
-rw-rw-r-- 1 ansheng ansheng 4 5月  26 15:52 old.txt
0
>>> shutil.copymode('old.txt', 'new.txt')
# 文件权限都变成644了
>>> os.system("ls -l old.txt new.txt")   
-rw-rw-r-- 1 ansheng ansheng 4 5月  26 15:54 new.txt
-rw-rw-r-- 1 ansheng ansheng 4 5月  26 15:52 old.txt
0
```

**shutil.copystat(src, dst, *, follow_symlinks=True)**

拷贝文件状态的信息，文件必须存在，不 copy 改动时间

```python
>>> os.system("stat old.txt new.txt")  
  文件：'old.txt'
  大小：4               块：8          IO 块：4096   普通文件
设备：801h/2049d        Inode：1835014     硬链接：1
权限：(0664/-rw-rw-r--)  Uid：( 1000/ ansheng)   Gid：( 1000/ ansheng)
最近访问：2016-05-26 15:53:09.813612241 +0800
最近更改：2016-05-26 15:52:54.830640166 +0800
最近改动：2016-05-26 15:52:54.830640166 +0800
创建时间：-
  文件：'new.txt'
  大小：4               块：8          IO 块：4096   普通文件
设备：801h/2049d        Inode：1835024     硬链接：1
权限：(0664/-rw-rw-r--)  Uid：( 1000/ ansheng)   Gid：( 1000/ ansheng)
最近访问：2016-05-26 15:56:22.540041783 +0800
最近更改：2016-05-26 15:54:24.244922722 +0800
最近改动：2016-05-26 15:55:38.353967649 +0800
创建时间：-
0
>>> shutil.copystat('old.txt', 'new.txt')
>>> os.system("stat old.txt new.txt")    
  文件：'old.txt'
  大小：4               块：8          IO 块：4096   普通文件
设备：801h/2049d        Inode：1835014     硬链接：1
权限：(0664/-rw-rw-r--)  Uid：( 1000/ ansheng)   Gid：( 1000/ ansheng)
最近访问：2016-05-26 15:53:09.813612241 +0800
最近更改：2016-05-26 15:52:54.830640166 +0800
最近改动：2016-05-26 15:52:54.830640166 +0800
创建时间：-
  文件：'new.txt'
  大小：4               块：8          IO 块：4096   普通文件
设备：801h/2049d        Inode：1835024     硬链接：1
权限：(0664/-rw-rw-r--)  Uid：( 1000/ ansheng)   Gid：( 1000/ ansheng)
最近访问：2016-05-26 15:53:09.813612000 +0800
最近更改：2016-05-26 15:52:54.830640000 +0800
最近改动：2016-05-26 15:56:48.765143115 +0800
创建时间：-
0
```

**shutil.copy(src, dst, *, follow_symlinks=True)**

拷贝文件和状态信息，同样不 copy 改动时间

```python
>>> os.system("stat old.txt new.txt")  
  文件：'old.txt'
  大小：4               块：8          IO 块：4096   普通文件
设备：801h/2049d        Inode：1835014     硬链接：1
权限：(0664/-rw-rw-r--)  Uid：( 1000/ ansheng)   Gid：( 1000/ ansheng)
最近访问：2016-05-26 15:53:09.813612241 +0800
最近更改：2016-05-26 15:52:54.830640166 +0800
最近改动：2016-05-26 15:52:54.830640166 +0800
创建时间：-
  文件：'new.txt'
  大小：0               块：0          IO 块：4096   普通空文件
设备：801h/2049d        Inode：1835023     硬链接：1
权限：(0664/-rw-rw-r--)  Uid：( 1000/ ansheng)   Gid：( 1000/ ansheng)
最近访问：2016-05-26 15:57:53.448632439 +0800
最近更改：2016-05-26 15:57:53.448632439 +0800
最近改动：2016-05-26 15:57:53.448632439 +0800
创建时间：-
0
>>> shutil.copy2('old.txt', 'new.txt')
>>> os.system("stat old.txt new.txt")  
  文件：'old.txt'
  大小：4               块：8          IO 块：4096   普通文件
设备：801h/2049d        Inode：1835014     硬链接：1
权限：(0664/-rw-rw-r--)  Uid：( 1000/ ansheng)   Gid：( 1000/ ansheng)
最近访问：2016-05-26 15:53:09.813612241 +0800
最近更改：2016-05-26 15:52:54.830640166 +0800
最近改动：2016-05-26 15:52:54.830640166 +0800
创建时间：-
  文件：'new.txt'
  大小：4               块：8          IO 块：4096   普通文件
设备：801h/2049d        Inode：1835023     硬链接：1
权限：(0664/-rw-rw-r--)  Uid：( 1000/ ansheng)   Gid：( 1000/ ansheng)
最近访问：2016-05-26 15:53:09.813612000 +0800
最近更改：2016-05-26 15:52:54.830640000 +0800
最近改动：2016-05-26 15:58:07.938760974 +0800
创建时间：-
0
```

**shutil.ignore_patterns(*patterns)**

This factory function creates a function that can be used as a callable for copytree()‘s ignore argument, ignoring files and directories that match one of the glob-style patterns provided. See the example below.

**shutil.copytree(src, dst, symlinks=False, ignore=None, copy_function=copy2, ignore_dangling_symlinks=False)**

递归的去拷贝文件夹



```python
>>> os.system("tree folder1")
folder1
├── dir
├── file.txt
├── sc.pyc
├── tmp
└── vgauthsvclog.txt.0 -> /tmp/vgauthsvclog.txt.0

2 directories, 3 files
0
# folder2目录必须不存在，symlinks=True只copy链接文件，如果等于False就copy源文件，ignore等于不copy的文件或者目录
>>> shutil.copytree('folder1', 'folder2', symlinks=False, ignore=shutil.ignore_patterns('*.pyc', 'tmp*'))   
>>> os.system("tree folder2")
folder2
├── dir
├── file.txt
└── vgauthsvclog.txt.0

1 directory, 2 files
0
```

**shutil.rmtree(path, ignore_errors=False, onerror=None)**

递归的去删除文件

```python
>>> os.system("ls -d folder2")
folder2
0
>>> shutil.rmtree('folder2')
>>> os.system("ls -d folder2")
ls: 无法访问'folder2': 没有那个文件或目录
512
```

**shutil.move(src, dst, copy_function=copy2)**

递归的去移动文件，它类似 mv 命令，其实就是重命名。

```python
>>> os.system("ls -ld folder1")
drwxrwxr-x 4 ansheng ansheng 4096 5月  26 16:09 folder1
0
>>> shutil.move('folder1', 'folder3')
>>> os.system("ls -ld folder1")      
ls: 无法访问'folder1': 没有那个文件或目录
512
>>> os.system("ls -ld folder3")
drwxrwxr-x 4 ansheng ansheng 4096 5月  26 16:09 folder3
0
```

**shutil.make_archive(base_name, format[, root_dir[, base_dir[, verbose[, dry_run[, owner[, group[, logger]]]]]]])**

Create an archive file (such as zip or tar) and return its name.


```python
>>> os.system("ls -dl folder3")
drwxrwxr-x 4 ansheng ansheng 4096 5月  26 16:21 folder3
0
# /home/ansheng/folder3是保存的文件，gztar是后缀名，/home/ansheng/folder3是要打包的路径
>>> shutil.make_archive("/home/ansheng/folder3", 'gztar', root_dir='/home/ansheng/folder3')
# 返回文件打包放在那儿了
'/home/ansheng/folder3.tar.gz'
>>> os.system("ls -dl /home/ansheng/folder3.tar.gz")
-rw-rw-r-- 1 ansheng ansheng 263 5月  26 16:22 /home/ansheng/folder3.tar.gz
0
```

可选参数如下：

|参数|说明|
|:--:|:--|
|base_name|压缩包的文件名，也可以是压缩包的路径。|
|format|压缩包种类，“zip”, “tar”, “bztar”，“gztar”|
|root_dir|要压缩的文件夹路径（默认当前目录）|
|owner|用户，默认当前用户|
|group|组，默认当前组|

shutil 对压缩包的处理是调用 ZipFile 和 TarFile 两个模块来进行的，后面会介绍这两个模块的使用方法。