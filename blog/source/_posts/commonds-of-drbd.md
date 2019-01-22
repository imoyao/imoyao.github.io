---
title: DRBD用户手册之命令篇
date: 2018-06-22 10:10:23
tags:
- DRBD
toc: true
---
本文基于`DRBD-8.4`版编写。
<!--more-->

# drbd.conf-配置文件

TODO

# drbdmeata-元数据

TODO

# drbd

TODO

# drbdadm-管理工具

## 名称

drbdadm - `DRBD`管理工具

## 概要

```
drbdadm [-d] [-c { file}] [-t {file}] [-s {cmd}] [-m { cmd}] [-S] [-h {host}] [-- { backend-options}] {command} [{all} | { resource[/volume>]...}]
```
## 描述

`Drbdadm`是`DRBD`程序套件的高级工具。 `Drbdadm`与`drbdsetup`和`drbdmeta`的关系可类比于 `ifup / ifdown`与`ifconfig` 。 `Drbdadm`通过调用`drbdsetup`和（或）`drbdmeta`程序读取相关配置文件并执行指定的命令。
`Drbdadm`可以运行整个资源或资源中的单个卷。 子命令： `attach` ， `detach` ， `primary` ， `secondary `， `invalidate` ， `invalidate-remote` ， `outdate` ， `resize` ， `verify` ， `pause-sync` ， `resume-sync` ， `role` ， `cstate` ， `dstate` ， `create-md` ， `show-gi` ， `get-gi` ， `dump-md` ， `wipe-md`可以作用于整个资源和单个卷上。
仅限资源级别的命令有：`connect`, `disconnect`, `up`, `down`, `wait-connect` 和 `dump` 。

## 选项

- -d ，-- dry-run

仅将`drbdsetup`的调用打印到`stdout`，但不会运行这些命令。

- -c ，-- config-file 文件

指定`drbdadm`将使用的配置文件。 如果未指定此参数，则`drbdadm`将查找`/etc/drbd-84.conf`、`/etc/drbd-83.conf`、`/etc/drbd-08.conf`和`/etc/drbd.conf` 。

- -t ，-- config-to-test 文件

指定一个额外的`drbdadm`检查文件。 该选项仅适用于`dump`和`sh-nop`命令。

- -s ，-- drbdsetup 文件

指定`drbdsetup`程序的完整路径。 如果省略此选项，`drbdadm`将首先内部查找它，然后在`PATH`环境变量中查找它。

- -m ，-- drbdmeta 文件

指定`drbdmeta`程序的完整路径。 如果省略此选项，`drbdadm`将首先内部查找它，然后在`PATH`中查找它。

- -S ， --stacked

指定应该在堆叠资源上执行此命令。

- -P ， --peer

指定要连接的对等节点。 只有当您正在使用的资源中有两个以上的主机时才需要此选项。

- 后端配置选项

双连字符（--）后面的所有选项都被视为后端选项。这些选项会传递给后端命令。 即`drbdsetup`、`drbdmeta`或`drbd-proxy-ctl` 。

## 命令

- attach

将本地支持块设备连接到DRBD资源的设备。

- detach

从DRBD资源的设备中删除备份存储设备。

- connect

建立资源设备的网络配置。 如果对等设备已配置，则两个`DRBD`设备将连接。 如果资源中有两个以上的主机部分，则需要使用`--peer`选项来选择要连接的对等端。

- disconnect

从资源中删除网络配置。 设备将进入`StandAlone`状态。

- syncer（注：`drbdadm --help` 未发现该命令）

将重新同步参数加载到设备中。

- up

是`attach`、`syncer`和 `connect`的快捷方式。

实际上，可以将`drbdadm up`拆分为以下几个动作：

1. 将drbd的资源关联到底层设备(metadata和data区)上，使之能通过底层设备存、取数据。该过程调用的是drbdsetup程序。
```
drbdadm attach drbd1
```
2. 加载drbd资源的同步参数。
```
drbdadm syncer drbd1
```
3. 连接对端。
```
drbdadm connect drbd1
```

这些命令在`drbdadm`中部分已弃用，放在这里只是为了说明`up`时所执行的几个步骤。

- down

是`disconnect` 和 `detach`的捷径。

- primary

将资源设备转化为主要角色。 您需要在访问设备之前执行此操作，如创建或挂载文件系统。

- secondary

将设备转回次要角色。 这是必需的，因为在连接状态的DRBD设备对中，两个节点中只能有一个节点是主端（除非在配置文件中明确设置了**allow-two-primaries** ）。

- invalidate

强制DRBD将本地存储设备上的数据视为不同步（out-of-sync）。 因此，DRBD将复制其对等体中的每个块，以使本地存储设备重新同步。 为避免竞争，你需要建立了的复制链接，或断开连接的次端。

- invalidate-remote

该命令类似于`invalidate`命令，但是是对等端的备份存储被视为无效，因此对端被本地节点的数据重写。 为避免竞争，您需要已建立的复制链接，或断开连接的主端。

- resize

`DRBD`重新检查所有大小限制，并相应调整资源的设备大小。 例如，如果您增加了备份存储设备的大小（当然是在两个节点上均进行次操作），那么在您的某个节点上调用此命令后，DRBD将采用新的大小。 由于必须同步新的存储空间，因此只有存在至少一个主节点时，此命令才可用。
`--size`选项可用于联机缩小`drbd`设备的可用大小。 用户必须负责确保设备上的文件系统不被该操作截断。
`--assume-peer-have-space`允许你调整当前未连接到对等设备的设备。 使用时需要小心，因为如果您不重新调整对等磁盘的大小，则两者的进一步连接尝试将失败。
`--assume-clean`允许您调整现有设备的大小并避免同步新的空间。 将附加空白存储添加到设备时，这样操作非常有用。 例：
```
# drbdadm -- --assume-clean resize r0
```
选项`-al-stripes`和`--al-stripe-size-kB`可用于在线更改 `activity log`的布局。 在使用内部元数据的情况下，这可能会同时缩小用户可见大小（使用`--size` ）或增加后备设备上的可用空间。

- check-resize

调用`drbdmeta`达到移动内部元数据的目的。 如果后台设备的大小已调整，而`DRBD`未运行，则必须将元数据移至设备的末尾，以便接下来的 `attach` 命令可以成功。

- create-md

初始化元数据存储。 这需要在`DRBD`资源首次上线之前完成。 如果有关于该命令的问题请看[drbdmeta](https://docs.linbit.com/man/v84/drbdmeta-8/)

- get-gi

显示数据生成标识符(`GI元祖`)的简短文字表示。

- show-gi

打印包含说明信息的数据生成标识符的文本表示。

- dump-md

以文本形式转储元数据存储的全部内容，包括存储的位图和活动日志。

- outdate

设置元数据中的过期标志。

- adjust

将设备的配置与你的配置文件同步。 在实际执行此命令之前，应始终检查`dry-run`模式的输出。

- wait-connect

等待设备连接到对等设备。

- role

显示设备的当前角色（local/peer）。 例如：`Primary/Secondary`

- state

不赞成使用（废止），“角色”的别名，参见上文。

- cstate

显示设备的当前连接状态。如：Connected、StandAlone等

- dump

解析配置文件并将其转储到`stdout`。 可用于检查配置文件的语法正确性。

- outdate

用于将节点的数据标记为过时。 通常由对等方的fence-peer处理程序使用。

- verify

开始在线验证。 在线验证期间，比较两个节点上的数据是否相等。 请参阅`/proc/drbd`进行在线验证。 如果发现不同步块，则它们不会自动重新同步。因此，请在验证完成后使用`disconnect` 和`connect`断开并连接资源。
另请参阅`drbd.conf`联机帮助页上有关数据完整性的注意事项。

- pause-sync

通过设置本地暂停标志暂时中止正在进行的重新同步。 如果本地和远程暂停标志均未设置，则同步进行。 可能需要推迟`DRBD`的重新同步到支持存储的`RAID`设置重新同步之后进行。

- resume-sync

取消设置本地同步暂停标志。

- new-current-uuid

生成新的`当前 UUID`并旋转所有其他UUID值。
这可以用来缩短集群的初始再同步。 有关更多详细信息，请参阅`drbdsetup`联机帮助页。

- dstate

以`local/peer`形式显示后备存储设备的当前状态。 如：UpToDate/UpToDate

- hidden-commands

显示所有命令没有记录的命令。

```shell

[root@imoyao ~]# drbdadm hidden-commands

These additional commands might be useful for writing   # 写脚本或许有用
nifty shell scripts around drbdadm:

 sh-nop                             sh-resources                       
 sh-resource                        sh-mod-parms                       
 sh-dev                             sh-udev                            
 sh-minor                           sh-ll-dev                          
 sh-md-dev                          sh-md-idx                          
 sh-ip                              sh-lr-of                           
 sh-b-pri                           sh-status                          
 proxy-up                           proxy-down                         
 new-resource                       

These commands are used by the kernel part of DRBD to   # drbd内核
invoke user mode helper programs:

 before-resync-target               after-resync-target                
 before-resync-source               pri-on-incon-degr                  
 pri-lost-after-sb                  fence-peer                         
 local-io-error                     pri-lost                           
 initial-split-brain                split-brain                        
 out-of-sync                        

These commands ought to be used by experts and developers:  # 开发人员

 sh-new-minor                       new-minor                          
 suspend-io                         resume-io                          
 set-gi                             new-current-uuid                   
 check-resize                       

```

# drbddisk.8

TODO

# drbdsetup.8-配置内核模块

TODO

# 版本信息

本文档针对DRBD发行版本8.4.0进行了修订。

# 作者

由Philipp Reisner <philipp.reisner@linbit.com>和Lars Ellenberg撰写<lars.ellenberg@linbit.com>。中译版由`imoyao`首发于别院牧志（`idealyard`）

# 报告错误

将错误报告给<drbd-user@lists.linbit.com>。

# 版权

版权所有2001-2011 LINBIT信息技术公司，Philipp Reisner，Lars Ellenberg。 这是免费软件; 请参阅复制条件的来源。 没有保修; 甚至不适用于适销性或针对特定用途的适用性。

# 推荐阅读

drbd.conf （5）， drbd （8）， drbddisk （8）， drbdsetup （8）， drbdmeta （8）和DRBD项目网站 [1]

# 参考链接

- [DRBD 8.4 Manual Pages](https://docs.linbit.com/man/v84/)