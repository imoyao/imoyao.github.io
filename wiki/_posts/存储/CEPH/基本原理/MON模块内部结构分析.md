# 1. 模块简介
Monitor 作为 Ceph 的 Metada Server 维护了集群的信息，它包括了 6 个 Map，
分别是 MONMap，OSDMap，PGMap，LogMap，AuthMap，MDSMap。
其中 PGMap 和 OSDMap 是最重要的两张 Map。

# 2. 模块的基本结构
![image.png](https://upload-images.jianshu.io/upload_images/2099201-beca04aae58bef45.png)

1. Monitor 内部使用一套 Paxos 来实现各种数据的更新，所以所有继承自 PaxosService 的 Monitor
   实现数据更新时需要通过 Paxos 达成一致后才能进行。
2. PaxosService 的 dispatch 内部调用子类的 preprocess_query 进行查询相关操作，如果非查询类处理，
再调用子类的 prepare_update 接口实现数据的更新，所以子类 Monitor 实现两个接口来处理相关的业务消息。

# 3. Monitor 业务消息
## 3.1 Monitor 自身
| 消息类型 | 消息结构体 | 消息作用 | 处理接口 |
|:---:|:---:|:---:|:---:|
| CEPH_MSG_PING | MPing | 定期 Ping Monitor 确认 Monitor 的存在 | handle_ping |
| CEPH_MSG_MON_GET_MAP | MMonGetMap | 认证前获取 MonMap | handle_mon_get_map |
| CEPH_MSG_MON_METADATA | MMonMetadata | 处理保存某个 Monitor 的系统信息（cpu，内存等）| handle_mon_metadata |
| MSG_MON_COMMAND | MMonCommand | 传递命令行消息给 Monitor，Monitor 再分发给相应的 XXXMonitor 进行处理 | handle_command |
| CEPH_MSG_MON_GET_VERSION | MMonGetVersion | 获取 cluster map 的版本信息 | handle_get_version |
| CEPH_MSG_MON_SUBSCRIBE | MMonSubscribe | Cluster map 订阅更新 | handle_subscribe |
| MSG_ROUTE | MRoute | 路由请求转发（待确认） | handle_route |
| MSG_MON_PROBE | MMonProbe | 启动加入时需要向其他 Monitor 发送 Probe 请求 | handle_probe |
| MSG_MON_SYNC | MMonSync | 同步 Paxos 状态数据 | handle_sync |
| MSG_MON_SCRUB | MMonScrub | MonitorDBStore 数据一致性检测 | handle_scrub |
| MSG_MON_JOIN | MMonJoin | 如果不在 MonMap 中申请加入到 MonMap | MonmapMonitor::prepare_join |
| MSG_MON_PAXOS | MMonPaxos | 选举完成后，leader 会触发 Paxos::leader_init，状态置为 STATE_RECOVERING，并发起该消息的 OP_COLLECT 流程 | Paxos::dispatch |
| MSG_MON_ELECTION | MMonElection | 发起选举流程 | Elector::dispatch |
| MSG_FORWARD | MForward | 将请求转发到 leader | handle_forward |
| MSG_TIMECHECK | MTimeCheck | Monitor 每隔 mon_timecheck_interval 检测所有 Monitor 的系统时间来检测节点之间的时间差 | handle_timecheck |
| MSG_MON_HEALTH | MMonHealth | 每隔 mon_health_data_update_interval 检测存放 Monitor 上面使用的 leveldb 数据的状态 | HealthMonitor::service_dispatch |

## 3.2 AuthMonitor
| 消息类型 | 消息结构体 | 消息作用 | 处理接口 |
|:---:|:---:|:---:|:---:|
| MSG_MON_COMMAND | MMonCommand | 处理 ceph auth xxx 命令行相关处理 | preprocess_command 处理 ceph auth get/export/list 等<br/>prepare_command 处理 ceph auth import/add/get-or-create/caps 等 |
| CEPH_MSG_AUTH | MAuth | 实现认证和授权消息处理 | prep_auth |

## 3.3 OSDMonitor
| 消息类型 | 消息结构体 | 消息作用 | 处理接口 |
|:---:|:---:|:---:|:---:|
| CEPH_MSG_MON_GET_OSDMAP | MMonGetOSDMap | 获取 OSDMap | preprocess_get_osdmap |
| MSG_OSD_MARK_ME_DOWN | MOSDMarkMeDown | OSD shutdown 之前通知 Monitor 发送该消息 | preprocess_mark_me_down <br/> prepare_mark_me_down |
| MSG_OSD_FAILURE | MOSDFailure | 1. OSD 每隔 OSD_TICK_INTERVAL 检测心跳无响应的 OSD，并将失败的 OSD report 给 Monitor<br/> 2. Monitor 判断上报次数>=mon_osd_min_down_reports，那么就将 target_osd 标识为 down | preprocess_failure |
| MSG_OSD_BOOT | MOSDBoot | 新 OSD 加入时发送请求到 Monitor，参考新 OSD 的加入流程 | preprocess_bootprepare_boot |
| MSG_OSD_ALIVE | MOSDAlive | OSD 判断 up_thru_wanted 决定是否发送请求给 Monitor，Monitor 发送 Incremental OSDMap 返回给 OSD |preprocess_alive <br/>prepare_alive |
| MSG_OSD_PGTEMP | MOSDPGTemp | Primary OSD 处于 backfilling 状态无法提供读取服务时，会发送该消息到 Monitor，将 PG 临时映射到其他的 OSD 上提供去服务 | preprocess_pgtemp<br/> prepare_pgtemp |
| MSG_REMOVE_SNAPS | MRemoveSnaps | 删除快照信息 | prepare_remove_snaps |
| CEPH_MSG_POOLOP | MPoolOp | 删除/创建 Pool，创建/删除 pool 快照等 | prepare_pool_op |

## 3.4  PGMonitor
| 消息类型 | 消息结构体 | 消息作用 | 处理接口 |
|:---:|:---:|:---:|:---:|
| CEPH_MSG_STATFS | MStatfs | 返回文件系统 osd 占用的 kb 容量 | handle_statfs |
| MSG_PGSTATS | MPGStats | 查询或者更新 pg 状态 | preprocess_pg_stats <br/>prepare_pg_stats |
| MSG_GETPOOLSTATS | MGetPoolStats | 获取 pool 汇总状态信息 | preprocess_getpoolstats |
| MSG_MON_COMMAND | MMonCommand | 处理 ceph pg xxx 相关命令行 | preprocess_command |

## 3.5 MonMapMonitor
| 消息类型 | 消息结构体 | 消息作用 | 处理接口 |
|:---:|:---:|:---:|:---:|
| MSG_MON_JOIN | MMonJoin | 更新 MonMap | preprocess_join<br/>prepare_join |
| MSG_MON_COMMAND | MMonCommand | 处理 ceph mon xxx 相关命令行 | preprocess_command<br/> prepare_command |

## 3.6 MDSMonitor
| 消息类型 | 消息结构体 | 消息作用 | 处理接口 |
|:---:|:---:|:---:|:---:|
| MSG_MDS_BEACON | | | |
| MSG_MDS_OFFLOAD_TARGETS  | | | |

## 3.7 LogMonitor
| 消息类型 | 消息结构体 | 消息作用 | 处理接口 |
|:---:|:---:|:---:|:---:|
| MSG_LOG | | | |
