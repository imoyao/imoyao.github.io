---
title: Python 标准库系列之 MySQLdb 模块
toc: true
date: 2020-05-23 18:21:46
tags:
- 编码
- 面向对象
top: 1

---
# Python 标准库系列之 MySQLdb 模块

MySQLdb 模块的主要功能就是提供 Python 操作 MySQL 数据库的一个 API,通过 MySQLdb 模块我们可以对数据库进行**`增`,`删`,`改`,`查`,** 等操作.

MySQLdb 工作流程如下:

![mysqldb-01](/images/2016/12/1483022284.png)

 ## connection

 `connection`方法用于创建客户端与数据库的网络连接.

 语法:

 ```python
MySQLdb.Connect(参数)
 ```

**参数**

|参数|类型|说明|
|:--:|:--|:--|
|host|字符串|MySQL 服务器地址|
|port|整型|MySQL 服务器端口号|
|user|字符串|MySQL 数据库用户名|
|passwd|字符串|MySQL 数据库密码|
|db|字符串|MySQL 数据库库名|
|charset|字符串|连接所使用的字符集|

**例如:**

```python
# 导入MySQLdb模块
>>> import MySQLdb
# 创建一个Connect连接
>>> conn = MySQLdb.Connect(host='127.0.0.1', user='root', passwd='as', db='USER', port=3306, charset="utf8")
>>> cursor = conn.cursor()
>>> print(cursor)
<MySQLdb.cursors.Cursor object at 0x7f4af5e15550>
>>> print(conn)
<_mysql.connection open to '127.0.0.1' at 15b1518>
# 关闭连接
>>> conn.close()
>>> print(conn)
<_mysql.connection closed at 15b1518>
```

**connection 对象支持的方法**

|方法名|说明|
|:--:|:--|
|cursor()|使用该连接创建并返回游标|
|commit()|提交当前事务|
|rollback()|回滚当前事务|
|close()|关闭连接|

## cursor

`cursor`用户执行查询和获取结果,执行流程如下:

![mysqldb-02](/images/2016/12/1483022315.png)

**cursor 对象所支持的方法**

|参数名|说明|
|:--:|:--|
|execute("SQL")|执行的 SQL 语句|
|fetchone()|获取结果的下一行|
|fetchmany(size)|获取结果的下几行|
|fetchall()|获取结果剩下的所有行|
|rowcount|最近一次 execute 返回数据的行数或影响的行数|
|close()|关闭游标对象|

## 事务

访问额更新数据库的一个程序执行单元,执行单元指的就是很多操作的集合,里面的每个操作都是用来访问个更新数据库.

- 原子性: 事务中包括的诸多操作要么都做要么都不做

比如银行转账,A 用户向 B 用户转账 100,A-100 和 B+100 这两个操作,要么都做,要么都不操作

1. 一致性: 事务必须使数据库从一致性状态变到另一个一致性状态
2. 隔离性: 一个事务的执行不能被其他事务干扰
3. 持久性: 事务一旦提交,他对数据库的改变是永久性的

**开发中怎样使用事务?**

1. 关闭自动 commit: 设置 conn.autocommit(False),`MySQLdb`默认已经为`False`
2. 正常结束事务: conn.commit()
3. 异常结束事务: conn.rollback()

## 实例

- SELECT 查询数据

先创建一个`user`表:

```sql
CREATE DATABASE USER;
USE USER;
CREATE TABLE `user` (
`userid` INT(11) NOT NULL AUTO_INCREMENT,
`username` VARCHAR(100) DEFAULT NULL,
PRIMARY KEY (`userid`)
) ENGINE=INNODB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8;
```

插入以下内容

```sql
INSERT INTO user(userid, username) VALUES(1, 'name1');
INSERT INTO user(userid, username) VALUES(2, 'name2');
INSERT INTO user(userid, username) VALUES(3, 'name3');
INSERT INTO user(userid, username) VALUES(4, 'name4');
INSERT INTO user(userid, username) VALUES(5, 'name5');
```

查看数据

```bash
mysql> SELECT * FROM user;
+--------+----------+
| userid | username |
+--------+----------+
|      1 | name1    |
|      2 | name2    |
|      3 | name3    |
|      4 | name4    |
|      5 | name5    |
+--------+----------+
5 rows in set (0.00 sec)
```

```python
>>> import MySQLdb
>>> conn = MySQLdb.Connect(host='127.0.0.1', user='root', passwd='as', db='USER', port=3306, charset="utf8")
>>> cursor = conn.cursor()
>>> SQL = "SELECT * FROM user"
# 返回获取到的多少行
>>> cursor.execute(SQL)
5
# 输出获取到的行数
>>> print(cursor.rowcount)
5
# 返回第一条数据
>>> cursor.fetchone()
(1, 'name1')
# 返回两条数据
>>> cursor.fetchmany(2)
((2, 'name2'), (3, 'name3'))
# 返回剩下的所有数据
>>> cursor.fetchall()
((4, 'name4'), (5, 'name5'))
```

- insert/update/delete

流程图:

![mysqldb-03](/images/2016/12/1483022364.png)

```python
>>> import MySQLdb
>>> conn = MySQLdb.Connect(host='127.0.0.1', user='root', passwd='as', db='USER', port=3306, charset="utf8")
>>> cursor = conn.cursor()
>>> cursor.execute("INSERT INTO user(userid, username) VALUES(50, 'name50')")
1
>>> cursor.execute("UPDATE user SET username='as' WHERE userid=1")
1
>>> cursor.execute("DELETE FROM user WHERE userid=2")
1
>>> conn.commit()
>>> cursor.close()
>>> conn.close()
```

查看数据库表内容

```bash
mysql> SELECT * FROM user;
+--------+----------+
| userid | username |
+--------+----------+
|      1 | as       |
|      3 | name3    |
|      4 | name4    |
|      5 | name5    |
|     50 | name50   |
+--------+----------+
5 rows in set (0.00 sec)
```
