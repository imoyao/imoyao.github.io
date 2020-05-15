---
title: 博客 idealyard 支持 emoji 显示问题
date: 2020-05-15 13:50:02
tags: 
- idealyard
- 博客
- utf8mb4
categories:
- Projects
- IdealYard
---
{%note info%}

## 注意
1. 以下演示内容基于数据库版本：
```shell
mysql --version
mysql  Ver 15.1 Distrib 5.5.64-MariaDB, for Linux (x86_64) using readline 5.1
```
2. utf8mb4 的最低 mysql 版本支持版本为 5.5.3+
{%endnote%}

## 前言
我们知道要想让数据库存储数据支持 emoji 显示必须将数据库编码格式设置为`utf8emb4`，可是我在代码中修改了数据库编码还是有问题，具体见此处 [Issues](https://github.com/imoyao/idealyard/issues/6) ，当时列出下面的怀疑：
- [x] ~~数据库设置为`utf8mb4`编码；~~
- [x] ~~单个表格编码未设置为`utf8mb4`；~~
- [x] ~~由于前端使用`pangujs`导致传到后端已经出错；~~

昨晚进行了排查及解决，现在记录一下。

## 排查
1. 首先查看数据库编码格式
```sql
MariaDB [iyblog_product]> show create database iyblog_product;
+----------------+----------------------------------------------------------------------------+
| Database       | Create Database                                                            |
+----------------+----------------------------------------------------------------------------+
| iyblog_product | CREATE DATABASE `iyblog_product` /*!40100 DEFAULT CHARACTER SET utf8mb4 */ |
+----------------+----------------------------------------------------------------------------+
1 row in set (0.00 sec)
```
2. 查看相应表的数据格式
```sql
MariaDB [iyblog_product]> show create table iy_article;

/*省略*/
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=utf8mb4 |

```
其实此处多余，因为代码里有如下定义：
```python
import os

class MySQLConfig:
    MYSQL_USERNAME = os.getenv('MYSQL_USER')
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD')
    MYSQL_HOST = 'localhost:3306'
    MYSQL_CHARSET = 'utf8mb4'  # 为了支持 emoji 显示，需要设置为 utf8mb4 编码
```

## 解决
之后通过搜索知道除了把数据库和表格设置为正确编码，还要修改数据库配置。

### 客户端配置
```shell
vi /etc/my.cnf.d/client.cnf 
```
```plain
#
# These two groups are read by the client library
# Use it for options that affect all clients, but not the server
#


[client]
default-character-set = utf8mb4     # 添加此行
# This group is not read by mysql client library,
# If you use the same .cnf file for MySQL and MariaDB,
# use it for MariaDB-only client options
[client-mariadb]
```

### 服务端配置
```bash
vi /etc/my.cnf.d/server.cnf
```
```plain
#
# These groups are read by MariaDB server.
# Use it for options that only the server (but not clients) should see
#
# See the examples of server my.cnf files in /usr/share/mysql/
#

# this is read by the standalone daemon and embedded servers
[server]
# this is only for the mysqld standalone daemon
[mysqld]                # 此行开始
character-set-client-handshake = FALSE
character-set-server = utf8mb4  
collation-server = utf8mb4_unicode_ci
init_connect='SET NAMES utf8mb4'

# this is only for embedded server
[embedded]

# This group is only read by MariaDB-5.5 servers.
# If you use the same .cnf file for MariaDB of different versions,
# use this group for options that older servers don't understand
[mysqld-5.5]

# These two groups are only read by MariaDB servers, not by MySQL.
# If you use the same .cnf file for MySQL and MariaDB,
# you can put MariaDB-only options here
[mariadb]
[mariadb-5.5]

```

### 重启 Mariadb 使配置生效
```plain
systemctl restart mariadb   # 如果是mysql需要起相应服务
```

### 验证
```sql
MariaDB [iyblog_product]> SHOW VARIABLES WHERE Variable_name LIKE 'character_set_%' OR Variable_name LIKE 'collation%';
```
```plain
+--------------------------+----------------------------+
| Variable_name            | Value                      |
+--------------------------+----------------------------+
| character_set_client     | utf8mb4                    |
| character_set_connection | utf8mb4                    |
| character_set_database   | utf8mb4                    |
| character_set_filesystem | binary                     |
| character_set_results    | utf8mb4                    |
| character_set_server     | utf8mb4                    |
| character_set_system     | utf8                       |
| character_sets_dir       | /usr/share/mysql/charsets/ |
| collation_connection     | utf8mb4_general_ci         |
| collation_database       | utf8mb4_general_ci         |
| collation_server         | utf8mb4_unicode_ci         |
+--------------------------+----------------------------+
11 rows in set (0.04 sec)

```
必须保证下面的变量编码是`utf8mb4`格式。
{%raw%}
<table>
  <tbody>
    <tr>
      <th>系统变量</th>
      <th>描述</th>
    </tr>
    <tr>
      <td>character_set_client</td>
      <td>(客户端来源数据使用的字符集)</td>
    </tr>
    <tr>
      <td>character_set_connection</td>
      <td>(连接层字符集)</td>
    </tr>
    <tr>
      <td>character_set_database</td>
      <td>(当前选中数据库的默认字符集)</td>
    </tr>
    <tr>
      <td>character_set_results</td>
      <td>(查询结果字符集)</td>
    </tr>
    <tr>
      <td>character_set_server</td>
      <td>(默认的内部操作字符集)</td>
    </tr>
  </tbody>
</table>
{%endraw%}

实际验证一下😅：
![emoji](/images/idealyard-emoji.png)

最后我们发现了一个新问题（TODO）：
链接的 slug 中直接把 emoji 也给显示出来了，此处需要对 emoji 进行过滤或者转换为字符说明。

## 参考链接
[mysql 存储 emoji 表情报错的处理方法【更改编码为 utf8mb4】_Mysql_脚本之家](https://www.jb51.net/article/144079.htm)