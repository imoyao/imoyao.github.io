---
title: PG 那点事
toc: true
date: 2020-05-23 11:02:28
tags:
- ceph

---

## 引言

PG，Placement Group，中文翻译为归置组，在 Ceph 中是一个很重要的概念，这篇文章将对 PG 进行深入浅出的讲解。

PG 是什么？

PG 就是目录！

我事先搭建了一个`3个host, 每个host有3个OSD`的集群，集群使用 3 副本，`min_size`为 2。 集群状态如下：

```javascript
[root@ceph-1 ~]# ceph osd tree
ID WEIGHT   TYPE NAME       UP/DOWN REWEIGHT PRIMARY-AFFINITY 
-1 17.90991 root default                                      
-2  5.96997     host ceph-1                                   
 0  1.98999         osd.0        up  1.00000       1.00000 
 1  1.98999         osd.1        up  1.00000       1.00000 
 2  1.98999         osd.2        up  1.00000       1.00000 
-4  5.96997     host ceph-2                                   
 3  1.98999         osd.3        up  1.00000       1.00000 
 4  1.98999         osd.4        up  1.00000       1.00000
 5  1.98999         osd.5        up  1.00000       1.00000 
-3  5.96997     host ceph-3                                   
 6  1.98999         osd.6        up  1.00000       1.00000 
 7  1.98999         osd.7        up  1.00000       1.00000 
 8  1.98999         osd.8        up  1.00000       1.00000
```

每一个 pool 都有一个 id，系统默认生成的 `rbd` 池的 id 号为 `0`，那么 `rbd` 池内的所有 PG 都会以 `0.` 开头，让我们看一下 `osd.0` 下面的 `current` 目录的内容：

```javascript
[root@ceph-1 ~]# ls /var/lib/ceph/osd/ceph-0/current/
0.0_head   0.1d_head  0.34_head  0.45_head  0.4e_head  
....省略部分内容
0.af_head  0.bc_head  0.d0_head  0.e2_head  0.f4_head
```

每个 OSD 的 `current` 目录下都保存了部分的 PG，而 `rbd` 池的 PG 则以 `0.xxx_head` 的目录形式存在！

现在我们通过 `rados` 向集群写入一个文件(`/root/char.txt`)，在集群内保存名为 `char` ,通过下面的指令查看该文件实际保存的位置：

```javascript
[root@ceph-1 ~]# ceph osd map rbd char
osdmap e109 pool 'rbd' (0) object 'char' -> pg 0.98165844 (0.44) -> up ([0,7,4], p0) acting ([0,7,4], p0)
```

可见，文件会保存在 PG `0.44`中，而这个 PG 位于`osd.0`,`osd.7`,`osd.4`中，之所以有这里有三个 OSD，是因为集群副本数为 3，可以在 0/7/4 这三个 OSD 的 current 下找到`0.44_head`目录。而同一份文件(比如这里的 /root/char.txt )的三个副本会分别保存在这三个同名的 PG 中。

执行指令，将`/root/char.txt`文件存入集群，并查看各个 OSD 的 PG 目录内容：

```javascript
[root@ceph-1 cluster]# rados -p rbd put char char.txt 
[root@ceph-1 0.44_head]# pwd && ll
/var/lib/ceph/osd/ceph-0/current/0.44_head
-rw-r--r--. 1 root root 8 8月  25 01:38 char__head_98165844__0
-rw-r--r--. 1 root root 0 8月  24 23:40 __head_00000044__0
[root@ceph-2 0.44_head]# pwd && ll
/var/lib/ceph/osd/ceph-4/current/0.44_head
-rw-r--r-- 1 root root 8 8月  25 13:38 char__head_98165844__0
-rw-r--r-- 1 root root 0 8月  25 11:40 __head_00000044__0
[root@ceph-3 0.44_head]# pwd && ll
/var/lib/ceph/osd/ceph-7/current/0.44_head
-rw-r--r-- 1 root root 8 8月  25 13:38 char__head_98165844__0
-rw-r--r-- 1 root root 0 8月  25 11:40 __head_00000044__0
```

可见，这三个 OSD 保存了这个文件的三个副本，这就是 Ceph 的多副本的基础，将一份数据保存成多个副本，按照一定规则分布在各个 OSD 中，而多副本的数据的一个特点就是，他们都保存在**同名**的 PG 下面，也就是同名的目录下。这样，我们就对 PG 有了一个直观的理解。

`active+clean` 想说爱你不容易

`active + clean` 是 PG 的健康状态，然而 PG 也会`生病`,有的是小感冒，有的则可能是一级伤残，下面就是集群进入恢复状态时的一个截图，这里面聚集了各种老弱病残，现在就来分析下每种病症的原因:

这里再次回忆下集群的配置：`size = 3, min_size = 2`

1、Degraded

降级：由上文可以得知，每个 PG 有三个副本，分别保存在不同的 OSD 中，在非故障情况下，这个 PG 是`active+clean` 状态，那么，如果保存 `0.44` 这个 PG 的 osd.4 挂掉了，这个 PG 是什么状态呢，操作如下：

```javascript
[root@ceph-2 ~]# service ceph stop osd.4
=== osd.4 === 
Stopping Ceph osd.4 on ceph-2...kill 6475...kill 6475...done
[root@ceph-2 ~]# ceph pg dump_stuck |egrep ^0.44
0.44    active+undersized+degraded    [0,7]    0    [0,7]    0
```

这里我们前往 `ceph-2` 节点，手动停止了 osd.4，然后查看此时 PG : 0.44 的状态，可见，它此刻的状态是`active+undersized+degraded`,当一个 PG 所在的 OSD 挂掉之后，这个 PG 就会进入`undersized+degraded` 状态，而后面的`[0,7]`的意义就是还有两个 0.44 的副本存活在 osd.0 和 osd.7 上。那么现在可以读取刚刚写入的那个文件吗？是可以正常读取的！

```javascript
[root@ceph-1 0.44_head]# rados  -p rbd get char char.txt
[root@ceph-1 0.44_head]# cat char.txt 
abcdefg
```

**降级** 就是在发生了一些故障比如 OSD 挂掉之后，Ceph 将这个 OSD 上的所有 PG 标记为 `degraded`，但是此时的集群还是可以正常读写数据的，降级的 PG 只是相当于小感冒而已，并不是严重的问题，而另一个词 `undersized`,意思就是当前存活的 PG 0.44 数为 2，小于副本数 3，将其做此标记，表明存货副本数不足，也不是严重的问题。

2、Peered

那么，什么才是 PG 的大病呢，`peered` 算是一个，刚刚我们关闭了 osd.4，集群里还活着两个 PG 0.44，现在我们关闭 osd.7，查看下 0.44 的状态：

```javascript
[root@ceph-3 0.44_head]# service ceph stop osd.7
=== osd.7 === 
Stopping Ceph osd.7 on ceph-3...kill 5986...kill 5986...done
[root@ceph-2 ~]# ceph pg dump_stuck |egrep ^0.44
0.44    undersized+degraded+peered    [0]    0    [0]    0
```

可见，现在只剩下独苗苗活在 osd.0 上了，并且 0.44 还多了一个状态：`peered`，英文的意思是仔细看，这里我们可以理解成`协商、搜索`，这时候读取`char.txt`文件，会发现指令会卡在那个地方一直不动，如此来解释`min_size`的作用，在 Ceph 中，它的全名叫做 `osd_pool_default_min_size`，这里大家就会问了，不是还活着一个呢吗，为什么就不能读取内容了，因为我们设置的 `min_size=2` ，在 Ceph 中的意义就是，如果存活数少于 2 了，比如这里的 1 ，那么 Ceph 就不会响应外部的 IO 请求。

在这里如果执行指令,将 min_size 设置为 1 :

```javascript
[root@ceph-2 ~]# ceph osd pool set rbd min_size 1
[root@ceph-2 ~]# ceph pg dump_stuck |egrep ^0.44
0.44    active+undersized+degraded    [0]    0    [0]    0
```

可以看到，0.44 没有了 `peered` 状态，并且文件可以正常读写了，因为`min_size=1`时，只要集群里面有一份副本活着，那就可以响应外部的 IO 请求。

**peered**，我们这里可以将它理解成它在等待其他兄弟姐妹上线，这里 min_size =2 ,也就是 osd.4 和 osd.7 的任意一个上线就可以去除这个状态了，处于 `peered` 状态的 PG 是不能响应外部的请求的，外部就会觉得 IO 被挂起。

3、Remapped

Ceph 强大的自我恢复能力，是我们选择它的一个重要原因，在上面的试验中，我们关闭了两个 OSD，但是至少还有一个 PG 0.44 存活在 osd.0 上，如果那两个盘真的坏了，Ceph 还是可以将这份仅存的数据恢复到别的 OSD 上的。

在 OSD 挂掉 5 分钟 ( mon_osd_down_out_interval = 300 )之后，这个 OSD 会被标记为 out 状态，可以理解为 Ceph 认为这个 OSD 已经不属于集群了，然后就会把 PG 0.44 remap 到别的 OSD 上去，这个 remap 到哪些 OSD 上也是按照一定的算法计算得到的，重映射之后呢，就会在另外两个 OSD 上找到 0.44 这个 PG，而这只是创建了这个目录而已，丢失的数据是要从仅存的 OSD 上回填到新的 OSD 上的，处于回填状态的 PG 就会被标记为`backfilling`。

所以当一个 PG 处于`remapped+backfilling`状态时，可以认为其处于自我克隆复制的自愈过程。

4、 Recover

这里我们先来做一个实验，首先开启所有 OSD 使得集群处于健康状态，然后前往 osd.4 的 PG 0.44 下面删除`char__head_98165844__0`这个文件，再通知 Ceph 扫描(`scrub`)这个 PG：

```javascript
[root@ceph-2 0.44_head]# pwd && rm -f char__head_98165844__0 
/var/lib/ceph/osd/ceph-4/current/0.44_head
[root@ceph-2 0.44_head]# ceph pg scrub 0.44
[root@ceph-2 0.44_head]# ceph pg dump |egrep ^0.44
active+clean+inconsistent [0,7,4]    0    [0,7,4]    0
```

可见，0.44 多了个 `inconsistent` 状态，顾名思义，Ceph 发现了这个 PG 的不一致状态，这样就可以理解这个 `inconsistent` 的意义了。

想要修复丢失的文件呢，只需要执行 `ceph pg repair 0.44`，ceph 就会从别的副本中将丢失的文件拷贝过来，这也是 ceph 自愈的一个情形。

现在再假设一个情形，在 osd.4 挂掉的过程中呢，我们对 `char` 文件进行了写操作，因为集群内还存在着两个副本，是可以正常写入的，但是 osd.4 内的数据并没有得到更新，过了一会，osd.4 上线了，Ceph 就发现，osd.4 的`char`文件是陈旧的，就通过别的 OSD 向 osd.4 进行数据的恢复，使其数据为最新的，而这个恢复的过程中，PG 就会被标记为 `recover`。

总结

至此，我们对 PG 在磁盘的具体意义进行了分析，相信大家也对 PG 有了更深入的理解，同时，对常见的 PG 状态进行了剖析，今后看到了长长的病例单也不会有所畏惧了。

## 参考链接
[《 大话 Ceph 》 之 PG 那点事儿](https://cloud.tencent.com/developer/article/1006292)