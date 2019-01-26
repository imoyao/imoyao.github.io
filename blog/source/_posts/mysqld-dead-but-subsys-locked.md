---
title: 记一次 MySQL 错误 —— mysqld-dead-but-subsys-locked
date: 2019-01-25 11:35:56
tags:
- MySQL
categories:
- 工作日常
toc: true
---
记一次`MySQL`服务出错排查过程。

<!--more-->

今天登录管理系统的时候输入账户信息没有反应，后台查看系统日志发现报错信息：
```shell
# in
tailf /var/log/ODSP.log

# out(部分有用信息)
2019-01-25 11:30:07 database [line:263]: Can't connect to local MySQL server through socket '/var/lib/mysql/mysql.sock' (2)
```
## 查看`MySQL`服务状态

```shell
# in
/etc/init.d/mysqld status

# out
mysqld dead but subsys locked
```
## 查看`MySQL`的`log`信息

```shell
# in
tailf /var/log/mysqld.log

# out（截取部分有用信息）
700101 00:28:38 mysqld_safe mysqld from pid file /var/run/mysqld/mysqld.pid ended
700101 00:28:42 mysqld_safe Starting mysqld daemon with databases from /secbox/var/db
700101  0:28:42 [ERROR] This MySQL server doesn't support dates later then 2038
700101  0:28:42 [ERROR] Aborting
```
## 查看系统时间

```shell
[root@master digitools]# date
Wed Jan  1 00:31:52 CST 2070
```
## 重新设置系统时间

```shell
[root@master digitools]# date -s "20190125 11:28:50"
Fri Jan 25 11:28:50 CST 2019
```
## 重新启动`MySQL`服务

```shell
[root@master digitools]# /etc/init.d/mysqld status
mysqld dead but subsys locked

[root@master digitools]# /etc/init.d/mysqld stop
Stopping mysqld:                                           [  OK  ]
[root@master digitools]# /etc/init.d/mysqld start
Starting mysqld:                                           [  OK  ]
# 上面两步命令也可以直接合并为执行 `/etc/init.d/mysqld restart`
[root@master digitools]# /etc/init.d/mysqld status
mysqld (pid  19402) is running...
```
## 日志恢复正常

```shell
190125 11:30:10  InnoDB: Initializing buffer pool, size = 8.0M
190125 11:30:10  InnoDB: Completed initialization of buffer pool
190125 11:30:10  InnoDB: Started; log sequence number 0 398010
190125 11:30:10 [Note] Event Scheduler: Loaded 0 events
190125 11:30:10 [Note] /usr/libexec/mysqld: ready for connections.
Version: '5.1.71'  socket: '/var/lib/mysql/mysql.sock'  port: 3306  Source distribution
```
至此，数据库异常问题修复，前台登录系统恢复正常。

## 参考阅读

* [Year 2038 problem](https://en.wikipedia.org/wiki/Year_2038_problem)