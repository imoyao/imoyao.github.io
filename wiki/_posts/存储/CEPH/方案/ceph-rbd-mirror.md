---
title: ceph-rbd-mirror 灾备方案
toc: true
date: 2020-05-23 11:02:28
tags:
- ceph

---
## 1.1 基本原理
![image.png](https://upload-images.jianshu.io/upload_images/2099201-ecfd775a52afa2ee.png)

RBD Mirror 原理其实和 MySQL 的主从同步原理非常类似，前者基于 journaling，后者基于 binlog，简单地说就是利用日志进行回放(replay)：通过在存储系统中增加 Mirror 组件，采用异步复制的方式，实现异地备份。(此处的 journal 是指 Ceph RBD 的 journal，而不是 OSD 的 journal)

该能力利用了 RBD image 的日志特性，以确保集群间的副本崩溃一致性。镜像功能需要在同伴集群（ peer clusters ）中的每一个对应的 pool 上进行配置，可设定自动备份某个存储池内的所有 images 或仅备份 images 的一个特定子集。 rbd-mirror 守护进程负责从远端集群拉取 image 的更新，并写入本地集群的对应 image 中。

当 RBD Journal 功能打开后，所有的数据更新请求会先写入 RBD Journal，然后后台线程再把数据从 Journal 区域刷新到对应的 image 区域。RBD journal 提供了比较完整的日志记录、读取、变更通知以及日志回收和空间释放等功能，可以认为是一个分布式的日志系统。

## 1.2 工作流程
![image.png](https://upload-images.jianshu.io/upload_images/2099201-7594cafde2621a95.png)

1、当接收到一个写入请求后，I/O 会先写入主集群的 Image Journal
2、Journal 写入成功后，通知客户端
3、客户端得到响应后，开始写入 image
3、备份集群的 mirror 进程发现主集群的 Journal 有更新后，从主集群的 Journal 读取数据，写入备份集群（和上面序号一样，是因为这两个过程同时发生）
4、备份集群写入成功后，会更新主集群 Journal 中的元数据，表示该 I/O 的 Journal 已经同步完成
5、主集群会定期检查，删除已经写入备份集群的 Journal 数据。
以上就是一个 rbd-mirror 工作周期内的流程，在现有的 Jewel 版本中 30s 为一次工作周期，暂时不能改变这个周期时间。

## 1.3 优点
1、当副本在异地的情况下，减少了单个集群不同节点间的数据写入延时；

2、减少本地集群或异地集群由于意外断电导致的数据丢失。

## 1.4 单向备份与双向备份
双向备份：两个集群之间互相同步，两个集群都要运行 rbd-mirror 进程。
单向备份：分为主集群和从集群，只在从集群运行 rbd-mirror 进程，主集群的修改会自动同步到从集群。

## 1.5 安装须知
 - RBD 镜像功能需要 Ceph Jewel 或更新的发行版本。
 - 目前 Jewel 版本只支持一对一，不支持一对多。
 - 两个集群 (local 和 remote) 需要能够互通。
 - RBD 需要开启 journal 特性， 启动后会记录 image 的事件。

# 2. mirroring 模式
mirroring 是基于存储池进行的 peer，ceph 支持两种模式的镜像，根据镜像来划分有：

**存储池模式**

*   一个存储池内的所有镜像都会进行备份

**镜像模式**

*   只有指定的镜像才会进行备份

[参见](http://wiki.intra.xiaojukeji.com/pages/viewpage.action?pageId=117858533)

## 2.1 存储池模式
### 2.1.1 创建存储池
创建一个用于测试的存储池：
```plain
#local集群
ceph osd pool create test_pool 100 100 replicated --cluster=local
pool 'test_pool' created
 
#remote集群
ceph osd pool create test_pool 100 100 replicated --cluster=remote
pool 'test_pool' created
```
### 2.1.2 启用存储池模式
开启存储池 rbdmirror 的镜像功能： 
```plain
#local集群
rbd  mirror pool enable test_pool pool --cluster=local
 
#remote集群
rbd mirror pool enable test_pool pool --cluster=remote
```
### 2.1.3 创建 RBD
主集群创建一个测试用的 RBD：
```plain
rbd create test_pool/test_image --size=1024 --cluster=local
``` 
### 2.1.4 主集群开启 jounaling 特性
启动后会才会记录 image 的事件，才可以被 rbd-mirror 检测到并同步到从集群：
```plain
rbd feature enable test_pool/test_image exclusive-lock
rbd feature enable test_pool/test_image journaling
```
### 2.1.5. 增加同伴集群
把 local 和 remote 设为同伴，这个是为了让 rbd-mirror 进程找到它 peer 的集群的存储池：
```plain
rbd mirror pool peer add test_pool client.admin@remote --cluster=local
 
rbd mirror pool peer add test_pool client.admin@local --cluster=remote
 
#如果需要删除peer 语法：
rbd mirror pool peer remove <pool-name> <peer-uuid>
```
查看 peer 的情况：
```plain
rbd mirror pool info --pool=test_pool --cluster=local
Mode: pool
Peers:
UUID NAME CLIENT
f0929e85-259d-450b-917e-9eb231b7e43b remote client.admin
 
 
rbd mirror pool info --pool=test_pool --cluster=remote
Mode: pool
Peers:
UUID NAME CLIENT
5851ba6a-e383-4ef0-9b9d-5ae34c9518a6 local client.admin
```
### 2.1.6 开启 rbd-mirror 的同步进程
a. 先用调试模式启动进程看看情况，在 remote 的机器上执行
```plain
#remote:
rbd-mirror -d --setuser ceph --setgroup ceph --cluster remote -i admin
```
b. 如果确认没问题就用服务来控制启动
```plain
#remote
vim /usr/lib/systemd/system/ceph-rbd-mirror@.service
 
#修改
Environment=CLUSTER=remote
```
c. 在 remote 机器上启动
```plain
systemctl start ceph-rbd-mirror@admin
ps -ef|grep rbd
ceph 4325 1 1 17:59 ? 00:00:00 /usr/bin/rbd-mirror -f --cluster remote --id admin --setuser ceph --setgroup ceph
```
### 2.1.7 检查同步结果
a. 查询 local 集群镜像的同步的状态
```plain
#local
rbd mirror image status test_pool/test_image --cluster remote
test_image:
 global_id: dabdbbed-7c06-4e1d-b860-8dd104509565
 state: up+replaying
 description: replaying, master_position=[object_number=2, tag_tid=2, entry_tid=3974], mirror_position=[object_number=3, tag_tid=2, entry_tid=2583], entries_behind_master=1391
 last_update: 2017-01-22 17:54:22
```
b. 检查数据是否同步到 remote 集群
```plain
#remote
rbd info test_pool/test_image
```

## 2.2 镜像模式
### 2.2.1 主集群开启 jounaling 特性
启动后会才会记录 image 的事件，才可以被 rbd-mirror 检测到并同步到从集群
```plain
#local
rbd feature enable test_pool/test_image exclusive-lock
rbd feature enable test_pool/test_image journaling
```
### 2.2.2 开启存储池的 mirror 的模式
```plain
#local:
rbd mirror pool enable test_pool image
 
#remote:
ceph osd pool create test_pool 100 100 replicated --cluster=remote
pool 'rbdmirror' created
 
rbd mirror pool enable test_pool image
```
### 2.2.3 开启 image 的 mirror
```plain
#local
rbd mirror image enable test_pool/test_image
Mirroring enabled
 
rbd info test_pool/test_image --cluster=local
rbd image 'test_image':
 size 10240 MB in 2560 objects
 order 22 (4096 kB objects)
 block_name_prefix: rbd_data.105774b0dc51
 format: 2
 features: layering, exclusive-lock, journaling
 flags:
 create_timestamp: Wed Dec 13 16:46:08 2017
 journal: 105774b0dc51
 mirroring state: enabled
 mirroring global id: 013f9e35-9d08-40fc-bf24-1e11a07a0910
 mirroring primary: true
```
### 2.2.4 增加同伴集群
把 local 和 remote 设为同伴，这个是为了让 rbd-mirror 进程找到它 peer 的集群的存储池：
```plain
rbd mirror pool peer add test_pool client.admin@remote --cluster=local
 
rbd mirror pool peer add test_pool client.admin@local --cluster=remote
 
#如果需要删除peer 语法：
rbd mirror pool peer remove <pool-name> <peer-uuid>
```
查看 peer 的情况：
```plain
rbd mirror pool info --pool=test_pool --cluster=local
Mode: pool
Peers:
UUID NAME CLIENT
f0929e85-259d-450b-917e-9eb231b7e43b remote client.admin
 
 
rbd mirror pool info --pool=test_pool --cluster=remote
Mode: pool
Peers:
UUID NAME CLIENT
5851ba6a-e383-4ef0-9b9d-5ae34c9518a6 local client.admin
```
### 2.2.5 开启 rbd-mirror 的同步进程
a. 先用调试模式启动进程看看情况，在 remote 的机器上执行
```plain
#remote:
rbd-mirror -d --setuser ceph --setgroup ceph --cluster remote -i admin
```
b. 如果确认没问题就用服务来控制启动
```plain
#remote
vim /usr/lib/systemd/system/ceph-rbd-mirror@.service
 
#修改
Environment=CLUSTER=remote
```
c. 在 remote 机器上启动
```plain
systemctl start ceph-rbd-mirror@admin
ps -ef|grep rbd
ceph 4325 1 1 17:59 ? 00:00:00 /usr/bin/rbd-mirror -f --cluster remote --id admin --setuser ceph --setgroup ceph
```
### 2.2.6 检查同步结果
a. 查询 local 集群镜像的同步的状态
```plain
#local
rbd mirror image status test_pool/test_image --cluster remote
test_image:
 global_id: dabdbbed-7c06-4e1d-b860-8dd104509565
 state: up+replaying
 description: replaying, master_position=[object_number=2, tag_tid=2, entry_tid=3974], mirror_position=[object_number=3, tag_tid=2, entry_tid=2583], entries_behind_master=1391
 last_update: 2017-01-22 17:54:22
```
b. 检查数据是否同步到 remote 集群
```plain
#remote
rbd info test_pool/test_image
```

# 3. 测试对比报告
## 3.1 单主集群性能
### 3.1.1 rbd 性能测试
1. 顺序读写
//block size 是 4M，30 个线程并发
测试结果：30 线程并发，带宽：935 MB/s  平均 IOPS：228.33
```plain
rbd bench-write test_image  --io-threads 30  --pool=test_pool   --io-pattern seq --io-total 17199730000 --io-size 4096000
elapsed:    18  ops:     4200  ops/sec:   228.33  bytes/sec: 935243763.72
```
2. 随机读写
//block size 是 4M，30 个线程并发
测试结果：30 线程并发，带宽：936 MB/s  平均 IOPS： 228.57
```plain
rbd bench-write test_image  --io-threads 30  --pool=test_pool   --io-pattern rand --io-total 17199730000 --io-size 4096000
elapsed:    18  ops:     4200  ops/sec:   228.57  bytes/sec: 936229596.77
```
## 3.2 主备集群性能
### 3.2.1 rbd 性能测试
1. 顺序读写
//block size 是 4M，30 个线程并发
测试结果：30 线程并发，带宽：182 MB/s 平均 IOPS：44.53
```plain
rbd bench-write test_image  --io-threads 30  --pool=test_pool   --io-pattern seq --io-total 17199730000 --io-size 4096000
elapsed:    94  ops:     4200  ops/sec:    44.53  bytes/sec: 182382108.66
```
2. 随机读写
//block size 是 4M，30 个线程并发
测试结果：30 线程并发，带宽：149 MB/s  平均 IOPS： 36.50
```plain
rbd bench-write test_image  --io-threads 30  --pool=test_pool   --io-pattern rand --io-total 17199730000 --io-size 4096000
elapsed:   115  ops:     4200  ops/sec:    36.50  bytes/sec: 149499469.69
```
## 3.3 测试结果
通过测试结果可以看出启用 rbd-mirror 会导致主集群性能下降 5 倍多。
工具 |  集群模式 | 块大小 | 并发数 | 顺序读写 | 随机读写 |
---|---|---|---|---|---|
rbd bench-write | 单主集群 | 4M | 30 | 带宽：935 MB/s <br/>平均 IOPS：228.33 | 带宽：936 MB/s <br/>平均 IOPS： 228.57
rbd bench-write | 主备集群 | 4M | 30 | 带宽：182 MB/s <br/>平均 IOPS：44.53 | 带宽：149 MB/s <br/>平均 IOPS： 36.50

# 4. 分析原因
## 4.1 journal 流程
1. 当 RBD Journal 功能打开后，所有的数据更新请求会先写入 Image Journal
2. 写入成功后，通知客户端
3. 客户端得到响应后，开始写 image
4. 备份集群的 mirror 进程发现主集群的 Journal 有更新后，从主集群的 Journal 读取数据，写入备份集群
5. 备份集群写入成功后，会更新主集群 Journal 中的元数据，表示该 I/O 的 Journal 已经同步完成

## 4.2 优化
 - Use a small SSD/NVMe-backed pool for journals
     - ‘rbd journal pool = <fast pool name>’
 - Batch multiple events into a single journal append 
     - ‘rbd journal object flush age = <seconds>’
 - Increase journal data width to match queue depth 
    - ‘rbd journal splay width = <number of objects>’ 
 - Future work: potentially parallelize journal append + image write between write barriers
```plain
1. rbd journal pool 功能没实现
sudo ceph daemon osd.0 config set rbd_journal_pool = test_pool3
{
    "error": "error setting 'rbd_journal_pool' to '= test_pool3': (38) Function not implemented"
}
 
2. 调整参数从10-100，效果不明显
rbd_journal_object_flush_age = 100
rbd_journal_splay_width = 100
```
## 4.3 官方待改进
### 4.3.1 引入一致性组
1. journaling 可以看做是另一个 rbd 的 image（一些 rados 对象），一般情况下，先写日志，然后返回客户端，然后被写入底层的 rbd 的 image，出于性能考虑，这个 journal 可以跟它的镜像不在一个存储池当中。

2. 目前是一个 image 一个 journal，最近应该会沿用这个策略，直到 ceph 引入一致性组。关于一致性组的概念就是一组卷，然后用的是一个 RBD image。可以在所有的组中执行快照操作，有了一致性的保证，所有的卷就都在一致的状态。

3.当一致性组实现的时候，我们就可以用一个 journal 来管理所有的 RBD 的镜像，可以给一个已经存在 image 开启 journal，ceph 将会将你的镜像做一个快照，然后对快照做一个复制，然后开启 journal，这都是后台执行的一个任务可以启用和关闭单个镜像或者存储池的 mirror 功能，

如果启用了 journal 功能，那么每个镜像将会被复制可以使用 rbd mirror pool enable 启用它。

### 4.3.2 并行写

1. Future work: potentially parallelize journal append + image write between write barriers

2. 参考[官方文档](https://events.static.linuxfound.org/sites/events/files/slides/Disaster%20Recovery%20and%20Ceph%20Block%20Storage-%20Introducing%20Multi-Site%20Mirroring_0.pdf)如下：
![image.png](https://upload-images.jianshu.io/upload_images/2099201-a6a5353f44dc4c15.png)

3. 官方类似问题：[https://www.spinics.net/lists/ceph-users/msg31676.html](https://www.spinics.net/lists/ceph-users/msg31676.html)
![image.png](https://upload-images.jianshu.io/upload_images/2099201-27c244104df33dbd.png)

## 4.4 结论
由于核心流程就是先写日志，然后写 image 需要写两份的逻辑，所以导致性能就会有损失。
根据官方的参数优化也没有明显的效果，建议等待官方更新 features。
