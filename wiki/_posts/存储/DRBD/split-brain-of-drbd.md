---
title: 关于 DRBD 裂脑问题的总结
date: 2018-05-27 10:57:00
tags:
- DRBD
- 裂脑
- 存储
cover: /images/logos/DRBD.png
subtitle: 裂脑一旦发生，需要及时排查问题所在，最大限度保护数据完整性。
reward: true
---
{% note info%}
本文在编写时基于[官网 8.4 英文版本](https://www.linbit.com/drbd-user-guide/users-guide-drbd-8-4/)。由于英语水平和当时认知所限，翻译中难免有聱牙诘屈甚至误导别人之处。今天翻阅官网发现已经出现了基于 9.0 版本的中文文档，所以大家可以直接去浏览[官方文档](https://www.linbit.com/drbd-user-guide/drbd-guide-9_0-cn/#about)。
{%endnote%}

## 什么是`DRBD`裂脑
裂脑(`split brain`)是指由于集群节点之间的所有网络链路的临时故障，以及可能由于集群管理软件的干预或人为错误，导致两个节点在断开连接时都切换到主节点（`primary`）角色的情况。这是一种潜在的有害状态，因为它意味着对数据的修改可能是在任一节点上进行的，而没有复制到对等节点。因此，在这种情况下，很可能已经创建了两个不同的数据集，这些数据集不能简单地合并。

## 怎么判定裂脑

### 查看日志信息

如果`DRBD`出现裂脑，会在 `/var/log/message` 出现一条日志：

```plain
Split-Brain detected but unresolved, dropping connection!
```
当发生`split brain`之后，如果查看连接状态，其中至少会有一个是`StandAlone`状态，另外一个可能也是`StandAlone`（如果是同时发现`split brain`状态），也有可能是 `WFConnection` 状态。

### 裂脑自动通知

如果进行配置，DRBD 会调用裂脑处理程序，当裂脑发生时就会被探测到。要配置这个程序，需要对资源`/etc/drbd.d/global_common.conf`添加如下配置：
```shell
resource <resource>

  handlers {

    split-brain <handler>;

    ...

  }

  ...

}
```

`<handler>`可能是目前系统中一个可执行的文件。

`Drbd`自带一个裂脑处理程序脚本`/usr/lib/drbd/notify-split-brain.sh`。它可以通过电子邮件的方式发送到指定的地址。要配合程序发送信息到 root@localhost（这假设是设置的系统管理员的邮件地址），配置如下：
```shell
resource <resource>

  handlers {

    split-brain "/usr/lib/drbd/notify-split-brain.sh root";

    ...

  }

  ...

}
```

当配置已经在资源上进行修改（同步到两个节点上），就不需要添加其他的处理就可以启动处理程序。`DRBD`会在下一次检测到裂脑时直接调用该处理程序。

如果要配置真实可用的报警邮箱地址，则除了将上面的通知地址改为真实邮件地址:
```shell
split-brain "/usr/lib/drbd/notify-split-brain.sh foo@bar.com
```
还需要修改一下`ssmtp`配置文件：
```shell
vim /etc/ssmtp/ssmtp.conf
# 填写真实收件服务器信息
mailhub=mail.masantu.com:25
```
更多配置参见 [这里 SSMTP - ArchWiki](https://wiki.archlinux.org/index.php/SSMTP)

### 世代标识符元组（GI）
参见[16.2. Generation Identifiers](https://docs.linbit.com/docs/users-guide-8.4/#s-gi)

DRBD 将其备份的数据的更新变化过程比拟成人类世代繁衍的过程。每个时点同一个双机的 DRBD 的两个节点上的数据都来自于同一份原始数据，我们可认为这个时点上两份数据源于同一祖先。主备节点的 DRBD 都会用一个叫作 GI(Generation ID)的标识符来标识当前的数据是哪个世代的，同样也会记录最近两个数据祖先的 GI 用于追朔当前数据的历史来源。DRBD 可以据此来判断两个节点是否是属于同一个双机,因为同一个双机的两份数据应该是从同一个祖先而来。
GI 作为 DRBD 的内部机制主要被用来：

1. 确定这两个节点是否是事实上的同一个集群的成员（而不是意外连接的两个节点）；
2. 确定触发全盘同步（`full re-synchronization`）还是只触发部分同步（`partial re-synchronization`）。
3. 确定后台重新同步的方向（如果需要全盘同步）；
4. 确定裂脑。

#### 数据迭代

当出现下列情形里`DRBD`会生成一个新的`GI`，用来标识新一代的数据：

1. 第一次全盘同步时；
2. 一个`Disconnected`的资源转换为`Primary`时；
3. 一个`Primary`的资源转换为`Disconnected`时。

因此,我们可以总结出：只要一个`DRBD`资源处于`Connected`的状态，并且两边磁盘的状态为`UpToDate`，那么此`DRBD`资源在两个节点上的`GI`一定是一样的。此结论反过来也同样成立。请注意，**当前实现使用最低位来编码节点的角色(`Primary/Secondary`)。 因此，即使它们被认为具有相同的数据生成，最低位在不同节点上也可能不同。**

每个新的数据生成都由一个`8`字节的通用唯一标识符（`UUID`）来标识。

#### `GI`元祖

`DRBD`在本地资源元数据中保存有关当前和历史数据生成的四条信息：

- 当前`UUID(C-UUID)`
从本地节点的角度来看，这是当前数据生成的生成标识符。 当资源被连接并完全同步时，当前`UUID`在节点之间是相同的。

- 位图`UUID(B-UUID)`
这是磁盘上同步位图跟踪的生成的`UUID`更改。 作为磁盘上的同步位图本身，此标识符仅在断开模式下才有用。 如果资源已连接，则此`UUID`始终为空（零）。

- 两个`历史UUID`

这些是当前之前两个数据世代的标识符。
1. 上一代数据的`UUID(H1-UUID)`；
2. 最近第二代数据的`UUID(H2-UUID)`，即上一代数据的上一代数据的`UUID`。

总的来说，这四个项目被称为代码标识符元组，或简称为`GI元组`。

#### `GI`如何变化

- 开始新的数据生成代

当节点与其对等方失去连接时（网络故障或人工干预都有可能），DRBD 将按照以下方式修改其本地生成标识符：

![图1 GI元祖在生成新的数据代时改变](/images/gi-changes-newgen.png)

1. 为新的数据代生成新的`UUID`，变为主节点的`C-UUID`；
2. 之前的 UUID 现在指向位图（`B-UUID`）以跟踪数据变化，因此它成为主节点的新位图`UUID`；
3. 备节点 GI 元祖保持不变。

- 开始重新同步

在开始重新同步时，`DRBD`在本地代标识符上执行如下修改：

![图2 GI元祖在重新开始同步时改变](/images/gi-changes-syncstart.png)

1. 在同步源端的`当前UUID`（C-UUID）保持不变；
2. 同步源端的`位图UUID`轮转为`第一历史UUID`（H1-UUID）；
3. 同步源端生成新的`位图UUID`（B-UUID）;
4. 该 UUID（_应指同步源端生成的`B-UUID`_）变为同步目标端的新的`当前UUID`（C-UUID）；
5. 同步目标端的`位图UUID`（B-UUID）和`历史UUID`（H1-UUID,H2-UUID）保持不变。

- 重新同步结束

当重新同步结束后，将执行以下更改：

![图3 当重新同步结束后，GI元祖发生改变](/images/gi-changes-synccomplete.png)

1. 同步源端`当前UUID`(C-UUID)保持不变；
2. 同步源端的`位图UUID`(B-UUID)轮转为`第一历史UUID`（H1-UUID），同时该 UUID(指`H1-UUID`)轮转为`第二历史UUID`(现有的第二历史 uuid 被丢弃)；
3. 同步源端的`位图UUID`(B-UUID)清空（置零）；
4. 同步目标端采用同步源端整个`GI元祖`。

当节点之间建立连接之后，两个节点之间会交换当前可用的代标识符,然后根据比对的结果采取相应的操作。以下是可能的几种结果：

- 两个节点上的当前`UUID(C-UUID)`都为空
本地节点检测到它的当前`UUID`和对方的当前`UUID`都是空的。这通常是发生于尚未启动初始完全同步的新配置资源的正常情况。此时没有同步发生;须手动人为触发启动。
- 单一节点上的当前`UUID(C-UUID)`为空
本地节点检测到对方的当前`UUID`为空，而其本身非空。这是新配置资源的正常情况，此时初始全盘同步刚刚触发，本地节点被选为初始同步源（`sync source`）。 `DRBD`将磁盘上的同步位图(`sync bitmap`)中的所有位全部置位（意味着它认为整个设备不同步），并开始将其作为同步源同步。相反，（即本地当前`UUID`为空，对等节点非空），除了本地节点成为同步目标（`sync target`）之外，`DRBD`执行相同的步骤。
- 当前`UUID(C-UUID)`相等
本地节点检测到它的当前`UUID`和对等节点的当前`UUID`非空且相等时。这是资源在`secondary`状态进入断开连接（`disconnected`）模式时的正常情况，并且在断开连接时并未在任一节点上升为 `primary` 状态。此时不会触发同步，因为两边的数据一致，没有必要。
- 位图`UUID（B-UUID）`匹配对等节点的当前``UUID（`C-UUID`）``
本地节点检测到其位图`UUID`匹配对等节点的当前`UUID`，且对等节点的位图`UUID`为空。这是本地节点处于 `primary` 状态，次要节点故障后正常且预期的情况。这意味着对端在此期间永远不会变为`primary`状态，并始终以相同的数据生成为前提运行。 `DRBD`此时以本地节点作为同步源（`sync source`）启动正常的后台重新同步（`re-sync`）。相反，如果本地节点检测到其位图`UUID`为空，且对等节点的位图与本地节点的当前`UUID`匹配，那么这是本地节点失败后的正常和预期情况。同样地，`DRBD`此时启动正常的后台重新同步，只不过本地节点成为同步目标（`sync target`）。
- 当前`UUID(C-UUID)`匹配对等节点的历史`UUID（h-UUID）`
本地节点检测到其当前`UUID`与对等节点的历史`UUID`之一(`h1/h2`)匹配。这意味着尽管两个数据集共享一个共同的祖先且对等节点具有最新的数据，但保存在对等节点的位图中的信息已过时并且不可用。因此，简单的正常同步不够的。 `DRBD`此时将整个设备标记为未同步（`out-of-sync`）并启动以本地节点作为同步目标（`sync target`）的全盘后台重新同步。在相反的情况下（本地节点的某个历史`UUID`与对等节点的当前`UUID`相匹配），除了本地节点成为同步源（`sync source`）之外，`DRBD`执行相同的步骤。
- 位图`UUID（B-UUID）`匹配，当前 `UUID(C-UUID)`不匹配
本地节点检测到其当前`UUID`与对等节点的当前`UUID`不同且位图`UUID`匹配。这是裂脑（`split brain`）的一种情况，两份数据有相同的父代。这意味着`DRBD`可以调用裂脑自动恢复策略进行数据恢复（如果已配置）。否则，`DRBD`断开连接并等待手动恢复。
- 当前`UUID（C-UUID）`和位图`UUID(B-UUID)`都不匹配
本地节点检测到它的当前`UUID`与对等节点的当前`UUID`不同，并且位图`UUID`不匹配。这是两份数据与无关父代产生的一种裂脑，因此即使配置了自动恢复策略也没有意义。 `DRBD`处于断开连接并等待手动恢复状态。
- 没有`UUID`匹配
最后，如果`DRBD`未能检测到两个节点之间的`GI`元组中的单个元素匹配，则会记录关于无关数据（`unrelated data`）的警告并断开连接。这是`DRBD`的防范措施，可防止之前无关联的两个集群节点的意外连接导致数据破坏。

以上逻辑使用代码表示如下：

```Python

empty_uuid = '0000000000000000'

def slice_seq(seq):
    """
    对GI元祖内元素进行切片操作
    :param seq: GI元祖
    :return:type:list
    """
    global empty_uuid
    sliced_seq = [item[:-1] if item != empty_uuid else item for item in seq]
    return sliced_seq


def cmp_both(seqa,seqb):
    for i in seqa:
        if i not in seqb:
            return 1
    return 0


def get_gi_action(drbdname):
    """
    调用'drbdadm get-gi DRBDNAME'命令获取drbd的 GI(Generation ID) 信息
    :param drbdname:type:str,drbd名称 like:'drbds1/drbdn301'
    :return:获取正常返回元祖(c_uuid, b_uuid, h1_uuid, h2_uuid)，获取失败返回None
    """
    get_gi_cmd = "drbdadm get-gi %s |awk -F: '{print $1,$2,$3,$4}'"%(drbdname)
    retcode,proc = utils.cust_popen(get_gi_cmd)
    message = proc.stderr.read(), proc.stdout.read()
    retstr = message[1]
    if retstr:
        c_uuid,b_uuid,h1_uuid,h2_uuid = tuple(retstr.split())
        return c_uuid,b_uuid,h1_uuid,h2_uuid
    else:
        debug.write_debug(debug.LINE(), "peradrbd", message)
        return None
  
        
def get_remote_gi(params):
    rtndata = {}
    result = {}
    drbdname = 'drbdname' in params and params['drbdname'] or ''
    if drbdname:
        if hasthedrbd(drbdname):
            gi_uuids = get_gi_action(drbdname)
            if gi_uuids is not None:
                rtndata['state'] = '0'
                result['message'] = ''
                result['gi_id'] = gi_uuids
            else:
                rtndata['state'] = '1'
                result['message'] = '11069'     # 获取 gi_id 出错
                result['gi_id'] = None
        else:
            rtndata['state'] = '1'
            result['message'] = '11060'  # the drbd not found

        rtndata['result'] = result
    else:
        rtndata = {'state': '1', 'result': {'message': '11059'}}  # drbdname error
    return rtndata


def exchange_gi_process(drbdname):
    """
    see:https://docs.linbit.com/docs/users-guide-8.4/#s-gi (16.2.4. How DRBD uses generation identifiers)
    :param drbdname:
    :return:type:str
    """
    local_gis = get_gi_action(drbdname)
    remote_gis = None
    global remoteip
    retresult = hautils.socketclient(ip=remoteip,
                                     **{'target': 'drbd', 'op': 'getremotegi', 'params': {'drbdname':drbdname}})
    if retresult:
        if retresult['state'] == '0':
            remote_gis = retresult['result']['gi_id']
        drbd_next = ''
        if local_gis is not None and remote_gis is not None:
            local_gis_sliced = slice_seq(local_gis)
            remote_gis_sliced = slice_seq(remote_gis)
            global empty_uuid
            print('sliced', local_gis_sliced, remote_gis_sliced)
            if local_gis_sliced[0] == empty_uuid and remote_gis_sliced[0] == empty_uuid:
                drbd_next = 'no_sync:(manual_sync)'

            elif local_gis_sliced[0] == empty_uuid or remote_gis_sliced[0] == empty_uuid:
                if remote_gis_sliced[0] == empty_uuid and local_gis_sliced[0] != empty_uuid:
                    drbd_next = 'full_re_sync:(local_source)'
                elif local_gis_sliced[0] == empty_uuid and remote_gis_sliced[0] != empty_uuid:
                    drbd_next = 'full_re_sync:(local_target)'

            elif local_gis_sliced[0] != empty_uuid and remote_gis_sliced[0] != empty_uuid and local_gis_sliced[0] == remote_gis_sliced[0]:
                drbd_next = 'consistent:(both_secondary)'

            elif local_gis_sliced[1] == remote_gis_sliced[0] and remote_gis_sliced[1] == empty_uuid:
                drbd_next = 'partial_re_sync:(local_source)'
            elif local_gis_sliced[1] == empty_uuid and remote_gis_sliced[1] == local_gis_sliced[0]:
                drbd_next = 'partial_re_sync:(local_target)'

            elif local_gis_sliced[0] in [remote_gis_sliced[2], remote_gis_sliced[3]]:
                drbd_next = 'full_re_sync:(local_target)'
            elif remote_gis_sliced[0] in [local_gis_sliced[2], local_gis_sliced[3]]:
                drbd_next = 'full_re_sync:(local_source)'

            elif local_gis_sliced[0] != remote_gis_sliced[0]:
                if local_gis_sliced[1] == remote_gis_sliced[1]:
                    drbd_next = 'split_brain:(auto_recover_able)'
                elif local_gis_sliced[1] != remote_gis_sliced[1]:
                    drbd_next = 'split_brain:(wait_for_manual_recover)'

            elif cmp_both(local_gis_sliced,remote_gis_sliced):
                drbd_next = 'unrelated_data:(wait_for_manual_recover)'
            else:
                debug.write_debug(debug.LINE(), "peradrbd", (local_gis_sliced, remote_gis_sliced))
        else:
            debug.write_debug(debug.LINE(), "peradrbd", (local_gis,remote_gis))
        return drbd_next

```

{%note info%}
**注意**
经分析官方文档中的`matches`并不是完全相等，而 `UUID is always empty (zero)` 是指 "'0'*16" 的字符串！
{%endnote%}

## 如何模拟一个 `Split-Brain`状态

1. 往主节点写入大文件，在未写入完前停止备节点的`DRBD`；
```plain
# on secondary
drbdadm down drbdxx
```
2. 停止主节点的`DRBD`；
```plain
# on primary
drbdadm down drbdxx
```
3. 启动备节点的`DRBD`，设置为主节点；
```plain
# on secondary
drbdadm up drbdxx
drbdadm primary drbdxx
```
4. 启动原主节点的`DRBD`，这时发现它的状态就是`StandAlone Secondary/Unknown UpToDate/DUnknown`，`Split-Brain` 情况出现。
```plain
# on primary
drbdadm up drbdxx
```

## 解决 DRBD 裂脑状态

### 设置自动修复
参见[5.17.2. Automatic split brain recovery policies](https://docs.linbit.com/docs/users-guide-8.4/#s-configure-split-brain-behavior )

{%note warning%}
**警告**
配置`DRBD`自动修复裂脑（或其他状况）导致的数据分歧情况可能使正在配置的数据丢失，如果你不知道你在干什么，那最好别干。（NO ZUO NO DIE）
{%endnote%}
{%note info%}
**提示**
您更应该查看系统防护策略，集群管理集成和冗余集群管理器通信连接状态，以避免出现数据分歧。（防患于未然而不是亡羊补牢）
{%endnote%}

在启用和配置`DRBD`的自动裂脑恢复策略之前，您必须了解`DRBD`为此提供了多种配置选项。 `DRBD` 根据检测到裂脑时主节点（`Primary role`）的数量应用其裂脑恢复程序。为此，`DRBD` 检查以下关键字，这些关键字均可在资源的网络配置部分中找到：

#### after-sb-0pri

裂脑被检测到的同时该资源在任一节点不是主节点。对于这种状况，`DRBD`可以理解以下关键字：
- disconnect: 不自动恢复，只调用裂脑通知程序（如果已配置），断开连接并保持断开；
- discard-younger-primary: 丢弃并回滚最后升主节点的改动；
- discard-least-changes: 丢弃并回滚修改更少节点的修改；
- discard-zero-changes: 如果有某一节点一点未改动，只需应用对另一主机所做的修改并继续；

#### after-sb-1pri

裂脑刚被检测到的同时该资源在一个节点上是主节点。对于这种状况，`DRBD`理解以下关键字：
- disconnect:同上
- consensus：应用上一步的策略之后，如果裂脑受害者可以选择拆分则会自动解决。否则，与`disconnect`指令相同。
- call-pri-lost-after-sb：应用上一步的策略之后，如果裂脑受害者节点可以选择拆分则调用`pri-lost-after-sb`处理程序，该处理程序必须在处理程序中进行配置，并且需要强制从集群中删除该节点。
- discard-secondary：将从端（`Secondary role`）节点视为裂脑受害者。

#### after-sb-2pri

裂脑刚被检测到时该资源在两个节点都处于主端。该选项接受与除`discard-secondary` 和 `consensus` 之外与 `after-sb-1pri` 相同的关键字。
{%note info%}
**提示**
`DRBD`还可以理解这三个选项下额外的关键字，这些关键字在这里被省略，因为它们很少被使用。请参阅`drbd.conf`的手册页以获取有关裂脑恢复关键字的详细信息，此处不再讨论。
{%endnote%}
例如，用作双主模式下`GFS`或`OCFS2`文件系统的块设备的资源可能会将其恢复策略定义如下：

```shell
resource <resource> {
  handlers {
    split-brain "/usr/lib/drbd/notify-split-brain.sh root"      # 脚本通知root用户，此处可以使用邮件提醒
    ...
  }
  net {
    after-sb-0pri discard-zero-changes;
    after-sb-1pri discard-secondary;
    after-sb-2pri disconnect;
    ...
  }
  ...
}
```

### 手动恢复

[6.3. Manual split brain recovery](https://docs.linbit.com/docs/users-guide-8.4/#s-resolve-split-brain)

在检测到裂脑后，一个节点将始终使资源处于`StandAlone`连接状态。另一个可能也处于`StandAlone`状态（如果两个节点同时检测到裂脑）或`WFConnection`（如果某方节点在另一节点检测到裂脑之前断开连接）。

此时，除非已将`DRBD`配置为自动从裂脑状态中恢复，否则必须通过选择一个节点进行手动干预，该节点的修改将被丢弃（此节点称为裂脑受害者）。这个干预使用下面步骤完成：

裂脑受害者需要处于`StandAlone`的连接状态，否则以下命令将返回错误。您可以通过发出以下内容确保它是`StandAlone`的：
```shell
drbdadm disconnect <resource>
drbdadm secondary <resource>
drbdadm connect --discard-my-data <resource>    # 8.4+  if 8.3,use 'drbdadm -- --discard-my-data connect <resource>' instead
```
在另一个节点（裂脑幸存者）上，如果它的连接状态也是`StandAlone`，你可以输入：
```shell
drbdadm connect <resource>
```
如果节点已处于`WFConnection`状态，则可以省略此步骤;它会自动重新连接。

如果受裂脑影响的资源是**堆叠**资源，请使用`drbdadm --stacked`而不是`drbdadm`。

连接后，裂脑受害者立即将其连接状态更改为`SyncTarget`，并将其导致裂脑的修改由其余主节点的数据覆盖。

裂脑受害者不会引发全盘同步。相反，它的局部修改已经被回滚，对裂脑幸存者的任何修改都会传递给受害者。
重新同步完成后，裂脑被视为已解决（`resolved`），两个节点再次形成完全一致的冗余复制存储系统（`DRBD`）。

## 参考链接

- [User’s Guide 8.4.x](https://docs.linbit.com/docs/users-guide-8.4/)
- [关于 DRBD v8.3 的同步机制](http://blog.sina.com.cn/s/blog_a30f2be401016d04.html)
- [一次 DRBD 裂脑行为的模拟](http://myhat.blog.51cto.com/391263/606318/)
- [drbd 裂脑处理 | IT 瘾](http://itindex.net/detail/50197-drbd)
- [什么是 DRBD 脑裂及如何模拟 DRBD 脑裂](http://www.3mu.me/%E4%BB%80%E4%B9%88%E6%98%AFdrbd%E8%84%91%E8%A3%82%E5%8F%8A%E5%A6%82%E4%BD%95%E6%A8%A1%E6%8B%9Fdrbd%E8%84%91%E8%A3%82/)
- [drbd 中 metadata 的理解(原创) – 蚊子世界](http://www.wenzizone.cn/2009/10/29/drbd%e4%b8%admetadata%e7%9a%84%e7%90%86%e8%a7%a3%e5%8e%9f%e5%88%9b.html)
