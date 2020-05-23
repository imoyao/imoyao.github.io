---
title: Ceph IO流程及数据分布
toc: true
date: 2020-05-23 11:02:28
tags:
- ceph
categories: CEPH
---

![rados_io_1.png](https://upload-images.jianshu.io/upload_images/2099201-db0fd6e3e3f49f68.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

## 1.1 正常IO流程图
![ceph_io_2.png](https://upload-images.jianshu.io/upload_images/2099201-2c47144a5118bcf0.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

**步骤：**
 1. client 创建cluster handler；
 2. client 读取配置文件；
 3. client 连接上monitor，获取集群map信息；
 4. client 读写io 根据crshmap 算法请求对应的主osd数据节点；
 5. 主osd数据节点同时写入另外两个副本节点数据；
 6. 等待主节点以及另外两个副本节点写完数据状态；
 7. 主节点及副本节点写入状态都成功后，返回给client，io写入完成；


## 1.2 新主IO流程图
**说明：**
如果新加入的OSD1取代了原有的 OSD4成为 Primary OSD, 由于 OSD1 上未创建 PG , 不存在数据，那么 PG 上的 I/O 无法进行，怎样工作的呢？
![ceph_io_3.png](https://upload-images.jianshu.io/upload_images/2099201-9cc1013f7e3dc8f9.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

**步骤：**
 1. client连接monitor获取集群map信息。
 2. 同时新主osd1由于没有pg数据会主动上报monitor告知让osd2临时接替为主。
 3. 临时主osd2会把数据全量同步给新主osd1。
 4. client IO读写直接连接临时主osd2进行读写。
 5. osd2收到读写io，同时写入另外两副本节点。
 6. 等待osd2以及另外两副本写入成功。
 7. osd2三份数据都写入成功返回给client, 此时client io读写完毕。
 8. 如果osd1数据同步完毕，临时主osd2会交出主角色。
 9. osd1成为主节点，osd2变成副本。

## 1.3 Ceph IO算法流程
![ceph_io_4.png](https://upload-images.jianshu.io/upload_images/2099201-b24c72ac8bbf1a19.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

 1. File用户需要读写的文件。File->Object映射：
      a. ino (File的元数据，File的唯一id)。
      b. ono(File切分产生的某个object的序号，默认以4M切分一个块大小)。
      c. oid(object id: ino + ono)。

2. Object是RADOS需要的对象。Ceph指定一个静态hash函数计算oid的值，将oid映射成一个近似均匀分布的伪随机值，然后和mask按位相与，得到pgid。Object->PG映射：
    a. hash(oid) & mask-> pgid 。
    b. mask = PG总数m(m为2的整数幂)-1 。

3. PG(Placement Group),用途是对object的存储进行组织和位置映射, (类似于redis cluster里面的slot的概念) 一个PG里面会有很多object。采用CRUSH算法，将pgid代入其中，然后得到一组OSD。PG->OSD映射： 
    a. CRUSH(pgid)->(osd1,osd2,osd3) 。


## 1.4 Ceph IO伪代码流程
```
locator = object_name
obj_hash =  hash(locator)
pg = obj_hash % num_pg
osds_for_pg = crush(pg)    # returns a list of osds
primary = osds_for_pg[0]
replicas = osds_for_pg[1:]
```

## 1.5 Ceph RBD IO流程
![ceph_rbd_io.png](https://upload-images.jianshu.io/upload_images/2099201-ed51d7d8050dbf64.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

**步骤：**
 1. 客户端创建一个pool，需要为这个pool指定pg的数量。
 2. 创建pool/image rbd设备进行挂载。
 3. 用户写入的数据进行切块，每个块的大小默认为4M，并且每个块都有一个名字，名字就是object+序号。
 4. 将每个object通过pg进行副本位置的分配。
 5. pg根据cursh算法会寻找3个osd，把这个object分别保存在这三个osd上。
 6. osd上实际是把底层的disk进行了格式化操作，一般部署工具会将它格式化为xfs文件系统。
 7. object的存储就变成了存储一个文rbd0.object1.file。


## 1.6 Ceph RBD IO框架图
![ceph_rbd_io1.png](https://upload-images.jianshu.io/upload_images/2099201-850a745bc0f44494.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

**客户端写数据osd过程：**
 1. 采用的是librbd的形式，使用librbd创建一个块设备，向这个块设备中写入数据。
 2. 在客户端本地同过调用librados接口，然后经过pool，rbd，object、pg进行层层映射,在PG这一层中，可以知道数据保存在哪3个OSD上，这3个OSD分为主从的关系。
 3. 客户端与primay OSD建立SOCKET 通信，将要写入的数据传给primary OSD，由primary OSD再将数据发送给其他replica OSD数据节点。

## 1.7 Ceph Pool和PG分布情况
![ceph_pool_pg.png](https://upload-images.jianshu.io/upload_images/2099201-d49d90ae6a918ef2.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

**说明：**
 - pool是ceph存储数据时的逻辑分区，它起到namespace的作用。
 - 每个pool包含一定数量(可配置)的PG。
 - PG里的对象被映射到不同的Object上。
 - pool是分布到整个集群的。
 - pool可以做故障隔离域，根据不同的用户场景不一进行隔离。


## 1.8 Ceph 数据扩容PG分布
**场景数据迁移流程：**
 - 现状3个OSD, 4个PG
 - 扩容到4个OSD, 4个PG

**现状：**
![ceph_recory_1.png](https://upload-images.jianshu.io/upload_images/2099201-4dda9e2648dabe90.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

**扩容后：**
![ceph_io_recry2.png](https://upload-images.jianshu.io/upload_images/2099201-9e324e87c6d086f3.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

**说明**
每个OSD上分布很多PG, 并且每个PG会自动散落在不同的OSD上。如果扩容那么相应的PG会进行迁移到新的OSD上，保证PG数量的均衡。

---

以下内容选自https://www.yuque.com/guoyujian/qw24na/oriucg

![img](https://cdn.nlark.com/yuque/0/2018/png/95634/1538658969124-c998c9bf-3806-46e8-bff9-ef61f8bd7c8c.png)

**无论使用哪种存储方式（对象、块、挂载），存储的数据都会被切分成对象（Objects）**。Objects size大小可以由管理员调整，通常为2M或4M。每个对象都会有一个唯一的OID，由ino与ono生成，虽然这些名词看上去很复杂，其实相当简单。ino即是文件的File ID，用于在全局唯一标示每一个文件，而ono则是分片的编号。比如：一个文件FileID为A，它被切成了两个对象，一个对象编号0，另一个编号1，那么这两个文件的oid则为A0与A1。Oid的好处是可以唯一标示每个不同的对象，并且存储了对象与文件的从属关系。由于ceph的所有数据都虚拟成了整齐划一的对象，所以在读写时效率都会比较高。

但是对象并不会直接存储进OSD中，因为对象的size很小，在一个大规模的集群中可能有几百到几千万个对象。这么多对象光是遍历寻址，速度都是很缓慢的；并且如果将对象直接通过某种固定映射的哈希算法映射到osd上，当这个osd损坏时，对象无法自动迁移至其他osd上面（因为映射函数不允许）。为了解决这些问题，**ceph引入了归置组的概念，即PG。**

**PG是一个逻辑概念，我们linux系统中可以直接看到对象，但是无法直接看到PG**。它在数据寻址时类似于数据库中的索引：每个对象都会固定映射进一个PG中，所以当我们要寻找一个对象时，只需要先找到对象所属的PG，然后遍历这个PG就可以了，无需遍历所有对象。而且在数据迁移时，也是以PG作为基本单位进行迁移，ceph不会直接操作对象。

对象时如何映射进PG的？还记得OID么？首先使用静态hash函数对OID做hash取出特征码，用特征码与PG的数量去模，得到的序号则是PGID。由于这种设计方式，PG的数量多寡直接决定了数据分布的均匀性，所以合理设置的PG数量可以很好的提升CEPH集群的性能并使数据均匀分布。

**最后PG会根据管理员设置的副本数量进行复制，然后通过crush算法存储到不同的OSD节点上（其实是把PG中的所有对象存储到节点上），第一个osd节点即为主节点，其余均为从节点。**



![img](https://cdn.nlark.com/yuque/0/2018/png/95634/1538659118685-db2fc1dc-9bb4-4153-890a-eeb8e8680d39.png)

上图中更好的诠释了ceph数据流的存储过程，数据无论是从三中接口哪一种写入的，最终都要切分成对象存储到底层的RADOS中。逻辑上通过算法先映射到PG上，最终存储近OSD节点里。图中除了之前介绍过的概念之外多了一个pools的概念。

**Pool是管理员自定义的命名空间，像其他的命名空间一样，用来隔离对象与PG**。我们在调用API存储即使用对象存储时，需要指定对象要存储进哪一个POOL中。**除了隔离数据，我们也可以分别对不同的POOL设置不同的优化策略，比如副本数、数据清洗次数、数据块及对象大小等。**



**Pool与PG的关系：**

![img](https://cdn.nlark.com/yuque/0/2018/png/95634/1538707082413-e2847300-dc31-42ce-abd0-05aa9eff400c.png)

一个Pool里设置的PG数量是预先设置的，PG的数量不是随意设置，需要根据OSD的个数及副本策略来确定：

Total PGs = ((Total_number_of_OSD * 100) / max_replication_count) / pool_count
线上尽量不要更改PG的数量，PG的数量的变更将导致整个集群动起来（各个OSD之间copy数据），大量数据均衡期间读写性能下降严重。
    

**Ceph的读写操作采用主从模型，客户端要读写数据时，只能向对象所对应的主osd节点发起请求**。主节点在接受到写请求时，会同步的向从OSD中写入数据。当所有的OSD节点都写入完成后，主节点才会向客户端报告写入完成的信息。因此保证了主从节点数据的高度一致性。而读取的时候，客户端也只会向主osd节点发起读请求，并不会有类似于数据库中的读写分离的情况出现，这也是出于强一致性的考虑。由于所有写操作都要交给主osd节点来处理，所以在数据量很大时，性能可能会比较慢，为了克服这个问题以及让ceph能支持事物，**每个osd节点都包含了一个journal文件。**

　Journal的作用类似于mysql innodb引擎中的事物日志系统。当有突发的大量写入操作时，ceph可以先把一些零散的，随机的IO请求保存到缓存中进行合并，然后再统一向内核发起IO请求。这样做效率会比较高，但是一旦osd节点崩溃，缓存中的数据就会丢失，所以数据在还未写进硬盘中时，都会记录到journal中，**当osd崩溃后重新启动时，会自动尝试从journal恢复因崩溃丢失的缓存数据。**因此journal的io是非常密集的，而且由于一个数据要io两次，很大程度上也损耗了硬件的io性能，所以通常在生产环境中**，使用ssd来单独存储journal文件以提高ceph读写性能。**

journal默认大小为5G，也就说每创建一个osd节点，还没使用就要被journal占走5G的空间。这个值是可以调整的，具体大小要依osd的总大小而定。