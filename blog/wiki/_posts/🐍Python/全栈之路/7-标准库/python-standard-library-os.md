---
title: Python 标准库系列之 os 模块
toc: true
date: 2020-05-23 18:21:46
tags:
- 编码
- 面向对象
top: 2

---

> This module provides a portable way of using operating system dependent functionality. If you just want to read or write a file see open(), if you want to manipulate paths, see the os.path module, and if you want to read all the lines in all the files on the command line see the fileinput module. For creating temporary files and directories see the tempfile module, and for high-level file and directory handling see the shutil module

## os 模块常用方法

|模块方法|说明|
|:--|:--|
|os.getcwd()|获取当前工作目录，即当前 python 脚本工作的目录路径|
|os.chdir("dirname")|改变当前脚本工作目录；相当于 shell 下 cd|
|os.curdir|返回当前目录: ('.')|
|os.pardir|获取当前目录的父目录字符串名：('..')|
|os.makedirs('dirname1/dirname2')|可生成多层递归目录|
|os.removedirs('dirname1')|若目录为空，则删除，并递归到上一级目录，如若也为空，则删除，依此类推|
|os.mkdir('dirname')|生成单级目录；相当于 shell 中 mkdir dirname|
|os.rmdir('dirname')|删除单级空目录，若目录不为空则无法删除，报错；相当于 shell 中 rmdir dirname|
|os.listdir('dirname')|列出指定目录下的所有文件和子目录，包括隐藏文件，并以列表方式打印|
|os.remove()|删除一个文件|
|os.rename("oldname","newname")|重命名文件/目录|
|os.stat('path/filename')|获取文件/目录信息|
|os.sep|输出操作系统特定的路径分隔符，win 下为`\\`,Linux 下为`/`|
|os.linesep|输出当前平台使用的行终止符，win 下为`\t\n`,Linux 下为`\n`|
|os.pathsep|输出用于分割文件路径的字符串|
|os.name|输出字符串指示当前使用平台。win->`nt`; Linux->`posix`|
|os.system("bash command")|运行 shell 命令，直接显示|
|os.environ|获取系统环境变量|
|os.path.abspath(path)|返回 path 规范化的绝对路径|
|os.path.split(path)|将 path 分割成目录和文件名二元组返回|
|os.path.dirname(path)|返回 path 的目录。其实就是 os.path.split(path)的第一个元素|
|os.path.basename(path)|返回 path 最后的文件名。如何 path 以`／`或`\`结尾，那么就会返回空值。即 os.path.split(path)的第二个元素|
|os.path.exists(path)|如果 path 存在，返回 True；如果 path 不存在，返回 False|
|os.path.isabs(path)|如果 path 是绝对路径，返回 True|
|os.path.isfile(path)|如果 path 是一个存在的文件，返回 True。否则返回 False|
|os.path.isdir(path)|如果 path 是一个存在的目录，则返回 True。否则返回 False|
|os.path.join(path1[, path2[,...]])|将多个路径组合后返回，第一个绝对路径之前的参数将被忽略|
|os.path.getatime(path)|返回 path 所指向的文件或者目录的最后存取时间|
|os.path.getmtime(path)|返回 path 所指向的文件或者目录的最后修改时间|

## 常用方法实例

- 获取当前工作目录

```python
 # 获取的进入python时的目录
 >>> os.getcwd()
'/root'
```

- 改变工作目录到`/tmp`下

```python
 # 当前目录是/root
 >>> os.getcwd()
'/root'
 # 切换到/tmp下
 >>> os.chdir("/tmp")
 # 当前目录变成了/tmp
 >>> os.getcwd()     
'/tmp'
```

- 获取`/root`目录下的所有文件，包括隐藏文件

```python
 >>> os.listdir('/root')
['.cshrc', '.bash_history', '.bash_logout', '.viminfo', '.bash_profile', '.tcshrc', 'scripts.py', '.bashrc', 'modules']
```

- 删除`/tmp`目录下的`os.txt`文件

```python
 >>> os.chdir("/tmp") 
 >>> os.getcwd()     
'/tmp'
 >>> os.listdir('./')   
['.ICE-unix', 'yum.log']
 >>> os.remove("yum.log")
 >>> os.listdir('./')    
['.ICE-unix']
```

- 查看`/root`目录信息

```python
 >>> os.stat('/root')        
posix.stat_result(st_mode=16744, st_ino=130817, st_dev=2051L, st_nlink=3, st_uid=0, st_gid=0, st_size=4096, st_atime=1463668203, st_mtime=1463668161, st_ctime=1463668161)
```

- 查看当前操作系统的平台

```python
 >>> os.name
'posix'
```

> win --> `nt`，Linux -> `posix`

- 执行一段`shell`命令

```python
 # 执行的命令要写绝对路径
 >>> os.system("/usr/bin/whoami")    
root
# 0代表命令执行成功，如果命令没有执行成功则返回的是非0
0
```

- 组合一个路径

```python
 >>> a1 = "/"
 >>> a2 = "root"
 >>> os.path.join(a1, a2)
'/root'
```