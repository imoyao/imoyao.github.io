## 1. 说明
 **故障现象描述：**
```plain
Flapping OSD's when RGW buckets have millions of objects
● Possible causes
○ The first issue here is when RGW buckets have millions of objects their
bucket index shard RADOS objects become very large with high
number OMAP keys stored in leveldb. Then operations like deep-scrub,
bucket index listing etc takes a lot of time to complete and this triggers
OSD's to flap. If sharding is not used this issue become worse because
then only one RADOS index objects will be holding all the OMAP keys.
```
RGW 的 index 数据以 omap 形式存储在 OSD 所在节点的 leveldb 中，当单个 bucket 存储的 Object 数量高达百万数量级的时候，deep-scrub 和 bucket list 一类的操作将极大的消耗磁盘资源，导致对应 OSD 出现异常，如果不对 bucket 的 index 进行 shard 切片操作(shard 切片实现了将单个 bucket index 的 LevelDB 实例水平切分到多个 OSD 上)，数据量大了以后很容易出事。

```plain
○ The second issue is when you have good amount of DELETEs it causes
loads of stale data in OMAP and this triggers leveldb compaction all the
time which is single threaded and non optimal with this kind of workload
and causes osd_op_threads to suicide because it is always compacting
hence OSD’s starts flapping.
```
RGW 在处理大量 DELETE 请求的时候，会导致底层 LevelDB 频繁进行数据库 compaction(数据压缩，对磁盘性能损耗很大)操作，而且刚好整个 compaction 在 LevelDB 中又是单线程处理，很容易到达 osdopthreads 超时上限而导致 OSD 自杀。

```plain
● Possible causes contd ...
○ OMAP backend is leveldb in jewel and older clusters. Any luminous
clusters which were upgraded from older releases have leveldb as
OMAP backend.
```
jewel 以及之前的版本的 OMAP 都是以 LevelDB 作为存储引擎，如果是从旧版本升级到最新的 luminous，那么底层 OMAP 仍然是 LevelDB。
```plain
○ All new luminous clusters have default OMAP backend as rocksdb
which is great because rocksdb has multithreaded compaction and in
Ceph we use 8 compaction thread by default and many other enhanced
features as compare to leveldb.
```
最新版本的 Luminous 开始，OMAP 底层的存储引擎换成了 rocksDB，rocksDB 采用多线程方式进行 compaction(默认 8 个），所以 rocksdb 在 compaction 效率上要比 LevelDB 强很多。

## 2. 根因跟踪
当 bucket index 所在的 OSD omap 过大的时候，一旦出现异常导致 OSD 进程崩溃，这个时候就需要进行现场"救火"，用最快的速度恢复 OSD 服务。

先确定对应 OSD 的 OMAP 大小，这个过大会导致 OSD 启动的时候消耗大量时间和资源去加载 levelDB 数据，导致 OSD 无法启动（超时自杀）。

特别是这一类 OSD 启动需要占用非常大的内存消耗，一定要注意预留好内存。（物理内存 40G 左右，不行用 swap 顶上）
![image.png](https://upload-images.jianshu.io/upload_images/2099201-48d1c1c182999c28.png)

## 3. 修复方式
### 3.1 临时解决方案
1. 关闭集群 scrub, deep-scrub 提升集群稳定性
```plain
$ ceph osd set noscrub
$ ceph osd set nodeep-scrub
```
2. 调高 timeout 参数，减少 OSD 自杀的概率
```plain
osd_op_thread_timeout = 90 #default is 15
osd_op_thread_suicide_timeout = 2000 #default is 150
If filestore op threads are hitting timeout
filestore_op_thread_timeout = 180 #default is 60
filestore_op_thread_suicide_timeout = 2000 #default is 180
Same can be done for recovery thread also.
osd_recovery_thread_timeout = 120 #default is 30
osd_recovery_thread_suicide_timeout = 2000 #default is 300
```

3. 手工压缩 LevelDB OMAP
在可以停 OSD 的情况下，可以对 OSD 进行 compact 操作，推荐在 ceph 0.94.6 以上版本，低于这个版本有 bug。 [https://github.com/ceph/ceph/pull/7645/files](https://github.com/ceph/ceph/pull/7645/files)
```plain
○ The third temporary step could be taken if OSD's have very large OMAP
directories you can verify it with command: du -sh /var/lib/ceph/osd/ceph-$id/current/omap, then do manual leveldb compaction for OSD's.
■ ceph tell osd.$id compact or
■ ceph daemon osd.$id compact or
■ Add leveldb_compact_on_mount = true in [osd.$id] or [osd] section
and restart the OSD.
■ This makes sure that it compacts the leveldb and then bring the
OSD back up/in which really helps.
```
```plain
#开启noout操作
$ ceph osd set noout
 
#停OSD服务
$ systemctl stop ceph-osd@<osd-id>
 
#在ceph.conf中对应的[osd.id]加上下面配置
leveldb_compact_on_mount = true
 
#启动osd服务
$ systemctl start ceph-osd@<osd-id>
 
 
#使用ceph -s命令观察结果，最好同时使用tailf命令去观察对应的OSD日志.等所有pg处于active+clean之后再继续下面的操作
$ ceph -s
#确认compact完成以后的omap大小:
du -sh /var/lib/ceph/osd/ceph-$id/current/omap
 
#删除osd中临时添加的leveldb_compact_on_mount配置
 
#取消noout操作(视情况而定，建议线上还是保留noout):
ceph osd unset noout
```

### 3.2 永久方案
#### 3.2.1 对 bucket 做 reshard 操作
对 bucket 做 reshard 操作，可以实现调整 bucket 的 shard 数量，实现 index 数据的重新分布。 仅支持 ceph 0.94.10 以上版本，需要停 bucket 读写，有数据丢失风险，慎重使用。

另外最新的 Luminous 可以实现动态的 reshard(根据单个 bucket 当前的 Object 数量，实时动态调整 shard 数量），其实这里面也有很大的坑，动态 reshard 对用户来讲不够透明，而且 reshard 过程中会造成 bucket 的读写发生一定时间的阻塞，所以从我的个人经验来看，这个功能最好关闭，能够做到在一开始就设计好单个 bucket 的 shard 数量，一步到位是最好。至于如何做好一步到位的设计可以看公众号之前的文章。(《RGW Bucket Shard 设计与优化》系列)
```plain
#注意下面的操作一定要确保对应的bucket相关的操作都已经全部停止，之后使用下面命令备份bucket的index
 
$ radosgw-admin bi list --bucket=<bucket_name> > <bucket_name>.list.backup
 
#通过下面的命令恢复数据
radosgw-admin bi put --bucket=<bucket_name> < <bucket_name>.list.backup
 
#查看bucket的index id
$ radosgw-admin bucket stats --bucket=bucket-maillist
{
    "bucket": "bucket-maillist",
    "pool": "default.rgw.buckets.data",
    "index_pool": "default.rgw.buckets.index",
    "id": "0a6967a5-2c76-427a-99c6-8a788ca25034.54133.1", #注意这个id
    "marker": "0a6967a5-2c76-427a-99c6-8a788ca25034.54133.1",
    "owner": "user",
    "ver": "0#1,1#1",
    "master_ver": "0#0,1#0",
    "mtime": "2017-08-23 13:42:59.007081",
    "max_marker": "0#,1#",
    "usage": {},
    "bucket_quota": {
        "enabled": false,
        "max_size_kb": -1,
        "max_objects": -1
    }
}
 
 
#Reshard对应bucket的index操作如下:
#使用命令将"bucket-maillist"的shard调整为4，注意命令会输出osd和new两个bucket的instance id
 
$ radosgw-admin bucket reshard --bucket="bucket-maillist" --num-shards=4
*** NOTICE: operation will not remove old bucket index objects ***
***         these will need to be removed manually             ***
old bucket instance id: 0a6967a5-2c76-427a-99c6-8a788ca25034.54133.1
new bucket instance id: 0a6967a5-2c76-427a-99c6-8a788ca25034.54147.1
total entries: 3
 
 
#之后使用下面的命令删除旧的instance id
 
$ radosgw-admin bi purge --bucket="bucket-maillist" --bucket-id=0a6967a5-2c76-427a-99c6-8a788ca25034.54133.1
 
#查看最终结果
$ radosgw-admin bucket stats --bucket=bucket-maillist
{
    "bucket": "bucket-maillist",
    "pool": "default.rgw.buckets.data",
    "index_pool": "default.rgw.buckets.index",
    "id": "0a6967a5-2c76-427a-99c6-8a788ca25034.54147.1", #id已经变更
    "marker": "0a6967a5-2c76-427a-99c6-8a788ca25034.54133.1",
    "owner": "user",
    "ver": "0#2,1#1,2#1,3#2",
    "master_ver": "0#0,1#0,2#0,3#0",
    "mtime": "2017-08-23 14:02:19.961205",
    "max_marker": "0#,1#,2#,3#",
    "usage": {
        "rgw.main": {
            "size_kb": 50,
            "size_kb_actual": 60,
            "num_objects": 3
        }
    },
    "bucket_quota": {
        "enabled": false,
        "max_size_kb": -1,
        "max_objects": -1
    }
}
```
## 4. 总结

1.  另外可以做到的就是单独使用 SSD 或者 NVME 作为 index pool 的 OSD，但是 Leveldb 从设计上对 SSD 的支持比较有限，最好能够切换到 rocksdb 上面去，同时在 jewel 之前的版本还不支持切换 omap 引擎到 rocksdb，除非打上下面的补丁 [https://github.com/ceph/ceph/pull/18010](https://github.com/ceph/ceph/pull/18010)

2.  bucket 的 index shard 数量提前做好规划，这个可以参考本公众号之前的几篇 bucket index shard 相关内容。

3.  jewel 之前的版本 LevelDB 如果硬件条件允许可以考虑切换到 rocksdb 同时考虑在业务高峰期关闭 deep-scrub。如果是新上的集群用 L 版本的 ceph，放弃 Filestore，同时使用 Bluestore 作为默认的存储引擎。

总而言之 bucket index 的性能需要有 SSD 加持，大规模集群一定要做好初期设计，等到数据量大了再做调整，很难做到亡羊补牢！

**参考：**
[Ceph 亚太峰会 RGW 议题分享](https://mp.weixin.qq.com/s?__biz=MzUyMDAwNjYyMw==&mid=2247483875&idx=1&sn=ddb35db83e72af2b14516a0948087c6c&chksm=f9f1bf53ce8636456a3b866eb717c651e0a37ea32e649f5a53ac8e9af57390ead59803b76ba9&mpshare=1&scene=1&srcid=0806so7DCFK0o40LfIVjKtBo#rd)
[RGW Bucket Shard 设计与优化](https://cloud.tencent.com/developer/article/1032854)
