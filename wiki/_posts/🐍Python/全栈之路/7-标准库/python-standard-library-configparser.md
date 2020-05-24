---
title: Python 标准库系列之 configparser 模块
toc: true
date: 2020-05-23 18:21:46
tags:
- 编码
- 面向对象
top: 8

---
# Python 标准库系列之 configparser 模块

> This module provides the ConfigParser class which implements a basic configuration language which provides a structure similar to what’s found in Microsoft Windows INI files. You can use this to write Python programs which can be customized by end users easily.

configparser 用于处理特定格式的文件，其本质上是利用 open 来操作文件。

**配置文件格式如下：**

```text
# 第一种注释方式
; 第二种注释方式
 
[node1]  # 节点
k1 = v1  # key = value
k2 : v2  # key : value
```

## 实例

创建一个`file.conf`文件，内容为空，然后进入`python`IDE：

```bash
[root@ansheng ~]# touch file.conf 
[root@ansheng ~]# python
Python 2.6.6 (r266:84292, Jul 23 2016, 15:22:56) 
[GCC 4.4.7 20120313 (Red Hat 4.4.7-11)] on linux2
Type "help", "copyright", "credits" or "license" for more information.
>>> 
```

为文件添加节点

```python
>>> import configparser
>>> config = configparser.ConfigParser()
>>> config.read('file.conf', encoding='utf-8')
['file.conf']
# 添加节点"node1","node2",然后写入文件
>>> config.add_section("node1")
>>> config.add_section("node2")
>>> config.write(open('file.conf', 'w'))
```

检查节点是否存在

```python
# 如果文件存在则返回"True"，否则就返回"False"
>>> print(config.has_section('node1'))
True
>>> print(config.has_section('node2'))
True
>>> print(config.has_section('node3'))
False
```

删除节点

```python
# 如果删除的节点存在则返回"True"，否则返回"False"
>>> config.remove_section("node2")
True
>>> config.write(open('file.conf', 'w'))
>>> print(config.has_section('node2'))
False
```

设置节点内的键值对

```python
# 添加完键值对之后别忘记了写入到文件中
>>> config.set('node1', 'Name', "ansheng")
>>> config.set('node1', 'Blog_URL', "https://blog.ansheng.me")
>>> config.set('node1', 'Hostname', "localhost.localhost")
>>> config.set('node1', 'IP', "127.0.0.1")
>>> config.write(open('file.conf', 'w'))
```

检查节点内的 key 是否存在

```python
# 如果节点的Key存在就返回"True"，否则返回"False"
>>> print(config.has_option('node1', 'Name'))
True
>>> print(config.has_option('node1', 'IP'))
True
>>> print(config.has_option('node1', 'VV'))
False
```

删除节点内的 key

```python
# 如果删除的节点存在就返回"True"，否则就返回"False"
>>> config.remove_option('node1', 'IP')
True
>>> config.write(open('file.conf', 'w'))
>>> print(config.has_option('node1', 'IP'))
False
```

获取指定节点下指定 key 的值

```python
# 默认返回的是字符串类型
>>> config.get('node1', 'Name')
'ansheng'
>>> config.get('node1', 'Blog_URL')
'https://blog.ansheng.me'
# 返回的字符串我们可以设置成一下三种数据类型，分别是"int"，"float"，"bool"
# v = config.getint('node1', 'k1')
# v = config.getfloat('node1', 'k1')
# v = config.getboolean('node1', 'k1')
```

获取指定节点下所有的 key

```python
# 返回节点下面所有的Key列表
>>> config.options('node1')
['name', 'blog_url', 'hostname']
```

获取指定节点下所有的键值对

```python
# 返回一个列表，列表中每个元组就是一个键值对
>>> config.items('node1')
[('name', 'ansheng'), ('blog_url', 'https://blog.ansheng.me'), ('hostname', 'localhost.localhost')]
```

获取所有节点

```python
# 获取当前文件中有多少个节点
>>> config.sections()
['node1']
```