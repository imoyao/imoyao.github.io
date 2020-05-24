---
title: 如何在 Linux 上安装 MySQL？
date: 2019-06-23 17:26:26
tags:
- MySQL
categories:
- 工作日常

toc: true
---
在`Linux`上面安装`MySQL`本应该是很容易的一件事，但是有的时候不注意细节还是很容易“翻车”，出现一些预料不到的问题。本文在实践中做一个简单的记录。

<!--more-->

# 工作环境
## Linux
```bash
[root@172 mysql]# uname -a
Linux 172.18.1.117 3.10.0-957.el7.x86_64 #1 SMP Thu Nov 8 23:39:32 UTC 2018 x86_64 x86_64 x86_64 GNU/Linux
# 发行版本
[root@172 mysql]# cat /etc/redhat-release
CentOS Linux release 7.6.1810 (Core) 
```
## MySQL 版本
```bash
# 安装完成之后才可以查询到
[root@172 mysql]# mysql --version
mysql  Ver 14.14 Distrib 5.7.26, for linux-glibc2.12 (x86_64) using  EditLine wrapper
```
# 下载
点击[此链接](https://dev.mysql.com/downloads/mysql/)选择适宜版本下载；  
如图所示进行选择

![选择合适版本下载](/images/download-mysql.png)

或者使用`wget`下载：
```bash
wget https://dev.mysql.com/get/Downloads/MySQL-5.7/mysql-5.7.26-linux-glibc2.12-x86_64.tar.gz
```

# 解压
我一般习惯在工作目录新建`temp`文件夹，然后存放这些临时文件。
```bash
pwd
/root/temp/
tar -xzvf mysql-5.7.26-linux-glibc2.12-x86_64.tar.gz
# 省略解压结果
……
```
# 创建安装目录并切换
```bash
# 创建文件夹
mkdir /usr/local/mysql
# 将解压文件移动到新建目录
mv mysql-5.7.26-linux-glibc2.12-x86_64/* /usr/local/mysql/
# 切换目录
cd /usr/local/mysql
```
# 检查并创建用户和用户组
```bash
[root@localhost local]# cat /etc/group | grep mysql
[root@localhost local]# cat /etc/passwd |grep mysql
[root@localhost local]# groupadd mysql
[root@localhost local]# useradd -r -g mysql mysql
```
## 创建数据存储目录并赋权
**注意**：忘记授权会出问题，各种各样的问题。我第一次安装的时候没有新建用户并赋予相应权限，导致安装出现
`Starting MySQL... ERROR! The server quit without updating PID file (/var/lib/mysql/xxx.pid).`等各种问题。
```bash
mkdir data
# 用户赋权
chown -R mysql mysql/
chgrp -R mysql mysql/
```
# 安装并初始化

```bash
/usr/local/mysql/bin/mysqld --initialize --user=mysql --basedir=/usr/local/mysql/ --datadir=/usr/local/mysql/data/   
--pid-file=/usr/local/mysql/data/mysql.pid --lc_messages_dir=/usr/local/mysql/share --lc_messages=en_US
```
**注意**:
1. 第一次安装时没有设置`--lc_messages_dir`和 `--lc_messages`出现以下报错，所以建议直接使用完整的命令，如果已经出现下面的报错。可以使用`rm -rf /usr/local/mysql/data/*`将数据删除之后重新初始化；
```bash
2019-06-23T08:38:15.774307Z 0 [ERROR] Can't find error-message file '/usr/local/mysql/share/errmsg.sys'. Check error-message file location and 'lc-messages-dir' configuration directive.
```
2. 此步骤如果出现`ERROR`错误一定要注意解决，不能继续操作，如：
    ```bash
    [ERROR] Can't find error-message file '/usr/local/mysql/share/errmsg.sys'. Check error-message file location and 'lc-messages-dir' configuration directive.
    ```
3. 记住最后一行生成的随机密码，安装成功后第一次登录需要使用：
    ```bash
    # 此处密码随机生成，注意记录
    2019-06-23T08:52:37.416821Z 1 [Note] A temporary password is generated for root@localhost: PDRO-ab.a8jd
    ```
4. 最容易出现这个错误：`Starting MySQL. ERROR! The server quit without updating PID file`，网上搜到的解决方案没有啥用，我本次安装走到这里没有出现这个错误，但是下面*启动服务*环节出现该报错，使用`rm  /etc/my.cnf -rf`居然有用，暂时不知道造成原因。
## 使用 mysqld_safe 启动服务
```bash
/usr/local/mysql/bin/mysqld_safe --user=mysql
2019-06-23T09:00:10.100530Z mysqld_safe error: log-error set to '/var/log/mariadb/mariadb.log', however file don't exists. Create writable for user 'mysql'.
```
根据提示修改配置或者新建`log`日志存放目录
```bash
[root@172 mysql]# mkdir /var/log/mariadb
[root@172 mysql]# touch /var/log/mariadb/mariadb.log
```
再次启动
```bash
[root@172 mysql]# bin/mysqld_safe --user=mysql
2019-06-23T09:00:58.541328Z mysqld_safe Logging to '/var/log/mariadb/mariadb.log'.
2019-06-23T09:00:58.546897Z mysqld_safe Directory '/var/lib/mysql' for UNIX socket file don't exists.
```
## 根据报错信息修改 my.cnf 中的配置项
```bash
[root@172 mysql]# vi /etc/my.cnf
# 此处省略，每个人的配置不一样（我已经将该文件删除了，没办法记住怎么配置的了，这里的错误信息很明确，根据错误修改到不报错即可）
[root@172 mysql]# bin/mysqld_safe --user=mysql
2019-06-23T09:03:54.795490Z mysqld_safe Logging to '/var/log/mariadb/mariadb.log'.
2019-06-23T09:03:54.845647Z mysqld_safe Starting mysqld daemon with databases from /usr/local/mysql/data
2019-06-23T09:03:55.148856Z mysqld_safe mysqld from pid file /var/run/mariadb/mariadb.pid ended
```
## 加入开机自启动项
将`/usr/local/mysql/support-files/mysql.server` 拷贝为`/etc/init.d/mysql`并设置运行权限，这样就可以使用`service mysql`命令启动/停止服务，
否则就只能使用`/usr/local/mysql/bin/mysqld_safe`命令来启动服务
如果自定义了安装路径,还需要把`mysql.server`中`basedir`的相关路径，改为自定义的路径，默认路径是`/usr/local/mysql`。本文使用默认路径，所以不用修改。
```bash
[root@dbserver support-files]# cp mysql.server /etc/init.d/mysql  
[root@dbserver support-files]# chmod +x /etc/init.d/mysql 
-- 把mysql注册为开机启动的服务
[root@dbserver support-files]# chkconfig --add mysql  
-- 查看是否添加成功
[root@dbserver support-files]#  chkconfig --list mysql  
Note: This output shows SysV services only and does not include native
      systemd services. SysV configuration data might be overridden by native
      systemd configuration.

      If you want to list systemd services use 'systemctl list-unit-files'.
      To see services enabled on particular target use
      'systemctl list-dependencies [target]'.

mysql          	0:off	1:off	2:on	3:on	4:on	5:on	6:off
```
## 启动服务
```bash
# service mysql start
Starting MySQL. ERROR! The server quit without updating PID file (/usr/local/mysql/data/172.18.1.117.pid).
```
此时删除配置文件，可以解决该报错（原因未知，没有深究）
```bash
[root@172 mysql]# rm  /etc/my.cnf -rf
```
重新启动
```bash
[root@172 mysql]# /etc/init.d/mysql start
Starting MySQL.Logging to '/usr/local/mysql/data/172.18.1.117.err'.
 SUCCESS! 
 ```
## 登录
```bash
[root@172 mysql]# /usr/local/mysql/bin/mysql -uroot -pPDRO-ab.a8jd
```
修改密码
```bash
# 有的文章说此处不能使用单引号，但是我使用单引号也成功了，好像没有问题。YOUR PASSWORD 为你自己设置的数据库的密码，这个要记住了，不然就要自己再去手动重置密码了！
mysql>  set password=password("YOUR PASSWORD");
Query OK, 0 rows affected, 1 warning (0.00 sec)
mysql> flush privileges;
Query OK, 0 rows affected (0.06 sec)
mysql> quit
Bye
```
## 添加环境变量
上一步中启动 mysql 的时候使用的是全路径，有的时候会比较麻烦，可以通过配置环境变量修改；
执行`vi ~/.bash_profile`修改文件中`PATH`一行，将`/usr/local/mysql/bin` 加入到`PATH=$PATH:$HOME/bin`一行之后
**注意**：这种方法只对当前登录用户生效。

# 参考阅读
[Linux 安装 mysql5.7.24 - 绿色落日的博客 - CSDN 博客](https://blog.csdn.net/qq_30000313/article/details/85333971)
[Linux 安装 mysql5.7.19](https://blog.csdn.net/zhou920786312/article/details/77750604)
