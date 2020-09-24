---
title: 一种基于 DRBD 实现的 ALUA 解决方案
date: 2020-07-22 10:19:18
tags:
- DRBD
- 存储
- ALUA
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
控制器：controller/host，指一台双控服务器上面的两台主控；
分组、节点：group/node，指双控服务器，如：A1,A2；
仲裁域：zone

## 具体实现
### 整体
双控服务器内部使用心跳口通信，两台双控服务器之间通过专用网络保障 DRBD 块设备的数据同步。同时配置第三节点作为仲裁服务器。正常情况下，通过两台双控机器的 AO 路径下发数据，块存储通过 DRBD 实现数据自动复制。

当 DRBD 因为网络链路异常时，首先`drbdadm pause-sync`暂停同步，然后根据资源配置中的超时尝试连接。与此同时，双控内部会去检查心跳口连接，如果心跳口通信正常，则开始内部接管流程：AN端接管AO端的业务，即原来控一上的资源被控二接管。在一定的超时时间后，如果网络没有恢复连接，则开始进行仲裁抢占。

{% note info %}
在这种情况下的恢复：此时 DRBD 备机上面恢复到什么程度？只是升主，资源被接管到在控二上面，不会恢复到原来各自资源还跑在各自控一上面的状况。
{% endnote %}

发生抢占时，通过 DRBD 资源配置文件中的 handler 自定义脚本向管理系统告知监测到链路异常事件发生，之后存储控制器相继发起 freeze 请求通过抢占仲裁服务保证最终只有一个数据节点（控制）继续提供服务。然后`drbdadm resume-sync`恢复抢占到节点的读写事件。而未抢占到仲裁的节点自动将 LUN 断开连接/通过 detach 脱离连接，然后本端（未抢占到仲裁端）自动降备（secondary），并将自身数据标记为 outdated，断开连接（down），不再对外提供服务，从而避免数据两边读写发生脑裂事故。

当链路异常修复之后，存储管理员手动恢复异常资源：将之前被标记为 down 的 DRBD 资源重新 up，如果需要则重连（connect），然后等待在此期间产生的数据从生产卷同步回流到备份卷。之后用户手动重置仲裁，在恢复前检查数据状态确保恢复至 UpToDate/UpToDate，此时DRBD 升主（primary），iSCST进行 attach 之后连接恢复。然后重置仲裁（unfreeze），handler 中的事件通知脚本表示数据同步完成，然后业务恢复正常，为下一次可能发生的生产意外提供可仲裁条件。

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

### 代码
此处只记录一部分关键性代码。
- 获取gRPC异常
参看此处：[python grpc: confusion with grpc._channel._Rendezvous · Issue #9270 · grpc/grpc](https://github.com/grpc/grpc/issues/9270)    
```python
import grpc
import logger

def do_rpc():
    try:
        pass
    except grpc.RpcError as e:
        logger.debug('===0=====reply Exception:{}', e)
        # see also:[python grpc: confusion with grpc._channel._Rendezvous · Issue #9270 · grpc/grpc](https://github.com/grpc/grpc/issues/9270)
        code = e.code()
        msg = e.details()
        if code == grpc.StatusCode.UNAVAILABLE:
            return {'state': '1', 'result': {'message': '14009'}}
        else:
            return {'state': '1', 'result': {'message': msg}}
```
- 更新配置文件
难点主要在于需要保持文件的一致性，刚开始使用加锁，但是似乎无法实现原子操作（文件写入还是会异常）后来使用重命名方法可以实现目的。具体参看：[使用 Python 进行稳定可靠的文件操作 - OSCHINA](https://www.oschina.net/translate/reliable-file-updates-with-python?lang=chs&p=1)    
```python
import json
from contextlib import contextmanager
import tempfile
import os

import setting
import logger

# CONTEXT_LOCK = threading.RLock() 

@contextmanager
def json_context(filename=setting.REFEREE_CONF_FP):
    """一个简单的上下文管理器，用于更新json配置
    :param context_lock: Lock, 上下文锁
    :param filename: str,
    :return:
    """
    # global CONTEXT_LOCK
    # if not context_lock:
    #     context_lock = CONTEXT_LOCK
    # context_lock.acquire()
    with open(filename, encoding='utf-8') as f:
        info = json.load(f, strict=False)
    yield info
    # 写进临时文件然后重命名 see also:https://www.oschina.net/translate/reliable-file-updates-with-python
    with tempfile.NamedTemporaryFile(
            'w', dir=os.path.dirname(filename), delete=False) as tf:
        json.dump(info, tf, indent=4)
        tempname = tf.name
    logger.info('-------tn---{},f:{}',tempname, filename)
    os.rename(tempname, filename)
```

## Q&A

1. 如何通知仲裁并实现抢占？
参见[使用 DRBD 和 Pacemaker 集群栈](https://www.linbit.com/drbd-user-guide/drbd-guide-9_0-cn/#ch-pacemaker)，因为我们使用 GFS 文件系统，所以参考此处：[将 GFS 与 DRBD 结合使用](https://www.linbit.com/drbd-user-guide/drbd-guide-9_0-cn/#ch-gfs)
> 将 DRBD 资源设置为包含共享的 Global File System(GFS)的块设备所需的步骤。它包括 GFS 和 GFS2。要在 DRBD 上使用 GFS，必须在 indexterm 中配置[DRBD|dual-primary mode](https://www.linbit.com/drbd-user-guide/drbd-guide-9_0-cn/#s-dual-primary-mode)。

我们首先需要对 DRBD 资源进行配置，具体资源配置为：
 ```plain
 resource r1 {
    net{
        timeout  300;
        ping-int 60;    # 如果DRBD设备对的TCP/IP连接空闲超过配置秒，DRBD将生成一个保持活动数据包，以检查其伙伴是否仍存活。 默认值为10。单位为秒
        ping-timeout 600; # 对等方必须回答保持活动数据包的时间。 如果对方的答复在此时间段内未收到，则视为已死亡。 默认单位是十分之一秒，默认值为5（半秒）。
        ko-count 7; # 在secondary 节点无法完成单个写请求的计数次数时，它将被逐出集群，即主节点进入StandAlone模式。默认值为0，即禁用此特性。
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

    on controller-x {
        address 10.10.12.3:32455;
    }

}
 ```
 字段解释在此[Ubuntu Manpage: drbdsetup - Setup tool for DRBD .](http://manpages.ubuntu.com/manpages/trusty/man8/drbdsetup.8.html)：
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
    执行的操作是：标记对端 outdate、对端 DRBD 降备(secondary)、本端 DRBD 断开与对端的连接（down）

  - before-resync-target: 同步目标端开始同步通知
    ```plain
    0: 通知成功
    其他: 通知失败，断开连接
    ```
  - after-resync-target: 同步目标端完成同步通知
    返回值不影响执行

    执行的操作是：
    1. 检查 DRBD 是否建立正常连接；
    2. 如果正常建立连接，则对端升主：`primary/secondary` 变为 `primary/primary`；
    3. SCST 重新`attach`输出，建立连接提供服务。

## 双主模式创建之后流程
1. 初始化角色为 secondary/secondary；
2. 将一端强制升主：primary，此时连接状态变为`SyncSource`和`SyncTarget`
等待同步完成
```plain
10:drbds10/0  Connected Primary/Secondary UpToDate/UpToDate 
```
之后控制升主。
3. 备机端收到指令升为主端

## 恢复
用户点击重置仲裁按钮，首先判断是否具备重置条件？
1. 是否已配置仲裁且仲裁已经发生抢占；
2. 被恢复节点是否已经具备恢复条件；
3. DRBD状态(dstate)是否已经处于`UpToDate/UpToDate`

判断以上情况均满足之后，发起重置grpc请求，重置仲裁以免下一次仲裁时发生脑裂。
需要在通知之后针对手动down的drbd进行恢复；
-  恢复流程：
1. 生产卷端connect，镜像卷端up；
之后：
1. 等待数据完成同步；
2. 用户点击界面reset。判断数据同步完成；
3. 重置仲裁、升主、attach输出继续提供服务；

## 推荐阅读
[双活数据中心架构分析及优缺点_存储我最懂-CSDN 博客](https://blog.csdn.net/shouqian_com/article/details/52525021)
