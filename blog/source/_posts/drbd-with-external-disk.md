---
title: 关于 DRBD 使用外部元数据
date: 2018-08-28 10:57:00
tags:
- DRBD
- meta-data
- 元数据
- 存储
---
裂脑一旦发生，需要及时排查问题所在，最大限度保护数据完整性。
<!--more-->

## `meta data`存放位置优缺点比较

### internal meta-data

meta-data和数据存放在同一个底层设备之上，它通过在设备末端预留一个区域以存储元数据做到这一点。

- 优点：

一旦meta-data创建之后，就和实际数据绑在了一起，在维护上会更简单方便，不用担心meta-data会因为某些操作而丢失。另外在硬盘损坏丢失数据的同时，meta-data也跟着一起丢失，当更换硬盘之后，只需要执行重建meta-data的命令即可，丢失的数据会很容易的从其他节点同步过来。

- 缺点：

如果底层设备是单一的磁盘，没有做raid，也不是lvm等，那么可能会对写入吞吐量产生负面影响。因为每一次写io都需要更新meta-data里面的信息，那么每次写io都会有两次，而且肯定会有磁头的较大寻道移动，因为meta-data都是记录在设备的最末端的，这样就会造成写io的性能降低。


### external meta data

`meta-data`存放在独立的，与存放数据的设备分开的设备之上。

- 优点：

与internal meta-data的缺点完全相对。对于某些写操作, 使用外部元数据会稍微改进延迟行为。

- 缺点：

由于meta-data存放在与数据设备分开的地方，就意味着如果磁盘故障且仅破坏生产数据 (而不是 DRBD 元数据), 则可以通过手动干预, 以使发起从幸存的节点到后续更换的磁盘上的完整数据同步。也就是管理维护会稍微麻烦一点，很小的一点点。

**注意：** 如果我们希望在已经存在数据的设备上面建立drbd的资源，并且不希望丢失该设备上面的数据，又没办法增大底层设备的容量，而且上层文件系统不支持收缩，我们就只能将meta data创建成external方式。

## 估算元数据大小

你可以使用以下公式计算 DRBD 元数据的精确空间要求:

![精确计算元数据大小](https://docs.linbit.com/ug-src/users-guide-8.4/images/metadata-size-exact.png)

Cs 是存储设备扇区大小。N是对端的数量，一般情况下drbd实现的是双节点，因此N=1，可以不用考虑。

您可以通过发出 blockdev --getsz <device>来检索设备大小。

```shell
[root@Storage ~]# blockdev --getsz /dev/StorPool1/SANLun2
2097152
```

结果中的Ms的大小也是用扇区表示的,要转换为 MB, 请除以 2048。(对于512字节的扇区大小, 这是除 s390 之外的所有 Linux 平台上的默认值)。
```python
In [23]: (math.ceil(2097152/2**18)*8+72)/float(2048)
Out[23]: 0.06640625
```

在实践中, 你可以使用一个合理的好的近似, 下面给出。请注意, 在此公式中, 单位为兆字节(megabytes), 而非扇区:

![预估计算元数据大小](https://docs.linbit.com/ug-src/users-guide-8.4/images/metadata-size-approx.png)

```shell
# 获取块设备大小
[root@Storage ~]# lsblk /dev/StorPool1/SANLun2
NAME              MAJ:MIN RM SIZE RO TYPE MOUNTPOINT
StorPool1-SANLun2 253:3    0   1G  0 lvm  
```
```python
# 预估元数据设备大小
In [30]: 1024/float(32768)+1
Out[30]: 1.03125
```
此处插播一个小的知识点,来源参考[这里](https://blog.csdn.net/starshine/article/details/8226320)（解释）和[这里](http://www.maixj.net/ict/kbkib-mbmib-gbgib-15095)（区别）。

| 名字      |缩写       |次方      |     名字  |缩写      |次方      |
|:--------- |:---------|:---------|:---------|:---------|:---------|
| kilobyte  | KB       | 10^3     | kibibyte |KiB       |2^10      |
| megabyte  | MB       | 10^6     | mebibyte |MiB       |2^20      |
| gigabyte  | GB       | 10^9     | gibibyte |GiB       |2^30      |
| terabyte  | TB       | 10^12    | tebibyte |TiB       |2^40      |
| petabyte  | PB       | 10^15    | pebibyte |PiB       |2^50      |
| exabyte   | EB       | 10^18    | exbibyte |EiB       |2^60      |
| zettabyte | ZB       | 10^21    | zebibyte |ZiB       |2^70      |
| yottabyte | YB       | 10^24    | yobibyte |YiB       |2^80      |

## 重置资源的大小

### 在线增加

需要满足两个条件：

1. 支持设备必须是逻辑卷

2. 当前的资源必须处于`connected`的连接状态。

在两个节点给设备增加大小后，再确认只有一个节点处于`primary`状态。然后输入：

```shell
drbdadm resize <resource>
```

此命令会触发新扇区的同步，完成主节点到备用节点间的同步。

如果你添加的空间是干净没有数据的，你可以使用`--assume-clean`选项：

```shell
drbdadm -- --assume-clean resize <resource>
```
来跳过额外的空间同步。

### 离线增加

（此为高级功能，请自审之后使用。）

1. 资源被配置为external meta data时

当DRBD在处于非活动情况下，在两个节点的支持设备被扩展时，且DRBD资源使用的是external meta data，那么新的大小会自动被识别，不需要管理员干预。DRBD设备将在下次两个节点活动并且成功建立网络连接之后，显示增加后的新容量。

2. 资源被配置为internal meta data时

当DRBD资源被配置为使用 internal meta data时，在新大小变为可用之前, 则必须将此元数据移动到已扩容设备的末尾。为此, 请完成以下步骤:

- down掉DRBD资源:

```shell
drbdadm down <resource>
```
- 在收缩之前将元数据保存在文本文件中

```shell
drbdadm dump-md <resource> > /tmp/metadata
```

**注意：** 以上步骤必须在两个节点上分别运行。不能在一个节点上保存了元数据然后在拷贝到另外一个节点上。否则就无法正常工作。

- 在两个节点上给支持的块设备增加容量

- 分别在两个节点上调整/tmp/metadata 文件中`la-size-sect`的大小信息。注：这里la-size-sect指定的是扇区数量

- 重新初始化元数据区域

```shell
drbdadm create-md <resource>
```

- 分别在两个节点上重新导入修正的元数据

```shell
## 此处使用bash脚本，需要确认可用性
# drbdmeta_cmd=$(drbdadm -d dump-md <resource>)
# ${drbdmeta_cmd/dump-md/restore-md} /tmp/metadata
Valid meta-data in place, overwrite? [need to type 'yes' to confirm]
yes
Successfully restored meta data
```

- 重新启用DRBD资源

```shell
drbdadm up <resource>
```
- 在一个节点上，设置DRBD为primary

```shell
drbdadm primary <resource>
```
至此，已完成DRBD设备大小的扩容。

### 在线缩小容量

注：在线缩小容量，仅支持`external metadata`

在缩小DRBD设备时必须首先缩小DRBD的上层块设备。例如文件系统。由于DRBD无法获知文件系统到底使用了多少空间，所以在缩小文件系统时需要格外小心防止数据丢失！文件系统是否可以被缩小取决于所使用的文件系统。大多数文件系统不支持在线缩减。XFS也不支持在线缩减。

因此，在缩小文件系统后，可以使用以下命令在线缩小DRBD设备容量。

```shell
drbdadm resize --size=<new-size>  <resource>
```

### 离线收缩容量

（此为高级功能，请自审之后使用。）

如果在 DRBD 处于非活动状态时收缩后备块设备, DRBD 将拒绝在下次尝试`attach`期间`attach`到此块设备, 因为它现在太小 (external meta-data), 或者它将无法找到其元数据 (internal meta-data)。要变通解决这些问题, 请使用此过程 (如果不能使用上面的在线收缩):

- 在DRBD还处于配置运行状态时，在一个节点上缩小文件系统

- down掉DRBD资源

```shell
drbdadm down <resource>
```

- 在缩小前保存元数据到一个文件中：
```shell
drbdadm dump-md <resource> > /tmp/metadata
```

**注意：** 以上步骤必须在两个节点上分别运行。不能在一个节点上保存了元数据然后在拷贝到另外一个节点上。否则就无法正常工作。

- 在两个节点上给支持的块设备缩小容量

- 分别在两个节点上调整/tmp/metadata 文件中`la-size-sect`的大小信息。注：这里la-size-sect指定的是扇区数量

- 重新初始化元数据区域

```shell
drbdadm create-md <resource>
```

- 分别在两个节点上重新导入修正的元数据

```shell
## 此处使用bash脚本，需要确认可用性
# drbdmeta_cmd=$(drbdadm -d dump-md <resource>)
# ${drbdmeta_cmd/dump-md/restore-md} /tmp/metadata
Valid meta-data in place, overwrite? [need to type 'yes' to confirm]
yes
Successfully restored meta data
```

- 重新启用DRBD资源

```shell
drbdadm up <resource>
```
## 其他说明

### 查看元数据
```shell
# down 掉drbd
[root@Storage ~]# drbdadm down drbds2
# 查看元数据出错
[root@Storage ~]# drbdadm dump-md drbds2
Found meta data is "unclean", please apply-al first
Command 'drbdmeta 2 v08 /dev/StorPool1/SANLun2 internal dump-md' terminated with exit code 255
# 暂时不明白这句操作的含义，待查
[root@Storage ~]# drbdadm apply-al drbds2
# 查看meata-data
[root@Storage ~]# drbdadm dump-md drbds2
# DRBD meta data dump
# 2018-08-29 01:48:20 +0800 [1535478500]
# Storage> drbdmeta 2 v08 /dev/StorPool1/SANLun2 internal dump-md
#

version "v08";

# md_size_sect 136
# md_offset 1073737728
# al_offset 1073704960
# bm_offset 1073672192

uuid {
    0xDDB03F0DAF07DEDC; 0x0000000000000000; 0xE4689A94FBB0E78B; 0xE4679A94FBB0E78B;
    flags 0x00000000;
}
# al-extents 1237;
la-size-sect 2097016;
bm-byte-per-bit 4096;
device-uuid 0x625F486D2CB120D1;
la-peer-max-bio-size 1048576;
al-stripes 1;
al-stripe-size-4k 8;
# bm-bytes 32768;
bm {
   # at 0kB
    4096 times 0x0000000000000000;
}
# bits-set 0;
```

从此命令中可以获知不同标记代数的uuid值，以及metadata的元数据信息，例如md_size_sect=1951744表示元数据所在分区占用了1951744个扇区。注意，该命令不要在drbd设备已启动的情况下执行。

知道这两个命令可以获取一些信息后，现在我们要做的是计算metadata部分的数据大小。这个大小在"修改drbd设备空间大小"时有用。

首先获取元数据所在分区的扇区数。即上面结果中的"md_size_sect"。不过也可以使用块设备工具blockdev来获取。

## 参考来源
- [16.1. DRBD meta data](https://docs.linbit.com/docs/users-guide-8.4/#s-metadata)
- [原创 | drbd中metadata的理解](https://www.wenzizone.cn/2009/10/29/drbd%E4%B8%ADmetadata%E7%9A%84%E7%90%86%E8%A7%A3%E5%8E%9F%E5%88%9B.html)
- [drbd配置简述](https://blog.csdn.net/yuanhangq220/article/details/46634249)
- [drbd(二)：配置和使用 - 骏马金龙 - 博客园](http://www.cnblogs.com/f-ck-need-u/p/8678883.html)