---
title: 一种基于 pyinotify 和 rsync 实现的文件目录同步方案
date: 2020-07-22 10:19:18
tags:
- 文件同步
- pyinotify
categories: 项目相关
password: estor
---
## 架构
pyinotify实现目录监控，rsync实现文件同步。
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
        logger.info('123456------------')
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
        logger.info(f'======000000000000-------{is_push}-----')



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