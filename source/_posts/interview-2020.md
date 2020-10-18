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
```python
import struct
bytes_len = struct.pack('i',len(send_msg))
```
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

## unitedStack(同方有云)
1. 跳出循环的方式
- break
- return
- raise Exception
2. 代码调试
- print
- log
- pdb
- pycharm debug
[Python 调试代码的 4 种方法：print、log、pdb、PyCharm 的 debug_xiemanR 的专栏-CSDN 博客](https://blog.csdn.net/xiemanR/article/details/72775737)
3. 索引优缺点
- 优点
索引可以减少服务器需要扫描的数据量，从而大大提高查询效率。
唯一索引能保证表中数据的唯一性。
利用索引对数据存储的特性，可以使查询语句避免排序和创建临时表。
索引可以将随机 I/O 变为顺序 I/O。
- 缺点
索引的创建和维护会造成工作量的增加。
索引会造成数据量的增加，除了数据表中数据占数据空间之外，每一个索引还要占一定的物理空间。
不恰当的使用索引会造成服务器重复扫描数据，造成查询浪费。
4. class 实现上下文管理器
实现`__enter__`和`__exit__`方法
5. js 异步编程返回的对象类型
Promise 对象
6. 什么是 RESTful？哪些操作是幂等的？
HTTP 幂等方法是指无论调用多少次都不会有不同结果的 HTTP 方法。它无论是调用一次，还是十次都无关紧要。结果仍应相同。再次强调，它只作用于结果而非资源本身。它仍可能被操纵（如一个更新的 timestamp），提供这一信息并不影响（当前）资源的表现形式。
{%raw%}
<table>
<tbody><tr><th>HTTP Method</th><th>Idempotent</th><th>Safe</th></tr>
    <tr><td>OPTIONS    </td><td>yes       </td><td>yes</td></tr>
    <tr><td>GET        </td><td>yes       </td><td>yes</td></tr>
    <tr><td>HEAD       </td><td>yes       </td><td>yes</td></tr>
    <tr><td>PUT        </td><td>yes       </td><td>no </td></tr>
    <tr><td>POST       </td><td>no        </td><td>no </td></tr>
    <tr><td>DELETE     </td><td>yes       </td><td>no </td></tr>
    <tr><td>PATCH      </td><td>no        </td><td>no </td></tr>
</tbody></table>
{%endraw%}
[哪些是幂等或/且安全的方法？ - RESTful 手册](https://sofish.github.io/restcookbook/http%20methods/idempotency/)

## 同方有云

1. Python中如何动态调用类方法？
参阅[Python 中动态调用函数或类的方法 | 别院牧志](/blog/2020-10-15/python-call-method-dynamically/)
2. 项目中实际使用继承和多态的例子？

## 志翔科技

- 简述一次web请求的过程？
![请求流程](https://image-static.segmentfault.com/406/600/4066004169-5987d7380cd99_articlex)
一次完整的HTTP请求过程从TCP三次握手建立连接成功后开始，客户端按照指定的格式开始向服务端发送HTTP请求。
1. 服务端接收请求后，对HTTP请求中的参数进行解析，包括请求的URL，请求方法，参数以及Cookie等参数，将其置于框架的一个内部数据结构中，便于后续的使用。
2. 在处理完请求参数后，会在请求正式*进入视图函数之前做一些额外处理*，例如：验证CSRF-Token，验证用户Cookie是否合法，请求的IP是否处于白名单中，如果验证信息未通过，则直接返回相应的HTTP状态码以及相关信息，增强网站的安全性。在所有的验证通过之后，Web框架根据URL找到对应的视图函数并进行处理，在处理过程中可能会涉及数据库，Redis以及消息队列的使用，并很可能存在异步任务的触发。
3. 之后根据请求类型和请求url中的路由与视图函数映射关系获取到底请求的是哪个视图，匹配完成之后，到view层的具体视图中执行特定的视图函数。在视图执行过程中，需要先到template末班层找到特定的html文件，再次过程中可能会操作model层（数据库），然后对视图进行渲染。
4. 在视图函数处理过程中，很有可能因为某些操作而导致异常的产生，此时Web应用应该判断异常产生的由来，并进行统一的*异常处理*。 不管是数据库连接异常，还是用户表单验证未通过，都应该给出一个统一的应答，这样便于前端的数据处理，也能够让用户知道到底发生了什么。
5. 处理完业务逻辑，最后返回一个HTTP的响应给客户端，HTTP的响应内容同样有标准的格式。无论是什么客户端或者是什么服务端，大家只要按照HTTP的协议标准来实现的话，那么它一定是通用的。

[一文理解Flask Web开发](https://smartkeyerror.com/Flask-Web)
[用户访问web服务器过程精解_达龙 - SegmentFault 思否](https://segmentfault.com/a/1190000010537218)
