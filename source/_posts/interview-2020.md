---
title: 2020 面试记录（持续更新）
date: 2020-06-09 09:23:06
tags:
- 面试
categories:
---
## 存储

### 文件存储和块存储的区别
| 存储方式 | 技术实现     | 优势          | 劣势       | 典型代表  |
|------|-------------------------------|-------------------------|---------------------------|---------------|
| 块存储  | 裸盘上划分逻辑卷，逻辑卷格式化成任意文件系统        | 支持多种文件系统，传输速度快，提供硬件容错机制 | 无法实现网络共享                  | FC\-SAN，iSCSI |
| 文件存储 | 在格式化的磁盘上存储文件                  | 提供网络共享                  | 网络传输速度制约读写速度，分层目录结构限制可扩展性 | NFS，FAT，EXT3  |
| 对象存储 | 以灵活可定制的对象为存储单元，元数据服务器提供快速并发寻址 | 读写速度较快的同时支持网络共享，对象灵活定义  | 管理软件的购买、使用和运维成本高          | Swift         |


#### 存储设备不同

1. 对象存储：对象存储的对应存储设备为 swift，**键值**存储，CEPH 的 RADOS。

2. 文件存储：文件存储的对应存储设备为 FTP，NAS，NFS 服务器，Ceph 的 CephFS。

3. 块存储：块存储的对应存储设备为 Cinder，硬盘，IPSAN、FCSAN、CEPH 的 RBD。

#### 特点不同

1. 对象存储：对象存储的特点是具备块存储的**高速**以及文件存储的共享等特性，只能进行全写全读，存储数据以大文件为主，要求足够的 IO 带宽。

2. 文件存储：文件存储的特点是一个具有**目录树**结构的大文件夹，大家都可以获取文件。

3. 块存储：块存储的特点是不能直接被操作系统访问，在分区、创建逻辑卷、格式化为指定文件系统后才可以使用，与平常主机内置硬盘的方式完全无异。
参见[块存储、文件存储、对象存储这三者的本质差别是什么？ - 知乎](https://www.zhihu.com/question/21536660)

### RAID 是什么？各类型之间的区别
 参见：[RAID 是什么？各类型之间的区别？ | 别院牧志](/wiki/%E5%AD%98%E5%82%A8/diff-raid/)

## Python

### 可变/不可变、引用类型/传值类型、深拷贝/浅拷贝
dict、list、set 是可变类型

## 中国电信云

1. TCP 的 socket 粘包问题
[Socket 中粘包问题浅析及其解决方案 - 代码星冰乐](https://www.hchstudio.cn/article/2018/d5b3/)
[Socket 粘包问题 - liuslayer - 博客园](https://www.cnblogs.com/liuslayer/p/5441870.html)
[socket 粘包问题解决 - 要一直走下去 - 博客园](https://www.cnblogs.com/staff/p/9643682.html)
[对于 Socket 粘包的困惑? - 知乎](https://www.zhihu.com/question/49144553)
[Socket 编程（4）TCP 粘包问题及解决方案 - melonstreet - 博客园](https://www.cnblogs.com/QG-whz/p/5537447.html)
[python--(socket 与粘包解决方案) - 孔辉 - 博客园](https://www.cnblogs.com/konghui/p/9804914.html#top)
[Python 中的粘包、socket 初识 - 知乎](https://zhuanlan.zhihu.com/p/99736833)
[怎么解决 TCP 网络传输「粘包」问题？ - 知乎](https://www.zhihu.com/question/20210025)
2. 后端数据校验怎么做的？
一般就是用装饰器或者 assert，网上查到一个[JSON Schema | The home of JSON Schema](http://json-schema.org/)和 Flask 专用的扩展[sanjeevan/flask-json-schema: Flask extension to validate JSON requests using the jsonschema spec](https://github.com/sanjeevan/flask-json-schema)
3. MySQL 事务语法

4. 磁盘点灯对盘位使用什么工具？
`smartctl`与`sas2ircu`
[linux 磁盘与磁盘槽位的对应关系](http://llxwj.top/post/storage/linux_disk_slot/)
[如何通过硬盘盘符查询硬盘槽位 - 华为服务器 维护宝典 14 - 华为](https://support.huawei.com/enterprise/zh/doc/EDOC1000041337/75f2d44b)

5. RESTful 的缺点是什么？
 1. 不是所有的东西都是“资源”，尤其是在业务系统中；
 2. 状态码，有的时候你需要“不存在的”一个状态码来描述你的操作；
一个适用于简单操作的接口规范而已，无规矩不成方圆，复杂操作并不适用，还是看业务发展需求的。
[Restful 的理解，Restful 优缺点 - Alan 大 bug - 博客园](https://www.cnblogs.com/binlin1987/p/6971808.html)
[REST 的缺点是什么？-InfoQ](https://www.infoq.cn/article/2013/06/rest-drawbacks)
6. gRPC 与 RESTful 有什么区别？
- 优点
1. protobuf 二进制消息，性能好/效率高（空间和时间效率都很不错）
2. proto 文件生成目标代码，简单易用
3. 序列化反序列化直接对应程序中的数据类，不需要解析后在进行映射(XML,JSON 都是这种方式)
4. 支持向前兼容（新加字段采用默认值）和向后兼容（忽略新加字段），简化升级
5. 支持多种语言（可以把 proto 文件看做 IDL 文件）
- 缺点
1. GRPC 尚未提供连接池，需要自行实现
2.  尚未提供“服务发现”、“负载均衡”机制
3. 因为基于 HTTP2，绝大部多数 HTTP Server、Nginx 都尚不支持，即 Nginx 不能将 GRPC 请求作为 HTTP 请求来负载均衡，而是作为普通的 TCP 请求。（nginx1.9 版本已支持）
4. Protobuf 二进制可读性差（貌似提供了 Text_Fromat 功能）
5. 默认不具备动态特性（可以通过动态定义生成消息类型或者动态编译支持）