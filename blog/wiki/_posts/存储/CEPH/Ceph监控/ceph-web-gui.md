---
title: ceph 开源监控软件对比
toc: true
date: 2020-05-23 11:02:28
tags:

---

# 1. 介绍
目前主流的 Ceph 开源监控软件有：Calamari、VSM、Inkscope、Ceph-Dash、Zabbix 等，下面简单介绍下各个开源组件。

# 2. 开源软件对比
## 2.1 Calamari
Calamari 对外提供了十分漂亮的 Web 管理和监控界面，以及一套改进的 REST API 接口（不同于 Ceph 自身的 REST API），在一定程度上简化了 Ceph 的管理。最初 Calamari 是作为 Inktank 公司的 Ceph 企业级商业产品来销售，红帽 2015 年收购 Inktank 后为了更好地推动 Ceph 的发展，对外宣布 Calamari 开源，秉承开源开放精神的红帽着实又做了一件非常有意义的事情。
![image.png](https://upload-images.jianshu.io/upload_images/2099201-d3f949d1ab326b55.png)

**优点：**
 - 轻量级
 - 官方化
 - 界面友好
 
**缺点：**
 - 不易安装
 - 管理功能滞后

## 2.2 VSM
Virtual Storage Manager (VSM)是 Intel 公司研发并且开源的一款 Ceph 集群管理和监控软件，简化了一些 Ceph 集群部署的一些步骤，可以简单的通过 WEB 页面来操作。
![image.png](https://upload-images.jianshu.io/upload_images/2099201-c2171d57015dfc0d.png)

**优点：**
 - 管理功能好
 - 界面友好 
 - 可以利用它来部署 Ceph 和监控 Ceph
 
**缺点：**
 - 非官方
 - 依赖 OpenStack 某些包

## 2.3 Inkscope
Inkscope 是一个 Ceph 的管理和监控系统，依赖于 Ceph 提供的 API，使用 MongoDB  来存储实时的监控数据和历史信息。
![image.png](https://upload-images.jianshu.io/upload_images/2099201-5fdb25de2e0443f0.png)

**优点：**
 - 易部署
 - 轻量级
 - 灵活（可以自定义开发功能）
 
**缺点：**
 - 监控选项少
 - 缺乏 Ceph 管理功能

2.4 Ceph-Dash
Ceph-Dash 是用 Python 开发的一个 Ceph 的监控面板，用来监控 Ceph 的运行状态。同时提供 REST API 来访问状态数据。
![image.png](https://upload-images.jianshu.io/upload_images/2099201-afd34e5efc737c19.png)

**优点：**
 - 易部署
 - 轻量级
 - 灵活（可以自定义开发功能）
