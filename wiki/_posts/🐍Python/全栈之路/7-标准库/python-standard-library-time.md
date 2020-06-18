---
title: Python 标准库系列之 time 模块
toc: true
date: 2020-05-23 18:21:46
tags:
- 编码
- 面向对象
top: 6

---

> This module provides various functions to manipulate time values.

|方法名|说明|
|:--:|:--|
|time.sleep(int)|等待时间|
|time.time()|输出时间戳，从 1970 年 1 月 1 号到现在用了多少秒|
|time.ctime()|返回当前的系统时间|
|time.gmtime()|将时间戳转换成 struct_time 格式|
|time.localtime()|以 struct_time 格式返回本地时间|
|time.mktime(time.localtime())|将 struct_time 格式转回成时间戳格式|
|time.strftime("%Y-%m-%d %H:%M:%S",time.gmtime())|将 struct_time 格式转成指定的字符串格式|
|time.strptime("2016-01-28","%Y-%m-%d")|将字符串格式转换成 struct_time 格式|

查看当前时间

```python
>>> time.time()
# 以时间戳的形式返回
1464154805.82723
>>> time.ctime()
'Wed May 25 13:42:51 2016'
```

返回当前的昨天时间

```python
>>> time.ctime()
'Wed May 25 13:42:51 2016'
# 今天的时间减去86640秒
>>> time.ctime(time.time()-86640)
'Tue May 24 13:39:58 2016'
```

将时间戳转换成 struct_time 格式

```python
>>> time.gmtime(time.time()-86640)
time.struct\_time(tm\_year=2016, tm\_mon=5, tm\_mday=24, tm\_hour=5, tm\_min=42, tm\_sec=23, tm\_wday=1, tm\_yday=145, tm_isdst=0)
>>> obj = time.gmtime(time.time()-86640)
>>> obj.tm_year
2016
>>> obj.tm_mon
5
>>> "%s-%s-%s" % (obj.tm\_year, obj.tm\_mon, obj.tm_mday)
'2016-5-24'
```

格式化

```python
>>> import time
>>> t = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
>>> t
'2016-09-21 14:04:54'
```