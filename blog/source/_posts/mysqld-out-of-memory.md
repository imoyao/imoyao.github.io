---
title: 记一次 MySQL 内存不足错误
date: 2019-11-05 22:24:50
tags:
- MySQL
---
## 缘起
今天在访问博客的时候，登录首页发现无法正常加载博文。因为之前也出现过这种错误，怀疑还是因为数据库的问题，所以果断查看 MySQL 日志：
```shell
vi /var/log/mariadb/mariadb.log 
```
打到文件最后，分析日志：
```shell
191104 17:48:04 mysqld_safe Number of processes running now: 0
191104 17:48:05 mysqld_safe mysqld restarted
191104 17:48:05 [Note] /usr/libexec/mysqld (mysqld 5.5.64-MariaDB) starting as process 11169 ...
191104 17:48:05 InnoDB: The InnoDB memory heap is disabled
191104 17:48:05 InnoDB: Mutexes and rw_locks use GCC atomic builtins
191104 17:48:05 InnoDB: Compressed tables use zlib 1.2.7
191104 17:48:05 InnoDB: Using Linux native AIO
191104 17:48:05 InnoDB: Initializing buffer pool, size = 128.0M
InnoDB: mmap(137756672 bytes) failed; errno 12
191104 17:48:05 InnoDB: Completed initialization of buffer pool
191104 17:48:05 InnoDB: Fatal error: cannot allocate memory for the buffer pool
**错误信息从此行开始**
191104 17:48:05 [ERROR] Plugin 'InnoDB' init function returned error.
191104 17:48:05 [ERROR] Plugin 'InnoDB' registration as a STORAGE ENGINE failed.
191104 17:48:05 [ERROR] mysqld: Out of memory (Needed 128917504 bytes)
191104 17:48:05 [Note] Plugin 'FEEDBACK' is disabled.
191104 17:48:05 [ERROR] Unknown/unsupported storage engine: InnoDB
191104 17:48:05 [ERROR] Aborting

191104 17:48:05 [Note] /usr/libexec/mysqld: Shutdown complete
**服务停止**
191104 17:48:05 mysqld_safe mysqld from pid file /var/run/mariadb/mariadb.pid ended
```
确认是 MySQL 服务的问题，首先手动把 MySQL 启动起来，保证应用正常使用：
```shell
systemctl restart mariadb
```
之后服务恢复正常
## 增加 swap 分区
因为本身内存很小只有 1G，而 5.6（？）之后默认使用 innodb 引擎，这个引擎又很消耗内存。所以最好的办法是使用大内存或者将 MySQL 降级到一个合适的版本，但是，如果不是真的喜欢，谁愿意做一条舔狗呢？如果不是没钱，谁愿意用低配服务器呢。所以，退而求其次的办法就是增加一个 swap 分区，在内存不足时，使用 swap 分区。
接下来记录创建一个 1024M 的 swap 分区的办法。
### 创建 swap 文件
```shell
dd if=/dev/zero of=/swapfile bs=1024 of=1048576 # 1024*1024
```
### 配置 swap 文件
```shell
mkswap /swapfile
```
### 立即启用 swap 文件
而不是重启之后才生效
```shell
swapon /swapfile
```
### 重启生效
```shell
vi /etc/fstab
```
最后一行追加
```shell
/swapfile       swap    swap defaults   0    0
```
### 验证
```shell
[root@VM_0_16_centos imoyao]# free -m
              total        used        free      shared  buff/cache   available
Mem:            991         697          70           0         223         120
Swap:          1023           0        1023
[root@VM_0_16_centos imoyao]# cat /proc/swaps 
Filename				Type		Size	Used	Priority
/swapfile                               file		1048572	520	-2
```
参考[MariaDB 在低配 VPS 上崩溃问题处理方案](https://www.aimz8.com/?p=286)
## 设置 MySQL 自动重启
### 是否设置 MySQL 服务 enable 
```shell
systemctl is-enabled mariadb
```
如果返回不是`enabled`则使用命令`systemctl enable mariadb`进行使能
### 编辑配置
```shell
/etc/systemd/system/multi-user.target.wants/mariadb.service
```
### 修改配置
在`Service`配置项中增加如下配置:
```bash
# nu:30
[Service]
……
Restart=always
RestartSec=3
……
```
### 配置生效
```shell
# 重新启动来重导Systemd配置：
sudo systemctl daemon-reload
# 重新启动MariaDB服务
systemctl restart mariadb
```
参见[如何配置 CentOS7 mariadb 服务在崩溃或重启后自动启动](https://www.codebye.com/how-to-config-centos7-mariadb-service-auto-start-after-reboot-or-crash.html)   
[mariadb 在低配 ECS 上崩溃问题](http://chengms.com/?p=151)  

## 修改 MySQL 配置(调小 innodb_buffer_pool_size 参数)
参见
- [MySQL5.7.12 占用内存过多的原因到底是什么?](https://www.v2ex.com/t/276069)  
- [MySQL 调优之 innodb_buffer_pool_size 大小设置](https://www.v2ex.com/t/276069)  
- [mariadb 内存占用优化](https://segmentfault.com/a/1190000017992793)  
- [MySQL 必须调整的 10 项配置优化](https://segmentfault.com/a/1190000003072283)  
- [MySQL 调优之 innodb_buffer_pool_size 大小设置](https://blog.csdn.net/sunny05296/article/details/78916775)  
- [低配服务器 VPS 运行 MYSQL 经常崩溃：[ERROR] mysqld: Out of memory (Needed 128663552 bytes)](http://www.bluestep.cc/%E4%BD%8E%E9%85%8D%E6%9C%8D%E5%8A%A1%E5%99%A8vps%E8%BF%90%E8%A1%8Cmysql%E7%BB%8F%E5%B8%B8%E5%B4%A9%E6%BA%83%EF%BC%9Aerror-mysqld-out-of-memory-needed-128663552-bytes/)  

## 版本信息
```shell
mysql --version
mysql  Ver 15.1 Distrib 5.5.64-MariaDB, for Linux (x86_64) using readline 5.1
```
```shell
[root@VM_0_16_centos imoyao]# cat /etc/system-release
CentOS Linux release 7.6.1810 (Core) 
```
**注意**：文中以`MariaDB`示例，关于其与`MySQL`的关系在此不做过多说明，如果使用`MySQL`作为数据库，以上配置命令可能略有不同。
## 参考链接
- [“mysqld: out of memory” – 4 major reasons why you get this error](https://bobcares.com/blog/mysqld-out-of-memory/)