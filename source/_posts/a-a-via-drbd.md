---
title: 一种基于 DRBD 的双活解决方案
date: 2020-07-22 10:19:18
tags:
- DRBD
- 存储
categories: 项目相关
password: estor
---
## 架构
我们通过 DRBD 双主模式实现两台双控存储服务器之间的数据同步的同时实现共同承担业务数据的读写。在初始化时，通过定义优先级实现生产卷和镜像卷的配置，保证生产卷配置更强从而承担更多的业务。
![整体设计图](/images/AA-DRBD/AA-DRBD.png)
## 定义
控制器：controller/host
分组、节点：group/node
仲裁域：zone

## 具体实现
### 整体
双控服务器在内部通过 heartbeat+pacemaker+corosync 实现宕机等异常发生时事件通知，DRBD 通过专用网络实现两个控制器之间的数据同步。同时配置第三节点做为仲裁服务器，当 DRBD 因为网络异常导致连接异常时，向管理系统告知事件发生，之后存储控制器通过抢占仲裁服务器保证最终只有一个数据节点继续提供服务，未抢占到仲裁的节点自动降备，自身数据标记为 outdated，不再对外提供服务，从而避免数据两边读写发生脑裂事故。当异常修复之后，存储管理员手动恢复异常服务器，将之前 DRBD 被标记为备机的节点重新激活，然后数据从主机同步到备机，两边的数据重新恢复 UpToDate，之后业务恢复正常。
### 仲裁服务
通过 go 编写仲裁服务包括以下几个部分：远程调用模块、仲裁模块、日志模块、数据管理模块、安全访问模块(暂定)
根据业务实际需要，目前仲裁服务支持以下功能：
1. 初始化（init）
2. 重置（reset）
3. 状态探测（probe）
4. 增加节点（add）
5. 删除节点（delete）
6. 更新节点（update）
7. 抢占（freeze）
8. 查询抢占结果（inquire）
9. 释放抢占（release）
10. 销毁（destroy）
### 管理系统
![管理系统流程图](/images/AA-DRBD/ODSP.png)

[完整流程 - ProcessOn](https://www.processon.com/view/link/5f100b71f346fb2bfb290a20)

### 界面
![仲裁服务初始化](/images/AA-DRBD/yxt-init.png)
![仲裁服务管理](/images/AA-DRBD/yxt-manage.png)
[原型图](https://modao.cc/app/701a9917a82f111aec9c62a32f241770?simulator_type=device&sticky)