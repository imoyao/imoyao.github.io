---
title: DRBD备忘记录
date: 2017-9-11 17:56:38
tags:
- 存储
- 集群
- DRBD
categories:
- 教程记录
---

在双控集群项目中用到了`DRBD`技术实现镜像，此处做一个简单的记录。

<!--more-->

![DRBD在Linux内核I/O栈的位置](https://docs.linbit.com/ug-src/users-guide-8.4/images/drbd-in-kernel.png)

开始阅读之前，请先注意示例中使用的DRBD版本

```shell
drbdadm -V
# DRBDADM_VERSION=8.4.3
```

注意：安装的kernel-devel的内核源码（内核源码路径/usr/src/kernel/）和当前系统的kernel版本(uname -r)不一致的话需要把当前内核更新一下。
在`2.6.33`及以上版本的内核默认中有`DRBD`,之前在用的`DRBD`主要`8.0`、`8.2`、`8.3` 三个版本,对应的`rpm`包是`drbd`,`drbd82`和`drbd83`，因此需要安装对应的内核模块，对应的名字为`kmod-drbd`,`kmod-drbd82`,`kmod-drbd83`。
由于`drbd`是作为内核模块进行工作的，故建议使用与内核对应的版本，对应关系如下表。

|Linux releases|DRBD releases|
|:---------|:---------|
| 2.6.33 | 8.3.7 |
| 2.6.34 | 8.3.7 |
| 2.6.35 | 8.3.8 |
| 2.6.36 | 8.3.8.1 |
| 2.6.37 | 8.3.9 |
| 2.6.38 | 8.3.9 |
| 2.6.39 | 8.3.10 |
| 3.0 - 3.4 | 8.3.11 |
| 3.5 - 3.7 | 8.3.13 |

**注意:**目前官网上面8.0 – 8.3.x已标注为`Deprecated`即不建议使用状态。

## 查看`DRBD`状态

```shell
drbd-overview

/etc/init.d/drbd status

cat /proc/drbd
以上命令略有不同，可自行对照
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
解释如下

res：资源名称

cs：资源连接状态

ro字段表示角色信息
第一次启动drbd时，两个drbd节点默认都处于Secondary状态，
Primary/Secondary（代表这个是主节点）
Secondary/Primary（代表这个是副节点）

ds 是磁盘状态信息，
Inconsistent/Inconsisten，即为“不一致/不一致”状态，表示两个节点的磁盘数据处于不一致状态。
UpToDate/Inconsistent（正在同步，数据还没有一致）
UpToDate/UpToDate （同步完成，数据一致）

```shell
20: cs:Connected ro:Primary/Secondary ds:UpToDate/UpToDate C r-----
    ns:80 nr:0 dw:96 dr:485764 al:1 bm:0 lo:0 pe:0 ua:0 ap:0 ep:1 wo:f oos:0
```

Ns表示网络发送的数据包信息，以K为字节

Dw是磁盘写信息

Dr是磁盘读信息

① `DRBD`资源的连接状态

```shell
[root@master ~]# drbdadm cstate drbd20
Connected
```

一个资源可能有以下连接状态中的一种

StandAlone： 独立，网络配置不可用；资源还没有被连接或是被管理断开（使用 `drbdadm disconnect` 命令），或是由于出现认证失败或是脑裂的情况
Disconnecting： 断开，断开只是临时状态，下一个状态是StandAlone独立的
Unconnected： 悬空，是尝试连接前的临时状态，可能下一个状态为WFconnection和WFReportParams
Timeout： 超时，与对等节点连接超时，也是临时状态，下一个状态为Unconected悬空
BrokerPipe：与对等节点连接丢失，也是临时状态，下一个状态为Unconected悬空
NetworkFailure：与对等节点推动连接后的临时状态，下一个状态为Unconected悬空
ProtocolError：与对等节点推动连接后的临时状态，下一个状态为Unconected悬空
TearDown 拆解：临时状态，对等节点关闭，下一个状态为Unconected悬空
WFConnection：等待和对等节点建立网络连接
WFReportParams：已经建立TCP连接，本节点等待从对等节点传来的第一个网络包
Connected 连接：DRBD已经建立连接，数据镜像现在可用，节点处于正常状态
StartingSyncS：完全同步，有管理员发起的刚刚开始同步，未来可能的状态为SyncSource或PausedSyncS
StartingSyncT：完全同步，有管理员发起的刚刚开始同步，下一状态为WFSyncUUID
WFBitMapS：部分同步刚刚开始，下一步可能的状态为SyncSource或PausedSyncS
WFBitMapT：部分同步刚刚开始，下一步可能的状态为WFSyncUUID
WFSyncUUID：同步即将开始，下一步可能的状态为SyncTarget或PausedSyncT
SyncSource：以本节点为同步源的同步正在进行
SyncTarget：以本节点为同步目标的同步正在进行
PausedSyncS：以本地节点是一个持续同步的源，但是目前同步已经暂停，可能是因为另外一个同步正在进行或是使用命令(`drbdadm pause-sync`)暂停了同步
PausedSyncT：以本地节点为持续同步的目标，但是目前同步已经暂停，这可以是因为另外一个同步正在进行或是使用命令(`drbdadm pause-sync`)暂停了同步
VerifyS：以本地节点为验证源的线上设备验证正在执行
VerifyT：以本地节点为验证目标的线上设备验证正在执行

② 查看硬盘状态

```shell
[root@master ~]# drbdadm dstate drbd20
UpToDate/UpToDate
```

本地和对等节点的硬盘有可能为下列状态之一：
Diskless 无盘：本地没有块设备分配给`DRBD`使用，这表示没有可用的设备，或者使用`drbdadm`命令手工分离或是底层的I/O错误导致自动分离
Attaching：读取无数据时候的瞬间状态
Failed 失败：本地块设备报告`I/O`错误的下一个状态，其下一个状态为`Diskless`无盘
Negotiating：在已经连接的DRBD设置进行`Attach`读取无数据前的瞬间状态
Inconsistent：数据是不一致的，在两个节点上（初始的完全同步前）这种状态出现后立即创建一个新的资源。此外，在同步期间（同步目标）在一个节点上出现这种状态
Outdated：数据资源是一致的，但是已经过时
DUnknown：当对等节点网络连接不可用时出现这种状态
Consistent：一个没有连接的节点数据一致，当建立连接时，它决定数据是`UpToDate`或是`Outdated`
UpToDate：一致的最新的数据状态，这个状态为正常状态

## 清除单个 `DRBD` 资源配置：(以drbd10为例)

```shell
drbd-overview       # drbd概览
drbdadm down drbd10         #down drbd
echo yes|drbdadm wipe-md drbd10     #清除metadata
cd /etc/drbd.d/         # 注意，此处根据drbd版本不同也可能在/usr/local/etc/drbd.d/
rm drbd10.res           #删除resource文件
```

## 重启 `DRBD` 服务

```shell
service drbd stop 
service drbd start 
```

## `DRBD`扩容

当遇到我们的`drbd resource`设备容量不够的时候，而且我们的底层设备支持在线增大容量的时候（比如lvm），我们可以先增大底层设备的大小，然后再通过`drbdadm resize resource_name`来实现对`resource`的扩容。
这里有需要注意的是：
只有在单主模式下可以这样做，而且需要先在两节点上都增大底层设备的容量，然后仅在主节点上执行`resize`命令。

在执行了`resize`命令后，将自动触发一次当前主节点到其他所有从节点的re-synchronization；

如果我们在`drbd`非工作状态下对底层设备进行了扩容，然后再启动`drbd`，将不需要执行`resize`命令（当然前提是在配置文件中没有对disk参数项指定大小），`drbd`自己会知道已经增大了容量；

在进行底层设备的增容操作的时候千万不要修改到原设备上面的数据，尤其是`drbd`的`meta`信息，否则有可能毁掉所有数据。

### 流程简单示例

```shell
# 先在两端扩展Lun（需要相同大小）     
lvextend -Ll(50G) lvpath

# drbd从端：（双主模式切换为主从模式）
drbdadm secondary drbd[Num]     

# drbd主端：
drbdadm resize drbd[Num]
```

## global_common.conf配置（示例）

```shell
global {
    usage-count no;     # 是否向官方发送统计报告（影响性能）
}
common {            # 定义drbd设备共享的属性信息
    handlers {
    }
    startup {       # 启动时候的相关设置
        wfc-timeout 50;
        become-primary-on both;     # 允许双主
    }

    disk {
        on-io-error detach;     # 配置I/O错误处理策略为分离
        no-disk-flushes ;
        no-disk-barrier;
        c-plan-ahead 0;
        c-fill-target 24M;
        c-min-rate 80M;
        c-max-rate 720M;
    } 
    net {               # 网络配置相关
        protocol C;     # 同步异步控制（见下方介绍）
        after-sb-0pri discard-younger-primary;  # 脑裂修复
        after-sb-1pri discard-secondary;
        after-sb-2pri call-pri-lost-after-sb;
        allow-two-primaries yes;        # 允许双主
        max-buffers        36k;
        sndbuf-size         1024k ;
        rcvbuf-size      2048k;
    }
    syncer {    # 同步相关的设置
            rate                   4194304k;    # bytes/second
            al-extents              6433;
    }
}
# Read_More:http://tech.sina.com.cn/smb/2008-12-22/1050926302.shtml

```

### 数据同步协议

`DRBD`有三种数据同步模式:同步，异步，半同步

1. 异步：指的是当数据写到磁盘上，并且复制的数据已经被放到我们的`tcp`缓冲区并等待发送以后，就认为写入完成；
2. 半同步：指的是数据已经写到磁盘上，并且这些数据已经发送到对方内存缓冲区，对方的`tcp`已经收到数据，并宣布写入；
3. 同步：指的是主节点已写入，从节点磁盘也写入；

`DRBD`的复制模型是靠`protocol`关键字来定义的：`protocol A`表示异步；`protocol B`表示半同步；`protocol C`表示同步，默认为`protocol C`。

在同步模式下只有主、从节点上两块磁盘同时损害才会导致数据丢失。在半同步模式下只有主节点宕机，同时从节点异常停电才会导致数据丢失。

**注意:**

1. 主从所在的磁盘分区最好大小相等,`DRBD`磁盘镜像相当于网络`RAID1`；（本人使用时强制相等，但网上没有关于分区大小是否一定要相同的确切说法）
2. 网络同步时需要一定的时间，在同步完成之前最好不要重启，否则会重新同步；
3. `DRBD`的主节点不会监控从节点的状态，所以有可能会造成数据重传；
4. 格式化只需要在`primary`节点上进行,且只能在主节点上挂载；若主节点下线,从节点上线,则从节点可以直接挂载,不需要再次格式化。集群中只有primary服务器可以挂载设备，secondary挂载会报错。只有在进行故障迁移升级为主时才需要挂载。
5. 如果`DRBD`状态下关机双控恢复不过来，尝试删除`DRBD`配置信息，然后停掉`DRBD`端ODSP和`mysql`重启之后即可；(此条仅针对公司项目)


## 单个`drbd`配置文件（以drbd10.res 为例）

### 项目中的配置方案

```shell
resource drbd11 {
    on controller-1 {
        device /dev/drbd11;
        disk /dev/StorPool11/SANLun11;
        address 192.168.2.10:57811;
        meta-disk internal;
    }
    on controller-2 {
        device /dev/drbd11;
        disk /dev/StorPool11/SANLun11;
        address 192.168.2.18:57811;
        meta-disk internal;
    }
}
```

### 另外一种配置方案

来自[这里](https://www.suse.com/documentation/sle_ha/book_sleha/data/sec_ha_drbd_configure.html)

```shell
resource r0 {   # ①
  device /dev/drbd0; # ②
  disk /dev/sda1;   # ③
  meta-disk internal;   # ④
  on alice {    # ⑤
    address  192.168.1.10:7788;     # ⑥
  }
  on bob { 
    address 192.168.1.11:7788; 
  }
  syncer {
    rate  7M;   # ⑦
  }
}
```
翻译以看懂为目的：

1.允许某些系统服务项关联的名称，如：nfs, http, mysql_0, postgres_wal等；
Name that allows some association to the service that needs them. For example, nfs, http, mysql_0, postgres_wal, etc.

2.`DRBD`设备名称及编号；
The device name for DRBD and its minor number.

在上面的例子中，`drbd`的编号是`0`。udev集成脚本提供符号链接`/dev/drbd/by-res/nfs/0`。或者，也可以省略配置中的设备节点名称，然后使用下面这种形式代替：
`drbd0 minor 0`（/dev/可选）或`/dev/drbd0`；

In the example above, the minor number 0 is used for DRBD. The udev integration scripts will give you a symbolic link /dev/drbd/by-res/nfs/0. Alternatively, omit the device node name in the configuration and use the following line instead:
drbd0 minor 0 (/dev/ is optional) or /dev/drbd0

3.节点之间进行复制的原始设备。注意：在本例中，两个节点上面的设备是相同的。若使用不同设备，请将磁盘参数移动到主机上。（？）

The raw device that is replicated between nodes. Note, in this example the devices are the same on both nodes. If you need different devices, move the disk parameter into the on host.

4.`meta-disk`参数通常包含隐式值，但是你也可以指定一个显式设备保存元数据。详情参见：

The meta-disk parameter usually contains the value internal, but it is possible to specify an explicit device to hold the meta data. See http://www.drbd.org/users-guide-emb/ch-internals.html#s-metadata for more information.

5.`on`节配置指明改配置应用于具体哪个`host`。

The on section states which host this configuration statement applies to.

6.各节点的`IP`地址和端口号。每个资源需要一个单独的端口，通常以`7788`开始。

The IP address and port number of the respective node. Each resource needs an individual port, usually starting with 7788.

7.同步率。将其设置为磁盘读写和网络带宽的三分之一。仅限制重新同步，而不是复制。

The synchronization rate. Set it to one third of the lower of the disk- and network bandwidth. It only limits the resynchronization, not the replication.

## 主从切换

主备节点切换有两种方式，分别是停止`DRBD`服务切换和正常切换。

### 正常切换

主切换成从，需要先卸载文件系统，再执行降级为从的命令

#### 主端
```shell
umount /data/
drbdadm secondary all
```
#### 从端

从切换成主，要先执行升主的命令，然后挂载文件系统

```shell
drbdadm  primary all
mount /dev/drbd0 /data/
```

### 停止drbd服务切换

基本思路：关闭主节点服务，此时挂载的`DRBD`分区就自动在主节点卸载了，然后在备用节点执行切换命令

```shell
[root@drbd2 ~]#drbdadm primary all
# 此时报错：
2: State change failed: (-7) Refusing to be Primary while peer is not outdated
Command 'drbdsetup 2 primary' terminated with exit code 11
# 因此，必须在备用节点执行如下命令：
[root@drbd2 ~]#drbdsetup /dev/drbd0 primary –o
# 或者
[root@drbd2~]#drbdadm -- --overwrite-data-of-peer primary all
```
当在备用节点执行切换到主节点命令后，原来的主用节点自动变为备用节点。无需在主用节点再次执行切换到备用节点的命令。

## 脑裂修复

当`DRBD`出现脑裂后，会导致`DRBD`两边的磁盘数据不一致，在确定要作为从的节点上切换成`secondary`，并放弃该资源的数据:

```shell
drbdadm secondary r0
drbdadm -- --discard-my-data connect r0
```
然后作为`primary`的节点重新连接`secondary`（如果这个节点当前的连接状态为`WFConnection`的话，可以省略），使用如下命令连接：

```shell
drbdadm connect r0
```

## 其他

### 双控配置互信（假定在控1执行）

```shell
echo y|ssh-keygen -t dsa -f ~/.ssh/id_dsa -N ""
cp ~/.ssh/id_dsa.pub ~/.ssh/authorized_keys
scp -r ~/.ssh controller-2:         #双控对端hostname
```

## 参考及阅读

- [官方手册](https://docs.linbit.com/docs/users-guide-8.4/)

- [SUSE高可用配置](https://www.suse.com/documentation/sle_ha/book_sleha/data/cha_ha_drbd.html)

- [使用DRBD实现复制存储](http://clusterlabs.org/doc/en-US/Pacemaker/1.1/html/Clusters_from_Scratch/ch07.html)

- [drbd 配置 - Rikewang - 博客园](http://www.cnblogs.com/wxl-dede/p/5114696.html)

- [CentOS下实现Heartbeat+DRBD+MySQL双机热备硬件故障自动切换高可用(HA)方案 | 三木的人生——3mu.me](
http://www.3mu.me/centos%E4%B8%8B%E5%AE%9E%E7%8E%B0heartbeatdrbdmysql%E5%8F%8C%E6%9C%BA%E7%83%AD%E5%A4%87%E7%A1%AC%E4%BB%B6%E6%95%85%E9%9A%9C%E8%87%AA%E5%8A%A8%E5%88%87%E6%8D%A2%E9%AB%98%E5%8F%AF%E7%94%A8ha/#respond)

- [High availability with the Distributed Replicated Block Device](https://www.ibm.com/developerworks/library/l-drbd/index.html)

- [记一次DRBD Unknown故障处理过程](https://yq.aliyun.com/articles/52043)

