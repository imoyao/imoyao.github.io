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

### 流程简单示例：

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
    usage-count no;
}
common {
    handlers {
    }
    startup {       #启动时候的相关设置
        wfc-timeout 50;
        become-primary-on both;     # 允许双主
    }

    disk {
        on-io-error detach;
        no-disk-flushes ;
        no-disk-barrier;
        c-plan-ahead 0;
        c-fill-target 24M;
        c-min-rate 80M;
        c-max-rate 720M;
    } 
    net {           # 网络配置相关
        protocol C;     # 同步异步控制（见下方介绍）
        after-sb-0pri discard-younger-primary;  #脑裂修复
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
异步：指的是当数据写到磁盘上，并且复制的数据已经被放到我们的tcp缓冲区并等待发送以后，就认为写入完成；
半同步：指的是数据已经写到磁盘上，并且这些数据已经发送到对方内存缓冲区，对方的`tcp`已经收到数据，并宣布写入；
同步：指的是主节点已写入，从节点磁盘也写入；

`DRBD`的复制模型是靠`protocol`关键字来定义的：`protocol A`表示异步；`protocol B`表示半同步；`protocol C`表示同步，默认为`protocol C`。

在同步模式下只有主、从节点上两块磁盘同时损害才会导致数据丢失。在半同步模式下只有主节点宕机，同时从节点异常停电才会导致数据丢失。

注意:
- `DRBD`的主不会监控从的状态所以有可能会造成数据重传

- 如果DRBD状态下关机双控恢复不过来，尝试删除drbd配置信息，然后停掉drbd端ODSP和mysql重启之后即可。

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

```
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

## 其他

### 双控配置互信（假定在控1执行）

```shell
echo y|ssh-keygen -t dsa -f ~/.ssh/id_dsa -N ""
cp ~/.ssh/id_dsa.pub ~/.ssh/authorized_keys
scp -r ~/.ssh controller-2:         #双控对端hostname
```

## 部分参考

- [官方手册](https://docs.linbit.com/docs/users-guide-8.4/)

- [SUSE高可用配置](https://www.suse.com/documentation/sle_ha/book_sleha/data/cha_ha_drbd.html)

- [使用DRBD实现复制存储](http://clusterlabs.org/doc/en-US/Pacemaker/1.1/html/Clusters_from_Scratch/ch07.html)

- [drbd 配置 - Rikewang - 博客园](http://www.cnblogs.com/wxl-dede/p/5114696.html)

- [记一次DRBD Unknown故障处理过程](https://yq.aliyun.com/articles/52043)