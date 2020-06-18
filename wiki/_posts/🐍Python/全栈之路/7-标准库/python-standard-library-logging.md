---
title: Python 标准库系列之 logging 模块
toc: true
date: 2020-05-23 18:21:46
tags:
- 编码
- 面向对象
top: 15

---

This module defines functions and classes which implement a flexible event logging system for applications and libraries.

The key benefit of having the logging API provided by a standard library module is that all Python modules can participate in logging, so your application log can include your own messages integrated with messages from third-party modules.

官方文档：https://docs.python.org/3.5/library/logging.html

logging 模块用于便捷记录日志且线程安全。

## 日志级别

|Level|Numeric value|
|:--:|:--|
|CRITICAL|50|
|ERROR|40|
|WARNING|30|
|INFO|20|
|DEBUG|10|
|NOTSET|0|

只有大于当前日志等级的操作才会被记录。

## 实例

写入单文件

代码

```python
#!/usr/bin/env python
# _*_ coding:utf-8 _*_
# 导入logging模块
import logging

# 创建一个log.log日志文件
logging.basicConfig(filename='log.log',
					# 格式化的字符串
                    format='%(asctime)s - %(name)s - %(levelname)s - %(module)s: %(message)s',
                    # 时间
                    datefmt='%Y-%m-%d %H:%M:%S %p',
                    # 错误级别
                    level=logging.NOTSET
                    )

logging.critical('critical')
logging.error('error')
logging.warning('warning')
logging.info('info')
logging.debug('debug')
logging.log(logging.INFO, 'NOTSET')
```

执行结果

```bsh
ansheng@ansheng-me:~$ ls 
log.py
ansheng@ansheng-me:~$ python log.py 
ansheng@ansheng-me:~$ ls
log.log  log.py
ansheng@ansheng-me:~$ cat log.log 
2016-05-27 21:46:15 PM - root - CRITICAL - log: critical
2016-05-27 21:46:15 PM - root - ERROR - log: error
2016-05-27 21:46:15 PM - root - WARNING - log: warning
2016-05-27 21:46:15 PM - root - INFO - log: info
2016-05-27 21:46:15 PM - root - DEBUG - log: debug
2016-05-27 21:46:15 PM - root - INFO - log: NOTSET
```

logging.basicConfig 函数各参数

|参数|说明|
|:--:|:--|
|filename|指定日志文件名|
|filemode|和 file 函数意义相同，指定日志文件的打开模式，'w'或'a'|
|format|指定输出的格式和内容，format 可以输出很多有用信息，如下所示|
|datefmt|指定时间格式，同 time.strftime()|
|level|设置日志级别，默认为 logging.WARNING|

format 参数

|参数|说明|
|:--:|:--|
|%(levelno)s|打印日志级别的数值|
|%(levelname)s|打印日志级别名称|
|%(pathname)s|打印当前执行程序的路径，其实就是 sys.argv[0]|
|%(filename)s|打印当前执行程序名|
|%(funcName)s|打印日志的当前函数|
|%(lineno)d|打印日志的当前行号|
|%(asctime)s|打印日志的时间|
|%(thread)d|打印线程 ID|
|%(threadName)s|打印线程名称|
|%(process)d|打印进程 ID|
|%(message)s|打印日志信息|

## 多文件日志

对于上述记录日志的功能，只能将日志记录在单文件中，如果想要设置多个日志文件，logging.basicConfig 将无法完成，需要自定义文件和日志操作对象。


```python
#!/usr/bin/env python
# _*_ coding:utf-8 _*_

import logging

# 创建文件
file_1 = logging.FileHandler("log1.log", "a")
# 创建写入的日志格式
fmt1 = logging.Formatter(fmt="%(asctime)s - %(name)s - %(levelname)s - %(module)s : %(message)s")
# 文件用格式
file_1.setFormatter(fmt1)

file_2 = logging.FileHandler("log2.log", "a")
fmt2 = logging.Formatter()
file_2.setFormatter(fmt2)

logger1 = logging.Logger("s1", level=logging.ERROR)
logger1.addHandler(file_1)
logger1.addHandler(file_2)

logger1.critical("1111")
```

```python
# 定义文件
file_2_1 = logging.FileHandler('l2_1.log', 'a')
fmt = logging.Formatter()
file_2_1.setFormatter(fmt)

# 定义日志
logger2 = logging.Logger('s2', level=logging.INFO)
logger2.addHandler(file_2_1)
```

如上述创建的两个日志对象

1. 当使用`logger1`写日志时，会将相应的内容写入 l1_1.log 和 l1_2.log 文件中
2. 当使用`logger2`写日志时，会将相应的内容写入 l2_1.log 文件中

## 更多参考
[Python之日志处理（logging模块） - 云游道士 - 博客园](https://www.cnblogs.com/yyds/p/6901864.html)
[python logging模块使用教程 - 简书](https://www.jianshu.com/p/feb86c06c4f4)
[第32天：Python logging 模块详解 - 纯洁的微笑博客](http://www.ityouknow.com/python/2019/10/13/python-logging-032.html)
[Python日志库logging总结-可能是目前为止将logging库总结的最好的一篇文章 - 掘金](https://juejin.im/post/5bc2bd3a5188255c94465d31#heading-6)