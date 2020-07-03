---
title: 双控接管理解
toc: true
date: 2020-07-01 12:27:56
tags: 工作记录
---
接管功能主要是为了提升单控系统的容灾能力，保证 HA，从而增加另一个控制器，保证在其中某一个控制器关机、断链路的时候业务可以正常使用。

## 定义
- 离线接管
当控制器宕机或者心跳口断开的时候发生的接管行为；
- 在线接管
由于控制器之间的部分网口链路断开引发的接管行为；

## 触发机制
[pacemaker 浅析_以前冷现在热-CSDN 博客_pacemaker](https://blog.csdn.net/a964921988/article/details/82628478)

我们使用 pacemaker 管理双控集群，pcs status 查看节点资源、状态信息：
```bash
[root@controller-1 ~]# pcs status
```
```plain
Cluster name: mycluster
Stack: corosync
Current DC: controller-2 (version 1.1.19-8.el7-c3c624ea3d) - partition with quorum
Last updated: Wed Jul  1 17:16:59 2020
Last change: Wed Jul  1 14:54:28 2020 by hacluster via crmd on controller-1

2 nodes configured
3 resources configured

Online: [ controller-1 controller-2 ]   # 表示存活的节点，如果离线会显示为offline

Full list of resources: # 显示所有集群监控的资源
# c* 用于分别控制器离线方式下的接管
 c1	(ocf::heartbeat:makeRAID):	Started controller-1    
 c2	(ocf::heartbeat:makeRAID):	Started controller-2
 # md* 用于控制器同名RAID的接管（我们把控一上的RAID统一命名为md1*，控二命名为md2* ）
 md11	(ocf::heartbeat:makeRAID):	Started controller-1  
 drbd-1	(ocf::heartbeat:IPaddr):	Started controller-1

Daemon Status:
  corosync: active/disabled
  pacemaker: active/disabled
  pcsd: active/enabled

```
其中：
	· c1/c2 资源分别用于控制 CA/CB 控制器离线情况下的接管
	· md* 资源用于控制同名 RAID 的接管
	· VIP-* /enp*资源用于控制 NAS 相关的在线接管
	· drbd-* 用于控制带有 drbd 功能的 SAN 相关的在线接管

~~c1/c2 资源以及 md*资源使用的都是 makeraid 资源代理脚本，位于/lib/ocf/resource.d/heartbeat/目录下，~~ 而其余使用 ipaddr2 实现虚拟 ip 地址的管理。

## 接管

### 离线接管
- 控制器宕机（关机）
某一控制器宕机，我们获取到控制器名称，然后把属于这个控制器的 RAID 迁移到需要接管的另一控制器之上。
1. 在接管 RAID 前，我们获取 RAID 之上的 VG、LV、Cache 等；
2. 在接管控制器上激活 RAID；
3. 激活 RAID 之上的 vg、lv（mount、iscsi 输出、DRBD、cache）
4. 继续提供服务；

- 心跳口通信出错
当两个控制器心跳口断裂后，会出现互相认为对方挂掉，试图接管对方资源各自形成集群。此时会导致数据不一致。

解决这种脑裂有以下方案：
1. 冗余心跳口
多路心跳通路+com 口
2. fence 技术
确保共享资源被完全释放，备份节点收不到心跳信息。通过单独线路发送关机指令关闭节点。（这种时候，有几率关掉的是正常节点）
3. 仲裁机制（仲裁盘）
如 HP MC/SG，使用单独划分的区域，不建立文件系统，两个控制器直接裸读写该区域，交换成员信息。
4. 磁盘锁
锁住共享磁盘，让对方完全抢不走共享资源（如果主动锁节点不解锁，另一方无计可施）

参见[HA 高可用集群中"脑裂"问题解决 - 运维总结 - 散尽浮华 - 博客园](https://www.cnblogs.com/kevingrace/p/7205846.html)
[双机脑裂(split-brain)解决办法_八月未央-CSDN 博客_split brain](https://blog.csdn.net/wuxbeyond/article/details/43451911)

检测到脑裂时，向仲裁节点发起仲裁，进行抢占，抢占到的节点获取资源，继续提供服务。

### 在线接管
在接管之前，首先使用底层接口确保被接管控制器的 IO 阻塞。
当检测到某一网口断开时，找到与之绑定的 RAID，然后在接管方进行激活。同时，其上顺带的 VG、LV 也一起接管过来。
之后放开 IO 阻塞，继续提供服务。

## 恢复接管
对网络进行检查，是否具备恢复前提；
具备之后阻塞 IO；
同步 RAID 配置；
找到原属于该控制器之上的资源，对 RAID 进行激活，对 VG、LV 进行激活；
放开 IO 阻塞，恢复提供服务。
