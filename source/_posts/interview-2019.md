---
title: 2019 面试记录
date: 2019-10-18 10:03:12
tags:
- 记录
- Python
- 后端
- 面试
---
## FunPlus (小视频业务)
### 数据库的事务隔离机制
#### 隔离级别

- READ UNCOMMITTED（未提交读）
这个级别，事务中的修改，即使没有提交，对其他事务也都是可见的。事务可以读取未提交的数据，被称为脏读（Dirty Read），这个级别性能不会比其他级别好太多，但缺乏其他级别的很多好处，一般很少使用。

- READ COMMITTED（提交读）
这个级别是大多数数据库系统的默认隔离级别（但 MySQL 不是）。一个事务从开始直到提交之前，所做的任何修改对其他事务都是不可见的。这个级别也叫作不可重复读（nonrepeatable read），因为两次执行同样的查询，可能会得到不一样的结果。

- REPEATABLE READ（可重复读）
该级别保证了在同一个事务中多次读取同样记录的结果是一致的，但依然无法解决另外一个幻读（Phantom Read）的问题。幻读，指的是当某个事务在读取某个范围内的记录时，另外一个事务又在该范围内插入了新的记录，当之前的事务再次读取该范围的记录时，会产生幻行（Phantom Row）。InnoDB 和 XtraDB 存储引擎通过多版本并发控制（MVCC）解决了幻读的问题。可重复读是 MySQL 的默认事务隔离级别。

- SERIALIZABLE（可串行化）
最高的隔离级别，强制事务串行执行，避免了前面说的幻读的问题。但每次读都需要获得表级共享锁，读写相互都会阻塞。

所有隔离级别
1. read uncommitted : 读取尚未提交的数据 ：哪个问题都不能解决

2. read committed：读取已经提交的数据 ：可以解决脏读 —- oracle 默认的

3. repeatable read：可重复读：可以解决脏读 和 不可重复读 —- mysql 默认的

4. serializable：串行化：可以解决 脏读 不可重复读 和 虚读—-相当于锁表

| 事务隔离级别          | 脏读 | 可重复读 | 幻读 |
| --------------------------- | ---- | -------- | ---- |
| 未提交读（read uncommited） | ×   | ×       | ×   |
| 提交读（read commited） | √  | ×       | ×   |
| 可重复读（repeatable read） | √  | √      | ×   |
| 串行化（serialziable)   | √  | √      | √  |

注：×表示有该问题，√表示解决该问题。

1. 脏读：事务 A 读取了事务 B 更新的数据，然后 B 进行回滚操作，那么 A 读取到的数据是脏数据；

2. 不可重复读：事务 A 多次读取同一数据，事务 B 在事务 A 多次读取的过程中，对数据作了更新并提交，导致事务 A 多次读取同一数据时，结果不一致;

3. 幻读：“当事务 A 要对数据表中某个字段的所有值进修改操作，此时有一个事务是插入一条记录 并提交给数据库，当提交事务 A 的用户再次查看时就会发现有一行数据未被修改，其实是事务 B 刚刚添加进去的”，这就是幻读；

隔离级别越高，越能保证数据的完整性和统一性，但是对并发性能的影响也越大。对于多数应用程序，可以优先考虑把数据库系统的隔离级别设为 Read Committed。它能够避免脏读，而且具有较好的并发性能。尽管它会导致不可重复读、幻读和第二类丢失更新这些并发问题，在可能出现这类问题的个别场合，可以由应用程序采用悲观锁或乐观锁来控制。

[MySQL 事务隔离机制&锁](https://blog.csdn.net/xiancaione/article/details/82157019)
[MySQL 隔离级别](https://blog.csdn.net/taylor_tao/article/details/7063639)
[数据库事务和四种隔离级别](https://blog.csdn.net/weixin_39651041/article/details/79980202)
[RR(REPEATABLE-READ) 与 RC(READ-COMMITED) 隔离级别的异同](http://tech.dianwoda.com/2018/09/06/rr-yu-rcge-chi-ji-bie-de-yi-tong/)

### flask 组件及源码剖析
- [Flask 自带的常用组件介绍](https://www.jianshu.com/p/8f01ad89406d)
    1. session
    2. flash，消息闪现
    3. jsonify，返回 json 化数据
    4. blueprint，构建大型应用条理化
    5. g，Flask 中的全局变量 g ，可以为特定请求临时存储任何需要的数据并且是线程安全的，当请求结束时，这个对象会被销毁，下一个新的请求到来时又会产生一个新的 g。
    6. abort，自定义错误
    7. current_app，应用上下文
- [一个 Flask 应用运行过程剖析](https://segmentfault.com/a/1190000009152550)
- [Flask 的请求处理流程和上下文](https://www.jianshu.com/p/2a2407f66438)
- [flask 源码解析](https://cizixs.com/2017/01/10/flask-insight-introduction/)
- [Flask 源码解析:Flask 应用执行流程及原理](https://www.cnblogs.com/weihengblog/p/9490561.html)
- [Flask 面试题](https://www.cnblogs.com/Utopia-Clint/p/10824238.html)
- [Flask 源码解读 | 浅谈 Flask 基本工作流程](https://blog.csdn.net/bestallen/article/details/54342120)

### redis 中的数据类型，其中列表和有序集合有什么区别
####  list 列表
List 内部数据结构是双向链表，可以在链表左、右两边分别操作，所以插入数据的速度很快。

也可以把 list 看成一种队列，所以在很多时候可以用 redis 用作消息队列，这个时候它的作用类似于 activeMq；

但是缺点就是在数据量比较大的时候，访问某个数据的时间可能会很长，但针对这种情况，可以使用 zset。

应用案例有时间轴数据，评论列表，消息传递等等，它可以提供简便的分页，读写操作。
#### Set 集合
Set 就是一个集合，内部数据结构是整数集合(intset)、HASH 表，集合的概念就是一堆**不重复值**的组合。利用 Redis 提供的 Set 数据结构，可以存储一些集合性的数据。

比如在微博应用中，可以将一个用户所有的关注人存在一个集合中，将其所有粉丝存在一个集合。

因为 Redis 非常人性化的为集合提供了求交集、并集、差集等操作，那么就可以非常方便的实现如共同关注、共同喜好、二度好友等功能，对上面的所有集合操作，你还可以使用不同的命令选择将结果返回给客户端还是存集到一个新的集合中。

1.共同好友、二度好友
2.利用唯一性，可以统计访问网站的所有独立 IP
3.好友推荐的时候，根据 tag 求交集，大于某个阈值（threshold）就可以推荐
#### Zset 集合（Sorted Sets）
Sorted Set 有点像 Set 和 Hash 的结合体。

和 Set 一样，它里面的元素是唯一的，但是 Set 里面的元素是无序的，而 Sorted Set 里面的元素都带有一个浮点值，叫做分数（score），内部数据结构**跳跃表**，所以这一点和 Hash 有点像，因为每个元素都映射到了一个值。
使它在 set 的基础上增加了一个**顺序属性**，这一属性在添加修改元素的时候可以指定，每次指定后，zset 会自动重新按新的值调整顺序。可以对指定键的值进行排序权重的设定，它应用排名模块比较多。

比如一个存储全班同学成绩的 Sorted Sets，其集合 value 可以是同学的学号，而 score 就可以是其考试得分，这样在数据插入集合的时候，就已经进行了天然的排序。另外还可以用 Sorted Sets 来做带权重的队列，比如普通消息的 score 为 1，重要消息的 score 为 2，然后工作线程可以选择按 score 的倒序来获取工作任务，让重要的任务优先执行。

zset 集合可以完成有序执行、按照`优先级执行`的情况；
- [redis 五种数据结构详解（string，list，set，zset，hash）](https://www.cnblogs.com/xuzhengzong/p/7724841.html)   
- [Redis 实战 - list、set 和 Sorted Set](https://www.cnblogs.com/tangge/p/10698821.html)    

## 独到科技

### 进程线程以及协程

1. 进程   
进程是具有一定独立功能的程序关于某个数据集合上的一次运行活动，**进程是系统进行资源分配和调度的基本单位**。每个进程都有自己的独立内存空间，不同进程通过进程间通信*（IPC）来通信。由于进程比较重量，占据独立的内存，所以上下文进程间的切换开销（栈、寄存器、虚拟内存、文件句柄等）比较大，但相对比较稳定安全。

2. 线程   
**线程是进程的一个实体，是 CPU 调度和分派的基本单位**，它是比进程更小的能独立运行的基本单位。线程自己基本上不拥有系统资源，只拥有一点在运行中必不可少的资源(如程序计数器，一组寄存器和栈)，但是它可与同属一个进程的其他的线程共享进程所拥有的全部资源。线程间通信主要通过共享内存，上下文切换很快，资源开销较少，但相比进程不够稳定容易丢失数据。

3. 协程   
协程是一种**用户态**的**轻量级线程**，**协程的调度完全由用户控制**。**协程拥有自己的寄存器上下文和栈**。协程调度切换时，将寄存器上下文和栈保存到其他地方，在切回来的时候，恢复先前保存的寄存器上下文和栈，直接操作栈则基本没有内核切换的开销，可以不加锁的访问全局变量，所以上下文的切换非常快。可以利用到并发优势，又可以**避免反复系统调用和进程切换造成的开销**。

#### 区别

- 进程与线程比较
线程是指进程内的一个执行单元，也是进程内的可调度实体。线程与进程的区别:
1. 地址空间:线程是进程内的一个执行单元，进程内至少有一个线程，它们共享进程的地址空间，而进程有自己独立的地址空间；
2. 资源拥有:进程是资源分配和拥有的单位，同一个进程内的线程共享进程的资源；
3. 线程是处理器调度的基本单位，但进程不是；
4. 每个独立的线程有一个程序运行的入口、顺序执行序列和程序的出口，但是线程不能够独立执行，必须依存在应用程序中，由应用程序提供多个线程执行控制；

- 协程与线程进行比较
1. 一个线程可以多个协程，一个进程也可以单独拥有多个协程，这样 python 中则能使用多核 CPU；
2. 线程进程都是同步机制，而协程则是**异步**；
3. 协程能保留上一次调用时的状态，每次过程重入时，就相当于进入上一次调用的状态；
内核态的线程是由操作系统来进行调度的，在切换线程上下文时，要先保存上一个线程的上下文，然后执行下一个线程，当条件满足时，切换回上一个线程，并恢复上下文。协程也是如此（指需要切换 → 保存 → 恢复上下文）。只不过，用户态的线程不是由操作系统来调度的，而是由程序员来调度的，是在用户态的。    
[进程和线程、协程的区别](https://www.cnblogs.com/lxmhhy/p/6041001.html)

### 二叉树的深度优先算法和广度优先算法
二叉树的**深度优先**遍历的非递归的通用做法是**采用栈**，**广度优先**遍历的非递归的通用做法是**采用队列**。
1：树的深度优先遍历主要分为：前序遍历、中序遍历以及后序遍历
    - 前序遍历：若二叉树为空则结束，否则依次先访问根节点，然后访问左子树，最后访问右子树。
    - 中序遍历：若二叉树为空则结束，否则先访问根节点的左子树，然后访问根节点，最后访问右子数。
    - 后序遍历：若二叉树为空则结束，否则先访问根节点的左子树，然后访问右子数，最后访问根节点。
     深度优先一般采用递归的方式实现，递归的深度为树的高度。
2：树的广度优先算法：广度优先是按照层次来遍历树的节点，先是根节点，然后依次遍历第二层子节点，当第二层子节点遍历完后，在依次遍历第三层子节点。广度优先采用队列来记录当前可遍历的节点，当遍历某个节点时，将其左孩子和右孩子结点依次入队，待该层遍历完了以后，再依次遍历下一层儿子结点。
3：非递归实现特点： 深度优先一般采用递归实现，如改用非递归，则可需要来模拟栈，当需要先遍历当前节点的儿子结点时（例如中序遍历）需要将其压入栈中，先遍历其儿子结点，然后再将其弹出栈，遍历当前节点。广度优先一般采用非递归来实现，用一个队列来保存依次需要遍历的节点。 
1. [二叉树深度优先遍历（DFS）和广度优先遍历（BFS）](https://www.masantu.com/blog/2019-10-28/binary-tree-BFS-and-DFS/)
2. [简述树的深度优先算法、广度优先算法，及非递归实现的特点](https://www.nowcoder.com/questionTerminal/b194924b44b144e8a238819a0a6dae42)   
3. [广度优先搜索(BFS)和深度优先搜索(DFS)](https://nullcc.github.io/2018/06/07/广度优先搜索(BFS)和深度优先搜索(DFS)/)
> https://nullcc.github.io/2018/06/07/广度优先搜索(BFS)和深度优先搜索(DFS)/

### Python 垃圾回收机制
[Python 垃圾回收机制](https://wiki.masantu.com/wiki/%F0%9F%92%BB%E5%B7%A5%E4%BD%9C/%F0%9F%90%8DPython/%E9%9D%A2%E8%AF%95/interview-of-python/#Python-%E5%9E%83%E5%9C%BE%E5%9B%9E%E6%94%B6%E6%9C%BA%E5%88%B6)
- 引用计数  
PyObject 是每个对象必有的内容，其中 ob_refcnt 就是做为引用计数。当一个对象有新的引用时，它的 ob_refcnt 就会增加，当引用它的对象被删除，它的 ob_refcnt 就会减少。引用计数为 0 时，该对象生命就结束了。
- 标记-清除机制   
基本思路是先按需分配，等到没有空闲内存的时候从寄存器和程序栈上的引用出发，遍历以对象为节点、以引用为边构成的图，把所有可以访问到的对象打上标记，然后清扫一遍内存空间，把所有没标记的对象释放。
- 分代技术  
分代回收是一种以空间换时间的操作方式，Python 将内存根据对象的存活时间划分为不同的集合，每个集合称为一个代，Python 将内存分为了 3“代”，分别为年轻代（第 0 代）、中年代（第 1 代）、老年代（第 2 代），他们对应的是 3 个链表，它们的垃圾收集频率与对象的存活时间的增大而减小。新创建的对象都会分配在年轻代，年轻代链表的总数达到上限时，Python 垃圾收集机制就会被触发，把那些可以被回收的对象回收掉，而那些不会回收的对象就会被移到中年代去，依此类推，老年代中的对象是存活时间最久的对象，甚至是存活于整个系统的生命周期内。同时，分代回收是建立在标记清除技术基础之上。

分代回收的整体思想是：将系统中的所有内存块根据其存活时间划分为不同的集合，每个集合就成为一个“代”，垃圾收集频率随着“代”的存活时间的增大而减小，存活时间通常利用经过几次垃圾回收来度量。

### Python 传值还是传引用

python 参数传递采用的是“**传对象引用**”的方式。这种方式相当于传值和传引用的一种综合。如果函数收到的是一个不可变对象（数字、字符或元组）的引用，就不能直接修改原始对象——相当于通过‘值传递’来传递对象。如果函数收到的是一个可变对象（字典、列表）的引用，就能修改对象的原始值——相当于‘传引用’来传递对象。

[Python 传值还是传引用？| 通过对象引用传递](https://www.masantu.com/blog/2019-04-13/python-pass-by-object-reference/)

## 中天联科

### 类属性和实例属性的区别，如何判断类 A 是否有属性 x
[类变量和实例变量](https://github.com/imoyao/interview_python#4-%E7%B1%BB%E5%8F%98%E9%87%8F%E5%92%8C%E5%AE%9E%E4%BE%8B%E5%8F%98%E9%87%8F)
```python
class A:
    X = 'Hello'     # 类属性

    def __init__(self,name='World'):
        self.name = name    # 实例属性

a = A('foo')
print(A.X)  # Hello
print(a.name)   #foo
print(hasattr(a,'X'))   # True
print(hasattr(A,'X'))   # True
print(hasattr(A,'name'))    # False
print(hasattr(a,'name'))    # True
setattr(a,'name','bar')
setattr(A,'X','Bye')
print(a.name)   # bar
print(A.X)  # Bye
```

### 什么是列表推导式？如何用一行代码判断一个文件夹下面文件数大于 10 个的子目录

```python
import os
print([_ for _ in range(10)])

def find_file_more_than_10(root_dir_fp=None, limit=10):
    if root_dir_fp is None:
        root_dir_fp = os.path.split((os.path.abspath(__file__)))[0]

    return [dirpath for dirpath, _, filenames in os.walk(root_dir_fp) if
            len(filenames) > limit]


if __name__ == '__main__':
    print(find_file_more_than_10())
```

### 什么是协程？什么是生成器

- 生成器
`yield`和生成器表达式`(i for i in range(10))`。

## 金山云

### 单例模式，如何实现？以及如何判断只有这一个实例
```python
class Singleton:    # py3
	_instance = {}
	def __new__(cls,*args,**kwargs):
		if not cls._instance:
			cls._instance = super(Singleton,cls).__new__(cls,*args,**kwargs)
		return cls._instance


def deco_singleton(cls):
	_instance = {}
	def wrapper(*args,**kwargs):
		if not cls in _instance:
			_instance[cls] = cls(*args,**kwargs)

		return _instance[cls]
	return wrapper

@deco_singleton
class A:
	pass
```

### 死锁产生的原因

### ping 域名的过程
[ping 某域名的过程详解](https://www.masantu.com/blog/2019-11-19/the-detail-of-ping-a-domain/)

### select 和 epoll 区别
1. [Python 全栈之路系列之 IO 多路复用](https://blog.ansheng.me/article/python-full-stack-way-io-multiplexing.html)
2. [select、poll、epoll 之间的区别总结[整理]](https://www.cnblogs.com/anker/p/3265058.html)
3. [Python 异步非阻塞 IO 多路复用 Select/Poll/Epoll 使用](https://www.haiyun.me/archives/1056.html)
4. [Python 使用 select 和 epoll 实现 IO 多路复用实现并发服务器](https://www.jianshu.com/p/cdfddb026db0)
5. [How To Use Linux epoll with Python](https://harveyqing.gitbooks.io/python-read-and-write/content/python_advance/how_to_use_linux_epoll.html)

## 艾普艾

### **Redis**的数据类型都有哪些，如果要实现计数器功能，应该选用哪种数据类型？使用 Redis，如果内存满了会怎么样
- 数据类型
string，list，set，zset，hash
- 计数器/限流器功能
1. 可以选用`string`类型，调用`incr()`方法，参见[INCR](https://redis.io/commands/INCR)
每次自增加 1
```shell
redis> SET mykey "10"
"OK"
redis> INCR mykey
(integer) 11
redis> GET mykey
"11"
```
2. 可以选用`hash`类型，调用`hincrby()`方法，参见[HINCRBY](https://redis.io/commands/hincrby)
对关联的统计项进行统一管理；
```shell
redis> HSET myhash field 5
(integer) 1
redis> HINCRBY myhash field 1
(integer) 6
redis> HINCRBY myhash field -1
(integer) 5
redis> HINCRBY myhash field -10
(integer) -5
```
3. 可以选用`set`类型，调用`sadd()`方法，参见[SADD](https://redis.io/commands/SADD)
多次调用只加一，防作弊刷数据等；
```shell
redis> SADD myset "Hello"
(integer) 1
redis> SADD myset "World"
(integer) 1
redis> SADD myset "World"
(integer) 0
redis> SMEMBERS myset
1) "Hello"
2) "World"
```
更多 Python 实例应用:[*Redis 多方式实现计数器功能（附代码）*](https://juejin.im/post/5da6923c5188252f192d2835)

#### 内存满了
此时不能继续写入数据，而且系统的其他操作任务也会受到影响。为防止这种现象发生，应该启用内存淘汰策略。
[Redis 内存满了的几种解决方法](https://blog.csdn.net/u014590757/article/details/79788076)
[Redis 过期--淘汰机制的解析和内存占用过高的解决方案](https://juejin.im/post/5dc81b4df265da4d4d0cfebc)

#### 更多
[10 个常见的 Redis 面试"刁难"问题](https://www.kancloud.cn/mangyusisha/php/701563)

### 常见状态码错误？301、302 错误及区别？502 错误出现时应该怎么解决
- 301/302
跳转，301 redirect: 301 代表**永久性**转移(Permanently Moved)；302 redirect: 302 代表**暂时性**转移(Temporarily Moved )

参见[http 状态码 301 和 302 详解及区别——辛酸的探索之路](http://blog.csdn.net/grandPang/article/details/47448395)

- 502 Bad Gateway Error

对用户访问请求的响应超时错误
1. DNS 测试，ping 测试
2. 检查防火墙端口，检查防火墙日志
3. 数据库调用延迟
4. 网络服务进程是否正常 

#### 参考

1. [502 Bad Gateway 怎么解决？](https://www.zhihu.com/question/21647204)
1. [How to Solve 502 Bad Gateway Issues?](https://www.keycdn.com/support/502-bad-gateway)

## 华胜天成

### 类属性的继承
```python
class Parent:
    x = 10

class Child1(Parent):
    pass


class Child2(Parent):
    pass

a = Parent()
b = Child1()
c = Child2()

print(a.x,b.x,c.x)  # (10, 10, 10)
a.x = 20
print(a.x,b.x,c.x)  # (20, 10, 10)
b.x = 30
print(a.x,b.x,c.x)  # (20, 30, 10)
```
```python
class A:
    x = 'a'

class B:
    x = 'b'

class C(A,B):
    pass

class D(B,A):
    pass

print(A.x,B.x,C.x,D.x)  # ('a', 'b', 'a', 'b')
A.x = 'a1'
print(A.x,B.x,C.x,D.x)  # ('a1', 'b', 'a1', 'b')
B.x = 'b1'
print(A.x,B.x,C.x,D.x)  # ('a1', 'b1', 'a1', 'b1')
C.x = 'c'
print(A.x,B.x,C.x,D.x)  # ('a1', 'b1', 'c', 'b1')
```

## 更多
[字节跳动、腾讯后台开发面经分享(2019.5)](https://juejin.im/post/5cf7ea91e51d4576bc1a0dc2)