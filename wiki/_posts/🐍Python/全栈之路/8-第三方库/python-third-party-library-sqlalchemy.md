---
title: Python 全栈之路系列之 SQLAlchemy
toc: true
date: 2020-05-23 18:21:46
tags:
- 编码
- SQLAlchemy
top: 5
---

`SQLAlchemy`的是`Python SQL`工具包和对象关系映射器，让应用程序开发者的全部功能和 SQL 的灵活性。

它提供了一套完整的众所周知的企业级持久性模式，专为高效率和高性能的数据库访问，改编成一个简单的`Python`化领域语言。

## SQLAlchemy 的哲学

SQL 数据库的行为不像对象集合的较具规模和业绩开始关系; 对象集合表现得不像越抽象开始关系表和行。 `SQLAlchemy`的目的是满足这两个原则。

`SQLAlchemy`认为数据库是关系代数发动机，而不仅仅是一个表的集合，行可以不仅从表中选择，但也加入和其他 select 语句; 任何这些单元可被组合成一个较大的结构，`SQLAlchem`y 的表达式语言基础上，从它的核心这个概念。

`SQLAlchemy`是最有名的对象关系映射器（ORM），提供数据映射模式 ，其中类可以在开放式的，多种方式被映射到数据库中的可选组件-允许对象模型和数据库模式中，以开发干净地分离从开始方式。

`SQLAlchemy`的对这些问题的总体思路是大多数其它`SQL/ORM`工具，根植于所谓的`complimentarity`-导向的方式完全不同; 而不是藏起来了 SQL 和关系对象的细节自动化墙后面，所有的进程都充分一系列组合的，透明的工具中暴露出来 。 该库发生在自动冗余任务的工作，而开发商仍然在数据库中是如何组织和 SQL 是如何构造的控制。

`SQLAlchemy`的主要目标是改变你对数据库和 SQL 的方式！

## SQLAlchemy 的使用

数据库的连接

**MySQL-Python**
```python
mysql+mysqldb://<user>:<password>@<host>[:<port>]/<dbname>
```
**pymysql** 
```python
mysql+pymysql://<username>:<password>@<host>/<dbname>[?<options>]
```
**MySQL-Connector**
```python
mysql+mysqlconnector://<user>:<password>@<host>[:<port>]/<dbname>
```

查看版本

```python
>>> import sqlalchemy
>>> sqlalchemy.__version__
'1.0.14'
```

### 创建与删除表

单表创建

```python
#!/usr/bin/env python
# _*_ coding:utf-8 _*_

import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Index, UniqueConstraint, ForeignKey
from sqlalchemy.orm import sessionmaker

engine = create_engine('mysql+pymysql://root:as@127.0.0.1:3306/tesql?charset=utf8', echo=True)  # echo=True输出生成的SQL语句

Base = declarative_base()  # 生成一个ORM基类

class UserInfo(Base):
    __tablename__ = 'UserInfo'  # 表名
    """
    创建字段
	index=True  普通索引
	unique=T  唯一索引
    """
    id = Column(Integer, primary_key=True, autoincrement=True)  # primary_key=主键,autoincrement=自增
    name = Column(String(32))
    password = Column(String(16))
	
    __table_args__ = (
        Index('id', 'name'),  # 联合索引
        UniqueConstraint('name', 'password', name='name_password')  # 联合唯一索引,name索引的名字
    )
	
    # 让查询出来的数据显示中文
    def __repr__(self):
        return self.name

Base.metadata.create_all(engine)  # 把所有集成Base类的类，创建表结构
```

上面的代码其实就是创建了一个`UserInfo`表，包含了三个字段，实际执行的 SQL 语句如下：

```sql
CREATE TABLE `UserInfo` (
	id INTEGER NOT NULL AUTO_INCREMENT, 
	name VARCHAR(32), 
	password VARCHAR(16), 
	PRIMARY KEY (id), 
	CONSTRAINT name_password UNIQUE (name, password)
)
```
因为在创建引擎的时候加入了`echo=True`，所以执行的 SQL 会在控制台输出出来，以便于我们排查问题。

创建一对多表

```python
class Favor(Base):
    __tablename__ = 'favor'
    nid = Column(Integer, primary_key=True, autoincrement=True)
    caption = Column(String(50), default='red', unique=True)


class Person(Base):
    __tablename__ = 'person'
    nid = Column(Integer, primary_key=True, autoincrement=True)
    favor_id = Column(Integer, ForeignKey("favor.nid"))
```

创建多对多表

```python
# 组
class Group(Base):
    __tablename__ = 'group'
    id = Column(Integer, primary_key=True)
    name = Column(String(64), unique=True, nullable=False)
    port = Column(Integer, default=22)


# 服务器
class Server(Base):
    __tablename__ = 'server'

    id = Column(Integer, primary_key=True, autoincrement=True)
    hostname = Column(String(64), unique=True, nullable=False)


# 服务器组，第三张表
class ServerToGroup(Base):
    __tablename__ = 'servertogroup'
    nid = Column(Integer, primary_key=True, autoincrement=True)
    server_id = Column(Integer, ForeignKey('server.id'))
    group_id = Column(Integer, ForeignKey('group.id'))
```

删除表

```python
Base.metadata.drop_all(engine)  # 把所有集成Base类的类，删除表
```

### 操作表

#### 增加数据

添加单条数据

```pythn
MySesion = sessionmaker(bind=engine)
session = MySesion()

# 创建一条数据
users = UserInfo(name='Hello', password='World')

# 把数据添加到表内
session.add(users)

# 提交生效
session.commit()
```

添加多少数据

```python
session.add_all([
    UserInfo(name='A', password='1'),
    UserInfo(name='B', password='2')
])
# 提交
session.commit()
```

#### 删除数据

```python
session.query(UserInfo).filter(UserInfo.name == 'a').delete()
session.commit()
```

#### 查询

获取某个表中的所有内容

```python
result = session.query(UserInfo).all()
print(result)
```

### 修改数据

```python
session.query(UserInfo).filter(UserInfo.id == 8).update({"name": "ffff"})
session.commit()
```

### 查询数据

获取所有
```python
result = session.query(UserInfo).all()
```
获取指定字段
```python
result = session.query(UserInfo.name, UserInfo.password).all()
```
获取指定的
```python
result = session.query(UserInfo).filter_by(name='b').all()
# 返回的是一个列表
```
获取第一条
```python
result = session.query(UserInfo).filter_by(name='b').first()
# 获取值中的某个属性
result.name
```
获取数据出现的个数
```python
result = session.query(UserInfo).filter_by(name='b').count()
```

使用`and_`和`or_`进行查询

导入`and_`, `or_`模块
```python
from sqlalchemy import and_, or_
```
`and_`
```python
for row in session.query(UserInfo).filter(and_(UserInfo.name == 'A', UserInfo.password == 1)):
    print(row)
```
`or_`
```python
for row in session.query(UserInfo).filter(or_(UserInfo.name == 'Hello', UserInfo.password == 1)):
    print(row)
```

关联查询

创建以下数据库

```python
#!/usr/bin/env python
# _*_ coding:utf-8 _*_

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, relationships
from sqlalchemy import Column, Integer, String, Index, UniqueConstraint, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine('mysql+pymysql://root:as@127.0.0.1:3306/tesql')

Base = declarative_base()


class Son(Base):
    __tablename__ = 'son'
    id = Column(Integer, primary_key=True)
    name = Column(String(32))
    father = relationship('Father')
    # 创建外键
    father_id = Column(Integer, ForeignKey('father.id'))


class Father(Base):
    __tablename__ = 'father'
    id = Column(Integer, primary_key=True)
    name = Column(String(32))
    son = relationship('Son')
	# son = relationship('Son', backref='Father') 相当于上面两个relationship


# 生成表
Base.metadata.create_all(engine)
```
往表里添加数据
```python
Session = sessionmaker(bind=engine)
session = Session()

# 添加父亲的数据
F = Father(name='as')
session.add(F)
session.commit()

# 添加儿子的数据
S1 = Son(name='Son1', father_id=1)
S2 = Son(name='Son2', father_id=1)
session.add_all([S1, S2])
session.commit()

# 另外一种添加数据的方式
F = session.query(Father).filter_by(id=1).first()
S3 = Son(name='Son3')
# 要用追加的方式进行添加，F.son是一个列表，如果不用append将会把之前的数据对应的值进行删除
F.son.append(S3)
session.add(F)
session.commit()
```

通过父亲找到所有的儿子

```python
result = session.query(Father).filter_by(name='as').first()
for n in result.son:
    print(n.name)
```
通过儿子找到父亲
```python
result = session.query(Son).filter_by(name='Son2').first()
print(result.father.name, result.name)
# son = relationship('Son', backref='Father')
# print(result.father.name, result.name)
```
join

```python
result = session.query(Father.name.label('kkk'), Son.name.label('ppp')).join(Son)
# label('kkk')相当于起了一个别名，等于sql中的as
print(result)
>>>>>
SELECT father.name AS kkk, son.name AS ppp 
FROM father JOIN son ON father.id = son.father_id
```

多对多实例

在上面的多对多的代码中的`Server`类加入一下代码：

```python
g = relationship("Group", secondary=ServerToGroup.__table__, backref='s')
# secondary 如果有第三张表自动加进来
```

然后生成数据库表.

添加组与主机的数据
```python
G1 = Group(name='G1', port=22)
G2 = Group(name='G2', port=22)

S1 = Server(hostname='Linux-node1')
S2 = Server(hostname='Linux-node2')

session.add_all([G1, G2, S1, S2])
session.commit()
```
往第三张表里面添加关联数据
```python
GS1 = ServerToGroup(server_id=1, group_id=1)
GS2 = ServerToGroup(server_id=2, group_id=2)
session.add_all([GS1, GS2])
session.commit()
```
通过`relationship`进行数据的添加
```python
# 获取ID=1的主机
S = session.query(Server).filter_by(id=1).first()
# 获取所有主机组
G = session.query(Group).all()

S.g = G
# 添加数据
session.add_all([S, ])
# 提交到数据库中
session.commit()
```