---
title: ceph-RBD那点事儿
toc: true
date: 2020-05-23 11:02:28
tags:
- ceph
categories: CEPH
---

## 引言

这篇文章主要介绍了 RBD 在 Ceph 底层的存储方式，解释了 RBD 的实际占用容量和 RBD 大小的关系，用几个文件的例子演示了文件在 RBD (更恰当的是 xfs)中的存储位置，最后组装了一个 RBD ，给出了一些 FAQ。

## RBD是什么

RBD : Ceph’s RADOS Block Devices , Ceph block devices are thin-provisioned, resizable and store data striped over multiple OSDs in a Ceph cluster.

上面是官方的阐述，简单的说就是：

- RBD 就是 Ceph 里的块设备，一个 4T 的块设备的功能和一个 4T 的 SATA 类似，挂载的 RBD 就可以当磁盘用。
- `resizable`:这个块可大可小。
- `data striped`:这个块在 Ceph里面是被切割成若干小块来保存，不然 1PB 的块怎么存的下。
- `thin-provisioned`:精简置备，我认为的很容易被人误解的 RBD 的一个属性，1TB 的集群是能创建无数 1PB 的块的。说白了就是，块的大小和在 Ceph 中实际占用的大小是没有关系的，甚至，刚创建出来的块是不占空间的，今后用多大空间，才会在 Ceph 中占用多大空间。打个比方就是，你有一个 32G 的 U盘，存了一个2G的电影，那么 RBD 大小就类似于 32G，而 2G 就相当于在 Ceph 中占用的空间。

RBD，和下面说的`块`，是一回事。

实验环境很简单，可以参考[一分钟部署单节点Ceph](http://xuxiaopang.com/2016/10/11/ceph-single-node-installation-el7-hammer/)这篇文章，因为本文主要介绍RBD，对 Ceph 环境不讲究，一个单 OSD 的集群即可。

创建一个1G的块 `foo`，因为是`Hammer`默认是`format 1`的块，具体和`format 2`的区别会在下文讲到：

```javascript
[root@ceph cluster]# ceph -s
    cluster fc44cf62-53e3-4982-9b87-9d3b27119508
     health HEALTH_OK
     monmap e1: 1 mons at {ceph=233.233.233.233:6789/0}
            election epoch 2, quorum 0 ceph
     osdmap e5: 1 osds: 1 up, 1 in
      pgmap v7: 64 pgs, 1 pools, 0 bytes data, 0 objects
            7135 MB used, 30988 MB / 40188 MB avail
                  64 active+clean
[root@ceph cluster]# rbd create foo --size 1024
[root@ceph cluster]# rbd info foo
rbd image 'foo':
    size 1024 MB in 256 objects
    order 22 (4096 KB objects)
    block_name_prefix: rb.0.1014.74b0dc51
    format: 1
[root@ceph cluster]# ceph -s
...
    pgmap v10: 64 pgs, 1 pools, 131 bytes data, 2 objects
            7136 MB used, 30988 MB / 40188 MB avail
                  64 active+clean
```

> Tips : `rbd` 的指令如果省略 `-p / --pool`参数，则会默认`-p rbd`，而这个**rbd pool**是默认生成的。

对刚刚的`rbd info`的几行输出简单介绍下：

```javascript
    size 1024 MB in 256 objects
    order 22 (4096 KB objects)
    block_name_prefix: rb.0.1014.74b0dc51
    format: 1
```

- `size`: 就是这个块的大小，即1024MB=1G，`1024MB/256 = 4M`,共分成了256个对象(object)，每个对象4M，这个会在下面详细介绍。
- `order 22`, 22是个编号，4M是22， 8M是23，也就是2^22 bytes = 4MB, 2^23 bytes = 8MB。
- `block_name_prefix`: 这个是块的最重要的属性了，这是每个块在ceph中的唯一前缀编号，有了这个前缀，把服务器上的OSD都拔下来带回家，就能复活所有的VM了。
- `format` : 格式有两种，1和2，下文会讲。

观察建`foo`前后的`ceph -s`输出，会发现多了两个文件，查看下：

```javascript
    pgmap v10: 64 pgs, 1 pools, 131 bytes data, 2 objects

[root@ceph cluster]# rados -p rbd ls
foo.rbd
rbd_directory
```

再查看这两个文件里面的内容：

```javascript
[root@ceph ~]# rados -p rbd get foo.rbd foo.rbd
[root@ceph ~]# rados -p rbd get rbd_directory rbd_directory
[root@ceph ~]# hexdump  -vC foo.rbd 
00000000  3c 3c 3c 20 52 61 64 6f  73 20 42 6c 6f 63 6b 20  |<<< Rados Block |
00000010  44 65 76 69 63 65 20 49  6d 61 67 65 20 3e 3e 3e  |Device Image >>>|
00000020  0a 00 00 00 00 00 00 00  72 62 2e 30 2e 31 30 31  |........rb.0.101|
00000030  34 2e 37 34 62 30 64 63  35 31 00 00 00 00 00 00  |4.74b0dc51......|
00000040  52 42 44 00 30 30 31 2e  30 30 35 00 16 00 00 00  |RBD.001.005.....|
root@ceph ~]# hexdump  -vC rbd_directory 
00000000  00 00 00 00 01 00 00 00  03 00 00 00 66 6f 6f 00  |............foo.|
```

这时候我们再创建一个 RBD 叫`bar`，再次对比查看:

```javascript
[root@ceph ~]# rbd create bar --size 1024
[root@ceph ~]# rados -p rbd ls
bar.rbd
foo.rbd
rbd_directory
[root@ceph ~]# rados -p rbd get rbd_directory rbd_directory
[root@ceph ~]# hexdump  -vC rbd_directory 
00000000  00 00 00 00 02 00 00 00  03 00 00 00 62 61 72 00  |............bar.|
00000010  00 00 00 03 00 00 00 66  6f 6f 00 00 00 00        |.......foo....|
```

多出了个`bar.rbd`文件，很容易联想到这个文件的内容是和`foo.rbd`内容类似的，唯一不同的是保存了各自的`block_name_prefix`。然后，`rbd_directory`里面多出了`bar`这个块名字。可以得出以下的推论：

每个块(RBD)刚创建(format 1)时都会生成一个`rbdName.rbd`这样的文件(ceph里的对象)，里面保存了这个块的`prefix`。 同时，`rbd_directory`会增加刚刚的创建的`rbdName`，顾名思义这个文件就是这个pool里面的所有RBD的索引。

为了简单试验，删掉刚刚的`bar`只留下`foo`:

```javascript
[root@ceph ~]# rbd rm bar
Removing image: 100% complete...done.
```

RBD 使用

建好了块，我们就开始使用这个块了：

```javascript
[root@ceph ~]# rbd map foo
/dev/rbd0
[root@ceph ~]# mkfs.xfs /dev/rbd0 
meta-data=/dev/rbd0              isize=256    agcount=9, agsize=31744 blks
         =                       sectsz=512   attr=2, projid32bit=1
         =                       crc=0        finobt=0
data     =                       bsize=4096   blocks=262144, imaxpct=25
         =                       sunit=1024   swidth=1024 blks
naming   =version 2              bsize=4096   ascii-ci=0 ftype=0
log      =internal log           bsize=4096   blocks=2560, version=2
         =                       sectsz=512   sunit=8 blks, lazy-count=1
realtime =none                   extsz=4096   blocks=0, rtextents=0
[root@ceph ~]# mkdir  /foo
[root@ceph ~]# mount /dev/rbd0 /foo/
[root@ceph ~]# df -h
文件系统        容量  已用  可用 已用% 挂载点
/dev/vda1        40G  7.0G   31G   19% /
...
/dev/rbd0      1014M   33M  982M    4% /foo
```

我喜欢记点东西，比如上面的`33M`就是刚格式化完的`xfs`系统的大小，算是一个特点吧。 先别急着用，集群发生了点变化，观察下：

```javascript
[root@ceph ~]# ceph -s
      pgmap v44: 64 pgs, 1 pools, 14624 KB data, 15 objects

[root@ceph ~]# rados -p rbd ls |sort 
foo.rbd
rb.0.1014.74b0dc51.000000000000
rb.0.1014.74b0dc51.000000000001
rb.0.1014.74b0dc51.00000000001f
rb.0.1014.74b0dc51.00000000003e
rb.0.1014.74b0dc51.00000000005d
rb.0.1014.74b0dc51.00000000007c
rb.0.1014.74b0dc51.00000000007d
rb.0.1014.74b0dc51.00000000007e
rb.0.1014.74b0dc51.00000000009b
rb.0.1014.74b0dc51.0000000000ba
rb.0.1014.74b0dc51.0000000000d9
rb.0.1014.74b0dc51.0000000000f8
rb.0.1014.74b0dc51.0000000000ff
rbd_directory
```

比刚刚多了13个文件，而且特别整齐还！观察这些文件的后缀，可以发现，后缀是以16进制进行编码的，那么从`0x00 -> 0xff`是多大呢，就是十进制的`256`，这个数字是不是很眼熟：

```javascript
    size 1024 MB in 256 objects
```

可是这里只有13个文件，并没有256个啊，这就是RBD的`精简置备`的一个验证，刚刚创建`foo`的时候，一个都没有呢，而这里多出的13个，是因为刚刚格式化成`xfs`时生成的。我们着重关注索引值为`0x00 & 0x01`这两个碎片文件(Ceph Object):

```javascript
[root@ceph ~]# rados -p rbd get rb.0.1014.74b0dc51.000000000000 rb.0.1014.74b0dc51.000000000000
[root@ceph ~]# rados -p rbd get rb.0.1014.74b0dc51.000000000001 rb.0.1014.74b0dc51.000000000001
[root@ceph ~]# hexdump -vC rb.0.1014.74b0dc51.000000000000|more
00000000  58 46 53 42 00 00 10 00  00 00 00 00 00 04 00 00  |XFSB............|
00000010  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  |................|
00000020  c5 79 ca f7 fc 5d 48 2d  81 5e 4c 75 29 3c 90 d3  |.y...]H-.^Lu)<..|
...

[root@ceph ~]# ll rb.* -h
-rw-r--r-- 1 root root 128K 10月 12 19:10 rb.0.1014.74b0dc51.000000000000
-rw-r--r-- 1 root root  16K 10月 12 19:10 rb.0.1014.74b0dc51.000000000001
[root@ceph ~]# file rb.0.1014.74b0dc51.000000000000
rb.0.1014.74b0dc51.000000000000: SGI XFS filesystem data (blksz 4096, inosz 256, v2 dirs)
[root@ceph ~]# rbd export foo hahahaha
Exporting image: 100% complete...done.
[root@ceph ~]# file hahahaha 
hahahaha: SGI XFS filesystem data (blksz 4096, inosz 256, v2 dirs)

[root@ceph ~]# hexdump -vC rb.0.1014.74b0dc51.000000000001
00000000  49 4e 41 ed 02 01 00 00  00 00 00 00 00 00 00 00  |INA.............|
00000010  00 00 00 02 00 00 00 00  00 00 00 00 00 00 00 00  |................|
00000020  00 00 00 00 00 00 00 00  57 fe 15 be 0b cb a3 58  |........W......X|
00000030  57 fe 15 be 0b cb a3 58  00 00 00 00 00 00 00 06  |W......X........|
00000040  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  |................|
...............太长了自己看~
[root@ceph ~]# hexdump -vC rb.0.1014.74b0dc51.000000000001|grep IN |wc -l
64
```

这里的每一行输出都是很值得思考的，首先我们导出刚刚提到的两个对象，查看第一个对象，开头就是`XFSB`，可以验证这是刚刚`mkfs.xfs`留下来的，这时候查看文件大小，发现并没有4M那么大，别担心一会会变大的，值得关注的是`file`第0x00个对象，输出居然是`XFS filesystem data`，进一步验证了刚刚`mkfs.xfs`的足迹，这和整个块的`file`信息是一样的，我猜测`xfs`把文件系统核心信息就保存在块设备的最最前面的128KB。而后面的第0x01个对象里面的`IN`输出是64，我不负责任得猜想这个可能是传说中的`inode`。抛去猜想这里给到的结论是：

在使用块设备的容量后，会按需生成对应的对象，这些对象的共同点是：命名遵循 `block_name_prefix+index`， `index` range from [0x00, 0xff]，而这个区间的大小正好是所有对象数的总和。

现在让我们把`foo`塞满：

```javascript
[root@ceph ~]# dd if=/dev/zero of=/foo/full-me 
dd: 正在写入"/foo/full-me": 设备上没有空间
记录了2010449+0 的读入
记录了2010448+0 的写出
1029349376字节(1.0 GB)已复制，37.9477 秒，27.1 MB/秒

[root@ceph ~]# ceph -s
      pgmap v81: 64 pgs, 1 pools, 994 MB data, 258 objects
            10500 MB used, 27623 MB / 40188 MB avail
```

这里写了将近1G的数据，重点在后面的`258 objects`，如果理解了前面说的内容，这258个对象自然是由`rbd_directoy`和`foo.rbd`还有256个`prefix+index`对象构成的，因为我们用完了这个块的所有容量，所以自然就生成了所有的256的小4M对象。

写入文件

我们把环境恢复到`foo`被填满的上一步，也就是刚刚`mkfs.xfs`和`mount /dev/rbd0 /foo`这里。向这个块里面写入文件：

```javascript
[root@ceph ~]# echo '111111111111111111111111111111111111111111' > /foo/file1.txt
[root@ceph ~]# echo '222222222222222222222222222222222222222222' > /foo/file2.txt
[root@ceph ~]# echo '333333333333333333333333333333333333333333' > /foo/file3.txt
[root@ceph ~]# rados -p rbd get rb.0.106a.74b0dc51.000000000001 rb.0.106a.74b0dc51.000000000001
```

这里我之所以只导出了`0x01`这个对象，是因为我之前已经导出过所有的对象，经过对比后发现，在写入文件之后，只有这个文件的大小增大了`diff`之后，很快找到了写入的内容。

```javascript
[root@ceph ~]# hexdump -vC rb.0.106a.74b0dc51.000000000001 
00000000  49 4e 41 ed 02 01 00 00  00 00 00 00 00 00 00 00  |INA.............|
00000010  00 00 00 02 00 00 00 00  00 00 00 00 00 00 00 01  |................|
00000020  00 00 00 00 00 00 00 00  57 fe 25 2f 32 6c 64 83  |........W.%/2ld.|
00000030  57 fe 25 2f 32 6c 64 83  00 00 00 00 00 00 00 36  |W.%/2ld........6|
00000040  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  |................|
00000050  00 00 00 02 00 00 00 00  00 00 00 00 00 00 00 00  |................|
00000060  ff ff ff ff 03 00 00 00  40 00 09 00 30 66 69 6c  |........@...0fil|
00000070  65 31 2e 74 78 74 00 00  40 03 09 00 48 66 69 6c  |e1.txt..@...Hfil|
00000080  65 32 2e 74 78 74 00 00  40 04 09 00 60 66 69 6c  |e2.txt..@...`fil|
00000090  65 33 2e 74 78 74 00 00  40 05 00 00 00 00 00 00  |e3.txt..@.......|
000000a0  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  |................|
000000b0  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  |................|
000000c0  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  |................|
...
00004000  31 31 31 31 31 31 31 31  31 31 31 31 31 31 31 31  |1111111111111111|
00004010  31 31 31 31 31 31 31 31  31 31 31 31 31 31 31 31  |1111111111111111|
00004020  31 31 31 31 31 31 31 31  31 31 0a 00 00 00 00 00  |1111111111......|
00004030  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  |................|
...
00005000  32 32 32 32 32 32 32 32  32 32 32 32 32 32 32 32  |2222222222222222|
00005010  32 32 32 32 32 32 32 32  32 32 32 32 32 32 32 32  |2222222222222222|
00005020  32 32 32 32 32 32 32 32  32 32 0a 00 00 00 00 00  |2222222222......|
00005030  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  |................|
...
00006000  33 33 33 33 33 33 33 33  33 33 33 33 33 33 33 33  |3333333333333333|
00006010  33 33 33 33 33 33 33 33  33 33 33 33 33 33 33 33  |3333333333333333|
00006020  33 33 33 33 33 33 33 33  33 33 0a 00 00 00 00 00  |3333333333......|
00006030  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  |................|
```

这里我们找到了文件名和文件的内容，这很`xfs`！因为是`xfs`将这些文件和他们的内容组织成这样的格式的，再关注下每一行前面的编号，这里同样是16进制编码，如果之前我对`IN == inode`的猜测是对的话，所有的`inode`即`IN`都出现在索引范围为`[0x00000000, 0x00004000)`的区间，这个`0x00004000`的单位是`byte`转换过来就是`16KB`，这个小4M内的所有的`inode`都保存在前16KB区间。而文件出现的第一个索引为`0x00004000`,第二个在`0x00005000`,第三个在`0x00006000`,之间相差了`0x1000 bytes`也就是`4096 bytes == 4KB`，还记得`mkfs.xfs`时的输出吗？

```javascript
[root@ceph ~]# mkfs.xfs /dev/rbd1
meta-data=/dev/rbd1              isize=256    agcount=9, agsize=31744 blks
         =                       sectsz=512   attr=2, projid32bit=1
         =                       crc=0        finobt=0
data     =                       bsize=4096   blocks=262144, imaxpct=25
         =                       sunit=1024   swidth=1024 blks
naming   =version 2              bsize=4096   ascii-ci=0 ftype=0
log      =internal log           bsize=4096   blocks=2560, version=2
         =                       sectsz=512   sunit=8 blks, lazy-count=1
realtime =none                   extsz=4096   blocks=0, rtextents=0
```

也就是这里的`bsize = 4096`使得文件之间间隔了4KB，很抱歉我的`xfs`知识还是一片空白，所以这里很多东西都靠猜，等我补完这一课会回来再做更正的。所以这里我们的结论就是：

RBD其实是一个完完整整的块设备，如果把1G的块想成一个1024层楼的高楼的话，`xfs`可以想象成住在这个大楼里的楼管，它只能在大楼里面，也就只能看到这1024层的房子，楼管自然可以安排所有的住户(文件or文件名)，住在哪一层哪一间，睡在地板还是天花板(文件偏移量)，隔壁的楼管叫做`ext4`,虽然住在一模一样的大楼里(`foo` or `bar`)，但是它们有着自己的安排策略，这就是文件系统如果组织文件的一个比喻了，我们就不做深究，明白到这里就好了。 然并卵，拆迁大队长跑来说，我不管你们(`xfs`or`ext4`)是怎么安排的，盖这么高的楼是想上天了？，然后大队长把这1024层房子，每4层(4MB)砍了一刀，一共砍成了256个四层，然后一起打包带走了，运到了一个叫做`Ceph`的小区里面，放眼望去，这个小区里面的房子最高也就四层(填满的)，有的才打了地基(还没写内容)。

这一节最主要的目的就是说明，在Ceph眼里，它并不关心这个RBD是做什么用处的，统统一刀斩成4M大小的对象，而使用这个RBD的用户(比如`xfs`)，它只能从RBD里面操作，它可能将一个大文件从三楼写到了五楼，但是Ceph不管，直接从四楼砍一刀，文件分了就分了，反正每个小四层都有自己的编号(index)，不会真的把文件给丢了。

最后再来个小操作(4214784=0x405000)：

```javascript
[root@ceph ~]# cat /foo/file2.txt 
222222222222222222222222222222222222222222
[root@ceph ~]# echo Ceph>Ceph
[root@ceph ~]# dd if=Ceph of=/dev/rbd0  seek=4214784 oflag=seek_bytes
记录了0+1 的读入
记录了0+1 的写出
5字节(5 B)已复制，0.0136203 秒，0.4 kB/秒
[root@ceph ~]# hexdump -Cv /dev/rbd0 -n 100 -s 0x405000
00405000  43 65 70 68 0a 32 32 32  32 32 32 32 32 32 32 32  |Ceph.22222222222|
00405010  32 32 32 32 32 32 32 32  32 32 32 32 32 32 32 32  |2222222222222222|
00405020  32 32 32 32 32 32 32 32  32 32 0a 00 00 00 00 00  |2222222222......|
00405030  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  |................|

[root@ceph ~]# cat /foo/file2.txt 
Ceph
2222222222222222222222222222222222222
```

> 需要执行`sync && echo 1 > /proc/sys/vm/drop_caches`后才能看到修改的效果。

**AMAZING!**，至少我是这么觉得的，我们通过查看`index`为`0x01`的小4M文件，得知了`file2.txt`这个文件内容在这个小4M内保存的位置为`0x5000`，因为`0x01`前面还有一个小4M文件即`0x00`，那么这个`file2.txt`在整个RBD内的偏移量为`4MB+0x5000B=0x400,000B+0x5000B=0x405000B=4214784`，也就是说保存在`/dev/rbd0`的偏移量为`0x405000`的位置，这时候用`dd`工具，直接向这个位置写入一个`Ceph`，再查看`file2.txt`的内容，果然，被修改了！

RBD 组装

受到[这篇文章](http://ceph.com/planet/ceph-recover-a-rbd-image-from-a-dead-cluster/)启发，我们开始组装一个RBD，所谓组装，就是把刚刚的13个小4M碎片从集群中取出来，然后利用这13个文件，重建出一个1G的RBD块，这里的实验环境没有那篇文章里面那么苛刻，因为集群还是能访问的，不像文章里提到的集群已死，不能执行ceph指令，需要从OSD里面把碎片文件一个个捞出来。

- 一点思考： 使用`find .`这种方法太慢了，有一个事实是，可以从任何一个`dead OSD` 导出这个集群的crushmap，我有一个为证实的猜想，能否将这个CRUSHMAP注入到一个活的集群，然后这两个集群的`ceph osd map <pool> <object>`的输出如果一样的话：
- `live`集群: `ceph osd map <pool> foo.rbd`，得到块名所存储的位置，前往`dead`集群找到之。
- `dead`集群: 读取`foo.rbd`文件读取`prefix`。希望你还能记得这个块的大小。
- `live`集群: 做个循环，读取`ceph osd map <pool> prefix+index[0x00,Max_index]`的输出，可以获取在`dead`集群的某个OSD的某个PG下面，这样就可以直接定位而不需要从`find .`结果来过滤了。
- 只是猜想，未证实，这两天证实过再回来订正。

通过[这个实验](http://xuxiaopang.com/2016/10/18/exp-get-crushmap-from-osdmap/),可以直接通过`osdmap`获取所有的`object`的存储位置，不需要平移crush了，十分方便快捷。

我们很快就可以把那13个文件拿出来了，现在开始组装：

```javascript
[root@ceph rbd]# ll
总用量 14636
-rw-r--r-- 1 root root  131072 10月 13 11:35 rb.0.1078.74b0dc51.000000000000
-rw-r--r-- 1 root root   28672 10月 13 11:35 rb.0.1078.74b0dc51.000000000001
-rw-r--r-- 1 root root   16384 10月 13 11:35 rb.0.1078.74b0dc51.00000000001f
-rw-r--r-- 1 root root   16384 10月 13 11:35 rb.0.1078.74b0dc51.00000000003e
-rw-r--r-- 1 root root   16384 10月 13 11:35 rb.0.1078.74b0dc51.00000000005d
-rw-r--r-- 1 root root 4194304 10月 13 11:36 rb.0.1078.74b0dc51.00000000007c
-rw-r--r-- 1 root root 4194304 10月 13 11:36 rb.0.1078.74b0dc51.00000000007d
-rw-r--r-- 1 root root 2129920 10月 13 11:36 rb.0.1078.74b0dc51.00000000007e
-rw-r--r-- 1 root root   16384 10月 13 11:36 rb.0.1078.74b0dc51.00000000009b
-rw-r--r-- 1 root root   16384 10月 13 11:36 rb.0.1078.74b0dc51.0000000000ba
-rw-r--r-- 1 root root   16384 10月 13 11:36 rb.0.1078.74b0dc51.0000000000d9
-rw-r--r-- 1 root root   16384 10月 13 11:36 rb.0.1078.74b0dc51.0000000000f8
-rw-r--r-- 1 root root 4194304 10月 13 11:36 rb.0.1078.74b0dc51.0000000000ff
```

组装的基本思想就是，先搭建一个1024层的大楼，然后，把刚刚的13个四层根据它的`index`,安插到对应的楼层，缺少的楼层就空在那就好了，脚本来自[刚刚的文章](https://raw.githubusercontent.com/smmoore/ceph/master/rbd_restore.sh)，我对其进行了一小部分的修改，使之适合我们这个实验，脚本将输出一个名为`foo`的块：

```javascript
#!/bin/sh
# Rados object size 这是刚刚的4M的大小
obj_size=4194304

# DD bs value
rebuild_block_size=512

#rbd="${1}" 
rbd="foo"  #生成的块名
#base="${2}" #prefix
base="rb.0.1078.74b0dc51"
#rbd_size="${3}" #1G
rbd_size="1073741824" 

base_files=$(ls -1 ${base}.* 2>/dev/null | wc -l | awk '{print $1}')
if [ ${base_files} -lt 1 ]; then
  echo "COULD NOT FIND FILES FOR ${base} IN $(pwd)"
  exit
fi

# Create full size sparse image.  Could use truncate, but wanted
# as few required files and dd what a must.
dd if=/dev/zero of=${rbd} bs=1 count=0 seek=${rbd_size} 2>/dev/null

for file_name in $(ls -1 ${base}.* 2>/dev/null); do
  seek_loc=$(echo ${file_name} | awk -F_ '{print $1}' | awk -v os=${obj_size} -v rs=${rebuild_block_size} -F. '{print os*strtonum("0x" $NF)/rs}')
  dd conv=notrunc if=${file_name} of=${rbd} seek=${seek_loc} bs=${rebuild_block_size} 2>/dev/null
done
```

从上面的脚本就可以看出，这是一个填楼工程，将其填完之后，我们来看得到的`foo`文件：

```javascript
[root@ceph rbd]# file foo
foo: SGI XFS filesystem data (blksz 4096, inosz 256, v2 dirs)
[root@ceph rbd]# du -sh foo 
15M    foo
[root@ceph rbd]# ll  -h foo
-rw-r--r-- 1 root root 1.0G 10月 13 12:26 foo
```

这时候，我们挂载会出现一个小问题，uuid重复：

```javascript
[root@ceph rbd]# mount foo /mnt
mount: 文件系统类型错误、选项错误、/dev/loop0 上有坏超级块、
       缺少代码页或助手程序，或其他错误

       有些情况下在 syslog 中可以找到一些有用信息- 请尝试
       dmesg | tail  这样的命令看看。
[root@ceph rbd]# dmesg |tail
[3270374.155472] XFS (loop0): Filesystem has duplicate UUID 1c4b010c-a2d8-4615-8307-be5419d94add - can't mount
```

原因很简单，还记得我们刚刚操作时的`mount /dev/rbd0 /foo`吗? `foo`块是`/dev/rbd0`的克隆，所以`foo`的`UUID`是和`/dev/rbd0`的是一样的，这时候我们`umount /foo`即可：

```javascript
[root@ceph rbd]# umount  /foo/
[root@ceph rbd]# mount foo /mnt
[root@ceph rbd]# ls /mnt/
file1.txt  file2.txt  file3.txt
[root@ceph rbd]# cat /mnt/file2.txt 
Ceph
2222222222222222222222222222222222222
```

神奇吧，我们用碎片文件组装了一个完完整整的RBD块，能和Ceph里map出来的RBD一样使用，并且数据也是一样的，相信如果理解了前几节的内容，对这个实验的结果就不会很意外了。

Format 1 VS Format 2

众所周知，RBD有两种格式：

- `Format 1`: `Hammer`以及`Hammer`之前默认都是这种格式，并且`rbd_default_features = 3`.
- `Format 2`: `Jewel`默认是这种格式，并且`rbd_default_features = 61`.

关于`features`的问题将在下节解释，这里我们只讨论这两种格式的RBD在ceph底层的存储有什么区别，首先安装一个`Jewel`版本的环境(或者改配置项)，方法很简单：

```javascript
[root@ceph install-ceph-in-one-minute]#  cd /root/install-ceph-in-one-minute/
[root@ceph install-ceph-in-one-minute]#  ./cleanup.sh 
kill: 向 945 发送信号失败: 没有那个进程
root       955   943  0 13:18 pts/4    00:00:00 grep ceph
root     20960     2  0 10月11 ?      00:00:00 [ceph-msgr]
root     22052     2  0 10月12 ?      00:00:00 [ceph-watch-noti]
umount: /var/lib/ceph/osd/ceph-0：未挂载
[root@ceph install-ceph-in-one-minute]# sed -i 's/hammer/jewel/g' install.sh 
[root@ceph install-ceph-in-one-minute]# ./install.sh
...
[root@ceph ~]# ceph -s
    cluster 04949396-488c-4244-a141-b2ae6de3ed38
     health HEALTH_OK
     monmap e1: 1 mons at {ceph=233.233.233.233:6789/0}
            election epoch 3, quorum 0 ceph
     osdmap e5: 1 osds: 1 up, 1 in
            flags sortbitwise
      pgmap v15: 64 pgs, 1 pools, 0 bytes data, 0 objects
            7234 MB used, 30889 MB / 40188 MB avail
                  64 active+clean
[root@ceph ~]# ceph -v
ceph version 10.2.3 (ecc23778eb545d8dd55e2e4735b53cc93f92e65b)
```

创建一个`foo`块，并观察集群多出了哪些文件:

```javascript
[root@ceph ~]# rbd create foo --size 1024
[root@ceph ~]# rbd info foo
rbd image 'foo':
    size 1024 MB in 256 objects
    order 22 (4096 kB objects)
    block_name_prefix: rbd_data.101474b0dc51
    format: 2
    features: layering, exclusive-lock, object-map, fast-diff, deep-flatten
    flags: 
[root@ceph ~]# rados -p rbd ls
rbd_object_map.101474b0dc51
rbd_header.101474b0dc51
rbd_id.foo
rbd_directory

[root@ceph ~]# rbd map foo
rbd: sysfs write failed
RBD image feature set mismatch. You can disable features unsupported by the kernel with "rbd feature disable".
In some cases useful info is found in syslog - try "dmesg | tail" or so.
rbd: map failed: (6) No such device or address
[root@ceph ~]# rbd feature disable foo deep-flatten
[root@ceph ~]# rbd feature disable foo fast-diff
[root@ceph ~]# rbd feature disable foo object-map
[root@ceph ~]# rbd feature disable foo exclusice-lock
[root@ceph ~]# rbd map foo
/dev/rbd1
[root@ceph ~]# rados -p rbd ls
rbd_header.101474b0dc51
rbd_id.foo
rbd_directory
```

多出了四个文件，在关闭`object-map`属性后，少了一个`rbd_object_map.101474b0dc51`文件，我们查看剩下的三个文件内容：

```javascript
[root@ceph ~]# rados -p rbd get rbd_header.101474b0dc51 rbd_header.101474b0dc51
[root@ceph ~]# rados -p rbd get rbd_id.foo rbd_id.foo
[root@ceph ~]# rados -p rbd get rbd_directory rbd_directory
[root@ceph ~]# hexdump -Cv rbd_directory 
[root@ceph ~]# hexdump -Cv rbd_header.101474b0dc51 
[root@ceph ~]# hexdump -Cv rbd_id.foo 
00000000  0c 00 00 00 31 30 31 34  37 34 62 30 64 63 35 31  |....101474b0dc51|
00000010
```

可以发现，`rbd_directory`不再保存所有RBD的名称，相比于`format1的 foo.rbd`，`format2`采用`rbd_id.rbdName`的形式保存了这个块的`prefix`，而另一个文件`rbd_header,xxxxxxxxprefix`显示的保存了这个`prefix`，我们再向这个块写入点文件：

```javascript
[root@ceph ~]# mkfs.xfs /dev/rbd1
[root@ceph ~]# ceph -s
      pgmap v187: 64 pgs, 1 pools, 14624 kB data, 16 objects
[root@ceph ~]# rados -p rbd ls|sort
rbd_data.101474b0dc51.0000000000000000
rbd_data.101474b0dc51.0000000000000001
rbd_data.101474b0dc51.000000000000001f
rbd_data.101474b0dc51.000000000000003e
rbd_data.101474b0dc51.000000000000005d
rbd_data.101474b0dc51.000000000000007c
rbd_data.101474b0dc51.000000000000007d
rbd_data.101474b0dc51.000000000000007e
rbd_data.101474b0dc51.000000000000009b
rbd_data.101474b0dc51.00000000000000ba
rbd_data.101474b0dc51.00000000000000d9
rbd_data.101474b0dc51.00000000000000f8
rbd_data.101474b0dc51.00000000000000ff
rbd_directory
rbd_header.101474b0dc51
rbd_id.foo
```

可以发现，生成的13个小4M文件的后缀和`format 1`的是一模一样的，只是命名规则变成了`rbd_data.[prefix].+[index]`,之所以后缀是一样的是因为`xfs`对于1G的块总是会这样构建文件系统，所以对于`F1 & F2`，这些小4M除了命名规范不一样外，实际保存的内容都是一样的，下面对这两种格式进行简要的对比总结：

| 格式     | rbd_diretory        | ID         | prefix                             | Data                                        |
| :------- | :------------------ | :--------- | :--------------------------------- | :------------------------------------------ |
| Format 1 | 保存了所有RBD的名称 | foo.rbd    | 在ID中                             | 形如 rb.0.1014.74b0dc51.000000000001        |
| Format 2 | 空                  | rbd_id.foo | 在ID中 并rbd_header.prefix显示输出 | 形如 rbd_data.101474b0dc51.0000000000000001 |

FAQ

1、 rbd feature disable

最常见的RBD使用问题，一般出现于`Format 2`的`rbd map`操作，需要关闭如下属性即可，**注意顺序**：

```javascript
[root@ceph ~]# rbd feature disable foo deep-flatten
[root@ceph ~]# rbd feature disable foo fast-diff
[root@ceph ~]# rbd feature disable foo object-map
[root@ceph ~]# rbd feature disable foo exclusice-lock
```

2、100TB的RBD要删几个月?

是的，之前看到调试的log发现，`rbd rm foo`的时候，是从index的0开始一个个得往后面删，所以100TB 的块有两千六百万个4M碎片组成，虽然实际上并没有用到这么多，但是一个个删的话，还是相当慢的，如果是`Format 1`我们可以`rados ls|grep block_name_prefix |xargs rados rm`这种思路删除，再删掉`foo.rbd`文件，再执行`rbd rm foo`就可以很快删掉了。这里[有一篇很详尽的文章](http://cephnotes.ksperis.com/blog/2014/07/04/remove-big-rbd-image/)介绍了删除方法。

3、为什么总是4M的块

`rbd_default_order = 22`这个配置项决定了切块的大小，默认值为22，参考了[这篇文章](http://fossies.org/linux/ceph/src/test/cli-integration/rbd/defaults.t)我得到了`order`和`size`的几个关系:

| order | size |
| :---- | :--- |
| 23    | 8M   |
| 22    | 4M   |
| 21    | 2M   |
| 20    | 1M   |

大概关系就是这样，暂时没找更详细的介绍，`man rbd`能看到更详细的信息。

> size = 2 `**` order bytes 也就是2的order次方。

4、 Features 编号

配置项为`rbd_default_features = [3 or 61]`,这个值是由几个属性加起来的：

- only applies to format 2 images
- +1 for layering,
- +2 for stripingv2,
- +4 for exclusive lock,
- +8 for object map
- +16 for fast-diff,
- +32 for deep-flatten,
- +64 for journaling

所以`61=1+4+8+16+32`就是`layering | exclusive lock | object map |fast-diff |deep-flatten`这些属性的大合集,需要哪个不需要哪个，做个简单的加法配置好`rbd_default_features`就可以了。 总结

这篇文章还是有点残缺的：

- RBD碎片在底层是以`rbd\udata.101474b0dc51.0000000000000000__head_DDFD75CF__0`这种命名方式保存的。

- `xfs`的`inode`猜测为证实。

- CRUSHMAP的平移注入是否会产生相同的

  ```
  ceph osd map
  ```

  结果。

  - 答案：会产生相同的结果，但是不需要平移，只需要一个`osdmap`就好了。

最简单的话来总结下RBD：Client从RBD内部看，RBD是一个整体，Ceph从RBD外部看，是若干的碎片。

## 参考链接
[《大话 Ceph》 之 RBD 那点事儿](https://cloud.tencent.com/developer/article/1006283)