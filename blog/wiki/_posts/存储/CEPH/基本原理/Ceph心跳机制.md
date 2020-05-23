# 1. 心跳介绍
心跳是用于节点间检测对方是否故障的，以便及时发现故障节点进入相应的故障处理流程。

**问题：**
 - 故障检测时间和心跳报文带来的负载之间做权衡。
 - 心跳频率太高则过多的心跳报文会影响系统性能。
 - 心跳频率过低则会延长发现故障节点的时间，从而影响系统的可用性。

**故障检测策略应该能够做到：**
 - 及时：节点发生异常如宕机或网络中断时，集群可以在可接受的时间范围内感知。
 - 适当的压力：包括对节点的压力，和对网络的压力。
 - 容忍网络抖动：网络偶尔延迟。
 - 扩散机制：节点存活状态改变导致的元信息变化需要通过某种机制扩散到整个集群。

# 2. Ceph 心跳检测
![ceph_heartbeat_1.png](https://upload-images.jianshu.io/upload_images/2099201-797b8f8c9e2de4d7.png)

**OSD 节点会监听 public、cluster、front 和 back 四个端口**
 - public 端口：监听来自 Monitor 和 Client 的连接。
 - cluster 端口：监听来自 OSD Peer 的连接。
 - front 端口：供客户端连接集群使用的网卡, 这里临时给集群内部之间进行心跳。
 - back 端口：供客集群内部使用的网卡。集群内部之间进行心跳。
 - hbclient：发送 ping 心跳的 messenger。

# 3. Ceph OSD 之间相互心跳检测
![ceph_heartbeat_osd.png](https://upload-images.jianshu.io/upload_images/2099201-a04c96ba04ec47df.png)

**步骤：**
 - 同一个 PG 内 OSD 互相心跳，他们互相发送 PING/PONG 信息。
 - 每隔 6s 检测一次(实际会在这个基础上加一个随机时间来避免峰值)。
 - 20s 没有检测到心跳回复，加入 failure 队列。


# 4. Ceph OSD 与 Mon 心跳检测
![ceph_heartbeat_mon.png](https://upload-images.jianshu.io/upload_images/2099201-06fcd181ba5c2671.png)

**OSD 报告给 Monitor：**
 - OSD 有事件发生时（比如故障、PG 变更）。
 - 自身启动 5 秒内。
 - OSD 周期性的上报给 Monito
   - OSD 检查 failure_queue 中的伙伴 OSD 失败信息。
   - 向 Monitor 发送失效报告，并将失败信息加入 failure_pending 队列，然后将其从 failure_queue 移除。
   - 收到来自 failure_queue 或者 failure_pending 中的 OSD 的心跳时，将其从两个队列中移除，并告知 Monitor 取消之前的失效报告。
   - 当发生与 Monitor 网络重连时，会将 failure_pending 中的错误报告加回到 failure_queue 中，并再次发送给 Monitor。
 - Monitor 统计下线 OSD
   - Monitor 收集来自 OSD 的伙伴失效报告。
   - 当错误报告指向的 OSD 失效超过一定阈值，且有足够多的 OSD 报告其失效时，将该 OSD 下线。


# 5. Ceph 心跳检测总结
Ceph 通过伙伴 OSD 汇报失效节点和 Monitor 统计来自 OSD 的心跳两种方式判定 OSD 节点失效。
 - **及时：**伙伴 OSD 可以在秒级发现节点失效并汇报 Monitor，并在几分钟内由 Monitor 将失效 OSD 下线。
 - **适当的压力：**由于有伙伴 OSD 汇报机制，Monitor 与 OSD 之间的心跳统计更像是一种保险措施，因此 OSD 向 Monitor 发送心跳的间隔可以长达 600 秒，Monitor 的检测阈值也可以长达 900 秒。Ceph 实际上是将故障检测过程中中心节点的压力分散到所有的 OSD 上，以此提高中心节点 Monitor 的可靠性，进而提高整个集群的可扩展性。
 - **容忍网络抖动：**Monitor 收到 OSD 对其伙伴 OSD 的汇报后，并没有马上将目标 OSD 下线，而是周期性的等待几个条件：
    - 目标 OSD 的失效时间大于通过固定量 osd_heartbeat_grace 和历史网络条件动态确定的阈值。
    - 来自不同主机的汇报达到 mon_osd_min_down_reporters。
    - 满足前两个条件前失效汇报没有被源 OSD 取消。
 - **扩散：**作为中心节点的 Monitor 并没有在更新 OSDMap 后尝试广播通知所有的 OSD 和 Client，而是惰性的等待 OSD 和 Client 来获取。以此来减少 Monitor 压力并简化交互逻辑。

# 6. 心跳设置
## 6.1 配置监视器/ OSD 互动
您已完成初始 Ceph 的配置之后，您可以部署和运行的 Ceph。当你执行一个命令，如 ceph health 或 ceph -s ， [Ceph 的监视器](http://ceph.com/docs/master/glossary/#term-ceph-monitor)将报告[CEPH 存储集群](http://ceph.com/docs/master/glossary/#term-ceph-storage-cluster)的当前状态。Ceph 的监视器通过每个[Ceph 的 OSD 守护](http://ceph.com/docs/master/glossary/#term-ceph-osd-daemon)实例，以及相邻的 Ceph OSD 守护实例，了解 Ceph 的存储集群的相关状态。Ceph 的监视器如果没有收到报告，或者如果它接收 Ceph 的存储集群的变化的报告，Ceph 的监视器更新的的[CEPH 集群](http://ceph.com/docs/master/glossary/#term-ceph-cluster-map)映射图的状态。

Ceph 为 Ceph 的监视器/ Ceph 的 OSD 守护程序交互提供合理的默认设置。但是，您可以覆盖默认值。以下部分描述如何用 Ceph 的监视器和 Ceph 的 OSD 守护实例互动来达到 Ceph 的存储集群监控的目的。

## 6.2. OSDS 检查心跳
每个 Ceph 的 OSD 守护程序检查其他 Ceph 的 OSD 守护进程的心跳每 6 秒。Ceph 的配置文件下的[OSD]部分加入 OSD   osd heartbeat interval ，或通过设定值在运行时，您可以更改心跳间隔。如果在 20 秒的宽限期内邻居的 Ceph 的 OSD 守护进程不显示心跳，Ceph 的 OSD 守护进程可能考虑周边的 Ceph OSD 守护挂掉，并向一个 Ceph 的 Monitor 报告，这将更新的 CEPH 集群地图。一个 OSD   osd heartbeat grace 可以在 Ceph 的配置文件下的[OSD]部分设置，或在运行时，你通过设置这个值改变这个宽限期。

## 6.3. OSDS 报告挂掉的 OSD
默认情况下，Ceph 的 OSD 守护程序必须向 Ceph 的监视器报告三次：另一个 Ceph 的 OSD 守护程序已经挂掉，在 Ceph 的 Monitor 承认该报告 Ceph 的 OSD 守护挂掉之前。在（早期 V0.62 版本之前）Ceph 的配置文件下的[MON]部分添加  osd min down reports setting，或者通过设定值在运行时，您可以更改 OSD 报告的挂掉的最低数量 。默认情况下，只有一个 Ceph 的 OSD 守护进程是必需报告另一个 Ceph 的 OSD 守护进程。您可以更改向 Ceph 监视器报告 Ceph 的 OSD 守护进程的 Ceph 的 OSD Daemones 的数量，通过添加一个 mon osd min down reporters 设置在 Ceph 的配置文件中，或者通过设定值在运行时。

## 6.4. 凝视失败的 OSD 报告
Ceph 的 OSD 守护进程如果不能和 Ceph 的配置文件（或群集地图）中定义的 OSD 守护同行，它将每 30 秒 ping 一个 Ceph 的监视器，为了最新副本的集群映射图。Ceph 的配置文件 下的[OSD]部分加入  osd mon heartbeat interval  设置，或通过在运行时设定值，您可以更改 Ceph 的监控心跳间隔。 

## 6.5. OSDS 报告其状态
Ceph 的 OSD 守护进程如果不向 Ceph 的监视器报告，至少每 120 秒一次，Ceph 的监视器会考虑 Ceph 的 OSD 守护已经挂掉。您可以更改 Ceph 的监控报告间隔，通过加入 osd mon report interval max 设置在 Ceph 的配置文件的[OSD]部分，或者通过设置在运行时的值。Ceph 的 OSD 守护进程会尝试报告其状态每 30 秒。在 Ceph 的配置文件下的[OSD]部分加入 osd mon report interval min s 设置，或者通过设定值在运行时，您可以更改 Ceph 的 OSD 守护报告间隔。

# 7. 配置设置
修改心跳设置时，你应该将它们包括在 您的配置文件的[global]部分。

## 7.1 监视器 MONITOR 设置
| 参数 | 说明 | 类型 | 默认值 |
|:---:|:---:|:---:|:---:|
|mon OSD min up ratio  | Ceph 的 OSD 未挂掉的最低比率在 Ceph 的 OSD 守护程序被仍定挂掉之前 | double | 0.3 |
|mon OSD min in ratio | Ceph 的 OSD 实例的最低比率在 Ceph 的 OSD 守护程序被仍定出局之前 | double | 0.3 |
|mon osd laggy halflife | laggy 估计会腐烂的秒数 | int | 60 * 60 |
|mon osd laggy weight | laggy 估计衰减的新样本的权重 | double | 0.3 |
|mon osd adjust heartbeat grace | 如果设置为 true，Ceph 将在 laggy 估计的基础上扩展 | bool | true |
|mon osd adjust down out interval | 如果设置为 true，Ceph 基于 laggy 估计扩展 | bool | true |
|mon osd auto mark in | Ceph 将标记任何引导的 Ceph 的 OSD 守护进程作为在 CEPH 存储集群 | bool | false |
|mon osd auto mark auto out in| Ceph 的标记引导 Ceph 的 OSD 守护 Ceph 的存储集群，集群中的自动标记 | bool | true |
| mon osd auto mark new in | 头孢将迎来启动新的 Ceph 的 OSD 守护在 Ceph 的存储集群 | bool | true |
| mon osd down out subtree limit| 最大的[CRUSH](http://ceph.com/docs/master/glossary/#term-crush)单位 Ceph 的类型，会自动标记出来 | String | rack |
|mon osd report timeout | 宽限期秒下来在声明反应迟钝 Ceph 的 OSD 守护前 | 32-bit Integer | 900 |
|mon osd min down reporters | Ceph 的 OSD 守护报告向下 Ceph 的 OSD 守护所需的最低数量 | 32-bit Integer | 1 |
| mon osd min down reports | Ceph 的 OSD 守护的最低次数必须报告说，另一个 Ceph 的 OSD 守护下来 | 32-bit Integer | 3 |

## 7.2 OSD 设置
| 参数 | 说明 | 类型 | 默认值 |
|:---:|:---:|:---:|:---:|
|OSD heartbeat address| 一个 Ceph 的 OSD 守护进程的网络地址的心跳 | Address | The host address |
|OSD heartbeat interval | 多久 Ceph 的 OSD 守护坪及其同行（以秒计）| 32-bit Integer | 6 |
|OSD heartbeat grace| Ceph 的 OSD 当一个守护进程并没有表现出心跳 Ceph 的存储集群认为，经过时间的 | 32-bit Integer | 20 |
| OSD mon heartbeat interval | Ceph 的的 OSD 守护坪一个 Ceph 的监视器如果它没有的 CEPH OSD 守护同行，多久 | 32-bit Integer | 30 |
| OSD mon report interval max | Ceph 的 OSD 守护进程报告 Ceph 的监视器 Ceph 的监视器前认为 Ceph 的 OSD 守护下来的时间以秒为单位的最大 | 32-bit Integer | 120 |
| OSD mon report inteval min | 秒为 Ceph 的 OSD 的守护 Ceph 的监视器，以防止 Ceph 的监视器考虑 Ceph 的 OSD 守护的最低数量 | 32-bit Integer | 5 (有效范围：应小于 OSD 周一 报告 间隔 最大)|
| OSD mon ACK timeout | 等待的秒数为 Ceph 的监视器确认请求统计 |  32-bit Integer | 30 |



