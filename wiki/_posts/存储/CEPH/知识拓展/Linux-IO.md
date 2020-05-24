---
title: 了解 Linux IO 调度算法
toc: true
date: 2020-05-23 11:02:28
tags:
- ceph

---

## I/O 调度程序的总结


![img](https://images0.cnblogs.com/i/609710/201403/051225079271803.jpg)

 

1) 当向设备写入数据块或是从设备读出数据块时,请求都被安置在一个队列中等待完成.

2) 每个块设备都有它自己的队列.

3) I/O 调度程序负责维护这些队列的顺序,以更有效地利用介质.I/O 调度程序将无序的 I/O 操作变为有序的 I/O 操作.

4) 内核必须首先确定队列中一共有多少个请求,然后才开始进行调度.

 

## I/O 调度的 4 种算法

1) CFQ(Completely Fair Queuing, 完全公平排队)

特点:

在最新的内核版本和发行版中,都选择 CFQ 做为默认的 I/O 调度器,对于通用的服务器也是最好的选择.

CFQ 试图均匀地分布对 I/O 带宽的访问,避免进程被饿死并实现较低的延迟,是 deadline 和 as 调度器的折中.

CFQ 对于多媒体应用(video,audio)和桌面系统是最好的选择.

CFQ 赋予 I/O 请求一个优先级,而 I/O 优先级请求独立于进程优先级,高优先级进程的读写不能自动地继承高的 I/O 优先级.

 

工作原理:

CFQ 为每个进程/线程单独创建一个队列来管理该进程所产生的请求,也就是说每个进程一个队列,各队列之间的调度使用时间片来调度,以此来保证每个进程都能被很好的分配到 I/O 带宽.I/O 调度器每次执行一个进程的 4 次请求.

 

2) NOOP(电梯式调度程序)

特点:

在 Linux2.4 或更早的版本的调度程序,那时只有这一种 I/O 调度算法.

NOOP 实现了一个 FIFO 队列,它像电梯的工作主法一样对 I/O 请求进行组织,当有一个新的请求到来时,它将请求合并到最近的请求之后,以此来保证请求同一介质.

NOOP 倾向饿死读而利于写.

NOOP 对于闪存设备,RAM,嵌入式系统是最好的选择.

 

电梯算法饿死读请求的解释:

因为写请求比读请求更容易.

写请求通过文件系统 cache,不需要等一次写完成,就可以开始下一次写操作,写请求通过合并,堆积到 I/O 队列中.

读请求需要等到它前面所有的读操作完成,才能进行下一次读操作.在读操作之间有几毫秒时间,而写请求在这之间就到来,饿死了后面的读请求.

 

3) Deadline(截止时间调度程序)

特点:

通过时间以及硬盘区域进行分类,这个分类和合并要求类似于 noop 的调度程序.

Deadline 确保了在一个截止时间内服务请求,这个截止时间是可调整的,而默认读期限短于写期限.这样就防止了写操作因为不能被读取而饿死的现象.

Deadline 对数据库环境(ORACLE RAC,MYSQL 等)是最好的选择.

 

4) AS(预料 I/O 调度程序)

特点:

本质上与 Deadline 一样,但在最后一次读操作后,要等待 6ms,才能继续进行对其它 I/O 请求进行调度.

可以从应用程序中预订一个新的读请求,改进读操作的执行,但以一些写操作为代价.

它会在每个 6ms 中插入新的 I/O 操作,而会将一些小写入流合并成一个大写入流,用写入延时换取最大的写入吞吐量.

AS 适合于写入较多的环境,比如文件服务器

AS 对数据库环境表现很差.

 

三) I/O 调度方法的查看与设置

 1) 查看当前系统的 I/O 调度

```plain
[root@localhost ~]# cat /sys/block/sda/queue/scheduler
noop anticipatory deadline [cfq] 
```

 

2) 临时更改 I/O 调度

例如:想更改到 noop 电梯调度算法:

```plain
[root@localhost ~]# echo noop > /sys/block/sda/queue/scheduler
```

 

3) 永久更改 I/O 调度

修改内核引导参数,加入 elevator=调度程序名

```plain
[root@localhost ~]# echo noop > /sys/block/sda/queue/scheduler
```

 

更改到如下内容:

```plain
kernel /boot/vmlinuz-2.6.18-8.el5 ro root=LABEL=/ elevator=deadline rhgb quiet
```

 

重启服务器后,查看调度方法:

```plain
[root@localhost ~]# cat /sys/block/sda/queue/scheduler
noop anticipatory [deadline] cfq
```

可以看见已经是 deadline 了

 

四) ionice

ionice 可以更改任务的类型和优先级,不过只有 cfq 调度程序可以用 ionice.

有三个例子说明 ionice 的功能:

采用 cfq 的实时调度,优先级为 7

```plain
[root@localhost ~]# ionice -c1 -n7  -ptime dd if=/dev/sda1 f=/tmp/test bs=2M count=300&
```

采用缺省的磁盘 I/O 调度,优先级为 3

```plain
[root@localhost ~]# ionice -c2 -n3  -ptime dd if=/dev/sda1 f=/tmp/test bs=2M count=300&
```

采用空闲的磁盘调度,优先级为 0

```plain
[root@localhost ~]# ionice -c3 -n0  -ptime dd if=/dev/sda1 f=/tmp/test bs=2M count=300&
```

ionice 的三种调度方法,实时调度最高,其次是缺省的 I/O 调度,最后是空闲的磁盘调度.

ionice 的磁盘调度优先级有 8 种,最高是 0,最低是 7.

**注意**:磁盘调度的优先级与进程 nice 的优先级没有关系.

一个是针对进程 I/O 的优先级,一个是针对进程 CPU 的优先级。

## 参考链接
- [IO 调度算法的选择](https://www.cnblogs.com/gomysql/p/3582185.html)