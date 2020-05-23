---
title: Ceph IO 流程及数据分布
toc: true
date: 2020-05-23 11:02:28
tags:
- ceph

---

![rados_io_1.png](https://upload-images.jianshu.io/upload_images/2099201-db0fd6e3e3f49f68.png)

## 1.1 正常 IO 流程图
![ceph_io_2.png](https://upload-images.jianshu.io/upload_images/2099201-2c47144a5118bcf0.png)

**步骤：**
 1. client 创建 cluster handler；
 2. client 读取配置文件；
 3. client 连接上 monitor，获取集群 map 信息；
 4. client 读写 io 根据 crshmap 算法请求对应的主 osd 数据节点；
 5. 主 osd 数据节点同时写入另外两个副本节点数据；
 6. 等待主节点以及另外两个副本节点写完数据状态；
 7. 主节点及副本节点写入状态都成功后，返回给 client，io 写入完成；


## 1.2 新主 IO 流程图
**说明：**
如果新加入的 OSD1 取代了原有的 OSD4 成为 Primary OSD, 由于 OSD1 上未创建 PG , 不存在数据，那么 PG 上的 I/O 无法进行，怎样工作的呢？
![ceph_io_3.png](https://upload-images.jianshu.io/upload_images/2099201-9cc1013f7e3dc8f9.png)

**步骤：**
 1. client 连接 monitor 获取集群 map 信息。
 2. 同时新主 osd1 由于没有 pg 数据会主动上报 monitor 告知让 osd2 临时接替为主。
 3. 临时主 osd2 会把数据全量同步给新主 osd1。
 4. client IO 读写直接连接临时主 osd2 进行读写。
 5. osd2 收到读写 io，同时写入另外两副本节点。
 6. 等待 osd2 以及另外两副本写入成功。
 7. osd2 三份数据都写入成功返回给 client, 此时 client io 读写完毕。
 8. 如果 osd1 数据同步完毕，临时主 osd2 会交出主角色。
 9. osd1 成为主节点，osd2 变成副本。

## 1.3 Ceph IO 算法流程
![ceph_io_4.png](https://upload-images.jianshu.io/upload_images/2099201-b24c72ac8bbf1a19.png)

 1. File 用户需要读写的文件。File->Object 映射：
      a. ino (File 的元数据，File 的唯一 id)。
      b. ono(File 切分产生的某个 object 的序号，默认以 4M 切分一个块大小)。
      c. oid(object id: ino + ono)。

2. Object 是 RADOS 需要的对象。Ceph 指定一个静态 hash 函数计算 oid 的值，将 oid 映射成一个近似均匀分布的伪随机值，然后和 mask 按位相与，得到 pgid。Object->PG 映射：
    a. hash(oid) & mask-> pgid 。
    b. mask = PG 总数 m(m 为 2 的整数幂)-1 。

3. PG(Placement Group),用途是对 object 的存储进行组织和位置映射, (类似于 redis cluster 里面的 slot 的概念) 一个 PG 里面会有很多 object。采用 CRUSH 算法，将 pgid 代入其中，然后得到一组 OSD。PG->OSD 映射： 
    a. CRUSH(pgid)->(osd1,osd2,osd3) 。


## 1.4 Ceph IO 伪代码流程
```plain
locator = object_name
obj_hash =  hash(locator)
pg = obj_hash % num_pg
osds_for_pg = crush(pg)    # returns a list of osds
primary = osds_for_pg[0]
replicas = osds_for_pg[1:]
```

## 1.5 Ceph RBD IO 流程
![ceph_rbd_io.png](https://upload-images.jianshu.io/upload_images/2099201-ed51d7d8050dbf64.png)

**步骤：**
 1. 客户端创建一个 pool，需要为这个 pool 指定 pg 的数量。
 2. 创建 pool/image rbd 设备进行挂载。
 3. 用户写入的数据进行切块，每个块的大小默认为 4M，并且每个块都有一个名字，名字就是 object+序号。
 4. 将每个 object 通过 pg 进行副本位置的分配。
 5. pg 根据 cursh 算法会寻找 3 个 osd，把这个 object 分别保存在这三个 osd 上。
 6. osd 上实际是把底层的 disk 进行了格式化操作，一般部署工具会将它格式化为 xfs 文件系统。
 7. object 的存储就变成了存储一个文 rbd0.object1.file。


## 1.6 Ceph RBD IO 框架图
![ceph_rbd_io1.png](https://upload-images.jianshu.io/upload_images/2099201-850a745bc0f44494.png)

**客户端写数据 osd 过程：**
 1. 采用的是 librbd 的形式，使用 librbd 创建一个块设备，向这个块设备中写入数据。
 2. 在客户端本地同过调用 librados 接口，然后经过 pool，rbd，object、pg 进行层层映射,在 PG 这一层中，可以知道数据保存在哪 3 个 OSD 上，这 3 个 OSD 分为主从的关系。
 3. 客户端与 primay OSD 建立 SOCKET 通信，将要写入的数据传给 primary OSD，由 primary OSD 再将数据发送给其他 replica OSD 数据节点。

## 1.7 Ceph Pool 和 PG 分布情况
![ceph_pool_pg.png](https://upload-images.jianshu.io/upload_images/2099201-d49d90ae6a918ef2.png)

**说明：**
 - pool 是 ceph 存储数据时的逻辑分区，它起到 namespace 的作用。
 - 每个 pool 包含一定数量(可配置)的 PG。
 - PG 里的对象被映射到不同的 Object 上。
 - pool 是分布到整个集群的。
 - pool 可以做故障隔离域，根据不同的用户场景不一进行隔离。


## 1.8 Ceph 数据扩容 PG 分布
**场景数据迁移流程：**
 - 现状 3 个 OSD, 4 个 PG
 - 扩容到 4 个 OSD, 4 个 PG

**现状：**
![ceph_recory_1.png](https://upload-images.jianshu.io/upload_images/2099201-4dda9e2648dabe90.png)

**扩容后：**
![ceph_io_recry2.png](https://upload-images.jianshu.io/upload_images/2099201-9e324e87c6d086f3.png)

**说明**
每个 OSD 上分布很多 PG, 并且每个 PG 会自动散落在不同的 OSD 上。如果扩容那么相应的 PG 会进行迁移到新的 OSD 上，保证 PG 数量的均衡。

---

以下内容选自https://www.yuque.com/guoyujian/qw24na/oriucg

![img](https://cdn.nlark.com/yuque/0/2018/png/95634/1538658969124-c998c9bf-3806-46e8-bff9-ef61f8bd7c8c.png)

**无论使用哪种存储方式（对象、块、挂载），存储的数据都会被切分成对象（Objects）**。Objects size 大小可以由管理员调整，通常为 2M 或 4M。每个对象都会有一个唯一的 OID，由 ino 与 ono 生成，虽然这些名词看上去很复杂，其实相当简单。ino 即是文件的 File ID，用于在全局唯一标示每一个文件，而 ono 则是分片的编号。比如：一个文件 FileID 为 A，它被切成了两个对象，一个对象编号 0，另一个编号 1，那么这两个文件的 oid 则为 A0 与 A1。Oid 的好处是可以唯一标示每个不同的对象，并且存储了对象与文件的从属关系。由于 ceph 的所有数据都虚拟成了整齐划一的对象，所以在读写时效率都会比较高。

但是对象并不会直接存储进 OSD 中，因为对象的 size 很小，在一个大规模的集群中可能有几百到几千万个对象。这么多对象光是遍历寻址，速度都是很缓慢的；并且如果将对象直接通过某种固定映射的哈希算法映射到 osd 上，当这个 osd 损坏时，对象无法自动迁移至其他 osd 上面（因为映射函数不允许）。为了解决这些问题，**ceph 引入了归置组的概念，即 PG。**

**PG 是一个逻辑概念，我们 linux 系统中可以直接看到对象，但是无法直接看到 PG**。它在数据寻址时类似于数据库中的索引：每个对象都会固定映射进一个 PG 中，所以当我们要寻找一个对象时，只需要先找到对象所属的 PG，然后遍历这个 PG 就可以了，无需遍历所有对象。而且在数据迁移时，也是以 PG 作为基本单位进行迁移，ceph 不会直接操作对象。

对象时如何映射进 PG 的？还记得 OID 么？首先使用静态 hash 函数对 OID 做 hash 取出特征码，用特征码与 PG 的数量去模，得到的序号则是 PGID。由于这种设计方式，PG 的数量多寡直接决定了数据分布的均匀性，所以合理设置的 PG 数量可以很好的提升 CEPH 集群的性能并使数据均匀分布。

**最后 PG 会根据管理员设置的副本数量进行复制，然后通过 crush 算法存储到不同的 OSD 节点上（其实是把 PG 中的所有对象存储到节点上），第一个 osd 节点即为主节点，其余均为从节点。**



![img](https://cdn.nlark.com/yuque/0/2018/png/95634/1538659118685-db2fc1dc-9bb4-4153-890a-eeb8e8680d39.png)

上图中更好的诠释了 ceph 数据流的存储过程，数据无论是从三中接口哪一种写入的，最终都要切分成对象存储到底层的 RADOS 中。逻辑上通过算法先映射到 PG 上，最终存储近 OSD 节点里。图中除了之前介绍过的概念之外多了一个 pools 的概念。

**Pool 是管理员自定义的命名空间，像其他的命名空间一样，用来隔离对象与 PG**。我们在调用 API 存储即使用对象存储时，需要指定对象要存储进哪一个 POOL 中。**除了隔离数据，我们也可以分别对不同的 POOL 设置不同的优化策略，比如副本数、数据清洗次数、数据块及对象大小等。**



**Pool 与 PG 的关系：**

![img](https://cdn.nlark.com/yuque/0/2018/png/95634/1538707082413-e2847300-dc31-42ce-abd0-05aa9eff400c.png)

一个 Pool 里设置的 PG 数量是预先设置的，PG 的数量不是随意设置，需要根据 OSD 的个数及副本策略来确定：

Total PGs = ((Total_number_of_OSD * 100) / max_replication_count) / pool_count
线上尽量不要更改 PG 的数量，PG 的数量的变更将导致整个集群动起来（各个 OSD 之间 copy 数据），大量数据均衡期间读写性能下降严重。
    

**Ceph 的读写操作采用主从模型，客户端要读写数据时，只能向对象所对应的主 osd 节点发起请求**。主节点在接受到写请求时，会同步的向从 OSD 中写入数据。当所有的 OSD 节点都写入完成后，主节点才会向客户端报告写入完成的信息。因此保证了主从节点数据的高度一致性。而读取的时候，客户端也只会向主 osd 节点发起读请求，并不会有类似于数据库中的读写分离的情况出现，这也是出于强一致性的考虑。由于所有写操作都要交给主 osd 节点来处理，所以在数据量很大时，性能可能会比较慢，为了克服这个问题以及让 ceph 能支持事物，**每个 osd 节点都包含了一个 journal 文件。**

　Journal 的作用类似于 mysql innodb 引擎中的事物日志系统。当有突发的大量写入操作时，ceph 可以先把一些零散的，随机的 IO 请求保存到缓存中进行合并，然后再统一向内核发起 IO 请求。这样做效率会比较高，但是一旦 osd 节点崩溃，缓存中的数据就会丢失，所以数据在还未写进硬盘中时，都会记录到 journal 中，**当 osd 崩溃后重新启动时，会自动尝试从 journal 恢复因崩溃丢失的缓存数据。**因此 journal 的 io 是非常密集的，而且由于一个数据要 io 两次，很大程度上也损耗了硬件的 io 性能，所以通常在生产环境中**，使用 ssd 来单独存储 journal 文件以提高 ceph 读写性能。**

journal 默认大小为 5G，也就说每创建一个 osd 节点，还没使用就要被 journal 占走 5G 的空间。这个值是可以调整的，具体大小要依 osd 的总大小而定。