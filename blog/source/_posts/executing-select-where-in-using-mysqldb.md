---
title: 关于在 Python 中 MySQL 的 WHERE 子句中执行 IN 操作（list，tuple）的问题
date: 2018-05-10 15:41:35
tags:
- Python
- MySQL
- SQL
---

今天在写代码的时候，有一处查询语句需要执行 `IN` 操作，结果直接`join`操作会出错。
<!--more-->

```Python
list_of_datas = [u'sde', u'sdf', u'sdb', u'sdc']
sql = "SELECT DiskId,Name,Sg,PhyId,ExpanderId,EProduct FROM Disk WHERE Used='2' AND Name IN (%s)" % ','.join(list_of_datas)
```

执行结果：

```SQL
SELECT DiskId, Name, Sg, PhyId, ExpanderId
	, EProduct
FROM Disk
WHERE Used = '2'
	AND Name IN (sde, sdf, sdb, sdc)
```

很明显与预期的结果是不一样的。因为 `IN` 操作中的选取字段应该是带引号的字符串，而不是直接显示的字符串。也就是说我们期望的`WHERE`子句中是`WHERE Used = '2' AND Name IN ('sde', 'sdf', 'sdb', 'sdc')`形式。

```Python
sql1 = "SELECT DiskId,Name,Sg,PhyId,ExpanderId,EProduct FROM Disk WHERE Used='2' AND Name IN (%s)" % ','.join(["'%s'" % item for item in list_of_datas])
```

执行结果：

```SQL
SELECT DiskId, Name, Sg, PhyId, ExpanderId
	, EProduct
FROM Disk
WHERE Used = '2'
	AND Name IN ('sde', 'sdf', 'sdb', 'sdc')
```

至此，可以满足我们的要求。不过，由于上面字符化操作感觉有点暴力，我们可以稍微改进一下：

```Python
format_strings= ','.join([repr(item) for item in list_of_datas])
print(format_strings)
```

执行结果：

```Python
u'sde',u'sdf',u'sdb',u'sdc'
```

此时 `SQL` 语句变成:

```SQL
SELECT DiskId,Name,Sg,PhyId,ExpanderId,EProduct FROM Disk WHERE Used='2' AND Name IN (u'sde',u'sdf',u'sdb',u'sdc')
```

这个是没办法正常查询出结果的，因为查询字段是 `unicode` 编码。

```Python
format_unicode_strings = ','.join([repr(item.encode('utf-8')) if isinstance(item,unicode) else repr(item) for item in list_of_datas])
```

此时结果满足我们的要求：

```SQL
SELECT DiskId, Name, Sg, PhyId, ExpanderId
	, EProduct
FROM Disk
WHERE Used = '2'
	AND Name IN ('sde', 'sdf', 'sdb', 'sdc')
```

至此，收工。

因为公司的代码封装函数是只能执行真正的 `SQL` 语句的，所以只能用上面的方法，查询网络上别人的解决方案发现下面的写法，以备参考。

```Python
>>> alist = ['1.1.1.1','2.2.2.2','3.3.3.3']                                                    
>>> select_str = 'select * from server where ip in (%s)' % ','.join(['%s'] * len(alist))       
>>> select_str  
'select * from server where ip in (%s,%s,%s)' 
 # 执行sql查询
cursor.execute(select_str,a)  
```

后面的写法有很多种，比如：

```Python
args = [1, 2, 3]
in_p = ', '.join((map(lambda x: '%s', args)))
realsql = sql % in_p
cursor.execute(realsql, args)
```

再比如：

```Python
args = [1, 2, 3]
in_p = ', '.join(itertools.repeat('%s', len(args)))
cursor.execute(sql % in_p, args)
```

完整示例代码:

```Python
#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by imoyao at 2018/5/18 17:17
import itertools
import MySQLdb


def excute_sql(sql):
    db = MySQLdb.connect(host="localhost", user="imoyao", passwd="111111", db="ODSP", charset="utf8")
    cr = db.cursor()
    cr.execute(sql)
    data = cr.fetchall()
    cr.close()
    db.close()
    return data


def excute_sql_datas(sqlstr, tupledata):
    db = MySQLdb.connect(host="localhost", user="imoyao", passwd="111111", db="ODSP", charset="utf8")
    cr = db.cursor()
    cr.execute(sqlstr,tupledata)
    data = cr.fetchall()
    cr.close()
    db.close()
    return data


if __name__ == '__main__':
    list_of_datas = [u'sde', u'sdf', u'sdb', u'sdc']
    format_strings = ','.join(
        [repr(item.encode('utf-8')) if isinstance(item, unicode) else repr(item) for item in list_of_datas])
    sql = "SELECT DiskId,Name,Sg,PhyId,ExpanderId,EProduct FROM Disk WHERE Used='2' AND Name IN (%s)" % format_strings
    print(excute_sql(sql))

    print('*'*40)

    sql2 = "SELECT DiskId,Name,Sg,PhyId,ExpanderId,EProduct FROM Disk WHERE Used='2' AND Name IN (%s)"
    # format_strings2 = ', '.join(map(lambda x: '%s', list_of_datas))
    # format_strings2 = ', '.join(['%s'] * len(list_of_datas))
    format_strings2 = ', '.join(itertools.repeat('%s', len(list_of_datas)))
    sqlstr = sql2 % format_strings2
    print(excute_sql_datas(sqlstr, list_of_datas))

```

参考链接：

1. [python mysql where in 对列表（list,,array）问题 - CSDN 博客](https://blog.csdn.net/u011085172/article/details/79044490)

2. [python - Executing "SELECT ... WHERE ... IN ..." using MySQLdb - Stack Overflow](https://stackoverflow.com/questions/4574609/executing-select-where-in-using-mysqldb)