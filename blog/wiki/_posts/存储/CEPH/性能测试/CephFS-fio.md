---
title: CephFS 异常测试
toc: true
date: 2020-05-23 11:02:28
tags:
- ceph

---

# 1. Cephfs 异常测试方案
CephFS 允许客户端缓存 metadata 30s，所以这里测试对 MDS stop/start 的时间间隔取为：2s，10s，60s。

| 测试组件 | 测试场景 | 挂载方式 | 测试方法 | 
|:---:|:---:|:---:|:---:|
| MDS | 单 MDS | fuse/kernel | 单个 MDS 挂掉情况 2s/10s/60s IO 情况 |
| | 主从 MDS 时 | fuse/kernel | 单主挂掉情况 2s/10s/60s IO 情况 |
| | 主从 MDS 时 | fuse/kernel | 主从同时挂掉情况 2s/10s/60s IO 情况 |
| MON | 单个 MON | fuse/kernel | 单个 MON 挂掉情况 2s/10s/60s IO 情况 |
| | 所有 MON | fuse/kernel | 所有 MON 挂掉情况 2s/10s/60s IO 情况 |
| OSD | 单个 OSD | fuse/kernel | 单个 OSD 挂掉情况 2s/10s/60s IO 情况	|
| | 集群一半 OSD |	fuse/kernel | 一半 OSD 挂掉情况 2s/10s/60s IO 情况 |
| | 集群所有 OSD 挂掉 | fuse/kernel | 所有 OSD 挂掉情况 2s/10s/60s IO 情况 |

# 2. 测试环境
 - **mon：**  ceph-xxx-osd01.ys, ceph-xxx-osd02.ys, ceph-xxx-osd03.ys
 - **osd：** ceph-xxx-osd01.ys, ceph-xxx-osd02.ys, ceph-xxx-osd03.ys
 - **mds：** ceph-xxx-osd04.ys, ceph-xxx-osd05.ys

# 3. 测试工具
## fio
fio 也是我们性能测试中常用的一个工具，详细介绍 Google 之。

**我们测试中固定配置：**
-filename=tstfile   指定测试文件的 name
-size=20G           指定测试文件的 size 为 20G
-direct=1           指定测试 IO 为 DIRECT IO
-thread             指定使用 thread 模式
-name=fio-tst-name  指定 job name

**测试 bandwidth 时：**
-ioengine=libaio/sync
-bs=512k/1M/4M/16M
-rw=write/read
-iodepth=64 -iodepth_batch=8 -iodepth_batch_complete=8

**测试 iops 时：**
-ioengine=libaio
-bs=4k
-runtime=300
-rw=randwrite/randread
-iodepth=64 -iodepth_batch=1 -iodepth_batch_complete=1

# 4. 测试步骤
## 4.1 MDS
### 4.1.1 单 MDS 挂掉
不需要测试，目前都是主从结构。

### 4.1.2 主从 MDS 主挂掉
```plain
#测试多个文件
#!/bin/bash
while true
do
  curtime=`date --date='0 days ago' +%s`
  fio -filename=/test/$curtime -direct=1 -iodepth 1 -thread -rw=randwrite -ioengine=libaio -bs=4m -size=20G -runtime=1 -group_reporting -name=mytest
done
 
#测试单个文件
fio -filename-testfile -size=20G -direct=1 -thread -name=/test/fio-test-name -ioengine=libaio -bs=512k/1M/4M/16M -rw=rw  -write_bw_log=rw -iodepth=64 -iodepth_batch=8 -iodepth_batch_complete=8
```
### 4.1.3 结论
| 挂载方式 |  写入方式 | 故障描述 |
|:---:|:---:|:---:|
| fuse | 单个文件 | 停掉主 MDS, io 会出现稍微的抖动 |
| | 多个文件 | 停掉主 MDS,会发生 1-2 秒的 io 夯住 |
| kernel | 单个文件 | 停掉主 MDS, io 会出现稍微的抖动 |
| | 多个文件 |  停掉主 MDS,会发生 1-2 秒的 io 夯住 |

**单个文件：**
![image.png](https://upload-images.jianshu.io/upload_images/2099201-b5f7a0431d4e73be.png)

### 4.1.4 主从 MDS 都挂掉
```plain
#测试多个文件
#!/bin/bash
while true
do
  curtime=`date --date='0 days ago' +%s`
  fio -filename=/test/$curtime -direct=1 -iodepth 1 -thread -rw=randwrite -ioengine=libaio -bs=4m -size=20G -runtime=1 -group_reporting -name=mytest
done
 
#测试单个文件
fio -filename-testfile -size=20G -direct=1 -thread -name=/test/fio-test-name -ioengine=libaio -bs=512k/1M/4M/16M -rw=rw  -write_bw_log=rw -iodepth=64 -iodepth_batch=8 -iodepth_batch_complete=8
 
#18:19:24 fio
#18:19:28 sh mdsstop.sh
```
### 4.1.5 结论
| 挂载方式 |  写入方式 | 故障描述 |
|:---:|:---:|:---:|
| fuse | 单个文件 | 停掉主从 MDS,40s 左右 io 夯死 |
| | 多个文件 | 停掉主从 MDS, io 立马夯死 |
| kernel | 单个文件 | 停掉主从 MDS,40s 左右 io 夯死 |
| |多个文件 |停掉主从 MDS, io 立马夯死 |

**单个文件模式：**
![image.png](https://upload-images.jianshu.io/upload_images/2099201-d61d5b8fe18ea85f.png)

## 4.2 MON
### 4.2.1 单个 MON 挂掉
```plain
#测试多个文件
#!/bin/bash
while true
do
  curtime=`date --date='0 days ago' +%s`
  fio -filename=/test/$curtime -direct=1 -iodepth 1 -thread -rw=randwrite -ioengine=libaio -bs=4m -size=20G -runtime=1 -group_reporting -name=mytest
done
 
#测试单个文件
fio -filename-testfile -size=20G -direct=1 -thread -name=/test/fio-test-name -ioengine=libaio -bs=512k/1M/4M/16M -rw=rw  -write_bw_log=rw -iodepth=64 -iodepth_batch=8 -iodepth_batch_complete=8
```
### 4.2.2 结论
| 挂载方式 |  写入方式 | 故障描述 |
|:---:|:---:|:---:|
| fuse | 单个文件 | 停掉单个 MON，客户端写入无影响. |
| | 多个文件 | 停掉单个 MON，客户端写入无影响. |
| kernel | 单个文件 | 停掉单个 MON，客户端写入无影响. |
| | 多个文件 | 停掉单个 MON，客户端写入无影响. |

### 4.2.3 所有 MON 挂掉
```plain
#测试多个文件
#!/bin/bash
while true
do
  curtime=`date --date='0 days ago' +%s`
  fio -filename=/test/$curtime -direct=1 -iodepth 1 -thread -rw=randwrite -ioengine=libaio -bs=4m -size=20G -runtime=1 -group_reporting -name=mytest
done
 
#测试单个文件
fio -filename-testfile -size=20G -direct=1 -thread -name=/test/fio-test-name -ioengine=libaio -bs=512k/1M/4M/16M -rw=rw  -write_bw_log=rw -iodepth=64 -iodepth_batch=8 -iodepth_batch_complete=8
```
### 4.2.4 结论
| 挂载方式 |  写入方式 | 故障描述 |
|:---:|:---:|:---:|
| fuse | 单个文件 | 所有的 MON 都挂掉,会在 60 秒左右 IO 夯死 |
| | 多个文件 | 所有的 MON 挂掉,会在挂掉后立刻 IO 夯死 |
| kernel | 单个文件 | 所有的 MON 都挂掉,会在 60 秒左右 IO 夯死 |
| | 多个文件 | 所有的 MON 挂掉，会在挂掉后 10 秒左右 IO 夯死. |

**单个文件模式(内核模式)：**
![image.png](https://upload-images.jianshu.io/upload_images/2099201-3c32ba07c96d4621.png)


**单个文件模式(fuse 模式)：**
![image.png](https://upload-images.jianshu.io/upload_images/2099201-7a71576adc5120d7.png)

## 4.3 OSD
### 4.3.1 单个 OSD 挂掉
```plain
#测试多个文件
#!/bin/bash
while true
do
  curtime=`date --date='0 days ago' +%s`
  fio -filename=/test/$curtime -direct=1 -iodepth 1 -thread -rw=randwrite -ioengine=libaio -bs=4m -size=20G -runtime=1 -group_reporting -name=mytest
done
 
#测试单个文件
fio -filename-testfile -size=20G -direct=1 -thread -name=/test/fio-test-name -ioengine=libaio -bs=512k/1M/4M/16M -rw=rw  -write_bw_log=rw -iodepth=64 -iodepth_batch=8 -iodepth_batch_complete=8
```
### 4.3.2 结论
| 挂载方式 |  写入方式 | 故障描述 |
|:---:|:---:|:---:|
| fuse | 单个文件 | 停掉一个 osd，MDS 客户端的写入无影响 |
| | 多个文件 | 停掉一个 osd，MDS 客户端的写入无影响. |
| kernel | 单个文件 | 停掉一个 osd，MDS 客户端的写入无影响 |
| | 多个文件 | 停掉一个 osd，MDS 客户端的写入无影响. |

### 4.3.3 集群一半 OSD 挂掉
```plain
#测试多个文件
#!/bin/bash
while true
do
  curtime=`date --date='0 days ago' +%s`
  fio -filename=/test/$curtime -direct=1 -iodepth 1 -thread -rw=randwrite -ioengine=libaio -bs=4m -size=20G -runtime=1 -group_reporting -name=mytest
done
 
#测试单个文件
fio -filename-testfile -size=20G -direct=1 -thread -name=/test/fio-test-name -ioengine=libaio -bs=512k/1M/4M/16M -rw=rw  -write_bw_log=rw -iodepth=64 -iodepth_batch=8 -iodepth_batch_complete=8
```
### 4.3.4 结论
| 挂载方式 |  写入方式 | 故障描述 |
|:---:|:---:|:---:|
| fuse | 单个文件 | 集群 2/3 的 osd 挂掉,MDS 客户端立刻会夯死. |
| | 多个文件 | 集群 2/3 的 osd 挂掉,MDS 客户端立刻会夯死. |
| kernel  | 单个文件	 | 集群 2/3 的 osd 挂掉,MDS 客户端立刻会夯死. |
| | 多个文件 | 集群 2/3 的 osd 挂掉,MDS 客户端立刻会夯死. |

### 4.3.5 集群所有 OSD 挂掉
```plain

#!/bin/bash
while true
do
  curtime=`date --date='0 days ago' +%s`
  fio -filename=/test/$curtime -direct=1 -iodepth 1 -thread -rw=randwrite -ioengine=libaio -bs=4m -size=20G -runtime=1 -group_reporting -name=mytest
done
 
#测试单个文件
fio -filename-testfile -size=20G -direct=1 -thread -name=/test/fio-test-name -ioengine=libaio -bs=512k/1M/4M/16M -rw=rw  -write_bw_log=rw -iodepth=64 -iodepth_batch=8 -iodepth_batch_complete=8
```
### 4.3.6 结论
| 挂载方式 |  写入方式 | 故障描述 |
|:---:|:---:|:---:|
| fuse | 单个文件 | 集群所有的 osd 挂掉,MDS 客户端会立刻夯死 |
|  | 多个文件 | 集群所有的 osd 挂掉,MDS 客户端会立刻夯死. |
| kernel | 单个文件	| 集群所有的 osd 挂掉,MDS 客户端会立刻夯死 |
| |多个文件 | 集群所有 的 osd 挂掉,MDS 客户端立刻会夯死. |
