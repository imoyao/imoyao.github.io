---
title: MySQL 中存储 IP 地址应该选用何种数据类型？
date: 2019-05-11 14:44:31
tags:
- MySQL
- Python
- 数据库
categories:
- 工作日常
toc: true
---
今天在项目开发时，遇到需要在数据库中存储 ip 地址，那么应该选用何种数据类型更加高效呢？
如果存储的是`IPV4`地址，可以选择使用`INT UNSIGNED`，然后借助 `MySQL` 自带的 `INET_ATON()` 和  `INET_NTOA()`来存取数据；
如果存储的是`IPV6`地址，可以选择使用`VARBINARY()`，然后借助 `INET6_ATON()`和`INET6_NTOA()` (`MySQL5.6+`支持)方法存取数据。

<!--more-->

## 针对`IPv4`地址

```sql
mysql> select inet_aton('127.0.0.1');
+------------------------+
| inet_aton('127.0.0.1') |
+------------------------+
|             2130706433 |
+------------------------+
1 row in set (0.00 sec)

mysql> select inet_ntoa(2130706433);
+-----------------------+
| inet_ntoa(2130706433) |
+-----------------------+
| 127.0.0.1             |
+-----------------------+
1 row in set (0.01 sec)

```
### 数据存取

- 存数据

    ```sql
    INSERT INTO `ip_addresses` (`ip_address`)
    VALUES (INET_ATON('127.0.0.1'));
    ```

- 取数据

    ```sql
    SELECT id, INET_NTOA(`ip_address`) AS ip
    FROM `ip_addresses`;
    ```

### `Python`实现

对于上面的代码，如果我们不想使用内置的`MySQL`方法，也可以在应用层使用自己封装的方法：

```python
import socket, struct
def ip2long(ip):  
    return struct.unpack("!L",socket.inet_aton(ip))[0]  
def long2ip(longip):  
    return socket.inet_ntoa(struct.pack('!L', longip))  
if __name__ == '__main__':  
    print('local ip address to long is %s'%ip2long('127.0.0.1'))  
    print('local ip address to long is %s'%ip2long('255.255.255.255'))  
    print('local ip address long to ip is %s'%long2ip(2130706433))  
    print('local ip address long to ip is %s'%long2ip(4294967295)) 

```
#### 更新
我们还可以使用 ipaddress 库对 ip 地址进行 int 和 str 之间的互转。代码如下：
```python
>>> import ipaddress

>>> int(ipaddress.ip_address('127.0.0.1'))
2130706433
>>> str(ipaddress.ip_address(2130706433))
'127.0.0.1'
```


## 针对`IPv6`地址

MySQL 提供内置函数`inet6_aton()`来存储和检索`IPv6`地址。敲黑板，不要把`IPv6`地址存储为整数，因为数字格式的`IPv6`地址需要比`UNSIGNED BIGINT`更多的字节。所以下面的函数返回`VARBINARY(16)`数据类型。让我们看一个例子。
```sql
mysql> select hex(inet6_aton('127.0.0.1'));
+---------------------------------+
| hex(inet6_aton('127.0.0.1'))    |
+---------------------------------+
| 7F000001                        |
+---------------------------------+
1 row in set (0.00 sec)

mysql> select hex(inet6_aton('2001:0db8:85a3:0000:0000:8a2e:0370:7334'));
+---------------------------------------------------------------------------+
| hex(inet6_aton('2001:0db8:85a3:0000:0000:8a2e:0370:7334'))                |
+---------------------------------------------------------------------------+
| 20010DB885A3000000008A2E03707334                                          |
+---------------------------------------------------------------------------+
1 row in set (0.00 sec)

mysql> select inet6_ntoa(unhex('20010DB885A3000000008A2E03707334'));
+----------------------------------------------------------------------------+
| inet6_ntoa(unhex('20010DB885A3000000008A2E03707334'))                      |
+----------------------------------------------------------------------------+
| 2001:db8:85a3::8a2e:370:7334                                               |
+----------------------------------------------------------------------------+
1 row in set (0.00 sec)
```


**注意**

假设你正在编写查找以`ip`地址为`127.0.0.1`连接的用户，可能写出如下的查询语句：

```sql
SELECT name FROM user WHERE inet_ntoa(ipaddress)='127.0.0.1';
```

请注意，此查询不会使用在`ipaddress`列上创建的索引，因为我们在`SQL`执行期间修改了索引列，它也会逐行将整数转换为真实的`IP`地址。所以要想让索引生效应该：
```sql
SET @ip = inet_aton('127.0.0.1');
SELECT name FROM user WHERE ipaddress = @ip;
```
或者
```sql
SELECT name FROM user WHERE ipaddress = inet_aton('127.0.0.1');
```
## 参考链接

- [How to store IP (internet protocol) address in MySQL?](https://www.rathishkumar.in/2017/08/how-to-store-ip-address-in-mysql.html)
- [Which MySQL datatype use for store an IP address?](https://itsolutionstuff.com/post/which-mysql-datatype-use-for-store-an-ip-address)
- [Most efficient way to store IP Address in MySQL](https://stackoverflow.com/questions/2542011/most-efficient-way-to-store-ip-address-in-mysql)
- [MySQL doc-function_inet6-aton](https://dev.mysql.com/doc/refman/5.6/en/miscellaneous-functions.html#function_inet6-aton)
- [IP 地址在数据库里面的存储方式](https://www.cnblogs.com/gomysql/p/4595621.html)
- [论 IP 地址在数据库中应该用何种形式存储？](https://www.cnblogs.com/skynet/archive/2011/01/09/1931044.html)
