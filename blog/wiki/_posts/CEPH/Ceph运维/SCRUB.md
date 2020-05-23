# 1. 基本概念
## 1.1 什么是 Scrub
Scrub 是 Ceph 集群副本进行数据扫描的操作，用于检测副本间数据的一致性，包括 scrub 和 deep-scrub。
其中 scrub 只对元数据信息进行扫描，相对比较快；而 deep-scrub 不仅对元数据进行扫描，还会对存储的数据进行扫描，相对比较慢。

## 1.2 Scrub 默认执行周期
OSD 的 scrub 默认策略是每天到每周（如果集群负载大周期就是一周，如果集群负载小周期就是一天）进行一次，
时间区域默认为全体（0 时-24 时），deep-scrub 默认策略是每周一次。

# 2. 配置
为了避开客户业务高峰时段，建议在晚上 0 点到第二天早上 5 点之间，执行 scrub 操作。

## 2.1 设置标识位
在任一 monitor 节点进行如下操作:
```plain
ceph osd set noscrub
ceph osd set nodeep-scrub
```

## 2.2 临时配置
先通过 tell 方式，让 scrub 时间区间配置立即生效，在任一 monitor 节点进行如下操作:
```plain
ceph tell osd.* injectargs '--osd_scrub_begin_hour 0'
ceph tell osd.* injectargs '--osd_scrub_end_hour 5'
ceph tell mon.* injectargs '--osd_scrub_begin_hour 0'
ceph tell mon.* injectargs '--osd_scrub_end_hour 5'
```

## 2.3 修改配置文件
为了保证集群服务重启或者节点重启依然有效，需要修改 Ceph 集群所有节点的配置文件 /etc/ceph/ceph.conf
```plain
# vim /etc/ceph/ceph.conf
[osd]
osd_scrub_begin_hour = 0    # scrub操作的起始时间为0点
osd_scrub_end_hour = 5      # scrub操作的结束时间为5点#ps: 该时间设置需要参考物理节点的时区设置
 
osd_scrub_chunk_min = 1  #标记每次scrub的最小数
osd_scrub_chunk_max = 1  #标记每次scrub的最大数据块
osd_scrub_sleep = 3  #标记当前scrub结束，执行下次scrub的等待时间，增加该值，会导致scrub变慢，客户端影响反而会减小
```

## 2.4 取消标识位
```plain
ceph osd unset noscrub
ceph osd unset nodeep-scrub
```

