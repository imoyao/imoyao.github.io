---
title: Python 标准库系列之 Memcache 模块
toc: true
date: 2020-05-23 18:21:46
tags:
- 编码
- 面向对象
top: 3

---
# Python 标准库系列之 Memcache 模块

这个模块是一个`Python`操作`memcached`的一个 API 接口。

Memcached 官网：http://memcached.org/
模块官网：https://pypi.python.org/pypi/python-memcached/

## What is Memcached

Free & open source, high-performance, distributed memory object caching system, generic in nature, but intended for use in speeding up dynamic web applications by alleviating database load.

Memcached is an in-memory key-value store for small chunks of arbitrary data (strings, objects) from results of database calls, API calls, or page rendering.

Memcached is simple yet powerful. Its simple design promotes quick deployment, ease of development, and solves many problems facing large data caches. Its API is available for most popular languages.

> 以上内容摘自官网的介绍，具体信息访问官网

## 安装 Memcached

包安装

Ubuntu

```bash
apt-get install memcached
```

CentOS

```bash
yum install memcached
```

源码安装

`Memcached`源码包安装的时候需要依赖于`libevent`

```bash
# Ubuntu
apt-get install libevent-dev
# CentOS
yum install libevent-devel
```

编译安装`memcached`

```bash
wget https://memcached.org/latest
tar -zxf memcached-1.x.x.tar.gz
cd memcached-1.x.x
./configure --prefix=/usr/local/memcached
make && make test && sudo make install
```

具体参数见`./configure --help`全选项，SASL 支持需要一些可选附加库。

启动

我这里安装的时候是采用包的方式进行安装的。

```bash
[root@anshengme ~]# memcached -d -m 10 -u root -l 0.0.0.0 -p 11211 -c 256 -P /tmp/memcached.pid
```

参数说明

|参数|描述|
|:--|:--|
|`-d`|是启动一个守护进程|
|`-m`|是分配给 Memcache 使用的内存数量，单位是 MB|
|`-u`|是运行 Memcache 的用户|
|`-l`|是监听的服务器 IP 地址|
|`-p`|是设置 Memcache 监听的端口,最好是 1024 以上的端口|
|`-c`|选项是最大运行的并发连接数，默认是 1024，按照你服务器的负载量来设定|
|`-P`|是设置保存 Memcache 的 pid 文件|

设置开机自启动

```bash
[root@anshengme ~]# chmod +x /etc/rc.d/rc.local
[root@anshengme ~]# echo 'memcached -d -m 10 -u root -l 0.0.0.0 -p 11211 -c 256 -P /tmp/memcached.pid' >> /etc/rc.local
```

关闭 memcached

```bash
[root@anshengme ~]# pkill `cat /tmp/memcached.pid`
```

测试

先查看 11211 端口是否启动

```bash
[root@anshengme ~]# netstat -tlnp | grep "11211"
tcp        0      0 0.0.0.0:11211           0.0.0.0:*               LISTEN      4245/memcached 
```

使用 telnet 查看启动的 11211 端口是否可以，可以则测试 OK，否则就需要你拍错了，但愿没有问题。

```bash
[root@anshengme ~]# telnet 127.0.0.1 11211
Trying 127.0.0.1...
Connected to 127.0.0.1.
Escape character is '^]'.

```

如果出现以下内容就代表启动成功！

## Memcache 使用

安装 Memcache

下载模块包，目前最新版

```bash
[root@anshengme ~]# wget https://pypi.python.org/packages/f7/62/14b2448cfb04427366f24104c9da97cf8ea380d7258a3233f066a951a8d8/python-memcached-1.58.tar.gz#md5=23b258105013d14d899828d334e6b044
```

解压并安装

```bash
[root@anshengme ~]# tar xf python-memcached-1.58.tar.gz 
[root@anshengme ~]# cd python-memcached-1.58
[root@anshengme python-memcached-1.58]# python setup.py install
```

进入 Python 解释器导入模块，如果导入成功就表示模块安装成功。

```bash
[root@anshengme python-memcached-1.58]# python
>>> import memcache
>>> 
```

首次体验

```python
# 导入memcache模块
>>> import memcache
# 连接到一台Memcached服务器
>>> conn = memcache.Client(['192.168.56.100:11211'])
# 设置一个值，如果存在则覆盖
>>> conn.set('k1', 'v1')
True
# 获取值的内容
>>> conn.get('k1')
'v1'
```

更多的使用方法

设置超时时间
```python
>>> conn.set('k', 'v', 1)
True
>>> conn.get('k')
```
设置值，如果存在就报错
```python
>>> conn.add('k','hello')
# False设置失败
False
>>> conn.get('k')
# 原值没变
'v'
```
修改值，不存在则返回 False
```python
>>> conn.replace('k','helloworld')
# 设置成功
True
>>> conn.get('k')
# 返回修改后的值
'helloworld'
>>> conn.replace('kkkk','hello')
# 修改一个不存在的值
False
```
设置多个值，值不存在则创建，存在则修改
```python
>>> conn.get('key1')
>>> conn.set_multi({'key1':'value1','key2':'value2'})
[]
>>> conn.get('key1')
'value1'
```
删除一个值
```python
>>> conn.get('key1')
'value1'
>>> conn.delete('key1')
1
>>> conn.get('key1')
```
删除多个值
```python
>>> conn.set_multi({'key3':'value3','key4':'value4'})
[]
>>> conn.delete_multi(['key3', 'key4'])
1
```
获取一个值和获取多个值
```python
>>> conn.set_multi({'key5':'value5','key6':'value6'})
[]
>>> conn.get('key5')
'value5'
>>> conn.get_multi(['key5','key6'])
{'key5': 'value5', 'key6': 'value6'}
```
修改指定 key 的值，在该值`后面`追加内容
```python
>>> conn.append('key5','after')
True
>>> conn.get('key5')
'value5after'
```
修改指定 key 的值，在该值 前面 插入内容
```python
>>> conn.prepend('key5','before')
True
>>> conn.get('key5')
'beforevalue5after'
```
自增与自减，将 Memcached 中的某一个值加或减少 N(N 默认为 1)
```python
>>> conn.set('number','9')
True
# 增加
>>> conn.incr('number')
10
# 增加
>>> conn.incr('number', 10)
20
# 减少
>>> conn.decr('number')
19
# 减少
>>> conn.decr('number', 10)
9
```

比如设置了这么一个值：
```python
conn.set('n','10)
```
现在 A 用户和 B 用户同时获取到了这两个值，如果有其中的任何一个用户对这个值进行了修改，那么另外一个用户在对这个值进行操作的时候就会报错。

如果要解决以上的问题可以使用`gets`与`cas`，测试代码如下：

```python
# -- s1.py
# _*_ coding:utf-8 _*_
import memcache
conn1 = memcache.Client(['192.168.56.100:11211'], debug=True, cache_cas=True)
conn1.set('n', 9)
# gets会获取到值并且获取计数器
result = conn1.gets('n')
print(result)
# 阻塞
input('>>>')
# 设置值
conn1.cas('n', 99)

# -- s2
# _*_ coding:utf-8 _*_
import memcache
conn2 = memcache.Client(['192.168.56.100:11211'], debug=True, cache_cas=True)
# gets会获取到值并且获取计数器
result = conn2.gets('n')
print(result)
# 阻塞
input('>>>')
# 设置值
conn2.cas('n', 100)
```
执行效果如下图：
![python-memcache-03](/images/2016/12/1483067689.gif)

多节点的操作

首先在服务器上面起四个`memcached`实例，每个实例都是一个单独的`memcached`服务

```bash
[root@anshengme ~]# netstat -tlnp | grep "memcached"
tcp        0      0 0.0.0.0:11211           0.0.0.0:*               LISTEN      1125/memcached      
tcp        0      0 0.0.0.0:11212           0.0.0.0:*               LISTEN      1330/memcached      
tcp        0      0 0.0.0.0:11213           0.0.0.0:*               LISTEN      1337/memcached      
tcp        0      0 0.0.0.0:11214           0.0.0.0:*               LISTEN      1344/memcached   
```

```python
# _*_ coding:utf-8 _*_

import memcache

# 连接到多台memcached服务器
conn = memcache.Client(
    # IP:端口，权重
    [('192.168.56.100:11211', 4),
     ('192.168.56.100:11212', 3),
     ('192.168.56.100:11213', 1),
     ('192.168.56.100:11214', 2)]
)

conn.set('k', 'v')
```

多节点数据存储流程

1. 先将一个字符串转换为一个数字
2. 得出的结果和节点的数量进行除法运算
3. 得出的结果肯定在节点数量之间，余数是几，就在那台节点上面存放数据

如图所示

![python-memcache-02](/images/2016/12/1483067656.png)

```python
# 将字符串转换为数字模块
import binascii

# 摘自memcache源码中的一部分
def cmemcache_hash(key):
    return ((((binascii.crc32(key) & 0xffffffff) >> 16) & 0x7fff) or 1)

	# result就是返回的数字
result = cmemcache_hash(bytes('k', encoding='utf-8'))
print(result)
```

## 基于 Memcached 的 Session 实例

主程序脚本

```python
# _*_coding:utf-8 _*_

import tornado.ioloop
import tornado.web
import MemcacheToSession

class BaseHandler(tornado.web.RequestHandler):
    def initialize(self):
        self.session = MemcacheToSession.Session(self)
        # pass

class MainHandler(BaseHandler):
    def get(self):
        Info = self.session.GetAll()

        self.render("template/index.html", Data=Info)

    def post(self, *args, **kwargs):
        # 获取传过来的值
        Key = self.get_argument('key')
        Val = self.get_argument('val')
        action = self.get_argument('action')
        if action == 'set':
            # 设置值
            self.session[Key] = Val
        elif action == 'del':
            del self.session[Key]

        # 获取所有信息
        Info = self.session.GetAll()
        # 返回给前端渲染
        self.render("template/index.html", Data=Info)

settings = {
    "tempalte_path": "template",
    "cookie_secret": "508CE6152CB93994628D3E99934B83CC",
}

application = tornado.web.Application([
    (r'/', MainHandler),
], **settings)

if __name__ == "__main__":
    application.listen(9999)
    tornado.ioloop.IOLoop.instance().start()
```
模板文件
```html
<!-- template\index.html -->
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
</head>
<body>

<form action="/" method="post">
    set/del：<input type="text" name="action" value="set"/>
    Key: <input type="text" name="key"/>
    Val: <input type="text" name="val"/>
    <input type="submit" value="设置"/>
</form>

{{ Data }}

</body>
</html>
```
设置 Session 的小模块
```python
# _*_ coding: utf-8 _*_

import memcache
import hashlib
import uuid
import json

# 连接memcached
conn = memcache.Client(
    ['192.168.56.100:11211']
)


class Session:
    CookieID = 'uc'
    ExpiresTime = 60 * 20

    def __init__(self, handler):
        """
        用于创建用户session在memcached中的字典
        :param handler: 请求头
        """
        self.handler = handler
        # 从客户端获取随机字符串
        SessionID = self.handler.get_secure_cookie(Session.CookieID, None)
        # 客户端存在并且在服务端也存在
        if SessionID and conn.get(SessionID):
            self.SessionID = SessionID
        else:
            # 获取随机字符串
            self.SessionID = self.SessionKey()
            # 把随机字符串写入memcached,时间是20分钟
            conn.set(self.SessionID, json.dumps({}), Session.ExpiresTime)
        # 每次访问超时时间就加20分钟
        conn.set(self.SessionID, conn.get(self.SessionID), Session.ExpiresTime)
        # 设置Cookie
        self.handler.set_secure_cookie('uc', self.SessionID)

    def SessionKey(self):
        """
        :return: 生成随机字符串
        """
        UUID = str(uuid.uuid1()).replace('-', '')
        MD5 = hashlib.md5()
        MD5.update(bytes(UUID, encoding='utf-8'))
        SessionKey = MD5.hexdigest()
        return SessionKey

    def __setitem__(self, key, value):
        """
        设置session
        :param key: session信息中的key
        :param value: 对应的Value
        """
        # 获取session_id
        SessionDict = json.loads(conn.get(self.SessionID))
        # 设置字典的key
        SessionDict[key] = value
        # 重新赋值
        conn.set(self.SessionID, json.dumps(SessionDict), Session.ExpiresTime)

    def __getitem__(self, item):
        """
        :param item: Session信息中对应的Key
        :return: 获取的Session信息
        """
        # 获取SessionID并转换为字典
        SessionDict = json.loads(conn.get(self.SessionID))
        # 获取对应的数据
        ResultData = SessionDict.get(item, None)
        return ResultData

    def __delitem__(self, key):
        """
        :param key: 要删除的Key
        """
        # 获取SessionID并转换为字典
        SessionDict = json.loads(conn.get(self.SessionID))
        # 删除字典的key
        del SessionDict[key]
        # 重新赋值
        conn.set(self.SessionID, json.dumps(SessionDict), Session.ExpiresTime)

    def GetAll(self):
        # 获取Session中所有的信息，仅用于测试
        SessionData = conn.get(self.SessionID)
        return SessionData
```
演示如下：
![python-memcache-04](/images/2016/12/1483067610.gif)