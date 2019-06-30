---
title: Linux 下如何安装 Redis？

date: 2019-04-11 10:03:08

tags:
- Redis
- NoSQL
- 数据库
- HOWTO

toc: true
---
`Redis`是一款高性能的`key-value`数据库，本文主要记录如何在`Linux`系统上进行安装，以及为`Python`开发安装对应的`redis`模块。

<!--more-->

## 测试环境

- `Linux`版本

    ```plain
    Ubuntu 18.04 LTS && NeoKylin 3.2
    ```

- `Python`版本

    ```plain
    Python 2.7.15rc1 && Python 2.6.6
    ```

- `Redis`版本

    ```plain
    redis-5.0.4
    ```

- `redis-py`版本

    ```plain
    redis-3.2.1 && redis-2.10.6
    ```


## 下载

下载地址：`http://redis.io/download`，下载最新稳定版本源码。

本文使用的版本为 `redis-5.0.4`。

## 安装

### Ubuntu

1. 解压缩

    首先要解压`Redis`压缩包。进入压缩包下载的路径，执行：
    
    ```shell
    tar xzf redis-5.0.4.tar.gz
    ```
2. 使用`GCC`编译源码

    ```shell
    cd redis-5.0.4
    make
    ```
3. 安装`Redis`

    ```shell
    make install
    ```
4. 验证

    ```shell
    root@local:~/temp# redis-server -v
    Redis server v=5.0.4 sha=00000000:0 malloc=jemalloc-5.1.0 bits=64 build=3dcf53963ddc396a
    root@local:~/temp# whereis redis-server
    redis-server: /usr/local/bin/redis-server
    ```

至此，`Redis`安装完成。

### CentOs

1. 编译安装

    ```shell
    make $$ make install
    ```
    此时报错
    ```shell
    CC adlist.o
    /bin/sh: cc: command not found
    make[1]: *** [adlist.o] Error 127
    make[1]: Leaving directory `/root/temp/redis-5.0.4/src'
    make: *** [all] Error 2
    ```

2. 安装 gcc

    ```shell
    yum install gcc -y
    ```
    
3. 重新 make

    ```shell
    make
    ```
    此时报错
    ```shell
    In file included from adlist.c:34:
    zmalloc.h:50:31: error: jemalloc/jemalloc.h: No such file or directory
    zmalloc.h:55:2: error: #error "Newer version of jemalloc required"
    make[1]: *** [adlist.o] Error 1
    make[1]: Leaving directory `/root/temp/redis-5.0.4/src'
    make: *** [all] Error 2
    ```
    在构建`Redis`时选择非默认内存分配器是通过设置`MALLOC`环境变量完成的， 默认情况下 Redis 是使用`malloc`为`libc`编译和链接的。
    而`libc`并不是`Linux`上默认的分配器，默认的是 `jemalloc`, 因为 `jemalloc` 被证明比`libc`有更少的碎片问题（`fragmentation problems`）。
    但是如果你没有`jemalloc` 而只有`libc` 当然 `make` 出错。 所以有两种解决办法：
    
- ~~方法一~~（不推荐）

    ```shell
    make MALLOC=libc
    ```

---

- 方法二

    ```sehll
    cd deps/
    make hiredis jemalloc linenoise lua geohash-int
    ```
    
原因参见： [浅谈 redis 采用不同内存分配器 tcmalloc 和 jemalloc](http://www.jb51.net/article/100575.htm)

>对于`tcmalloc`，`jemalloc`和`libc`对应的三个内存分配器。其性能和碎片率如何呢？
>下面是一个简单测试结果，使用`Redis`自带的`redis-benchmark`写入等量数据进行测试，数据摘自采用不同分配器时`Redis info`信息。
>我们可以看到，采用`tcmalloc`时碎片率是最低的，为`1.01`，`jemalloc`为`1.02`，而`libc`的分配器碎片率为`1.31`，

4. 编译安装

    ```shell
    make $$ make install
    ```

5. 验证

    ```shellplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplain
    redis-server -v
    Redis server v=5.0.4 sha=00000000:0 malloc=jemalloc-5.1.0 bits=64 build=b139020f90f1d493
    whereis redis-server
    redis-server: /usr/local/bin/redis-server
    ```
至此，`Redis`安装完成。

## 配置

通过配置文件，设置`Redis`服务开机自启动。

1. 设置自启动配置文件

    1. 切换目录
        
        ```shell
        cd utils/
        ```
    2. 复制脚本文件
    
        ```shell
        cp redis_init_script /etc/init.d/redisd
        ```
        将`redis_init_script`文件重新命名为`redisd`，作为系统启动服务名（以`d`结尾表示是自启动服务，约定俗成）。
    
    3. 修改配置
        ```shell
        vi /etc/init.d/redisd
        ```
    4. 修改`redisd`文件，注意要在文件头部加上两句注释来设定该服务的运行级别
    
        ```shell
        #!/bin/sh
        # chkconfig:   2345 90 10
        ```

2.  设置`Redis`控制脚本的配置文件

    1. 切换目录
        ```shell
        cd -
        cd ..
        ```
    2. 在`redis`安装目录下，找到`redis.conf`文件
        ```shell
        ls
        ```
        如下
        ```shell
        00-RELEASENOTES  INSTALL     runtest           tests
        BUGS             Makefile    runtest-cluster   utils
        CONTRIBUTING     MANIFESTO   runtest-sentinel
        COPYING          README.md   sentinel.conf
        deps             redis.conf  src
        ```
    3. 复制配置文件并重命名
        ```shell
        cp redis.conf /etc/redis/6379.conf
        ```
    4. 编辑`Redis`配置文件
        1. 设置`daemonize`为`yes`，使服务可以后台运行：
        
            ```shell
            # nu:136
            daemonize yes
            ```
        2. 设置`log`文件路径：
            ```shell
            # nu:171
            logfile /var/log/redis/redis-server.log
            ```
        3. 设置持久化文件存放路径：
            ```shell
            # nu:263
            dir /var/lib/redis
            ```
    5. 保存退出，并创建相应的目录结构：
        ```shell
        mkdir /var/log/redis
        touch /var/log/redis/redis-server.log
        mkdir /var/lib/redis
        ```
3. 设置开机自启
    #### Ubuntu
    ```shell
    # 赋权
    chmod +x /etc/init.d/redisd
    # 更新系统启动项
    update-rc.d redisd defaults
    ```
    #### CentOS
    ```shell
    [root@master init.d]# chmod +x ./redisd
    [root@master init.d]# chkconfig redisd on
    ```
## 附：常用`redis`管理命令

- 启动`Redis`服务：

```shell
service redisd start
[root@master init.d]# service redisd start
Starting Redis server...
# 验证
[root@master init.d]# ps aux|grep redis|grep -v grep
root      6728  0.1  0.4  55572  9820 ?        Ssl  11:03   0:00 /usr/local/bin/redis-server 127.0.0.1:6379 
```

- 关闭服务：

```shell
[root@master init.d]# service redisd stop
Stopping ...
Redis stopped
[root@master init.d]# ps aux|grep redis|grep -v grep

```

- 重启服务：

```shell
service redisd restart

```

- 在控制台中登录`redis`客户端：

```plain
[root@master init.d]# redis-cli
# 测试redis连通性
127.0.0.1:6379> ping
PONG
127.0.0.1:6379> set hello world
OK
127.0.0.1:6379> get hello
"world"

```

## 安装提供`Python`支持

### pip 安装

```shell
pip install redis
```

### 源码安装

去`https://pypi.org/project/redis/`下载源码，`Ubuntu`上使用最新版本`redis 3.2.1`

1. 解压

    ```shell
    tar -xzvf redis-3.2.1.tar.gz
    ```

2. 切换目录
    
    ```shell
    cd redis-3.2.1
    ```

3. 安装

    ```shell
    python setup.py install
    ```
4. 验证
    
    ```shell
    root@local:~/temp/redis-3.2.1# python
    Python 2.7.15rc1 (default, Apr 15 2018, 21:51:34) 
    [GCC 7.3.0] on linux2
    Type "help", "copyright", "credits" or "license" for more information.
    >>> import redis
    >>> import redis
    >>> 
    >>> r = redis.Redis(host='localhost', port=6379, db=0)
    >>> ret = r.get('hello')
    >>> print ret
    world
    ```

---

**小插曲**

关于 redis-py 的 Python 低版本支持

在`CentOS`上安装`redis-3.2.1`的时候由于`python`版本较低（`2.6.6`）出现以下问题
```shell
[root@master redis-3.2.1]# python setup.py install
Traceback (most recent call last):
  File "setup.py", line 4, in <module>
    from setuptools import setup
ImportError: No module named setuptools
```
安装`setuptools-0.6c9`之后执行`python setup.py install`报错：

```shell
Traceback (most recent call last):
  File "setup.py", line 7, in <module>
    from redis import __version__
  File "/root/temp/pyredis-3.2.1/redis/__init__.py", line 1, in <module>
    from redis.client import Redis, StrictRedis
  File "/root/temp/pyredis-3.2.1/redis/client.py", line 3046
    return {decode(encode(k)): v for k, v in iteritems(data)}
                                   ^
SyntaxError: invalid syntax
```
去官网查看，发现最新版版本支持为：
```shell
Meta
……
 Tags: Redis, key-value store

Requires: Python >=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*
```
以及
> Python Version Support
> redis-py 3.0 now supports Python 2.7 and Python 3.4+. Python 2.6 and 3.3 support has been dropped.

最后安装较低版本（`redis-2.10.6`）成功，步骤同上，不再赘述。

读者可以从 [这里](https://pypi.org/project/redis/#history) 获取历史版本：`https://pypi.org/project/redis/#history`

## 参考链接

- [Redis Quick Start](https://redis.io/topics/quickstart)
- [Ubuntu 安装 Redis 并设置为开机自启动服务](https://blog.csdn.net/softwave/article/details/53838194)
- [Python 操作 Redis 数据库](https://www.cnblogs.com/cnkai/p/7642787.html)

