---
title: ceph 集群警告和错误类型
toc: true
date: 2020-05-23 11:02:28
tags
---

| 指标 | 说明 | 级别 |
|---|---|---|
|noscrub flag(s) set | 防止集群做清洗操作 | |
|full flag(s) set | 使集群到达设置的 full_ratio 值。会导致集群阻止写入操作 | |
|nodeep-scrub flag(s) set | 防止集群进行深度清洗操作 | |
|pause flag(s) set | 集群将会阻止读写操作，但不会影响集群的 in、out、up 或 down 状态。集群扔保持正常运行,就是客户端无法读写 | |
|noup  flag(s) set | 防止 osd 进入 up 状态 | |
|nodown flag(s) set | 防止 osd 进入 down 状态 | |
|noout flag(s) set | 防止 osd 进入 out 状态 | |
|noin flag(s) set | 防止 osd 纳入 ceph 集群。有时候我们新加入 OSD，并不想立马加入集群，可以设置该选项 | |
|nobackfill  flag(s) set | 防止集群进行数据回填操作 | |
|norebalance flag(s) set | 防止数据均衡操作 | |
|norecover flag(s) set | 避免关闭 OSD 的过程中发生数据迁移 | |
|notieragent flag(s) set | | |
|osds exist in the crush map but not in the osdmap | osd crush weight 有值但是 osd weight 无值 | |
|application not enabled on 1 pool(s) | 没有定义池的使用类型 | |
|osds have slow requests | 慢查询 | |
|Monitor clock skew detected | 时钟偏移 | |
|bigdata failing to advance its oldest client/flush tid | 客户端和 MDS 服务器之间通信使用旧的 tid | |
|Many clients (34) failing to respond to cache pressure | 如果某个客户端的响应时间超过了 mds_revoke_cap_timeout （默认为 60s ）这条消息就会出现 | |
|mons down, quorum | Ceph Monitor down | |
|in osds are down| OSD down 后会出现 | |
|cache pools are missing hit_sets | 使用 cache tier 后会出现 | |
|has mon_osd_down_out_interval set to 0 | has mon_osd_down_out_interval set to 0 ||
|is full | pool 满后会出现 | |
|near full osd | near full osd | |
|unscrubbed pgs | 有些 pg 没有 scrub  | |
|pgs stuck | PG 处于一些不健康状态的时候，会显示出来 | |
|requests are blocked | slow requests 会警告 | |
|osds have slow requests | slow requests 会警告 | |
| recovery |  需要 recovery 的时候会报 | |
| at/near target max | 使用 cache tier 的时候会警告 | |
| too few PGs per OSD | 每个 OSD 的 PG 数过少 | |
| too many PGs per OSD | too many PGs per OSD | |
| > pgp_num | > pgp_num | |
| has many more objects per pg than average (too few pgs?) | 每个 Pg 上的 objects 数过多 ||
| no osds | 部署完就可以看到，运行过程中不会出现 | |
| full osd | OSD 满时出现 | |
| pgs are stuck inactive for more than | Pg 处于 inactive 状态，该 Pg 读写都不行 | |
| scrub errors | scrub 错误出现，是 scrub 错误?还是 scrub 出了不一致的 pg | |



