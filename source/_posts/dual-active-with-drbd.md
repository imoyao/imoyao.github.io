---
title: 一种基于 DRBD 实现的双活解决方案
date: 2020-07-22 10:19:18
tags:
- DRBD
- 存储
categories: 项目相关
password: estor
cover: /images/dual.jpg
---
{% note info %}
**版本信息**    
cat /proc/drbd 
version: 8.4.5 (api:1/proto:86-101)
srcversion: D71ED6FF152163F9B784DD3 
{% endnote %}
## 架构
我们通过 DRBD 双主模式实现两台双控存储服务器之间的数据同步的同时实现共同承担业务数据的读写。在初始化时，通过定义优先级实现生产卷和镜像卷的配置，保证生产卷配置更强从而承担更多的业务。
![整体设计图](/images/AA-DRBD/AA-DRBD.png)
## 定义
控制器：controller/host
分组、节点：group/node
仲裁域：zone

## 具体实现
### 整体
双控服务器在底层通过 DRBD 专用网络实现两个控制器之间的数据同步。同时配置第三节点做为仲裁服务器。 正常情况下。通过两台双控机器的 AO 路径下发数据，块存储通过 DRBD 实现数据自动复制。   

当 DRBD 因为网络链路异常时，首先`drbdadm pause-sync`同步，然后通过 DRBD 配置文件中的 handler 自定义脚本向管理系统告知监测到链路异常事件发生，之后存储控制器通过抢占仲裁服务保证最终只有一个数据节点继续提供服务，然后`drbdadm resume-sync`恢复抢占到节点的读写事件。而未抢占到仲裁的节点自动将 LUN 断开连接，然后本端（未抢占到仲裁端）自动降备，自身数据标记为 outdated，断开连接，不再对外提供服务，从而避免数据两边读写发生脑裂事故。

如果情况向更糟发生，即接管业务端继续发生接管事件：此时 AN 端处理逻辑是发生控制器之间的接管。将原来控一上的业务接管到控二上面，drbd 重新输出提供业务支持；对于非抢占组控制器：如果控制器之间接管发生，它也会接管资源，只是必须保证 drbd 是标记`outdated`，同时不会向上游提供服务。   
{% note info %}
在这种情况下的恢复，此时 drbd 备机上面恢复到什么程度？只是升主，资源被接管到在控二上面，不会恢复到原来一样还跑在控一上面的状况。
{% endnote %}

当链路异常修复之后，存储管理员手动恢复异常服务器，将之前 DRBD 被标记为备机的节点重新激活，然后数据从主机同步到备机，两边的数据重新建立数据恢复 UpToDate，之后等待 handler 中的事件通知脚本表示数据同步完成，然后业务恢复正常。

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

## Q&A

1. 如何通知仲裁并实现抢占？
参见[使用 DRBD 和 Pacemaker 集群栈](https://www.linbit.com/drbd-user-guide/drbd-guide-9_0-cn/#ch-pacemaker)，因为我们使用 GFS 文件系统，所以参考此处：[将 GFS 与 DRBD 结合使用](https://www.linbit.com/drbd-user-guide/drbd-guide-9_0-cn/#ch-gfs)
> 将 DRBD 资源设置为包含共享的 Global File System(GFS)的块设备所需的步骤。它包括 GFS 和 GFS2。要在 DRBD 上使用 GFS，必须在 indexterm 中配置[DRBD|dual-primary mode](https://www.linbit.com/drbd-user-guide/drbd-guide-9_0-cn/#s-dual-primary-mode)。

我们首先需要对 drbd 资源进行配置，具体资源配置为：
 ```plain
 resource r1 {
    net{
        timeout  300;
        ping-int 60;
        ping-timeout 600; 
        ko-count 7;
        socket-check-timeout 1;
        protocol C;
        allow-two-primaries yes;        # 允许双主
    }

    disk{
        fencing resource-and-stonith;       # 定义双主模式下连接断开时的处理策略 ①
    }

    handlers{
        fence-peer "/root/DRBD/notify/drbd_notify.sh drbd1 fence-peer";     # 配置连接断开时的fence功能
        before-resync-target "/root/DRBD/notify/drbd_notify.sh drbd1 sync-target-start";    # 同步目标端（target）开始同步通知
        after-resync-target "/root/DRBD/notify/drbd_notify.sh brbd1 sync-target-done";  # 同步目标端完成同步通知
    }

    device /dev/drbd1;

    disk  /dev/StorPool11/SANLun10;
    meta-disk internal;
    on controller-1 {
        address 10.10.12.2:32455;
    }

    on controller-2 {
        address 10.10.12.3:32455;
    }

}
 ```
 1. 磁盘 fencing 配置策略
    - dont-care：默认策略，不执行 fencing 策略
    - resource-only:仅执行 fence-peer，需要说明的是，该功能并不是 fence-peer 的使能开关，而是说明除 fence-peer 外不需要做额外的其他工作
    - resource-and-stonith：冻结 io 并等待 fence-peer 的执行结果，根据执行结果决定是否解除冻结， 解除冻结需要对端处于 outdate 状态。
 2. handler 配置策略
  - fence-peer
    目前我们自定义的返回码如下所示:
    ```plain
    3：对端处磁盘于inconsistent或者更糟糕的状态，
     返回该值后，本端将把对端磁盘状态设置为inconsistent状态。
    4：对端处于outdate状态，返回该值后，本端将把对端磁盘状态设置为outdate。本端挂起将会被解除 
    5: 对端已经关机，返回该值后，本端将对端磁盘状态设置为outdate，本端挂起将会被解除
    6：对端角色为主，返回该值后，本端磁盘状态自动变为outdate状态
    7：对端被成功爆头，返回该值后，本端将对端磁盘状态设置为outdate，本端挂起将会被解除
    101: 将本端所有io以错误码-EIO返回，磁盘状态不改变，挂起状态将会被解除
    其他值: 打印 “fence-peer helper broken, returned N"日志后返回，不做其他处理。
    ```

    执行的操作是：标记对端 outdate、对端 drbd 降备(secondary)、本端 drbd 断开与对端的连接（disconnect）

  - before-resync-target: 同步目标端开始同步通知
    0: 通知成功
    其他: 通知失败，断开连接

  - after-resync-target: 同步目标端完成同步通知
    返回值不影响执行

    执行的操作是：
    1. 对端升主、重新建立连接
    2. 置标志位，可以升主
## 推荐阅读
[双活数据中心架构分析及优缺点_存储我最懂-CSDN 博客](https://blog.csdn.net/shouqian_com/article/details/52525021)