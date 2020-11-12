---
title: Python 如何实现跨主机文件目录同步？（基于 watchdog 和 rsync）
date: 2020-07-22 10:19:18
tags:
- 文件同步
- pyinotify
- watchdog
categories: 项目相关
password: estor
---
## 更新
{% note danger %}
根据该文：[Why you should not use pyinotify | teideal glic deisbhéalach](http://www.serpentine.com/blog/2008/01/04/why-you-should-not-use-pyinotify/)，pyinotify 并**不是**一个监控文件的好的方案，总结一下主要问题有：
1. 函数异常处理不正确
使用 pyinotify 的程序很容易丢失其目录层次结构的各个部分。如果`inotify_add_watch`调用失败并不会调用`OSError`，而是返回一个-1 的错误码，但是没有错误信息告诉调用者到底是什么错误（如添加的是一个不存在的目录还是超出系统 `max_user_watches` 限制）。
2. 性能差
每次要遍历 20 个元素的字典，同时对每个报告的时间执行最多 60 次的属性查找，其中基于%格式最多可达 40 次！在程序运行时，执行 top 查看一下内存占用吧！
3. 锁机制
4. 代码不够 pythonic，接口丑陋。

在[这里· Issue #87 · seb-m/pyinotify](https://github.com/seb-m/pyinotify/issues/87)作者并没有正面回复社区的疑问。
{% endnote %}
鉴于上述原因，本人不再尝试 pyinotify，转向使用[watchdog](https://github.com/gorakhargosh/watchdog)，代码写法参考了[此处](https://stackoverflow.com/a/18599427)和[此处](http://thepythoncorner.com/dev/how-to-create-a-watchdog-in-python-to-look-for-filesystem-changes/)。
## 代码
```python
# coding=utf-8
# !/usr/bin/python

from datetime import datetime
import time
import random

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class MyHandler(FileSystemEventHandler):
    """
    [python watchdog monitoring file for changes - Stack Overflow](https://stackoverflow.com/questions/18599339/python-watchdog-monitoring-file-for-changes/18599427#18599427)
    """

    def __init__(self):
        self.last_modified = datetime.now()
        super(MyHandler).__init__()

    def on_created(self, event):
        print(f"hey, {event.src_path} has been created! last_modified：{self.last_modified}")

    def on_deleted(self, event):
        print(f"Nope! Someone deleted {event.src_path}!")

    def on_modified(self, event):

        print(f'event type: {event.event_type}  path : {event.src_path},last_modified：{self.last_modified}')


def main(path='.'):
    event_handler = MyHandler()
    observer = Observer()
    observer.schedule(event_handler, path=path, recursive=False)
    observer.start()

    try:
        while True:
            # for test
            int_t = random.randint(1, 10)
            with open('test.txt','a+') as f:
                f.write(f'hahahahah-------{int_t}\n')
                time.sleep(int_t)

            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


if __name__ == "__main__":
    main()

```

更多关于文件系统监控的项目可以参考[这里](https://github.com/gorakhargosh/watchdog#why-watchdog)。

---

## 前言
在使用 DRBD 用于块设备同步时由于网络异常可能出现数据不一致，此时为了避免 DRBD 脑裂引入仲裁机制，而引入仲裁机制的时候，我们难免需要使用配置文件记录一部分配置文件的信息，之后，在某一个仲裁成员机上修改配置，配置文件信息应该保证同步到其他成员机上。本文使用[pyinotify](http://pythonic.zoomquiet.top/data/20081023114228/index.html)和 rsync 实现一种文件同步的方案，其中 pyinotify 实现目录监控，rsync 实现文件同步。
{% note info %}
Pyinotify 底层实现依赖于 Linux 的 inofy 机制，而这属于 kernel 2.6.13 以上的特性。
{% endnote %}

## 代码
```python

import os
import datetime

import pyinotify
from loguru import logger

import utils

REFEREE_CONF_DIR = '/etc/digitools/referee/'


class EventHandler(pyinotify.ProcessEvent):
    """
    自定义事件处理封装，参见上方说明
    """
    # # 自定义写入哪个文件，可以自己修改
    # logging.basicConfig(level=logging.INFO, filename=NOTIFY_LOG_FP)

    logger.info("Starting monitor...")

    def process_IN_ATTRIB(self, event):
        self.sync_file()
        logger.info("CREATE event : %s  %s" % (os.path.join(event.path, event.name), datetime.datetime.now()))

    def process_IN_CREATE(self, event):
        self.sync_file()
        logger.debug("CREATE event : %s  %s" % (os.path.join(event.path, event.name), datetime.datetime.now()))

    def process_IN_DELETE(self, event):
        self.sync_file()
        logger.warning("DELETE event : %s  %s" % (os.path.join(event.path, event.name), datetime.datetime.now()))


    def process_IN_MODIFY(self, event):
        self.sync_file()
        logger.info("MODIFY event : %s  %s" % (os.path.join(event.path, event.name), datetime.datetime.now()))

    @staticmethod
    def sync_file(is_push=True):
        """
        同步节点文件
        查询数据库找到所有节点，然后向其他3节点同步配置
        生产卷推，镜像卷拉（关机之后，再起来应该已经发生仲裁，检查即可）
        :return:
        """
        logger.info('----do sth--')



def syncfile_action(sync_info=None, is_push=True):  # TODO: 同步需要对rsync配置进行修改 ODSP\nas\digirsync.py
    """
    通过rsync同步配置文件
    :return: 0 成功 非0 失败
    :param sync_info: info, sync_info = {'src': '/etc/referee/', 'dest': '/etc/referee/'}
    :param is_push: bool, 即为：push/pull
    :return:
    #更多参见： [第2章 rsync(一)：基本命令和用法 - 骏马金龙 - 博客园](https://www.cnblogs.com/f-ck-need-u/p/7220009.html)
    Access via rsync daemon:
      Pull: rsync [OPTION...] [USER@]HOST::SRC... [DEST]
            rsync [OPTION...] rsync://[USER@]HOST[:PORT]/SRC... [DEST]
      Push: rsync [OPTION...] SRC... [USER@]HOST::DEST
            rsync [OPTION...] SRC... rsync://[USER@]HOST[:PORT]/DEST
    """
    # # push
    # rsync -aztvrpog --partial /etc/digitools/referee/ root@10.10.12.61::referee --password-file=/tmp/rsync_pw
    # rsync -aztvrpog /etc/digitools/referee/ rsync://root@10.10.12.61/referee --password-file=/tmp/rsync_pw
    # # pull
    # rsync -aztvrpog --partial  rsync://root@10.10.12.61/referee /etc/digitools/referee/ --password-file=/tmp/rsync_pw
    host = sync_info.get('host')
    module = sync_info.get('module')
    fp = sync_info.get('fp')
    assert fp.endswith('/')  # 为了保证同步不出错，统一风格
    if is_push:
        sync_str = f'{fp} rsync://root@{host}/{module}'
    else:
        sync_str = f'rsync://root@{host}/{module} {fp}'

    cmd = f'rsync -aztvrpog --partial {sync_str} --password-file={digirefer.REFEREE_SYNC_PW_FP}'
    logger.info(cmd)
    retcode, proc = utils.cust_popen(cmd)
    if retcode != 0:
        message = proc.stderr.read()
        logger.debug(message)
    return retcode


def oa_notifier():
    # watch manager
    wml = pyinotify.WatchManager()
    # 可自定义监控文件操作类型
    # multi_event = pyinotify.IN_OPEN | pyinotify.IN_CLOSE_NOWRITE | pyinotify.IN_MODIFY | pyinotify.IN_DELETE | pyinotify.IN_CREATE | pyinotify.IN_ATTRIB
    # wm.add_watch(setting.OA_UPLOAD_PATH, multi_event, rec=True)
    # 可以自己修改的监控的目录
    wml.add_watch(REFEREE_CONF_DIR, pyinotify.ALL_EVENTS, rec=True)
    # event handler
    eh = EventHandler()
    # notifier
    notifier = pyinotify.Notifier(wml, eh)
    notifier.loop()


def main():
    wm1 = pyinotify.WatchManager()
    s1 = pyinotify.Stats()  # Stats is a subclass of ProcessEvent
    notifier1 = pyinotify.ThreadedNotifier(wm1, default_proc_fun=EventHandler(s1))
    notifier1.start()
    wm1.add_watch(REFEREE_CONF_DIR, pyinotify.ALL_EVENTS, rec=True, auto_add=True)


if __name__ == '__main__':
    oa_notifier()
```
## 注意事项

关于双向同步可能导致的无限循环问题，可参考此处：[服务器之间实时双向同步有什么较好的解决方案？ - SegmentFault 思否](https://segmentfault.com/q/1010000002552394)

> 可能会导致死循环，但你可以通过排除同步临时文件（..开头，--exclude-from=your_rsync_exclude.lst）来避免这个问题

>使用 rsync 一定要注意的一点是，源路径如果是一个目录的话，带上尾随斜线和不带尾随斜线是不一样的，不带尾随斜线表示的是整个目录包括目录本身，带上尾随斜线表示的是目录中的文件，不包括目录本身。

例如：
```shell
[root@imoyao ~]# rsync -a /etc /tmp
[root@imoyao ~]# rsync -a /etc/ /tmp
```
第一个命令会在`/tmp`目录下创建`etc`目录，而第二个命令不会在`/tmp`目录下创建`etc`目录，源路径`/etc/`中的所有文件都直接放在`/tmp`目录下。


## 推荐阅读
Windows 可能有用的解决方案：[Tim Golden's Python Stuff: Watch a Directory for Changes](http://timgolden.me.uk/python/win32_how_do_i/watch_directory_for_changes.html)
[python - Detect File Change Without Polling - Stack Overflow](https://stackoverflow.com/questions/5738442/detect-file-change-without-polling)