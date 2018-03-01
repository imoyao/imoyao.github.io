---
title: DRBD 脑裂问题
date: 2018-02-27 10:57:00
tags:
- DRBD
- 脑裂
---

什么是DRBD脑裂

脑裂(split brain)实际上是指在某种情况下，造成drbd的两个节点断开了连接，都以primary的身份来运行。当drbd某primary节点连接对方节点准备发送信息的时候如果发现对方也是primary状态，那么会会立刻自行断开连接，并认定当前已经发生split brain了，这时候他会在系统日志中记录以下信息：“Split-Brain detected,dropping connection!”当发生split brain之后，如果查看连接状态，其中至少会有一个是StandAlone状态，另外一个可能也是StandAlone（如果是同时发现split brain状态），也有可能是WFConnection的状态。

解决DRBD脑裂

如果DRBD出现脑裂，会在/var/log/message 出现一条日志：

1
Split-Brain detected but unresolved, dropping connection!
同时DRBD状态变为Unknown。

要解决这种情况，必须选择一个应丢弃其修改的节点，在要删除修改的节点上执行：

#drbdadm secondary db  #db是资源名名
#drbdadm -- --discard-my-data connect all (或者使用资源组代替all)
在需要保留数据的另一节点上执行

#drbdadm connect db
注意：如果执行

1
drbdadm -- --discard-my-data connect all 
2
时出错误
3
r0: Failure: (102) Local address(port) already in use.
4
那么先在主上执行drbdadm connect db，然后再到从上执行
5
drbdadm -- --discard-my-data connect all 
6
就可以了
如何模拟Split-Brain

(1) 往主节点写入大文件，在未写入完前停止备节点的DRBD
(2) 停止主节点的DRBD
(3) 启动备节点的DRBD，设置为主节点.
(4) 启动原主节点的DRBD，这时发现它的状态就是Unknown，Split-Brain 情况出现。

一次DRBD脑裂行为的模拟

模拟总结：
1、DRBD的资源只能在主或辅的一台机器上挂载。
2、在做主辅的手工切换时的步骤：
a、先将原来挂载的东西进行卸载，这个时候你的应用会停，不建议手工切换主辅
b、将原来的主设置成辅 #drbdadm secondary resource_name
c、将原来的辅设置成主 #drbdadm primary resource_name
d、挂载资源

更多详情请见：

一次DRBD脑裂行为的模拟：http://myhat.blog.51cto.com/391263/606318/

http://www.3mu.me/%E4%BB%80%E4%B9%88%E6%98%AFdrbd%E8%84%91%E8%A3%82%E5%8F%8A%E5%A6%82%E4%BD%95%E6%A8%A1%E6%8B%9Fdrbd%E8%84%91%E8%A3%82/

drbd中metadata的理解[原创] – 蚊子世界
http://www.wenzizone.cn/2009/10/29/drbd%e4%b8%admetadata%e7%9a%84%e7%90%86%e8%a7%a3%e5%8e%9f%e5%88%9b.html