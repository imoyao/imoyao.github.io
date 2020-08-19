---
title: PyCharm 最新专业版（2020.2.2）激活
date: 2019-12-25 22:23:02
update: 2020-08-25 22:23:02
tags: 
- PyCharm
- Python
top: 1
subtitle: 如果经济允许，请支持正版软件！
cover: /images/PyCharm.png
---

## 说明

本记录来源网络，仅用于个人记录，若收到官方律师函后果自负。希望不差钱的同学爱护同行，支持正版，去[官网购买 PyCharm Professional](https://www.jetbrains.com/zh-cn/pycharm/buy/#personal?billing=yearly)，组织用户可以在 [这里](https://www.jetbrains.com/zh-cn/pycharm/buy/#discounts?billing=yearly)关注优惠政策。

## 更新
1. 跳转到该开源项目：[ide-eval-resetter: Reset your IDE eval information.](https://gitee.com/pengzhile/ide-eval-resetter)；
2. 下载插件[releases](https://gitee.com/pengzhile/ide-eval-resetter/releases)，安装扩展（类似于Chrome 安装非官方扩展的方法）；
![PyCharm-2020.2](/images/PyCharm-2020-2.png)
3. 点击 `Help` 或 `Get Help` -> `Reset IDE's Eval` 菜单；
4. 重启 IDE；
5. 重新评估，以后每个月重新操作一次。
6. 祝大家早日实现“编辑器自由”！
---
以下为个人记录备用，用于迷路之后的操作，普通使用者可以忽略。
1. 关注公众号，发`?`求助；
2. 收到回复之后破解谜面；
3. 安装 pycryptodome
    ```bash
    pip3 install -i https://pypi.douban.com/simple pycryptodome
    ```
4. 获取地址，得到谜底。
```python
# -*- coding:utf-8 -*-
from Crypto.Hash import MD2
# 原文
txt = "73.25"
# md2加密1亿次
for i in range(100000000):
    txt = MD2.new(txt.encode("utf8")).hexdigest()
print(txt)
```

### PyCharm 和操作系统版本信息
```plain
PyCharm 2020.2 (Professional Edition)
Build #PY-202.6397.98, built on July 27, 2020
Licensed to PyCharm Evaluator
Expiration date: September 21, 2020
Runtime version: 11.0.7+10-b944.20 amd64
VM: OpenJDK 64-Bit Server VM by JetBrains s.r.o.
Windows 10 10.0
GC: ParNew, ConcurrentMarkSweep
Memory: 976M
Cores: 4
Registry: ide.balloon.shadow.size=0
Non-Bundled Plugins: Assets Compressor, BashSupport, com.nvlad.tinypng-optimizer, io.zhile.research.ide-eval-resetter, com.jetbrains.lang.ejs, com.jetbrains.plugins.jade, org.jetbrains.plugins.vue, com.illuminatedcloud2.intellij
```