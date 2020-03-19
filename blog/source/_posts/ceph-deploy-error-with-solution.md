---
title: Ceph 错误收集记录
date: 2020-03-16 20:41:54
tags:
- ceph
- processing
categories:
- 工作日常
subtitle: 想想说人生无悔，都是赌气的话。人生若无悔，那该多无趣啊。<br>所以说程序运行遇到报错是很正常的一件事。😜
cover: /images/sarah-kilian-52jRtc2S_VE-unsplash.jpg
---
## [errno 2] error connecting to the cluster
### 解释
安装 ceph 集群之后执行`ceph -s`报错如上，这个是因为认证文件没有分发到个节点导致的无法认证。
### 解决方案
```plain
ceph-deploy admin admin-node node1 [noden] # 后面跟你集群中的所有节点名
```
## daemons have recently crashed
### 解释
一个或多个 Ceph 守护进程最近崩溃了，管理员还没有存档（确认）这个崩溃。这可能表示软件错误、硬件问题(例如，故障磁盘)或其他问题。
### 解决方案
1. 查看 crash 信息
```plain
ceph crash ls-new
```
2. 查看归档信息
```plain
ceph crash info <crash-id>
```
3. 归档 crash 信息
```plain
ceph crash archive <crash-id>
```
你也可以使用`ceph crash archive-all`命令归档 所有信息
更多参考：
- [Crash Module — Ceph Documentation](https://docs.ceph.com/docs/master/mgr/crash/)
- [ceph 报 daemons have recently crashed_网络_lyf0327 的博客-CSDN 博客](https://blog.csdn.net/lyf0327/article/details/103315698/)