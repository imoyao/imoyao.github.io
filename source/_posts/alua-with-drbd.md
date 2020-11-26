---
title: 一种基于 DRBD 实现的 ALUA 解决方案
date: 2020-07-22 10:19:18
tags:
- DRBD
- 存储
- ALUA
- 双活
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
分组/节点：group/node，指每台双控服务器，如：A，B；
仲裁域：zone

## 具体实现
### 整体
双控服务器内部使用心跳口通信，两台双控服务器之间通过专用网络保障 DRBD 块设备的数据同步。同时配置第三节点作为仲裁服务器。正常情况下，通过两台双控机器的 AO 路径下发数据，块存储通过 DRBD 实现数据自动复制。

当 DRBD 因为网络链路异常导致数据复制出错时，首先`drbdadm pause-sync`暂停 IO 同步，然后根据资源配置中的超时配置尝试重新建立连接。与此同时，双控内部会去检查心跳口连接，如果心跳口通信正常，则开始内部接管流程：AN 端接管 AO 端的业务，即原来控一上的资源被控二接管。在一定的超时时间后，如果网络没有恢复连接，则开始进行仲裁抢占。

{% note info %}
在这种情况下的恢复：此时 DRBD 备机上面恢复到什么程度？只是升主，资源被接管到在控二上面，不会恢复到原来各自资源还跑在各自控一上面的状况。
{% endnote %}
- 如果设置仲裁且处于`enable`状态
发生抢占时，通过 DRBD 资源配置文件中的 handler 自定义脚本向管理系统告知监测到链路异常事件发生，之后存储控制器相继发起 freeze 请求通过抢占仲裁服务保证最终只有一个数据节点（控制）继续提供服务。然后`drbdadm resume-sync`恢复抢占到节点的读写事件。而未抢占到仲裁的节点自动将 LUN 断开连接/通过 detach 脱离连接，然后本端（未抢占到仲裁端）自动降备（secondary），并将自身数据标记为 outdated，断开连接（down），不再对外提供服务，从而避免数据两边读写发生脑裂事故。

- 如果仲裁处于`disable`的禁用状态
则接收到 handler 事件之后，需要生产卷明确告知镜像卷抢占才会发生接管。所谓的明确告知有以下两种情况：
1. 生产卷机器整体关机
2. 生产卷两台控制器相继下线，通过[BBU](https://forum.huawei.com/enterprise/zh/thread-344765-1-1.html)告知镜像卷需要接管，当两次同时告知，则镜像卷接管。

此时我们将这种状态定义为`isFake`模式，即：仲裁组成员配置，但是仲裁服务器没有配置。
在这种情况下，我们可以对仲裁组成员进行管理操作（如删除、添加、编辑），这时候后端逻辑是修改数据库和配置文件，但是不会真正发起 rpc 调用事件。当用户点击界面的启用仲裁时，则要求用户必须配置仲裁服务器地址（ip）和端口（port)，此时才会真正的仲裁服务实际生效，否则，此时的仲裁服务是一种降级模式。即只有在用户点击明确告知关闭一组设备时，另一组设备才能将服务顶上去生效。

当链路异常修复之后，存储管理员手动恢复异常资源：将之前被标记为 down 的 DRBD 资源重新 up，如果需要则重连（connect），然后等待在此期间产生的数据从生产卷同步回流到备份卷。之后用户手动重置仲裁，在恢复前检查数据状态确保恢复至 UpToDate/UpToDate，此时 DRBD 升主（primary），iSCST 进行 attach 之后连接恢复。然后重置仲裁（unfreeze），handler 中的事件通知脚本表示数据同步完成，然后业务恢复正常，为下一次可能发生的生产意外提供可仲裁条件。

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
- 获取 gRPC 异常
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
# global.conf
    disk {
        on-io-error detach;
        no-disk-flushes ;
        no-disk-barrier;
        c-plan-ahead 0;
        c-fill-target 24M;
        c-min-rate 80M;
        c-max-rate 720M;
    } 

```
本地扇区访问出错时，依赖于 on-io-error 配置。
- pass-on: 主端将错误上报上层，本端磁盘进入 inconsistent 状态；
- call-local-io-error：调用本地脚本，磁盘先进入 fail 的状态，最后进入 diskless 状态；
- detach：磁盘状态先进入 fail 的状态，最后进入 diskless 状态；

当本地完全无法访问时，则出现本端处于没有磁盘的状态，如果资源处于连接状态则将请求发到对端。

 ```plain
 # 单个资源配置
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
3. DRBD 状态(dstate)是否已经处于`UpToDate/UpToDate`

判断以上情况均满足之后，发起重置 grpc 请求，重置仲裁以免下一次仲裁时发生脑裂。
需要在通知之后针对手动 down 的 drbd 进行恢复；
-  恢复流程：
1. 生产卷端 connect，镜像卷端 up；
之后：
1. 等待数据完成同步；
2. 用户点击界面 reset。判断数据同步完成；
3. 重置仲裁、升主、attach 输出继续提供服务；

## TODO（待整理）

## 有仲裁

### 一台双控整体关机
此时会发生抢占，可能是两种结果：

1. 被关机端抢占到仲裁（应该避免）
 此时正常存活端被 detach 掉 cache，scst 继续输出，但无法提供读写；关机端重启之后，DRBD 会自动升主，输出可以读写，而未关机端只能依靠用户手动启动服务，然后两边同步数据，等到数据同步完成，自动调用`do_after_sync`升主并`attach`服务；
2. 未关机端抢占到仲裁（希望实现）
 此时关机端 detach 掉 cache，开机之后 DRBD 以 secondary 的身份起来，然后主端自动将期间的数据同步过去，数据同步完成之后，调用`do_after_sync`升主，然后此时需要进入`do_add_action`逻辑，即需要手动添加 cache 同时启动 san 服务重新 enable 服务；
### 网络异常

#### 抢占
首先根据 drbd 资源中的 net 的配置，即使检测到网络异常也不会立刻发生仲裁的抢占，而是先发生组内接管。在 timeout 之后，如果网络还是没有恢复，则会发生抢占，调用 handler 中的脚本去 grpc 发生仲裁抢占，参见：ODSP.drbd_notify_action.TaggedActor.fence_peer，然后势必有一边抢占到仲裁（exit_code=4），另一边则为其他组成员已抢占(exit_code=101)，抢占到的一边继续 drbd 提供读写服务，未抢占到的一边 down 掉服务,参见：ODSP.referee.take_action.refuse，数据过来返回 error。

管理员介入，恢复网络异常，同时通过页面错误恢复 drbd 连接，即重启操作，参见：ODSP.drbd.peradrbd.do_up，此步应该确保 down 掉的 drbd 全部 up 起来，后台显示 connect 状态。

等待建立连接的 drbd 自动恢复数据同步。

#### 恢复

用户点击仲裁重置按钮，此时首先判断是否具备仲裁恢复条件：每个 drbd 都恢复到 UpToDate/UpToDate 状态（表示数据恢复完成），参见：ODSP.drbd.peradrbd.before_reset_rfr，然后发起重置操作，重置成功修改数据库和配置，同时对刚才 refuse 掉的 drbd 进行 provide 操作。参见：ODSP.referee.take_action.provide，此时仲裁恢复。整个流程参见：ODSP.referee.perarefer.reset_referee

### 双控内部一台控制器宕机

根据 net 超时配置不同仲裁可能发生抢占，也有可能不发生。

#### 发生抢占
1. 如果是宕机（B1）端(B2)抢占到仲裁，则另一台机器（A）会 refuse

   ##### 接管
  
  此时未关机端会直接都不提供服务，drbd 全 down 掉，而关机这边存活的控制器(B2)在发生接管后升主并接管完成。
  
  *TODO：*
  
  - [ ] 此时是否会触发 after_sync_target 事件，如果不触发，又不使用界面的 reset 仲裁功能，A 端什么时候升主？
  
  ~~等待同步完成，A 端使用 ODSP.drbd_notify_action.TaggedActor.after_sync_target 逻辑自动升主并连接提供服务。~~

2. 如果非宕机端抢占到仲裁（A），宕机这边(B)也会接管资源
     A 机器继续提供读写服务，宕机端（B1）资源会在继续在线的控制器(B2)这边发生接管。涉及 drbd 部分逻辑参见：ODSP.diskraid.raidaction.switch_drbd

     - 接管
       1. 修改 take_over_all 逻辑，提供快速处理链路的方案（take_over_all 会因为无法断开而导致链路不返回失败，处理由于 drbd 设备没有升主无法完成 cache 接管操作），对双主 drbd 需要单独处理
       2. 只需要 ODSP.drbd_notify_action.TaggedActor.after_sync_target 脚本处理：升主、建立连接继续提供服务（此时链路通）
       
     - 恢复
       等待另一台控制器重新开机，此时需要先点击控制器管理界面的恢复接管。（目前 cache 连接会提示`connect is failed`）资源恢复，然后 drbd 处于 secondary 状态
    - [ ] 需要处理 scst 混合输出问题

等待另一台控制器重新开机，此时需要先点击控制器管理界面的恢复接管。目前 cache 连接会提示`connect is failed`，因为接管这边必须是 drbd primary 状态。而之前设计的逻辑是点击恢复仲裁才会去 drbd 升主。

#### 不发生抢占

暂时没有考虑

### 初始化

1. 如果没有发生仲裁，通过同步目标端的`ODSP.drbd_notify_action.TaggedActor#before_sync_target`通知输出同步源端，通过 sync_after 输出同步目标端（目前是点界面的，希望是主动的）；
2. 如果发生仲裁，则抢占成功端可以正常输出，代码参见`ODSP.san.digisan.decoratedealaddcahe`；抢占失败端和接管恢复一样，根据设计思路选择手动或者主动的输出方式（目前是点界面的，希望是主动的）；需要确保输出的配置和之前没有变化。
   - [ ] 需要处理 scst 混合输出问题

### scst 混合输出问题

​	初始化和恢复涉及 scstadm -config /etc/scst.conf, 该命令需要 drbd 卷均添加 cache 完毕，否则会报错甚至导致内核崩溃。

## 无仲裁

关机、重启操作和两台机器相继拔电源线会触发 bbu 事件。参见：`ODSP.referee.perarefer.bbu_notify`
我们的主导思想是：让先关机一边转变成镜像卷，而后关机的一台机器成为生产卷组，这样就可以保证即使两台机器都关机，也不会因为重新启动的先后顺序问题导致现在的数据更旧端变成生产卷使数据刷写下去。

这种状况下有三种情景需要考虑：

1. grp1 关机，grp2 保持开机（在关机机器重新开机过程中不关机）

   grp1 开机之后状态变为 Secondary/Primary。点击 reset 时需要通过 count 判断在哪边进行升主操作，如果 count 是 2，则说明是数据多端，则发送到镜像卷端去 provide 提供服务

2. grp1 关机，grp2 之后也关机

   开机之后是 Secondary/Secondary 状态。此时升主操作只能在现在的生产卷端（后关机节点）进行，然后点击界面 reset 重置仲裁。

3. 两台设备同时掉电关机

  此时可能同时 count=2 或者来不及置 count，则会发生脑裂！此时两边均不可升主(drbd 数据量可能会有细微差异)。
  
{% note info %}
我们现在限制只可以在生产卷端点击 reset，这样的话，peovide 只需要发送到对端（必然是镜像端）去执行即可，不需要耗时去判断那边是生产卷端。
{% endnote %}

{% note danger %}
**问题**
1. 由于网络异常，socket 置 count 未成功，则无法判断那边是最后数据多端
2. 如果镜像卷先关机，也需要置 count 表示发生仲裁
{% endnote %}

## 推荐阅读
[双活数据中心架构分析及优缺点_存储我最懂-CSDN 博客](https://blog.csdn.net/shouqian_com/article/details/52525021)
