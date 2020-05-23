---
title: CRUSH那点事儿
toc: true
date: 2020-05-23 11:02:28
tags:
- ceph
categories: CEPH
---

## 引言

> 那么问题来了，把一份数据存到一群Server中分几步？

Ceph的答案是：两步。

1. 计算PG
2. 计算OSD



首先，要明确Ceph的一个规定：在Ceph中，一切皆对象。

不论是视频，文本，照片等一切格式的数据，Ceph统一将其看作是对象，因为追其根源，所有的数据都是二进制数据保存于磁盘上，所以每一份二进制数据都看成一个对象，不以它们的格式来区分他们。

那么用什么来区分两个对象呢？**对象名**。也就是说，每个不同的对象都有不一样的对象名。于是，开篇的问题就变成了：

> 把一个对象存到一群Server中分几步？

这里的一群Server，由Ceph组织成一个集群，这个集群由若干的磁盘组成，也就是由若干的OSD组成。于是，继续简化问题：

> 把一个对象存到一堆OSD中分几步?

## Ceph中的逻辑层

Ceph为了保存一个对象，对上构建了一个逻辑层，也就是池(pool)，用于保存对象，这个池的翻译很好的解释了pool的特征，如果把pool比喻成一个中国象棋棋盘，那么保存一个对象的过程就类似于把一粒芝麻放置到棋盘上。

Pool再一次进行了细分，即将一个pool划分为若干的PG(归置组 Placement Group)，这类似于棋盘上的方格，所有的方格构成了整个棋盘，也就是说所有的PG构成了一个pool。

现在需要解决的问题是，对象怎么知道要保存到哪个PG上，假定这里我们的pool名叫rbd，共有256个PG，给每个PG编个号分别叫做`0x0, 0x1, ...0xF, 0x10, 0x11... 0xFE, 0xFF`。

要解决这个问题，我们先看看我们拥有什么，1，不同的对象名。2，不同的PG编号。这里就可以引入Ceph的计算方法了 : HASH。

对于对象名分别为`bar`和`foo`的两个对象，对他们的对象名进行计算即:

- HASH(‘bar’) = 0x3E0A4162
- HASH(‘foo’) = 0x7FE391A0
- HASH(‘bar’) = 0x3E0A4162

对对象名进行HASH后，得到了一串十六进制输出值，也就是说通过HASH我们将一个对象名转化成了一串数字，那么上面的第一行和第三行是一样的有什么意义？ 意义就是对于一个同样的对象名，计算出来的结果永远都是一样的，但是HASH算法的确将对象名计算得出了一个随机数。

有了这个输出，我们使用小学就会的方法：求余数！用随机数除以PG的总数256，得到的余数一定会落在[0x0, 0xFF]之间，也就是这256个PG中的某一个：

- 0x3E0A4162 % 0xFF ===> 0x62
- 0x7FE391A0 % 0xFF ===> 0xA0

于是乎，对象`bar`保存到编号为`0x62`的PG中，对象`foo`保存到编号为`0xA0`的PG中。对象`bar`永远都会保存到PG 0x62中！ 对象`foo`永远都会保存到PG 0xA0中！

现在又来了一亿个对象，他们也想知道自己会保存到哪个PG中，Ceph说：“自己算”。于是这一亿个对象，各自对自己对象名进行HASH，得到输出后除以PG总数得到的余数就是要保存的PG。

求余的好处就是对象数量规模越大，每个PG分布的对象数量就越平均。

所以每个对象自有名字开始，他们要保存到的PG就已经确定了。

那么爱思考的小明同学就会提出一个问题，难道不管对象的高矮胖瘦都是一样的使用这种方法计算PG吗，答案是，YES! 也就是说Ceph不区分对象的真实大小内容以及任何形式的格式，只认对象名。毕竟当对象数达到百万级时，对象的分布从宏观上来看还是平均的。

这里给出更Ceph一点的说明，实际上在Ceph中，存在着多个pool，每个pool里面存在着若干的PG，如果两个pool里面的PG编号相同，Ceph怎么区分呢? 于是乎，Ceph对每个pool进行了编号，比如刚刚的rbd池，给予编号0，再建一个pool就给予编号1，那么在Ceph里，PG的实际编号是由`pool_id+.+PG_id`组成的，也就是说，刚刚的`bar`对象会保存在`0.62`这个PG里，`foo`这个对象会保存在`0.A0`这个PG里。其他池里的PG名称可能为`1.12f, 2.aa1,10.aa1`等。

## Ceph中的物理层

理解了刚刚的逻辑层，我们再看一下Ceph里的物理层，对下，也就是我们若干的服务器上的磁盘，通常，Ceph将一个磁盘看作一个OSD(实际上，OSD是管理一个磁盘的程序)，于是物理层由若干的OSD组成，我们的最终目标是将对象保存到磁盘上，在逻辑层里，对象是保存到PG里面的，那么现在的任务就是`打通PG和OSD之间的隧道`。PG相当于一堆余数相同的对象的组合，PG把这一部分对象打了个包，现在我们需要把很多的包平均的安放在各个OSD上，这就是CRUSH算法所要做的事情：`CRUSH计算PG->OSD的映射关系`。

加上刚刚的对象映射到PG的方法，我们将开篇的两步表示成如下的两个计算公式：

- 池ID + HASH(‘对象名’) % pg_num ===> PG_ID
- CRUSH(PG_ID) ===> OSD

## 使用HASH代替CRUSH？

在讨论CRUSH算法之前，我们来做一点思考，可以发现，上面两个计算公式有点类似，为何我们不把

- `CRUSH(PG_ID) ===> OSD`
  改为
- `HASH(PG_ID) %OSD_num ===> OSD`

我可以如下几个由此假设带来的副作用：

- 如果挂掉一个OSD，`OSD_num-1`，于是所有的`PG % OSD_num`的余数都会变化，也就是说这个PG保存的磁盘发生了变化，对这最简单的解释就是，这个PG上的数据要从一个磁盘全部迁移到另一个磁盘上去，一个优秀的存储架构应当在磁盘损坏时使得数据迁移量降到最低，CRUSH可以做到。
- 如果保存多个副本，我们希望得到多个OSD结果的输出，HASH只能获得一个，但是CRUSH可以获得任意多个。
- 如果增加OSD的数量，OSD_num增大了，同样会导致PG在OSD之间的胡乱迁移，但是CRUSH可以保证数据向新增机器均匀的扩散。

所以HASH只适用于一对一的映射关系计算，并且两个映射组合(对象名和PG总数)不能变化，因此这里的假设不适用于PG->OSD的映射计算。因此，这里开始引入CRUSH算法。

## 引入CRUSH算法

千呼万唤始出来，终于开始讲CRUSH算法了，如果直接讲Sage的博士论文或者`crush.c`的代码的话，可能会十分苦涩难懂，所以我决定尝试大话一把CRUSH，希望能让没有接触过CRUSH的同学也能对其有所理解。

首先来看我们要做什么：

- 把已有的PG_ID映射到OSD上，有了映射关系就可以把一个PG保存到一个磁盘上。
- 如果我们想保存三个副本，可以把一个PG映射到三个不同的OSD上，这三个OSD上保存着一模一样的PG内容。

再来看我们有了什么：

- 互不相同的PG_ID。
- 如果给OSD也编个号，那么就有了互不相同的OSD_ID。
- 每个OSD最大的不同的就是它们的容量，即4T还是800G的容量，我们将每个OSD的容量又称为OSD的权重(weight)，规定4T权重为4，800G为0.8，也就是以T为单位的值。

现在问题转化为：如何将PG_ID映射到有各自权重的OSD上。这里我直接使用CRUSH里面采取的`Straw`算法，翻译过来就是抽签，说白了就是挑个最长的签，这里的签指的是OSD的权重。

那么问题就来了，总不至于每次都挑容量最大的OSD吧，这不分分钟都把数据存满那个最大的 OSD了吗？是的，所以在挑之前先把这些OSD`搓一搓`，这里直接介绍CRUSH的方法，如下图(可忽视代码直接看文字)：

[![Alt text](http://www.xuxiaopang.com/images/1478244507156.png)](http://www.xuxiaopang.com/images/1478244507156.png)

- CRUSH_HASH( PG_ID, OSD_ID, r ) ===> draw
- ( draw &0xffff ) * osd_weight ===> osd_straw
- pick up high_osd_straw

第一行，我们姑且把r当做一个常数，第一行实际上就做了搓一搓的事情:将PG_ID, OSD_ID和r一起当做CRUSH_HASH的输入，求出一个十六进制输出，这和HASH(对象名)完全类似，只是多了两个输入。所以需要强调的是，对于相同的三个输入，计算得出的`draw`的值是一定相同的。

这个`draw`到底有啥用？其实，CRUSH希望得到一个随机数，也就是这里的`draw`，然后拿这个随机数去乘以OSD的权重，这样把随机数和OSD的权重搓在一起，就得到了每个OSD的实际签长，而且每个签都不一样长(极大概率)，就很容易从中挑一个最长的。

说白了，CRUSH希望`随机`挑一个OSD出来，但是还要满足权重越大的OSD被挑中的概率越大，为了达到随机的目的，它在挑之前让每个OSD都拿着自己的权重乘以一个随机数，再取乘积最大的那个。那么这里我们再定个小目标：挑个一亿次！从宏观来看，同样是乘以一个随机数，在样本容量足够大之后，这个随机数对挑中的结果不再有影响，起决定性影响的是OSD的权重，也就是说，OSD的权重越大，宏观来看被挑中的概率越大。

这里再说明下CRUSH造出来的随机数`draw`，前文可知，对于常量输入，一定会得到一样的输出，所以这并不是真正的随机，所以说，CRUSH是一个`伪随机`算法。下图是`CRUSH_HASH`的代码段，我喜欢叫它搅拌搅拌再搅拌得出一个随机数:

[![Alt text](http://www.xuxiaopang.com/images/1478244378743.png)](http://www.xuxiaopang.com/images/1478244378743.png)

如果看到这里你已经被搅晕了，那让我再简单梳理下PG选择一个OSD时做的事情：

- 给出一个PG_ID，作为CRUSH_HASH的输入。
- CRUSH_HASH(PG_ID, OSD_ID, r) 得出一个随机数(重点是随机数，不是HASH)。
- 对于所有的OSD用他们的权重乘以每个OSD_ID对应的随机数，得到乘积。
- 选出乘积最大的OSD。
- 这个PG就会保存到这个OSD上。

现在趁热打铁，解决一个PG映射到多个OSD的问题，还记得那个常量`r`吗？我们把`r+1`，再求一遍随机数，再去乘以每个OSD的权重，再去选出乘积最大的OSD，如果和之前的OSD编号不一样，那么就选中它，如果和之前的OSD编号一样的话，那么再把`r+2`，再次选一次，直到选出我们需要的三个不一样编号的OSD为止！


当然实际选择过程还要稍微复杂一点，我这里只是用最简单的方法来解释CRUSH在选择OSD的时候所做的事情。

下面我们来举个例子，假定我们有6个OSD，需要从中选出三个副本：

| osd_id | weight | CRUSH_HASH | (CRUSH_HASH & 0xffff)* weight |
| :----: | :----: | :--------: | :---------------------------: |
| osd.0  |   4    | 0xC35E90CB |            0x2432C            |
| osd.1  |   4    | 0xA67DE680 |          **0x39A00**          |
| osd.2  |   4    | 0xF9B1B224 |            0x2C890            |
| osd.3  |   4    | 0x42454470 |            0x111C0            |
| osd.4  |   4    | 0xE950E2F9 |            0x38BE4            |
| osd.5  |   4    | 0x8A844538 |            0x114E0            |

这是`r = 0`的情况，这时候，我们选出`(CRUSH_HASH & 0xFFFF) * weight`的值最大的一个，也就是`osd.1`的`0x39A00`,这就是我们选出的第一个OSD。
然后，我们再让`r = 1`，再生成一组`CRUSH_HASH`的随机值，乘以OSD的weight，再取一个最大的得到第二个OSD，依此得到第三个OSD，如果在此过程中，选中了相同的OSD，那么将`r`再加一，生成一组随机值，再选一次，直到选中三个OSD为止。

## CRUSH算法的应用

理解了上面CRUSH选择OSD的过程，我们就很容易进一步将CRUSH算法结合实际结构，这里给出Sage在他的博士论文中画的一个树状结构图：
[![Alt text](http://www.xuxiaopang.com/images/1478486778573.png)](http://www.xuxiaopang.com/images/1478486778573.png)

最下面的蓝色长条可以看成一个个主机，里面的灰色圆柱形可以看成一个个OSD，紫色的cabinet可以也就是一个个机柜， 绿色的row可以看成一排机柜，顶端的root是我们的根节点，没有实际意义，你可以把它看成一个数据中心的意思，也可以看成一个机房的意思，不过只是起到了一个树状结构的根节点的作用。

基于这样的结构选择OSD，我们提出了新的要求：

- 一共选出三个OSD。
- 这三个OSD需要都位于一个row下面。
- 每个cabinet内至多有一个OSD。

这样的要求，如果用上一节的CRUSH选OSD的方法，不能满足二三两个要求，因为OSD的分布是随机的。

那么要完成这样的要求，先看看我们现在有什么：

- 每个OSD的weight。
- 每个主机也可以有一个weight，这个weight由主机内的所有OSD的weight累加而得。
- 每个cabinet的weight由所有主机的weight累加而得，其实就是这个cabinet下的所有OSD的权重之和。
- 同理推得每个row的weight有cabinet累加而得。
- root的weight其实就是所有的OSD的权重之和。

所以在这棵树状结构中，每个节点都有了自己的权重，每个节点的权重由`下一层`节点的权重累加而得，因此根节点root的权重就是这个集群所有的OSD的权重之和，那么有了这么多权重之后，我们怎么选出那三个OSD呢？

仿照CRUSH选OSD的方法：

- CRUSH从root下的所有的row中选出一个row。
- 在刚刚的一个row下面的所有cabinet中，CRUSH选出三个cabinet。
- 在刚刚的三个cabinet下面的所有OSD中，CRUSH分别选出一个OSD。

因为每个row都有自己的权重，所以CRUSH选row的方法和选OSD的方法完全一样，用row的权重乘以一个随机数，取最大。然后在这个row下面继续选出三个cabinet，再在每个cabinet下面选出一个OSD。

这样做的根本意义在于，将数据平均分布在了这个集群里面的所有OSD上，如果两台机器的权重是16：32，那么这两台机器上分布的数据量也是1：2。同时，这样选择做到了三个OSD分布在三个不同的cabinet上。

那么结合图例这里给出CRUSH算法的流程：

- take(root) ============> [root]
- choose(1, row) ========> [row2]
- choose(3, cabinet) =====> [cab21, cab23, cab24] *在[row2]下*
- choose(1, osd) ========> [osd2107, osd2313, osd2437] *在三个cab下*
- emit ================> [osd2107, osd2313, osd2437]

这里给出CRUSH算法的两个重要概念：

- BUCKET/OSD : OSD和我们的磁盘一一对应，bucket是除了OSD以外的所有非子叶节点，比如上面的cabinet,row,root等都是。
- RULE ： CRUSH选择遵循一条条选择路径，一个选择路径就是一个rule。

RULE一般分为三步走 : `take`–>`choose N`–>`emit`。`Take`这一步负责选择一个根节点，这个根节点不一定是`root`，也可以是任何一个Bucket。`choose N`做的就是按照每个Bucket的weight以及每个`choose`语句选出符合条件的Bucket，并且，**下一个choose的选择对象为上一步得到的结果**。`emit`就是输出最终结果，相当于出栈。

这里再举个简单的例子，也就是我们最常见的三个主机每个主机三个OSD的结构：
[![Alt text](http://www.xuxiaopang.com/images/1478497045877.png)](http://www.xuxiaopang.com/images/1478497045877.png)

我们要从三个host下面各选出一个OSD，使得三个副本各落在一个host上，这时候，就能保证挂掉两个host，还有一个副本在运行了，那么这样的RULE就形如：

- take(root) ============> [default] 注意是根节点的名字
- choose(3, host) ========> [ceph-1, ceph-2, ceph-3]
- choose(1, osd) ========> [osd.3, osd.1, osd.8]
- emit()

这里我们来简单总结一下：我们把一个生产环境的机房画成一个树状结构，最下面一层为OSD层，每个OSD有自己的权重，OSD的上面由host/rack/row/room/root等等节点构成，每个节点的权重都是由下层的节点累加而成，CRUSH选择每个节点的算法(straw)都是一样的，用它们的weight乘以一个随机数取其中最大，只是我们通过`choose`的语句来判断选择的节点类型和个数。最后不要忘了选出来的结果是PG->OSD的映射，比如:`pg 0.a2 ---> [osd.3, osd.1, osd.8]`和`pg 0.33 ---> [osd.0, osd.5, osd.7]`, 每个PG都有自己到OSD的映射关系，这个关系用公式总结就是： `CRUSH(pg_id) ---> [osd.a, osd.b ...osd.n]`。

到目前为止，我们已经完成了一份数据保存到一群Server的第二步，再整体回顾下这个流程：

- 每个文件都有一个唯一的对象名。
- Pool_ID + HASH(对象名) % PG_NUM 得到PG_ID
- CRUSH(PG_ID) 得到该PG将要保存的OSD组合
- 这个对象就会保存到位于这些OSD上的PG上(PG就是磁盘上的目录)

所以，HASH算法负责计算对象名到PG的映射，CRUSH负责计算PG到OSD的映射，暂且记住这一点。

## CRUSH里的虚虚实实

现在，我们有三台主机，每台主机上的配置如下：

| 主机名 |          磁盘数          |
| :----: | :----------------------: |
| ceph-1 | 4T SATA * 3  800G SSD *1 |
| ceph-2 | 4T SATA * 3  800G SSD *1 |
| ceph-3 | 4T SATA * 3  800G SSD *1 |

但是想要构建成如下的结构：
[![Alt text](http://www.xuxiaopang.com/images/1478501078240.png)](http://www.xuxiaopang.com/images/1478501078240.png)

这里我们不能把一台主机劈成两半把SATA盘和SSD各分一半，所以就来介绍下CRUSH里面的虚虚实实，什么是实？所有的OSD都是实实在在的节点！什么是虚？除了OSD之外的所有Bucket都是虚的！

也就是说，我们可以建立几个Bucket，分别名叫`ceph-1-sata`,`root-sata`,`ceph-1-ssd`, `root-ssd`，而这些Bucket不需要和实际结构有任何关系，可以看成是我们假想出来的结构，为了达到分层的目的，我们可以假象出任意形式的bucket。

将所有的SATA添加到`ceph-x-sata`节点下，再将`ceph-x-sata`加入到根节点`root-sata`下，同理处理剩下的三个SSD盘。那么现在可以制定两个RULE：

- rule-sata：
  - take(root-sata)
  - choose(3, host)
  - choose(1, osd)
  - emit
- rule-ssd:
  - take(root-ssd)
  - choose(3, host)
  - choose(1, osd)
  - emit

具体的建造指令可以参考之前的[自定义CRUSH一节](http://xuxiaopang.com/2016/10/10/ceph-full-install-el7-jewel/#自定义crush)

这一节想要说明的是，CRUSH里面的节点除了OSD之外的所有bucket都是可以自定义的，并不需要和实际的物理结构相关，但要记住这样做的目的是将OSD分开，从而建立适当的RULE去选择OSD，所以不要把树状结构建立的脱离了实际情况，比如从三个机器上各挑一个OSD然后放到一个自定义的host节点下，虽然可以这样做，但是是没有意义的，说白了要根据自己的数据分布要求去构建OSD树结构，因为CRUSH只认RULE,并不知道你底层的实际结构！！！

甚至，你可以像[这篇文章](http://cephnotes.ksperis.com/blog/2015/02/02/crushmap-example-of-a-hierarchical-cluster-map/)里面一样构建出花式的树状结构！一切都在于你的想象力以及集群的应用需求。

[![Alt text](http://www.xuxiaopang.com/images/1478503163385.png)](http://www.xuxiaopang.com/images/1478503163385.png)

## Ceph中的CRUSH

现在再正式介绍CRUSH算法在Ceph中的存在形式，首先导出一个集群的CRUSH Map:

```
[root@ceph-1 ~]# ceph osd getcrushmap -o /tmp/mapgot crush map from osdmap epoch 67[root@ceph-1 ~]# crushtool -d /tmp/map -o /tmp/map.txt [root@ceph-1 ~]# cat /tmp/map.txt # begin crush maptunable choose_local_tries 0tunable choose_local_fallback_tries 0tunable choose_total_tries 50tunable chooseleaf_descend_once 1tunable straw_calc_version 1# devicesdevice 0 osd.0device 1 osd.1device 2 osd.2device 3 osd.3device 4 osd.4device 5 osd.5device 6 osd.6device 7 osd.7device 8 osd.8# typestype 0 osdtype 1 hosttype 2 chassistype 3 racktype 4 rowtype 5 pdutype 6 podtype 7 roomtype 8 datacentertype 9 regiontype 10 root# bucketshost ceph-2 {	id -2		# do not change unnecessarily	# weight 5.970	alg straw	hash 0	# rjenkins1	item osd.0 weight 1.990	item osd.1 weight 1.990	item osd.2 weight 1.990}host ceph-1 {	id -3		# do not change unnecessarily	# weight 5.970	alg straw	hash 0	# rjenkins1	item osd.3 weight 1.990	item osd.4 weight 1.990	item osd.5 weight 1.990}host ceph-3 {	id -4		# do not change unnecessarily	# weight 5.970	alg straw	hash 0	# rjenkins1	item osd.6 weight 1.990	item osd.7 weight 1.990	item osd.8 weight 1.990}root default {	id -1		# do not change unnecessarily	# weight 17.910	alg straw	hash 0	# rjenkins1	item ceph-2 weight 5.970	item ceph-1 weight 5.970	item ceph-3 weight 5.970}# rulesrule replicated_ruleset {	ruleset 0	type replicated	min_size 1	max_size 10	step take default	step chooseleaf firstn 0 type host	step emit}# end crush map[root@ceph-1 ~]#
```

简单介绍下几个区域的意义：

- `tunable`：还记得`CRUSH_HASH`算法中的`r`变量吗，选择失败的时候这个值经常会自加一，`choose_total_tries 50`这个50就是用来限定总共失败的次数的，CRUSH算法本身是个递归算法，所以给定一个总共失败次数防止算法无限选择失败。那么如果要选出3副本，选失败了50次只选出一个OSD，那么最终结果是？CRUSH将输出`[osd.a， ，]`这样的输出，也就是说只给出一个OSD，一般很少会遇到这种情况，除非你要从一个只有一个host的root下面去选出三个host。
- `devices` : 就是所有的OSD的集合。
- `types`: 就是集群内所有的Bucket+OSD的类型的取值范围，所有的Bucket都要属于这些类型，当然，你可以自己增删这里给出的类型，注意`type`后面的数字必须唯一，因为CRUSH算法在保存类型时不是使用字符串，而是类型对应的数字，所以类型名称在CRUSH眼里是没有意义的。
- `buckets`：就是树上的除了OSD以外的节点，从内容来看可以发现，每个bucket都有向下包含关系，这里看到ID和类型的ID是一样的，CRUSH在底层并不保存节点的名称字符串，而是以数字保存的，值得一提的是，OSD的ID是大于等于零的，bucket的ID是小于零的。还有就是`alg straw`，因为straw是最公平的选择方法，其实还有三个算法(uniform, tree, list)，因为没有straw综合分高，所以就不介绍了。
- `rules`： 最下面的rule区域是我们修改的最多的地方，`replicated_ruleset`这个是这个rule的名称，需要唯一，同样CRUSH只保存这个rule的ID，其ID就是`ruleset 0`这里的`0`,所以需要添加一个rule的时候需要注意名称和ID都不能重复。下面的三个`step`就是RULE的三步走策略，里面具体的参数我就不再赘述，可以[参考官方文档的这一章](http://docs.ceph.com/docs/master/rados/operations/crush-map/)。

还是简单的讲解下这句`step chooseleaf firstn 0 type host`， 实际的RULE里面分为`choose`和`chooseleaf`两种，其中`choose`用于选择多个Bucket，Bucket是最终选择结果，相当于`choose(3, Bucket)`。`chooseleaf`用于选择多个Bucket，并在这些Bucket下各选出一个OSD，OSD是最终选择结果，相当于`choose(3, Bucket) + choose(1, osd)`。`type`后面的`host`就是要选择的Bucket类型。`firstn`后面的`0`,是选择的副本数，`0`等于副本数，也就是3的意思，具体参考官方文档的解释。

所以Sage论文中的图，对应到实际CRUSH的RULE就是：

```
rule Sage_Paper {	ruleset 0	type replicated	min_size 1	max_size 10	step take root	step choose firstn 1 type row	step chooseleaf firstn 0 type cabinet	step emit}
```

## 总结

介绍完了这两步走的核心流程之后，最后再着重强调下`计算`两字，可以发现，从对象计算PG再到PG计算OSD组合，从头到尾都是通过计算得到最终的映射关系的，但是这些计算不论放在客户端还是服务器端，计算的结果都是相同的，因为里面所谓的随机值都是伪随机，只要传入一样的输入得到的输出结果都是一样的，所以Ceph把计算对象存储位置的任务发放给客户端，实际上，客户端在计算完一个对象需要保存的OSD之后，直接和OSD建立通讯，将数据直接存入OSD中，只要集群的Map没有变化，客户端和服务端计算出来的保存位置都是一样的，所以这大大的降低了服务器端的计算压力。

本文没有直接介绍CRUSH算法，而是从`把一个对象存进Ceph`的流程来分析，着重解释了对象到PG的映射，PG到OSD的映射这两个流程，介绍了它们的计算方法。

最后再给一个别人画的计算路径图，仅供理解。
[![Alt text](http://www.xuxiaopang.com/images/1478573403493.png)](http://www.xuxiaopang.com/images/1478573403493.png)

## 参考链接
[大话Ceph--CRUSH那点事儿](http://www.xuxiaopang.com/2016/11/08/easy-ceph-CRUSH/)