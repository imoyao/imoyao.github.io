---
title: first-wiki
toc: true
date: 2020-05-23 11:02:28
tags:

---
# 1\. 节点故障检测概述

节点的故障检测是分布式系统无法回避的问题，集群需要感知节点的存活，并作出适当的调整。通常我们采用心跳的方式来进行故障检测，并认为能正常与外界保持心跳的节点便能够正常提供服务。一个好的故障检测策略应该能够做到：

*   **及时**：节点发生异常如宕机或网络中断时，集群可以在可接受的时间范围内感知；
*   **适当的压力**：包括对节点的压力，和对网络的压力；
*   **容忍网络抖动**
*   **扩散机制**：节点存活状态改变导致的元信息变化需要通过某种机制扩散到整个集群；

不同的分布式系统由于其本身的结构不同，以及对一致性、可用性、可扩展性的需求不同，会针对以上几点作出不同的抉择或取舍。下面我们就来看看 Ceph 是怎么做的。

# 2\. Ceph 故障检测机制

Ceph 作为有中心的分布式结构，元信息的维护和更新自然的都由其中心节点 Ceph Monitor 来负责。节点的存活状态发生改变时，也需要 Monitor 来发现并更新元信息并通知给所有的 OSD 节点。最自然的，我们可以想到让中心节点 Monitor 保持与所有 OSD 节点之间频繁的心跳，但如此一来，当有成百上千的 OSD 节点时 Monitor 变会有比较大的压力。之前在[Ceph Monitor and Paxos](http://catkang.github.io/2016/07/17/ceph-monitor-and-paxos.html)中介绍过 Ceph 的设计思路是通过更智能的 OSD 和 Client 来减少对中心节点 Monitor 的压力。同样的，在节点的故障检测方面也需要 OSD 和 Monitor 的配合完成。下面的介绍基于当前最新的 11.0.0 版本。

## **2.1 OSD 之间心跳**

属于同一个 pg 的 OSD 我们称之为伙伴 OSD，他们会相互发送 PING\PONG 信息，并且记录发送和接收的时间。OSD 在 cron 中发现有伙伴 OSD 相应超时后，会将其加入 failure_queue 队列，等待后续汇报。

**参数：**
 - osd_heartbeat_interval(6): 向伙伴 OSD 发送 ping 的时间间隔。实际会在这个基础上加一个随机时间来避免峰值。
 - osd_heartbeat_grace(20)：多久没有收到回复可以认为对方已经 down

## 2.2 OSD 向 Monitor 汇报伙伴 OSD 失效
1. OSD 发送错误报告
 - OSD 周期性的检查 failure_queue 中的伙伴 OSD 失败信息；
 - 向 Monitor 发送失效报告，并将失败信息加入 failure_pending 队列，然后将其从 failure_queue 移除；
 - 收到来自 failure_queue 或者 failure_pending 中的 OSD 的心跳时，将其从两个队列中移除，并告知 Monitor 取消之前的失效报告；
 - 当发生与 Monitor 网络重连时，会将 failure_pending 中的错误报告加回到 failure_queue 中，并再次发送给 Monitor。

2. Monitor 统计下线 OSD
 - Monitor 收集来自 OSD 的伙伴失效报告；
 - 当错误报告指向的 OSD 失效超过一定阈值，且有足够多的 OSD 报告其失效时，将该 OSD 下线。

**参数:**
 - osd_heartbeat_grace(20): 可以确认 OSD 失效的时间阈值；
 - mon_osd_reporter_subtree_level(“host”)：在哪一个级别上统计错误报告数，默认为 host，即计数来自不同主机的 osd 报告
 - mon_osd_min_down_reporters(2): 最少需要多少来自不同的 mon_osd_reporter_subtree_level 的 osd 的错误报告
 - mon_osd_adjust_heartbeat_grace(true)：在计算确认 OSD 失效的时间阈值时，是否要考虑该 OSD 历史上的延迟，因此失效的时间阈值通常会大于 osd_heartbeat_grace 指定的值

## 2.3 OSD 到 Monitor 心跳
 - OSD 当有 pg 状态改变等事件发生，或达到一定的时间间隔后，会向 Monitor 发送 MSG_PGSTATS 消息，这里称之为 OSD 到 Monitor 的心跳。
 - Monitor 收到消息，回复 MSG_PGSTATSACK，并记录心跳时间到 last_osd_report。
 - Monitor 周期性的检查所有 OSD 的 last_osd_report，发现失效的节点，并标记为 Down。

**参数：**
 - mon_osd_report_timeout(900)：多久没有收到 osd 的汇报，Monitor 会将其标记为 Down；
 - osd_mon_report_interval_max(600)：OSD 最久多长时间向 Monitor 汇报一次；
 - osd_mon_report_interval_min(5)：OSD 向 Monitor 汇报的最小时间间隔

# 3. 总结
可以看出，Ceph 中可以通过伙伴 OSD 汇报失效节点和 Monitor 统计来自 OSD 的心跳两种方式发现 OSD 节点失效。回到在文章开头提到的一个合格的故障检测机制需要做到的几点，结合 Ceph 的实现方式来理解其设计思路。

 - **及时**：伙伴 OSD 可以在秒级发现节点失效并汇报 Monitor，并在几分钟内由 Monitor 将失效 OSD 下线。当然，由于 Ceph 对一致性的要求，这个过程中客户端写入会不可避免的被阻塞；
 - **适当的压力**：由于有伙伴 OSD 汇报机制，Monitor 与 OSD 之间的心跳统计更像是一种保险措施，因此 OSD 向 Monitor 发送心跳的间隔可以长达 600 秒，Monitor 的检测阈值也可以长达 900 秒。Ceph 实际上是将故障检测过程中中心节点的压力分散到所有的 OSD 上，以此提高中心节点 Monitor 的可靠性，进而提高整个集群的可扩展性；
 - **容忍网络抖动**：Monitor 收到 OSD 对其伙伴 OSD 的汇报后，并没有马上将目标 OSD 下线，而是周期性的等待几个条件：1，目标 OSD 的失效时间大于通过固定量 osd_heartbeat_grace 和历史网络条件动态确定的阈值；2，来自不同主机的汇报达到 mon_osd_min_down_reporters。3，满足前两个条件前失效汇报没有被源 OSD 取消。
 - **扩散**：作为中心节点的 Monitor 并没有在更新 OSDMap 后尝试广播通知所有的 OSD 和 Client，而是惰性的等待 OSD 和 Client 来获取。以此来减少 Monitor 压力并简化交互逻辑。
