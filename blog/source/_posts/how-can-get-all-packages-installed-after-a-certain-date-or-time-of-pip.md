---
title: 如何获取到指定日期之后安装的 Python 模块
date: 2019-12-07 14:18:48
tags:
- Python
- pip

categories:

- 工作日常
---
今天在装包的时候，不小心将本该装到 Python 虚拟环境中的包安装到了机器真实环境中，所以需要对其筛选并清除，那么如何找到特定日期之后安装的 Python 包呢？在[这里](https://stackoverflow.com/questions/10256093/how-to-convert-ctime-to-datetime-in-python)找到了解决方案，最后做了一个简单的封装，如下：

```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by imoyao at 2019/12/7 13:33
"""
Usage:
修改 specific_time（like:2019-12-07）,以找到该日期之后安装的 pip 包
"""
import os
import time
import datetime
from pip._internal.utils.misc import get_installed_distributions


def get_all_packages():
    """
    see also: https://stackoverflow.com/questions/10256093/how-to-convert-ctime-to-datetime-in-python
    获取到所有安装的 packages
    :return:
    """
    install_packages = get_installed_distributions()
    return install_packages


def get_after_date_packages(date=None):
    """
    获取指定日期之后安装的 package
    :param date:str, like:2019-12-07
    :return:
    """
    if not date:
        date = datetime.datetime.today().strftime('%Y-%m-%d')

    install_packages = get_all_packages()
    for package in install_packages:
        package_ctime = os.path.getctime(package.location)  # package 创建时间
        time_array = time.localtime(package_ctime)
        strftime_package = time.strftime("%Y-%m-%d", time_array)

        if strftime_package >= date:  # 转换为 %Y-%m-%d 之后比较大小
            # 打印安装时间和 package 名称
            print(time.strftime('%Y-%m-%d-%H:%M:%S', time_array), package)


if __name__ == '__main__':
    specific_time = '2019-11-06'
    get_after_date_packages(specific_time)

```
使用的时候只需要将年月日以`%Y-%m-%d`的格式给出就可以打印出该日期之后安装的包了。

发现一个可以处理`卸载命令的增强，能删除卸载软件包的所有依赖关系问题`的包：

```
pip install pef
```

- [remove a package plus unused dependencies.](https://stackoverflow.com/questions/7915998/does-uninstalling-a-package-with-pip-also-remove-the-dependent-packages)

## 举一反三，Linux环境中的呢？
- [How To List Installed Packages Sorted By Installation Date In Linux](https://www.ostechnix.com/list-installed-packages-sorted-installation-date-linux/)
- [How can one remove all packages installed after a certain date/time?](https://askubuntu.com/questions/548683/how-can-one-remove-all-packages-installed-after-a-certain-date-time)