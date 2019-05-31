---
title: DRBD状态指标记录
date: 2018-08-29 11:26:43
tags:
- DRBD
- Linux
- 高可用
categories:
- 教程记录
---
在管理`DRBD`的时候，需要关注`drbd`相关的各种状态指标，本文主要记录相关的指令及显示含义。
<!--more-->

## `DRBD`状态概览

```shell
drbd-overview
drbd status
cat /proc/drbd      # 9.0废止在drbd9中，更多的是使用drbdadm或drbdsetup来获取节点的状态信息。
```
以上命令略有不同，可自行对照

```shell
[root@Storage drbd]# pwd
/usr/lib/drbd
[root@Storage drbd]# ./drbd status
# 输出示例
drbd driver loaded OK; device status:
version: 8.4.3 (api:1/proto:86-101)
GIT-hash: 89a2942***221f964d3ee515 build by root@third, 2017-07-20 10:58:42
m:res          cs            ro                 ds                 p       mounted       fstype
0:drbd0        Connected     Primary/Secondary  UpToDate/UpToDate  C
1:drbd1^^0     StandAlone    Primary/Unknown    UpToDate/DUnknown  r----s
……
6:drbd6        Connected     Primary/Secondary  UpToDate/UpToDate  C       /xxx  ext4

```
缩写解释

- res：资源名称
- cs：connect state,资源连接状态
- ro：role，表示节点角色信息
第一次启动drbd时，两个drbd节点默认都处于Secondary状态，
Primary/Secondary（代表这个是主节点）
Secondary/Primary（代表这个是副节点）
- ds：disk state,磁盘状态信息
Inconsistent/Inconsisten，即为“不一致/不一致”状态，表示两个节点的磁盘数据处于不一致状态。
UpToDate/Inconsistent（正在同步，数据还没有一致）
UpToDate/UpToDate （同步完成，数据一致）
- C drbd的复制协议，即A、B、C协议。
- r-----是IO标记，反映的是该资源的IO状态信息。共有6种IO状态标记符号。

## 连接状态

节点间通过TCP连接进行通信，在建立连接、断开连接、特殊情况下有很多种连接状态。

DRBD连接建立完成，表示元数据区、数据区等一切都已准备好，可以进行任何数据同步的操作。
```shell
[root@master ~]# drbdadm cstate drbd20
Connected
```

一个资源可能有以下连接状态中的一种

- Unconfigured：设备在等待配置
- **WFConnection**：当前节点正在等待对端节点出现。例如对方节点`drbdadm down`后，本节点将处于本状态。
- **StandAlone**：无连接。出现这种状态可能是因为：未连接过、使用`drbdadm disconnect`断开连接、节点由于身份验证的原因未成功加入drbd集群使得连接被删除、脑裂后断开连接。
- Disconnecting：断开连接的一个临时过渡状态。它很快就会切入下一状态就是`StandAlone`。
- Unconnected：尝试再次发起`TCP`连接时的一个临时连接状态(是连接超时后再次发送连接请求产生的状态)，它的下一个状态可能是`WFConnection`，也可能是`WFReportParams`。
- Timeout：和对端通信超时时的临时状态。下一个状态就是`Unconnection`。
- BrokenPipe：和对端连接丢失时的临时状态。下一个状态是`Unconnection`。
- NetworkFailure：和对端连接丢失时的临时状态。下一个状态是`Unconnection`。(没错，和上面的一样)
- ProtocolError：和对端连接丢失时的临时状态。下一个状态是`Unconnection`。(没错，还是和上面的一样)
- TearDown：对端关闭TCP连接时的临时状态。下一个状态是`Unconnection`。
- **Connected**：DRBD连接已经建立完成，数据镜像已经激活成功。这个状态是`drbd`正常运行时的状态。
- WFReportParams：TCP连接已经建立完成，该节点正在等待对端的第一个数据包。
- StartingSyncS：全盘数据同步中。只有在初始化时才应该全盘同步。下一个状态是：`SyncSource`或`PauseSyncS`。
- StartingSyncT：全盘数据同步中。只有在初始化时才应该全盘同步。下一个状态是：`WFSyncUUID`。
- WFBitMapS：部分数据正在同步。下一个状态是：`SyncSource`或`PauseSyncS`。
- WFBitMapT：部分数据正在同步。下一个状态是：`WFSyncUUID`。
- WFSyncUUID：同步马上就要开始了。下一个状态：`SyncTarget`或`PauseSyncT`。
- **SyncSource**：正在同步，且本节点是数据同步的源端。
- **SyncTartget**：正在同步，且本节点是数据同步的目标端。
- PauseSyncS：本节点是同步的源端节点，但同步过程当前被暂停。出现这种状态的原因可能是当前同步进程依赖于另一个同步进程完成，或者使用`drbdadm pause-sync`手动中断了同步操作。
- PauseSyncT：本节点是同步的目标端，但同步过程当前被暂停。出现这种状态的原因可能是当前同步进程依赖于另一个同步进程完成，或者使用`drbdadm pause-sync`手动中断了同步操作。
- VerifyS：正在进行在线设备验证，且本节点将成为验证的源端。
- VerifyT：正在进行在线设备验证，且本节点将成为验证的目标端。

在drbd9中，`WFConnection`状态改为`connecting`状态。删除了`WFReportParams`状态。添加了以下几个同步相关的状态：

- Off：该卷组还未同步，因为连接未建立。
- **Established**：所有对该卷组的写操作已经在线完成同步。这是`drbd`正常运行时的状态。
- Ahead：数据同步操作被挂起，因为网络套接字中达到了一定的堵塞程度，无法应付更多的负载。该状态需要配置`on-congestion`选项来启用。
- Behind：对端将数据同步操作挂起，因为网络套接字中达到了一定的堵塞程度，无法应付更多的负载。该状态需要在对端节点上配置`on-congestion`选项来启用。

## 角色状态

资源的角色状态既可以从/proc/drbd文件中获取，也可以使用下面的命令来获取。
```shell
[root@drbd1 ~]# drbdadm role data1
Primary/Unknown
```
在角色状态信息中，本地节点总是标记在第一位，远程节点标记在结尾。

可能的节点角色状态有：

- Primary：资源的primary角色，该角色状态下的drbd设备可以进行挂载、读、写等。在没有启用多主复制模型(dual-primary mode)，只能有一个primary节点。
- Secondary：资源的secondary角色。该角色状态下的drbd设备会接收来自primary端的数据更新(除非和对端不是primary)。且该角色的drbd设备不可挂载、不可读、不可写。
- Unknown：资源的角色未知。本地节点的角色状态绝对不可能会是这种状态。只有对端节点断开连接时对端节点才处于Unknown状态。

## 硬盘状态

```shell
[root@master ~]# drbdadm dstate drbd20
UpToDate/UpToDate
```

在磁盘状态信息中，本地节点的磁盘状态总是标记在第一位，远程节点标记在结尾。本地和对等节点的硬盘有可能为下列状态之一：

- Diskless 无盘：本地没有块设备分配给`DRBD`使用，这意味着资源可能从没有和它的底层块设备进行关联绑定(attach)，也可能是手动detach解除了关联，还可能是出现了底层I/O错误时自动分离（detach）。
- Attaching：读取无数据时候的瞬间状态
- Failed：失败，本地块设备报告`I/O`错误的下一个状态，其下一个状态为`Diskless`无盘
- Negotiating：在已经连接的DRBD设置进行`Attach`读取无数据前的瞬间状态
- Inconsistent：数据不一致，在两个节点上（初始的完全同步前）这种状态出现后立即创建一个新的资源。此外，在同步期间（同步目标端）正接收同步数据时，也会进入不一致状态。
- Outdated：数据资源是一致的，但是已经过时。(例如，已经同步后secondary下线了，之后又上线了，在还没开始重新同步的时候就是Outdated状态)
- DUnknown：当对等节点网络连接不可用时出现这种状态
- Consistent：连接断开时的数据处于一致性状态，当连接建立后，将决定数据是`UpToDate`还是`Outdated`状态
- UpToDate：一致的、最新的数据状态，这个状态为正常状态

## IO状态标记

IO状态标记表示的是当前资源的IO操作状态。共有6种状态：

- IO挂起：r或s都可能表示IO挂起，一般是r。r=running，s=suspended。
- 串行重新同步：资源正在等待进行重新同步，但被resync-after选项延迟了同步进度。该状态标记为"a"，通常该状态栏应该处于"-"。
- 对端初始化同步挂起：资源正在等待进行重新同步，但对端节点因为某些原因而IO挂起。该状态标记为"p"，通常该状态栏应该处于"-"。
- 本地初始化同步挂起：资源正在等待进行重新同步，但本节点因为某些原因而IO挂起。该状态标记为"u"，通常该状态栏应该处于"-"。
- 本地IO阻塞：通常该状态栏应该处于"-"。可能有以下几种标记：
    - d：因为DRBD内部原因导致的IO阻塞。
    - b：后端设备正处于IO阻塞。
    - n：网络套接字阻塞。
    - a：网络套接字和后端块设备同时处于阻塞状态。
- Activity Log更新挂起：当al更新被挂起时，处于该状态，标记为"s"，通常该状态栏应该处于"-"。(如果不知道什么是Active Log，请无视本标记)

## 性能指标

习惯上，我们使用`cat /proc/drbd `获取`drbd`状态信息。主要是一些计数器和计量器的值。
```shell
[root@Storage ~]# cat /proc/drbd 
version: 8.4.3 (api:1/proto:86-101)
srcversion: 9D811F04CD6DC2C9A9A608F 

 3: cs:Connected ro:Secondary/Secondary ds:UpToDate/UpToDate C r-----
    ns:0 nr:0 dw:0 dr:0 al:0 bm:0 lo:0 pe:0 ua:0 ap:0 ep:1 wo:f oos:0

301: cs:Connected ro:Secondary/Secondary ds:UpToDate/UpToDate C r-----
    ns:0 nr:0 dw:0 dr:0 al:0 bm:0 lo:0 pe:0 ua:0 ap:0 ep:1 wo:f oos:0
```

drbd84中使用缩写符号来标记性能指标，而drbd9中使用全称来表示。例如drbd84中的ns和drbd9中的send是同一个意思。

- ns/send (network send)：通过网络连接发送给对端的数据量，单位为Kb。
- nr/receive (network receive)：通过网络连接接收到对端发送来的数据量，单位为Kb。
- dw/written (disk write)：该卷(volume)写入本地磁盘的数据量，单位为Kb。
- dr/read (disk read)：该卷(volume)从本地磁盘读取的数据量，单位为Kb。
- al/al-writes (activity log)：元数据区中al更新的次数。
- bm/bm-writes (bit map)：元数据区中bitmap更新的次数。
- lo/lower-pending (local count)：DRBD发起的打开本地IO子系统的请求次数。
- pe/pending (pending)：本地发送给对端但却没有回复的次数。
- ua/unacked (unacknowledged)：接收到对端发送的请求但却没有给予回复的请求数量。
- ap/upper-pending (application pending)：转发给DRBD的IO块的请求，但DRBD还没给予回复的请求数量。
- ep (epochs):epoch对象的数量。通常为1。drbd9中没有该指标。
- wo/write-ordering (write order):当前正在使用的write order方法：b(barrier), f(flush), d(drain)或n(none)。
- oos/out-of-sync (out of sync):当前不同步的数据量，单位为Kb。

上面所有"未给予回复"的指标数量都表示动作还未完成，需要回复后才表示操作完成。这些未回复数值不能太大。

此外，drbd9中添加了以下几个指标：

- resync-suspended：重新同步操作当前是否被挂起。可能的值为no/user/peer/dependency。
- blocked：本地IO的拥挤情况。
    - no：本地IO不拥挤。
    - upper：DRBD层之上的IO被阻塞。例如到文件系统上的IO阻塞。可能有以下几种原因：
        - 管理员使用drbdadm suspend-io命令挂起了I/O操作。
        - 短暂的IO阻塞，例如attach/detach导致的。
        - 删除了缓冲区。
        - bitmap的IO等待。
    - lower：底层设备处于拥挤状态。
    
## 参考链接

- [drbd(三)：drbd的状态说明 - 骏马金龙 - 博客园](http://www.cnblogs.com/f-ck-need-u/p/8684648.html)