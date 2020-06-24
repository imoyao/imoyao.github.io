---
title: 基于 DRBD 实现的双活方案
toc: true
date: 2020-06-18 12:27:56
tags: DRBD
---
存储双活的仲裁之所以成为关键点，最重要的原因还是在于，从整体上看，存储跨站点双活技术是一个对称式的方案架构，两边一比一配比，中间通过链路（FC 或者 IP）连接，其最核心的难点公认是链路这个部分，这点从各家厂商方案披露支持的 RTT（往返延迟）和距离可以看出端倪。链路中断将造成两端健康的存储节点都认为对方挂掉，试图争取 Shared Resource（共享资源），并试图修改集群成员关系，各自组成一个集群，产生 Brain-Split（脑裂）现象，如果没有合理的机制去防范脑裂，将因互相抢夺共享资源自立集群，而导致共享卷数据读写不一致，产生更严重的后果。在存储双活方案，防范脑裂通用的做法就是使用仲裁机制，在第三站点放置仲裁服务器或者仲裁存储阵列。
通常有以下三种方式：
一是优先级站点方式。这种方式最简单，在没有第三方站点的情况下使用，从两个站点中选一个优先站点，发生脑裂后优先站点仲裁成功。但如集群发生脑裂后，优先站点也发生故障，则会导致业务中断，因此这种方案并非推荐的方案；
二是软件仲裁方式。这种方式应用比较普遍，采用专门的仲裁软件来实现，仲裁软件放在第三站点，可以跑在物理服务器或虚拟机上，甚至可以部署到公有云上；
三是阵列仲裁盘方式。这种方式是在第三站点采用另外一台阵列创建仲裁盘。这种方式稳定性，可靠性比较高。

## 参考资料

[五种业界主流存储双活方案解析（仲裁与两地三中心） - 邓毓 - twt 企业 IT 交流平台](https://www.talkwithtrend.com/Article/245299)
[五种业界主流存储双活架构设计方案特点对比分析 - 邓毓 - twt 企业 IT 交流平台](https://www.talkwithtrend.com/Article/244809)
---
[为什么双数据中心无法做到完美的灾备自动切换？ - 知乎](https://zhuanlan.zhihu.com/p/136877267)
[从 IT 应用架构角度，畅谈双活数据中心容灾解决方案 - 架构 - dbaplus 社群：围绕 Data、Blockchain、AiOps 的企业级专业社群。技术大咖、原创干货，每天精品原创文章推送，每周线上技术分享，每月线下技术沙龙。](https://dbaplus.cn/news-21-1223-1.html)
[突破存储跨中心双活方案设计阶段难点之一：脑裂风险 - 51CTO.COM](https://stor.51cto.com/art/201710/554440.htm)
[从两地三中心到双活数据中心-稀里哗啦的瞎说-51CTO 博客](https://blog.51cto.com/leesbing/1769519)
[双机热备+负载均衡线上方案(Heartbeat+DRBD+NFS+Keepalived+Lnmp) - Rayn——做今天最好的自己 - OSCHINA](https://my.oschina.net/Rayn/blog/161012)
[Pacemaker 集群管理 实现 DRBD 存储及应用高可用-baochenggood-ChinaUnix 博客](http://blog.chinaunix.net/uid-26719405-id-4711740.html)
[drbd+heartbeat 实现应用高可用_老老_新浪博客](http://blog.sina.com.cn/s/blog_53c33d890100bf50.html)
[Distributed Replicated Block Device 的高可用性](https://www.ibm.com/developerworks/cn/linux/l-drbd/index.html)
[沃趣科技-文档-MySQL 高可用之 DRBD](http://www.woqutech.com/docs_info.php?id=513)
[Linux 高可用(HA)之 Corosync+Pacemaker+DRBD+MySQL/MariaDB 实现高可用 MySQ/MariaDB 集群 | Linux–不是那么难](https://www.dwhd.org/20150530_014731.html)