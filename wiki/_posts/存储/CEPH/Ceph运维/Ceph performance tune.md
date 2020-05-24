---
title: first-wiki
toc: true
date: 2020-05-23 11:02:28
tags:

---
# [Ceph 性能优化总结](https://www.jianshu.com/p/dd572541df2e)

1. 硬件层面
   硬件规划
   SSD 选择
   BIOS 设置
2. 软件层面
   Linux OS
   Ceph Configurations
   PG Number 调整
   CRUSH Map
   其他因素

------

## 硬件优化

#### 1. 硬件规划

Processor
ceph-osd 进程在运行过程中会消耗 CPU 资源，所以一般会为每一个 ceph-osd 进程绑定一个 CPU 核上。当然如果你使用 EC 方式，可能需要更多的 CPU 资源。

ceph-mon 进程并不十分消耗 CPU 资源，所以不必为 ceph-mon 进程预留过多的 CPU 资源。

ceph-msd 也是非常消耗 CPU 资源的，所以需要提供更多的 CPU 资源。

内存
ceph-mon 和 ceph-mds 需要 2G 内存，每个 ceph-osd 进程需要 1G 内存，当然 2G 更好。

网络规划
万兆网络现在基本上是跑 Ceph 必备的，网络规划上，也尽量考虑分离 cilent 和 cluster 网络。

#### 2. SSD 选择

硬件的选择也直接决定了 Ceph 集群的性能，从成本考虑，一般选择 SATA SSD 作为 Journal，Intel® SSD DC S3500 Series 基本是目前看到的方案中的首选。400G 的规格 4K 随机写可以达到 11000 IOPS。如果在预算足够的情况下，推荐使用 PCIE SSD，性能会得到进一步提升，但是由于 Journal 在向数据盘写入数据时 Block 后续请求，所以 Journal 的加入并未呈现出想象中的性能提升，但是的确会对 Latency 有很大的改善。

如何确定你的 SSD 是否适合作为 SSD Journal，可以参考 SÉBASTIEN HAN 的 Ceph: How to Test if Your SSD Is Suitable as a Journal Device?，这里面他也列出了常见的 SSD 的测试结果，从结果来看 SATA SSD 中，Intel S3500 性能表现最好。

#### 3. BIOS 设置

Hyper-Threading(HT)
基本做云平台的，VT 和 HT 打开都是必须的，超线程技术(HT)就是利用特殊的硬件指令，把两个逻辑内核模拟成两个物理芯片，让单个处理器都能使用线程级并行计算，进而兼容多线程操作系统和软件，减少了 CPU 的闲置时间，提高的 CPU 的运行效率。

关闭节能
关闭节能后，对性能还是有所提升的，所以坚决调整成性能型(Performance)。当然也可以在操作系统级别进行调整，详细的调整过程请参考链接，但是不知道是不是由于 BIOS 已经调整的缘故，所以在 CentOS 6.6 上并没有发现相关的设置。

```bash
for CPUFREQ in /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor; do [ -f $CPUFREQ ] || continue; echo -n performance > $CPUFREQ; done
```

NUMA

简单来说，NUMA 思路就是将内存和 CPU 分割为多个区域，每个区域叫做 NODE,然后将 NODE 高速互联。 node 内 cpu 与内存访问速度快于访问其他 node 的内存，NUMA 可能会在某些情况下影响 ceph-osd。解决的方案，一种是通过 BIOS 关闭 NUMA，另外一种就是通过 cgroup 将 ceph-osd 进程与某一个 CPU Core 以及同一 NODE 下的内存进行绑定。但是第二种看起来更麻烦，所以一般部署的时候可以在系统层面关闭 NUMA。CentOS 系统下，通过修改/etc/grub.conf 文件，添加 numa=off 来关闭 NUMA。

```cpp
kernel /vmlinuz-2.6.32-504.12.2.el6.x86_64 ro root=UUID=870d47f8-0357-4a32-909f-74173a9f0633 rd_NO_LUKS rd_NO_LVM LANG=en_US.UTF-8 rd_NO_MD SYSFONT=latarcyrheb-sun16 crashkernel=auto  KEYBOARDTYPE=pc KEYTABLE=us rd_NO_DM   biosdevname=0 numa=off
```

## 软件优化

#### 1. Linux OS

Kernel pid max

```ruby
echo 4194303 > /proc/sys/kernel/pid_max
```

Jumbo frames, 交换机端需要支持该功能，系统网卡设置才有效果

```undefined
ifconfig eth0 mtu 9000
```

永久设置

```bash
echo "MTU=9000" | tee -a /etc/sysconfig/network-script/ifcfg-eth0
/etc/init.d/networking restart
```

read_ahead, 通过数据预读并且记载到随机访问内存方式提高磁盘读操作，查看默认值

```cpp
cat /sys/block/sda/queue/read_ahead_kb
```

根据一些 Ceph 的公开分享，8192 是比较理想的值

```bash
echo "8192" > /sys/block/sda/queue/read_ahead_kb
```

swappiness, 主要控制系统对 swap 的使用，这个参数的调整最先见于 UnitedStack 公开的文档中，猜测调整的

原因主要是使用 swap 会影响系统的性能。

```bash
echo "vm.swappiness = 0" | tee -a /etc/sysctl.conf
```

I/O Scheduler，关于 I/O Scheculder 的调整网上已经有很多资料，这里不再赘述，简单说 SSD 要用 noop，SATA/SAS 使用 deadline。

```bash
echo "deadline" > /sys/block/sd[x]/queue/scheduler
echo "noop" > /sys/block/sd[x]/queue/scheduler
```

cgroup 这方面的文章好像比较少，昨天在和 Ceph 社区交流过程中，Jan Schermer 说准备把生产环境中的一些脚本贡献出来，但是暂时还没有，他同时也列举了一些使用 cgroup 进行隔离的原因。

不在 process 和 thread 在不同的 core 上移动(更好的缓存利用)
减少 NUMA 的影响
网络和存储控制器影响 - 较小
通过限制 cpuset 来限制 Linux 调度域(不确定是不是重要但是是最佳实践)
如果开启了 HT，可能会造成 OSD 在 thread1 上，KVM 在 thread2 上，并且是同一个 core。Core 的延迟和性能取决于其他一个线程做什么。

#### 2. Ceph Configurations

###### [global]

| 参数名          | 描述                                           | 默认值 | 建议值           |
| --------------- | ---------------------------------------------- | :----- | :--------------- |
| public network  | 客户端访问网络                                 |        | 192.168.100.0/24 |
| cluster network | 集群网络                                       |        | 192.168.1.0/24   |
| max open files  | 如果设置了该选项，Ceph 会设置系统的 max open fds | 0      | 131072           |

查看系统最大文件打开数可以使用命令

```undefined
cat /proc/sys/fs/file-max
```

###### [osd] - filestore

| 参数名                               | 描述                                                         | 默认值    | 建议值      |
| ------------------------------------ | ------------------------------------------------------------ | :-------- | :---------- |
| filestore xattr use omap             | 为 XATTRS 使用 object map，EXT4 文件系统时使用，XFS 或者 btrfs 也可以使用 | false     | true        |
| filestore max sync interval          | 从日志到数据盘最大同步间隔(seconds)                          | 5         | 15          |
| filestore min sync interval          | 从日志到数据盘最小同步间隔(seconds)                          | 0.1       | 10          |
| filestore queue max ops              | 数据盘最大接受的操作数                                       | 500       | 25000       |
| filestore queue max bytes            | 数据盘一次操作最大字节数(bytes)                              | 100 << 20 | 10485760    |
| filestore queue committing max ops   | 数据盘能够 commit 的操作数                                     | 500       | 5000        |
| filestore queue committing max bytes | 数据盘能够 commit 的最大字节数(bytes)                          | 100 << 20 | 10485760000 |
| filestore op threads                 | 并发文件系统操作数                                           | 2         | 32          |

- 调整 omap 的原因主要是 EXT4 文件系统默认仅有 4K
- filestore queue 相关的参数对于性能影响很小，参数调整不会对性能优化有本质上提升

###### [osd] - journal

| 参数名                    | 描述                                     | 默认值   | 建议值      |
| ------------------------- | ---------------------------------------- | :------- | :---------- |
| osd journal size          | OSD 日志大小(MB)                          | 5120     | 20000       |
| journal max write bytes   | journal 一次性写入的最大字节数(bytes)     | 10 << 20 | 1073714824  |
| journal max write entries | journal 一次性写入的最大记录数            | 100      | 10000       |
| journal queue max ops     | journal 一次性最大在队列中的操作数        | 500      | 50000       |
| journal queue max bytes   | journal 一次性最大在队列中的字节数(bytes) | 10 << 20 | 10485760000 |

- Ceph OSD Daemon stops writes and synchronizes the journal with the filesystem, allowing Ceph OSD Daemons to trim operations from the journal and reuse the space.
- 上面这段话的意思就是，Ceph OSD 进程在往数据盘上刷数据的过程中，是停止写操作的。

###### [osd] - osd config tuning

| 参数名                      | 描述                                     | 默认值             | 建议值                                       |
| --------------------------- | ---------------------------------------- | :----------------- | :------------------------------------------- |
| osd max write size          | OSD 一次可写入的最大值(MB)                | 90                 | 512                                          |
| osd client message size cap | 客户端允许在内存中的最大数据(bytes)      | 524288000          | 2147483648                                   |
| osd deep scrub stride       | 在 Deep Scrub 时候允许读取的字节数(bytes)  | 524288             | 131072                                       |
| osd op threads              | OSD 进程操作的线程数                      | 2                  | 8                                            |
| osd disk threads            | OSD 密集型操作例如恢复和 Scrubbing 时的线程 | 1                  | 4                                            |
| osd map cache size          | 保留 OSD Map 的缓存(MB)                    | 500                | 1024                                         |
| osd map cache bl size       | OSD 进程在内存中的 OSD Map 缓存(MB)         | 50                 | 128                                          |
| osd mount options xfs       | Ceph OSD xfs Mount 选项                   | rw,noatime,inode64 | rw,noexec,nodev,noatime,nodiratime,nobarrier |

增加 osd op threads 和 disk threads 会带来额外的 CPU 开销

###### [osd] - recovery tuning

| 参数名                   | 描述                                         | 默认值 | 建议值 |
| ------------------------ | -------------------------------------------- | :----- | :----- |
| osd recovery op priority | 恢复操作优先级，取值 1-63，值越高占用资源越高 | 10     | 4      |
| osd recovery max active  | 同一时间内活跃的恢复请求数                   | 15     | 10     |
| osd max backfills        | 一个 OSD 允许的最大 backfills 数                 | 10     | 4      |

###### [osd] - client tuning

| 参数名                  | 描述                                                         |  默认值  |  建议值   |
| ----------------------- | ------------------------------------------------------------ | :------: | :-------: |
| rbd cache               | RBD 缓存                                                      |   true   |   true    |
| rbd cache size          | RBD 缓存大小(bytes)                                           | 33554432 | 268435456 |
| rbd cache max dirty     | 缓存为 write-back 时允许的最大 dirty 字节数(bytes)，如果为 0，使用 write-through | 25165824 | 134217728 |
| rbd cache max dirty age | 在被刷新到存储盘前 dirty 数据存在缓存的时间(seconds)           |    1     |     5     |

关闭 Debug

#### 3. PG Number

PG 和 PGP 数量一定要根据 OSD 的数量进行调整，计算公式如下，但是最后算出的结果一定要接近或者等于一个 2 的指数。

```undefined
Total PGs = (Total_number_of_OSD * 100) / max_replication_count
```

例如 15 个 OSD，副本数为 3 的情况下，根据公式计算的结果应该为 500，最接近 512，所以需要设定该 pool(volumes)的 pg_num 和 pgp_num 都为 512.

```bash
ceph osd pool set volumes pg_num 512
ceph osd pool set volumes pgp_num 512
```

#### 4. CRUSH Map

CRUSH 是一个非常灵活的方式，CRUSH MAP 的调整取决于部署的具体环境，这个可能需要根据具体情况进行分析，这里面就不再赘述了。

#### 5. 其他因素的影响

`ceph osd perf`
生产过程中一个由于在集群中存在一个性能不好的磁盘，导致整个集群性能下降的 case。通过 osd perf 可以提供磁盘 latency 的状况，同时在运维过程中也可以作为监控的一个重要指标，很明显在下面的例子中，OSD 8 的磁盘延时较长，所以需要考虑将该 OSD 剔除出集群：

```undefined
ceph osd perf
osd fs_commit_latency(ms) fs_apply_latency(ms)
  0                    14                   17
  1                    14                   16
  2                    10                   11
  3                     4                    5
  4                    13                   15
  5                    17                   20
  6                    15                   18
  7                    14                   16
  8                   299                  329
```

#### ceph.conf

```csharp
[global]#全局设置
fsid = xxxxxxxxxxxxxxx                           #集群标识ID 
mon initial members = node1, node2, node3               #初始monitor (由创建monitor命令而定)
mon host = 10.0.1.1,10.0.1.2,10.0.1.3            #monitor IP 地址
auth cluster required = cephx                    #集群认证
auth service required = cephx                           #服务认证
auth client required = cephx                            #客户端认证
osd pool default size = 2                             #默认副本数设置 默认是3
osd pool default min size = 1                           #PG 处于 degraded 状态不影响其 IO 能力,min_size是一个PG能接受IO的最小副本数
public network = 10.0.1.0/24                            #公共网络(monitorIP段) 
cluster network = 10.0.2.0/24                           #集群网络
max open files = 131072                                 #默认0#如果设置了该选项，Ceph会设置系统的max open fds

##############################################################
[mon]
mon data = /var/lib/ceph/mon/ceph-$id
mon clock drift allowed = 1                             #默认值0.05#monitor间的clock drift
mon osd min down reporters = 13                         #默认值1#向monitor报告down的最小OSD数
mon osd down out interval = 600      #默认值300      #标记一个OSD状态为down和out之前ceph等待的秒数
##############################################################
[osd]
osd data = /var/lib/ceph/osd/ceph-$id
osd journal size = 20000 #默认5120                          #osd journal大小
osd journal = /var/lib/ceph/osd/$cluster-$id/journal    #osd journal 位置
osd mkfs type = xfs                                     #格式化系统类型
osd max write size = 512 #默认值90                   #OSD一次可写入的最大值(MB)
osd client message size cap = 2147483648   #默认值100    #客户端允许在内存中的最大数据(bytes)
osd deep scrub stride = 131072                      #默认值524288         #在Deep Scrub时候允许读取的字节数(bytes)
osd op threads = 16                                         #默认值2                   #并发文件系统操作数
osd disk threads = 4                                         #默认值1                   #OSD密集型操作例如恢复和Scrubbing时的线程
osd map cache size = 1024                              #默认值500                 #保留OSD Map的缓存(MB)
osd map cache bl size = 128                            #默认值50                #OSD进程在内存中的OSD Map缓存(MB)
osd mount options xfs = "rw,noexec,nodev,noatime,nodiratime,nobarrier"   #默认值rw,noatime,inode64  #Ceph OSD xfs Mount选项
osd recovery op priority = 2                 #默认值10              #恢复操作优先级，取值1-63，值越高占用资源越高
osd recovery max active = 10              #默认值15              #同一时间内活跃的恢复请求数 
osd max backfills = 4                           #默认值10                  #一个OSD允许的最大backfills数
osd min pg log entries = 30000           #默认值3000           #修建PGLog是保留的最大PGLog数
osd max pg log entries = 100000         #默认值10000         #修建PGLog是保留的最大PGLog数
osd mon heartbeat interval = 40           #默认值30            #OSD ping一个monitor的时间间隔（默认30s）
ms dispatch throttle bytes = 1048576000 #默认值 104857600 #等待派遣的最大消息数
objecter inflight ops = 819200                   #默认值1024           #客户端流控，允许的最大未发送io请求数，超过阀值会堵塞应用io，为0表示不受限
osd op log threshold = 50                            #默认值5                  #一次显示多少操作的log
osd crush chooseleaf type = 0                       #默认值为1              #CRUSH规则用到chooseleaf时的bucket的类型
filestore xattr use omap = true                         #默认false#为XATTRS使用object map，EXT4文件系统时使用，XFS或者btrfs也可以使用
filestore min sync interval = 10                          #默认0.1#从日志到数据盘最小同步间隔(seconds)
filestore max sync interval = 15                          #默认5#从日志到数据盘最大同步间隔(seconds)
filestore queue max ops = 25000                        #默认500#数据盘最大接受的操作数
filestore queue max bytes = 1048576000            #默认100   #数据盘一次操作最大字节数(bytes
filestore queue committing max ops = 50000       #默认500     #数据盘能够commit的操作数
filestore queue committing max bytes = 10485760000 #默认100 #数据盘能够commit的最大字节数(bytes)
filestore split multiple = 8                                               #默认值2         #前一个子目录分裂成子目录中的文件的最大数量
filestore merge threshold = 40                                        #默认值10       #前一个子类目录中的文件合并到父类的最小数量
filestore fd cache size = 1024                                         #默认值128              #对象文件句柄缓存大小
filestore op threads = 32                                                  #默认值2                    #并发文件系统操作数
journal max write bytes = 1073714824                           #默认值1048560    #journal一次性写入的最大字节数(bytes)
journal max write entries = 10000                                   #默认值100         #journal一次性写入的最大记录数
journal queue max ops = 50000                                      #默认值50            #journal一次性最大在队列中的操作数
journal queue max bytes = 10485760000                       #默认值33554432   #journal一次性最大在队列中的字节数(bytes)
##############################################################
[client]
rbd cache = true       #默认值 true      #RBD缓存
rbd cache size = 335544320       #默认值33554432           #RBD缓存大小(bytes)
rbd cache max dirty = 134217728     #默认值25165824      #缓存为write-back时允许的最大dirty字节数(bytes)，如果为0，使用write-through
rbd cache max dirty age = 30     #默认值1                #在被刷新到存储盘前dirty数据存在缓存的时间(seconds)
rbd cache writethrough until flush = false     #默认值true  #该选项是为了兼容linux-2.6.32之前的virtio驱动，避免因为不发送flush请求，数据不回写
#设置该参数后，librbd会以writethrough的方式执行io，直到收到第一个flush请求，才切换为writeback方式。
rbd cache max dirty object = 2     #默认值0              #最大的Object对象数，默认为0，表示通过rbd cache size计算得到，librbd默认以4MB为单位对磁盘Image进行逻辑切分
#每个chunk对象抽象为一个Object；librbd中以Object为单位来管理缓存，增大该值可以提升性能
rbd cache target dirty = 235544320   #默认值16777216    #开始执行回写过程的脏数据大小，不能超过 rbd_cache_max_dirty
```