---
title: CentOS7环境下配置DRBD
date: 2018-01-11 11:26:43
tags:
- DRBD
- Linux
- CentOS
categories:
- 工作日常
---
本文主要记录`DRBD`的配置过程和功能验证。
<!--more-->

本文使用`64`位`CentOS`，基本环境：

```shell
+-----------------------+              |               +----------------------+
| [ DRBD_A (Server#1) ] | 10.10.17.18  |  10.10.17.19  | [DRBD_B (Server#2) ] |
|       node01          +--------------+---------------+         node02       |
|                       |                              |                      |
+-----------------------+                              +----------------------+

DRBD 服务器A ：ip:10.10.17.18，hostname：DRBD_A
DRBD 服务器B ：ip:10.10.17.19，hostname：DRBD_B
```
## 建立磁盘分区

- 分区之前

```shell
[root@DRBD_A ~]# lsblk      # 查询块设备信息
NAME                  MAJ:MIN RM  SIZE RO TYPE MOUNTPOINT
fd0                     2:0    1    4K  0 disk
sda                     8:0    0   16G  0 disk
├─sda1                  8:1    0  500M  0 part /boot
└─sda2                  8:2    0 15.5G  0 part
  ├─centos_bogon-root 253:0    0 13.9G  0 lvm  /
  └─centos_bogon-swap 253:1    0  1.6G  0 lvm  [SWAP]
sdb                     8:16   0    5G  0 disk
└─StorPool-SANLun10   253:2    0    2G  0 lvm
sr0                    11:0    1 1024M  0 rom
drbd0                 147:0    0    2G  1 disk
```
- 进行分区

```shell
[root@DRBD_A ~]# fdisk /dev/sdb     # 在sdb上新建分区
Welcome to fdisk (util-linux 2.23.2).

Changes will remain in memory only, until you decide to write them.
Be careful before using the write command.

Device does not contain a recognized partition table
Building a new DOS disklabel with disk identifier 0xb25d5d26.

Command (m for help): n         #  新建
Partition type:
   p   primary (0 primary, 0 extended, 4 free)
   e   extended
Select (default p):
Using default response p
Partition number (1-4, default 1):
First sector (2048-10485759, default 2048):
Using default value 2048
Last sector, +sectors or +size{K,M,G} (2048-10485759, default 10485759): +1G
Partition 1 of type Linux and of size 1 GiB is set

Command (m for help): w         #  写入
The partition table has been altered!

Calling ioctl() to re-read partition table.
Syncing disks.
```
- 分区之后

```shell
[root@DRBD_A ~]# lsblk
NAME                  MAJ:MIN RM  SIZE RO TYPE MOUNTPOINT
fd0                     2:0    1    4K  0 disk
sda                     8:0    0   16G  0 disk
├─sda1                  8:1    0  500M  0 part /boot
└─sda2                  8:2    0 15.5G  0 part
  ├─centos_bogon-root 253:0    0 13.9G  0 lvm  /
  └─centos_bogon-swap 253:1    0  1.6G  0 lvm  [SWAP]
sdb                     8:16   0    5G  0 disk
├─sdb1                  8:17   0    1G  0 part      # 新分区
└─StorPool-SANLun10   253:2    0    2G  0 lvm
sr0                    11:0    1 1024M  0 rom
drbd0                 147:0    0    2G  0 disk /media
```

## 修改配置文件

### 更改DRBD全局配置

首先根据需求更改`DRBD`全局配置`/etc/drbd.d/global_common.conf`:

此处可参阅另一篇文章：[DRBD全局配置](https://imoyao.github.io/blog/2017-09-11/Record_of_drbd/#global-common-conf配置（示例）)

### 创建`DRBD`配置文件

由于`DRBD`是基于块设备的存储复制解决方案，所以此处使用`Lun`作为演示。

```shell
vi r0.res
resource r0 {
    # DRBD device
    device /dev/drbd0;
    # block device
    disk /dev/StorPool/SANLun10;    # 磁盘路径，若为disk则修改为/dev/sdb1
    meta-disk internal;
    on DRBD_A {
        # IP address:port
        address 10.10.17.18:7788;
    }
    on DRBD_B {
        address 10.10.17.19:7788;
    }
}
```
`注意：`本机主机名(`hostname`)和地址(`ip`)必须严格按照真实情况配置，两边`.res`文件内容尽量保持一致。

配置文件创建完成之后，在两个服务器上分别执行如下命令，创建`DRBD`资源，当然你也可以通过`scp`把配置文件拷过去，然后执行相关命令。

其中上述配置文件的meta-disk有三种记录方式：internal/device/device[index_num]。其中不管是哪种方式，metadata存放的分区不能格式化，哪怕使用internal时metadata和一般data在同一个分区也不能格式化该分区。

internal是将元数据也写入到数据分区的尾部，即数据和元数据同分区。如果指定的device没有给定index时，则表示元数据存储到该设备中。如果某节点指定device[index_num]，那么指定几次元数据分区索引就必须大于128M的几倍，例如上述文件中drbd1.longshuai.com节点指定了/dev/sdb1[0]，那么sdb1就必须大于128M，如果此时其他资源的节点也指定了同一台服务器的/dev/sdb1[1]，则指定了两次就必须大于256M。指定为internal和device时，元数据区的大小是drbd自行计算的。
上面index的说法来自[这里](http://www.cnblogs.com/f-ck-need-u/p/8678883.html#1-drbd-)，具体没有实际验证。

```shell
drbdadm create-md r0
```
然后启动DRBD：

```shell
drbdadm up r0
```
我在测试时没有操作下一步操作，但是数据也可以完成同步。查询了一下，网上说`drbdadm up`这个命令相当于`attach`、`syncer`、`connect`的总集合。但是后台使用`systemctl status drbd `获取到的状态还是`inactive (dead)`，欢迎大家提出自己的看法。

------
在两个服务器上分别启动`DRBD`服务：

```shell
/etc/init.d/drbd start
```
------

把`DRBD_A`做为主服务器：

```shell
# 无数据时
drbdadm primary r0
# 有数据时，把本端作为primary端，本地数据分发到其他节点。
drbdadm -- --overwrite-data-of-peer primary r0
```
使用如下命令查看`DRBD`服务的状态信息：

```shell
/etc/init.d/drbd status
#或者
drbd-overview
```

此时，写入`DRBD_A`端(`/dev/drbd1`)的数据都会同步到`DRBD_B`端。

## 测试数据同步

### `Primary`端

- 格式化`drbd`

```shell
mkfs.xfs /dev/drbd0
```
- 挂载设备

```shell
mount /dev/drbd0 /media
```
- 写入数据

```shell
cd /media/
mkdir drbd_test
cd drbd_test/
echo "hello World" > hello.txt
```
- 卸载设备

```shell
cd ~
umount /media
```
- 本端降级

```shell
drbdadm secondary r0
```

### `Secondary`端

- 从端升主

```shell
drbdadm primary r0
```
- 挂载设备

```shell
mount /dev/drbd0 /media
```
**注意：** 此时从端不需要再次格式化，否则数据丢失。

- 验证数据

```shell
cd /media
ls
cat ./drbd_test/hello.txt
# 返回
hello World
```

参考来源

- [CentOS 7 : DRBD : Configure : Server World](https://www.server-world.info/en/note?os=CentOS_7&p=drbd&f=2)



