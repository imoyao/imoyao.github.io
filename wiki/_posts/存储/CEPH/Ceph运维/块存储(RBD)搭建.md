# 1. 管理存储池
## 1.1  创建存储池
``
PG数量的预估
集群中单个池的PG数计算公式如下：PG 总数 = (OSD 数 * 100) / 最大副本数 / 池数 (结果必须舍入到最接近2的N次幂的值)
``

```shell
# ceph osd pool create {pool-name} {pg-num} [{pgp-num}] [replicated] [crush-ruleset-name]
 
# ceph osd pool create test_pool 512 512 replicated
pool 'test_pool' created

# 默认初始化RBD pool
# rbd pool init <pool-name>
```
## 1.2  删除存储池
```shell
# ceph osd pool delete {pool-name} [{pool-name} --yes-i-really-really-mean-it]
 
# ceph osd pool delete test_pool test_pool --yes-i-really-really-mean-it
pool 'test_pool' removed
```
## 1.3 重命名存储池
```shell
# ceph osd pool rename {current-pool-name} {new-pool-name}
 
# ceph osd pool rename test_pool test_new_pool
pool 'test_pool' renamed to 'test_new_pool'
```
## 1.4 查看存储池列表
```shell
# ceph osd lspools
1 rbd,2 test_data,3 test_metadata,5 test,6 benmark_test,7 .rgw.root,8 default.rgw.control,9 default.rgw.meta,10 default.rgw.log,11 default.rgw.buckets.index,12 web-services,13 test_pool,
```
# 2. 管理块设备镜像
## 2.1 创建块设备镜像
```shell
# rbd create --size {megabytes} {pool-name}/{image-name}
# 如果pool_name不指定，则默认的pool是rbd。 下面的命令将创建一个10GB大小的块设备：
 
# rbd create --size 10240 test_image -p test_pool
```
## 2.2 删除块设备镜像和恢复块设备镜像
```shell
# rbd rm {pool-name}/{image-name}
 
# rbd rm test_pool/test_image

# 恢复块设备镜像
rbd trash restore {pool-name}/{image-id}
```
## 2.3 查看块设备镜像
```shell
# rbd info {pool-name}/{image-name}
 
# rbd info test_pool/test_image
rbd image 'test_image':
    size 10240 MB in 2560 objects
    order 22 (4096 kB objects)
    block_name_prefix: rbd_data.172e42ae8944a
    format: 2
    features: layering
    flags:
    create_timestamp: Wed Nov  8 17:50:34 2017
```
## 2.4 将块设备映射到系统内核
```shell
# rbd map {image name} --name client.admin -m {monitor node ip or hostname} --cluster {cluster name}
 
# rbd map test_pool/test_image
/dev/rbd1
 
#如果打印：
rbd: sysfs write failed
RBD image feature set mismatch. You can disable features unsupported by the kernel with "rbd feature disable".
In some cases useful info is found in syslog - try "dmesg | tail" or so.
rbd: map failed: (6) No such device or address
 
 
#表示当前系统不支持feature，禁用当前系统内核不支持的feature：
rbd feature disable test_pool/test_image exclusive-lock, object-map, fast-diff, deep-flatten
 
dmesg
image uses unsupported features: 0x40
不支持特性 0x40 = 64，也就是不支持特性 journaling
 
#rbd-nbd用户态
yum install  kmod-nbd
yum  install rbd-nbd
sudo rbd-nbd map test_pool/test_image

# 若有如下报错 missing required protocol features missing 400000000000000，则表明当前内核缺少ceph当前版本所需特性，可做如下处理（正式环境中不建议如此，最好在搭建集群前升级内核）：
ceph osd crush show-tunables
ceph osd crush tunables hammer
ceph osd crush reweight-all
```

> 注意：在进行 map 时遇到一个问题：server 部署在 CentOS 7.7，内核版本 3.10.发行版自带；client CentOS7.3，kernel4.14，自行升级过内核，map 失败 feature set mismatch, my 106b84a842a42 < server's 40106b84a842a42, missing 400000000000000，使用发行版自带的 3.10 内核，map 成功，原因尚未知；

## RBD 特性解析

RBD 支持的特性，及具体 BIT 值的计算如下

| 属性 | 功能 | BIT 码 |
|---|---|---|
| layering | 支持分层 | 1 |
| striping | 支持条带化 v2 | 2 |
| exclusive-lock | 支持独占锁 | 4 |
| object-map | 支持对象映射（依赖 exclusive-lock ） | 8 |
| fast-diff	| 快速计算差异（依赖 object-map ）| 16 |
| deep-flatten | 支持快照扁平化操作 | 32 |
| journaling | 支持记录 IO 操作（依赖独占锁）| 64 |


## 2.5  列出已映射块设备和取消块设备映射到系统内核
```shell
# rbd showmapped
id pool image snap device    
0  test test  -    /dev/rbd0 

# rbd unmap {image-name}
 
# rbd unmap test_pool/test_image
```
## 2.6 格式化块设备镜像
```shell
# mkfs.ext4 /dev/rbd1
 
# mkfs.xfs -f  /dev/nbd0
```
# 3. 挂载文件系统
```shell
# mkdir /mnt/ceph-block-device
# mount /dev/rbd0/ /mnt/ceph-block-device
# cd /mnt/ceph-block-device
```
