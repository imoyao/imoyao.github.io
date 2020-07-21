---
title: CEPH 集群操作入门--配置
toc: true
date: 2020-05-26 12:27:56
tags: CEPH
---

# 概述

Ceph 存储集群是所有 Ceph 部署的基础。 基于 RADOS，Ceph 存储集群由两种类型的守护进程组成：Ceph OSD 守护进程（OSD）将数据作为对象存储在存储节点上; Ceph Monitor（MON）维护集群映射的主副本。 Ceph 存储集群可能包含数千个存储节点。 最小系统将至少有一个 Ceph Monitor 和两个 Ceph OSD 守护进程用于数据复制。

Ceph 文件系统，Ceph 对象存储和 Ceph 块设备从 Ceph 存储集群读取数据并将数据写入 Ceph 存储集群。

配置和部署

Ceph 存储集群有一些必需的设置，但大多数配置设置都有默认值。 典型部署使用部署工具来定义集群并引导监视器。 有关 ceph-deploy 的详细信息，请参阅部署。

# 配置

## 存储设备

### 概述

有两个 Ceph 守护进程将数据存储在磁盘上：

Ceph OSD（或 Object Storage Daemons）是 Ceph 中存储大部分数据的地方。 一般而言，每个 OSD 都由单个存储设备支持，如传统硬盘（HDD）或固态硬盘（SSD）。 OSD 还可以由多种设备组合支持，例如用于大多数数据的 HDD 和用于某些元数据的 SSD（或 SSD 的分区）。 集群中 OSD 的数量通常取决于将存储多少数据，每个存储设备的大小以及冗余的级别和类型（复制或纠删码）。

Ceph Monitor 守护程序管理集群状态，如集群成员和身份验证信息。 对于较小的集群，只需要几 GB，但对于较大的集群，监控数据库可以达到几十甚至几百 GB。

### 准备硬盘

Ceph 注重数据安全，就是说， Ceph 客户端收到数据已写入存储器的通知时，数据确实已写入硬盘。使用较老的内核（版本小于 2.6.33 ）时，如果日志在原始硬盘上，就要禁用写缓存；较新的内核没问题。

用 hdparm 禁用硬盘的写缓冲功能。

sudo hdparm -W 0 /dev/hda 0 

在生产环境，我们建议操作系统和 OSD 数据分别放到不同的硬盘。如果必须把数据和系统放在同一硬盘里，最好给数据分配一个单独的分区。

### OSD 后端

OSD 可以通过两种方式管理它们存储的数据。从 Luminous 12.2.z 版本开始，新的默认（和推荐）后端是 BlueStore。在 Luminous 之前，默认（也是唯一的选项）是 FileStore。

#### BLUESTORE

BlueStore 是一种专用存储后端，专为管理 Ceph OSD 工作负载的磁盘数据而设计。在过去十年中，使用 FileStore 支持和管理 OSD 的经验激发了它的动力。关键的 BlueStore 功能包括：

* 直接管理存储设备。 BlueStore 使用原始块设备或分区。这避免了可能限制性能或增加复杂性的任何中间抽象层（例如 XFS 等本地文件系统）。
* 使用 RocksDB 进行元数据管理。我们嵌入了 RocksDB 的键/值数据库，以便管理内部元数据，例如从对象名到磁盘上的块位置的映射。
* 完整数据和元数据校验和。默认情况下，写入 BlueStore 的所有数据和元数据都受一个或多个校验和的保护。在未经验证的情况下，不会从磁盘读取数据或元数据或将其返回给用户。
* 内联压缩。在写入磁盘之前，可以选择压缩写入的数据。
* 多设备元数据分层。 BlueStore 允许将其内部日志（预写日志）写入单独的高速设备（如 SSD，NVMe 或 NVDIMM）以提高性能。如果有大量更快的存储空间可用，内部元数据也可以存储在速度更快的设备上。
* 高效的写时复制。 RBD 和 CephFS 快照依赖于在 BlueStore 中高效实现的写时复制克隆机制。这能为常规快照和 erasure coded pools（依赖于克隆以实现有效的两阶段提交）实现更高效的 IO。

#### FILESTORE

FileStore 是在 Ceph 中存储对象的传统方法。它依赖于标准文件系统（通常为 XFS）与键/值数据库（传统上为 LevelDB，现为 RocksDB）的组合，用于某些元数据。FileStore 经过了充分测试并广泛用于生产，但由于其整体设计和依赖传统文件系统来存储对象数据而遭受许多性能缺陷。虽然 FileStore 通常能够在大多数 POSIX 兼容的文件系统（包括 btrfs 和 ext4）上运行，但我们只建议使用 XFS。 btrfs 和 ext4 都有已知的漏洞和缺陷，它们的使用可能会导致数据丢失。默认情况下，所有 Ceph 配置工具都将使用 XFS。

OSD 守护进程有赖于底层文件系统的扩展属性（ XATTR ）存储各种内部对象状态和元数据。底层文件系统必须能为 XATTR 提供足够容量， btrfs 没有限制随文件的 xattr 元数据总量； xfs 的限制相对大（ 64KB ），多数部署都不会有瓶颈； ext4 的则太小而不可用。使用 ext4 文件系统时，一定要把下面的配置放于 ceph.conf 配置文件的 \[osd\] 段下；用 btrfs 和 xfs 时可以选填。

filestore xattr use omap = true 

## 配置 Ceph

### 概述

你启动 Ceph 服务时，初始化进程会把一系列守护进程放到后台运行。 Ceph 存储集群运行两种守护进程：

* Ceph 监视器 （ ceph-mon ）
* Ceph OSD 守护进程 （ ceph-osd ）

要支持 Ceph 文件系统功能，它还需要运行至少一个 Ceph 元数据服务器（ ceph-mds ）；支持 Ceph 对象存储功能的集群还要运行网关守护进程（ radosgw ）。为方便起见，各类守护进程都有一系列默认值（很多由 ceph/src/common/config\_opts.h 配置），你可以用 Ceph 配置文件覆盖这些默认值。

### 选项名称

所有 Ceph 配置选项都有一个唯一的名称，由用小写字符组成的单词组成，并用下划线（\_）字符连接。

在命令行中指定选项名称时，可以使用下划线（\_）或短划线（ \- ）字符进行互换（例如， \- mon-host 相当于--mon\_host）。

当选项名称出现在配置文件中时，也可以使用空格代替下划线或短划线。

### 配置来源

每个 Ceph 守护程序，进程和库将从以下列出的几个源中提取其配置。 当两者都存在时，列表中稍后的源将覆盖列表中较早的源。

* 编译后的默认值
* 监视器集群的集中配置数据库
* 存储在本地主机上的配置文件
* 环境变量
* 命令行参数
* 由管理员设置的运行时覆盖

Ceph 进程在启动时所做的第一件事就是解析通过命令行，环境和本地配置文件提供的配置选项。 然后连接监视器集群，检测配置是否可用。 一旦完成检测，如果配置可用，守护程序或进程启动就会继续。

BOOTSTRAP 选项  
由于某些配置选项会影响进程联系监视器，认证和恢复集群存储配置，因此可能需要将它们存储在本地节点上并设置在本地配置文件中。这些选项包括：

* mon\_host，集群的监视器列表
* mon\_dns\_serv\_name（默认值：ceph-mon），用于通过 DNS 检查以识别集群监视器的 DNS SRV 记录的名称
* mon\_data，osd\_data，mds\_data，mgr\_data 以及类似的选项用来定义守护程序存储其数据的本地目录
* keying，ketfile，and/or key，可用于指定用于向监视器进行身份验证的身份验证凭据。请注意，在大多数情况下，默认密钥环位置位于上面指定的数据目录中。

在绝大多数情况下，这些的默认值是合适的，但 mon\_host 选项除外，它标识了集群监视器的地址。当 DNS 用于识别监视器时，可以完全避免本地 ceph 配置文件。任何进程可以通过选项--no-mon-config 以跳过从集群监视器检索配置的步骤。 这在配置完全通过配置文件管理或监视器集群当前已关闭但需要执行某些维护活动的情况下非常有用。

### 配置

任何给定的进程或守护程序对每个配置选项都有一个值。但是，选项的值可能会因不同的守护程序类型而异，甚至是相同类型的守护程序也会有不同的配置。Ceph 选项存储在监视器配置数据库或本地配置文件中被分组为多个部分，以指示它们应用于哪些守护程序或客户端。

这些部分包括：

* \[global\]

　　描述：全局下的设置会影响 Ceph 存储集群中的所有 daemon 和 client。  
　　示例：

log\_file = /var/log/ceph/\$cluster-\$type.\$id.log

* \[mon\]

　　描述：mon 下的设置会影响 Ceph 存储集群中的所有 ceph-mon 守护进程，并覆盖全局中的相同设置。  
　　示例：mon\_cluster\_log\_to\_syslog = true

* \[mgr\]

　　说明：mgr 部分中的设置会影响 Ceph 存储群集中的所有 ceph-mgr 守护程序，并覆盖全局中的相同设置。  
　　示例：mgr\_stats\_period = 10

* \[osd\]

　　描述：osd 下的设置会影响 Ceph 存储集群中的所有 ceph-osd 守护进程，并覆盖全局中的相同设置。  
　　示例：osd\_op\_queue = wpq

* \[mds\]

　　描述：mds 部分中的设置会影响 Ceph 存储集群中的所有 ceph-mds 守护程序，并覆盖全局中的相同设置。  
　　示例：mds\_cache\_size = 10G

* \[client\]

　　描述：客户端下的设置会影响所有 Ceph 客户端（例如，挂载的 Ceph 文件系统，挂载的 Ceph 块设备等）以及 Rados Gateway（RGW）守护程序。  
　　示例：objecter\_inflight\_ops = 512

  
还可以指定单个守护程序或客户端名称。例如，mon.foo，osd.123 和 client.smith 都是有效的节名。

任何给定的守护程序都将从全局部分，守护程序或客户端类型部分以及指定名称的部分中提取其设置。指定名称部分中的设置优先，例如，如果在同一源（即，在同一配置文件中）的 global，mon 和 mon.foo 中指定了相同的选项，则将使用 mon.foo 值。

请注意，本地配置文件中的值始终优先于监视器配置数据库中的值，而不管它们出现在哪个部分。

### 元变量

元变量可以显着简化 Ceph 存储集群配置。 当在配置值中设置元变量时，Ceph 会在使用配置值时将元变量扩展为具体值。 Ceph 元变量类似于 Bash shell 中的变量扩展。Ceph 支持以下元变量：

* \$cluster

　　描述：扩展为 Ceph 存储群集名称。 在同一硬件上运行多个 Ceph 存储集群时很有用。  
　　例如：

/etc/ceph/\$cluster.keyring

　　默认值：CEPH

* \$type

　　描述：扩展为守护进程或进程类型（例如，mds，osd 或 mon）  
　　例如：

/var/lib/ceph/\$type

* \$id

　　描述：扩展为守护程序或客户端标识符。 对于 osd.0，这将是 0; 对于 mds.a，它将是 a。  
　　例如：

/var/lib/ceph/\$type/\$cluster-\$id

* \$host

　　描述：扩展为运行进程的主机名。

* \$name

　　描述：扩展为

\$type.\$id

　　例如：

/var/run/ceph/\$cluster-\$name.asok

* \$ pid

　　描述：扩展为守护进程 pid。  
　　例如：

/var/run/ceph/\$cluster-\$name-\$pid.asok

### 配置文件

默认的 Ceph 配置文件位置相继排列如下：

1.  \$CEPH\_CONF（CEPH\_CONF 环境变量所指示的路径）;
2.  \-c path / path（-c 命令行参数）;
3.  /etc/ceph/ceph.conf
4.  〜/.ceph/配置
5.  ./ceph.conf（就是当前所在的工作路径。
6.  仅限 FreeBSD 系统， /usr/local/etc/ceph/\$cluster.conf

Ceph 配置文件使用 ini 样式语法。 您可以通过前面的注释添加注释，使用'＃'或';'。 

### 监控配置数据库

监视器集群管理整个集群可以使用的配置选项数据库，从而为整个系统提供简化的中央配置管理。绝大多数配置选项可以并且应该存储在此处，以便于管理和透明。少数设置可能仍需要存储在本地配置文件中，因为它们会影响连接到监视器，验证和获取配置信息的能力。在大多数情况下，这仅限于 mon\_host 选项，尽管通过使用 DNS SRV 记录也可以避免这种情况。

监视器存储的配置选项有全局部分，守护程序类型部分或特定守护程序部分中，就像配置文件中的选项一样。此外，选项还可以具有与其关联的掩码，以进一步限制该选项适用于哪些守护进程或客户端。掩码有两种形式：

* 类型:location：其中 type 是 CRUSH 属性，如 rack 或 host，location 是该属性的值。例如，host：foo 将选项限制为在特定主机上运行的守护程序或客户端。
* class:device-class ：其中 device-class 是 CRUSH 设备类的名称（例如，hdd 或 ssd）。例如，class：ssd 会将选项仅限制为 SSD 支持的 OSD。 （此掩码对非 OSD 守护进程或客户端没有影响。）

设置配置选项时，可以是由斜杠（/）字符分隔的服务名称，掩码或两者的组合。例如，osd / rack：foo 意味着 foo 机架中的所有 OSD 守护进程。查看配置选项时，服务名称和掩码通常分为单独的字段或列，以便于阅读。

命令

以下 CLI 命令用于配置集群：

* ceph config dump

　　将转储集群的整个配置数据库。

* ceph config get \<who>

　　将转储特定守护程序或客户端（例如，mds.a）的配置，存储在监视器的配置数据库中。

* ceph config set \<who> \<option> \<value>

　　将在监视器的配置数据库中设置配置选项。

* ceph config show \<who>

　　将显示正在运行的守护程序的报告运行配置。如果还有正在使用的本地配置文件或者在命令行或运行时覆盖了选项，则这些设置可能与监视器存储的设置不同。选项值的来源将作为输出的一部分进行报告。

* ceph config assimilate-conf -i \<input file> -o \<output file>

　　将从输入文件中提取配置文件，并将任何有效选项移动到监视器的配置数据库中。任何无法识别，无效或无法由 monitor 控制的设置都将以存储在输出文件中的缩写配置文件的形式返回。此命令对于从旧配置文件转换为基于监视器的集中式配置非常有用。

### help

您可以通过以下方式获得特定选项的帮助：

ceph config help \<option>

请注意，这将使用已经编译到正在运行的监视器中的配置架构。 如果您有一个混合版本的集群（例如，在升级期间），您可能还想从特定的运行守护程序中查询选项模式：

ceph daemon \<name> config help \[option\]

例如

\[root\@node1 \~\]# ceph config help log\_file
log\_file \- path to log file \(std::string, basic\)
  Default \(non\-daemon\): 
  Default \(daemon\): /var/log/ceph/\$cluster-\$name.log
  Can update at runtime: false See also: \[log\_to\_stderr,err\_to\_stderr,log\_to\_syslog,err\_to\_syslog\]

或

\[root\@node1 \~\]# ceph config help log\_file -f json-pretty
\{ "name": "log\_file", "type": "std::string", "level": "basic", "desc": "path to log file", "long\_desc": "", "default": "", "daemon\_default": "/var/log/ceph/\$cluster-\$name.log", "tags": \[\], "services": \[\], "see\_also": \[ "log\_to\_stderr", "err\_to\_stderr", "log\_to\_syslog", "err\_to\_syslog" \], "enum\_values": \[\], "min": "", "max": "", "can\_update\_at\_runtime": false \}

 level 属性可以是 basic，advanced 或 dev 中的任何一个。 开发选项供开发人员使用，通常用于测试目的，不建议操作员使用。

### 运行时修改

在大多数情况下，Ceph 允许您在运行时更改守护程序的配置。 此功能对于增加/减少日志记录输出，启用/禁用调试设置，甚至用于运行时优化非常有用。

一般来说，配置选项可以通过 ceph config set 命令以通常的方式更新。 例如，在特定 OSD 上启用调试日志级别：

ceph config set osd.123 debug\_ms 20

请注意，如果在本地配置文件中也自定义了相同的选项，则将忽略监视器设置（其优先级低于本地配置文件）。

覆盖参数值

您还可以使用 Ceph CLI 上的 tell 或 daemon 接口临时设置选项。 这些覆盖值是短暂的，因为它们只影响正在运行的进程，并且在守护进程或进程重新启动时被丢弃/丢失。

覆盖值可以通过两种方式设置：

1.从任何主机，我们都可以通过网络向守护进程发送消息：

ceph tell osd.123 config set debug\_osd 20

tell 命令还可以接受守护程序标识符的通配符。 例如，要调整所有 OSD 守护进程的调试级别：

ceph tell osd.\* config set debug\_osd 20

2.从进程运行的主机开始，我们可以通过/ var / run / ceph 中的套接字直接连接到进程：

ceph daemon \<name> config set \<option> \<value>

例如

ceph daemon osd.4 config set debug\_osd 20

请注意，在 ceph config show 命令输出中，这些临时值将显示为覆盖源。

### 查看运行参数值

您可以使用 ceph config show 命令查看为正在运行的守护程序设置的参数。 例如：

ceph config show osd.0

将显示该守护进程的（非默认）选项。 您还可以通过以下方式查看特定选项：

ceph config show osd.0 debug\_osd

或查看所有选项（即使是那些具有默认值的选项）：

ceph config show-with-defaults osd.0

您还可以通过管理套接字从本地主机连接到该守护程序来观察正在运行的守护程序的设置。 例如：

ceph daemon osd.0 config show

将转储所有当前设置：

ceph daemon osd.0 config diff

将仅显示非默认设置（以及值来自的位置：配置文件，监视器，覆盖等），以及：

ceph daemon osd.0 config get debug\_osd

将报告单个选项的值。

## 常用设置

### 概述

单个 Ceph 节点可以运行多个守护进程。 例如，具有多个驱动器的单个节点可以为每个驱动器运行一个 ceph-osd。 理想情况下，某些节点只运行特定的 daemon。 例如，一些节点可以运行 ceph-osd 守护进程，其他节点可以运行 ceph-mds 守护进程，还有其他节点可以运行 ceph-mon 守护进程。

每个节点都有一个由主机设置标识的名称。 监视器还指定由 addr 设置标识的网络地址和端口（即域名或 IP 地址）。 基本配置文件通常仅为每个监视器守护程序实例指定最小设置。 例如：

\[global\]
mon\_initial\_members \= ceph1
mon\_host \= 10.0.0.1

主机设置是节点的短名称（即，不是 fqdn）。 它也不是 IP 地址。 在命令行中输入 hostname \-s 以检索节点的名称。 除非您手动部署 Ceph，否则请勿将主机设置用于初始监视器以外的任何其他设置。 在使用 chef 或 ceph-deploy 等部署工具时，您不能在各个守护程序下指定主机，这些工具将在集群映射中为您输入适当的值。

### 网络

有关配置与 Ceph 一起使用的网络的详细讨论，请参阅网络配置参考。

### 监控

Ceph 生产集群通常使用至少 3 个 Ceph Monitor 守护程序进行部署，以确保监视器实例崩溃时的高可用性。 至少三（3）个监视器确保 Paxos 算法可以确定哪个版本的 Ceph Cluster Map 是法定人数中大多数 Ceph 监视器的最新版本。

注意您可以使用单个监视器部署 Ceph，但如果实例失败，则缺少其他监视器可能会中断数据服务可用性。

Ceph 监视器通常侦听端口 6789.例如：

\[mon.a\]
host \= hostName
mon addr \= 150.140.130.120:6789

默认情况下，Ceph 希望您将以下列路径存储监视器的数据：

/var/lib/ceph/mon/\$cluster-\$id

您或部署工具（例如，ceph-deploy）必须创建相应的目录。 在完全表达元变量和名为“ceph”的集群的情况下，上述目录将评估为：

/var/lib/ceph/mon/ceph-a

有关其他详细信息，请参阅“监视器配置参考”。

### 认证

Bobtail 版本的新功能：0.56

对于 Bobtail（v 0.56）及更高版本，您应该在 Ceph 配置文件的\[global\]部分中明确启用或禁用身份验证。

auth cluster required = cephx
auth service required \= cephx
auth client required \= cephx

此外，您应该启用 message signing（消息签名）。升级时，我们建议先明确禁用身份验证，然后再执行升级。 升级完成后，重新启用身份验证。 有关详细信息，请参阅 Cephx 配置参考。

### OSD

Ceph 生产集群通常部署 Ceph OSD 守护进程，一般一个 OSD 守护进程运行在一个存储驱动器上。 典型部署指定 jorunal 大小。 例如：

\[osd\]
osd journal size \= 10000 \[osd.0\]
host \= \{hostname\} #manual deployments only.

默认情况下，Ceph 希望您使用以下路径存储 Ceph OSD 守护程序的数据：

/var/lib/ceph/osd/\$cluster-\$id

您或部署工具（例如，ceph-deploy）必须创建相应的目录。 在完全表达元变量和名为“ceph”的集群的情况下，上述目录将评估为：

/var/lib/ceph/osd/ceph-0

您可以使用 osd 数据设置覆盖此路径。 我们不建议更改默认位置。 在 OSD 主机上创建默认目录。

ssh \{osd-host\} sudo mkdir /var/lib/ceph/osd/ceph-\{osd-number\}

osd 数据路径理想地导致具有硬盘的安装点，该硬盘与存储和运行操作系统和守护进程的硬盘分开。 如果 OSD 用于操作系统磁盘以外的磁盘，请准备与 Ceph 一起使用，并将其安装到刚刚创建的目录中：

ssh \{new-osd-host\} sudo mkfs -t \{fstype\} /dev/\{disk\} sudo mount -o user\_xattr /dev/\{hdd\} /var/lib/ceph/osd/ceph-\{osd-number\}

我们建议在运行 mkfs 时使用 xfs 文件系统。（不建议使用 btrfs 和 ext4，不再测试。）有关其他配置详细信息，请参阅 OSD 配置参考。

### 心跳

在运行时操作期间，Ceph OSD 守护进程检查其他 Ceph OSD 守护进程并将其发现报告给 Ceph Monitor。 您不必提供任何设置。 但是，如果您遇到网络延迟问题，则可能希望修改设置。

有关其他详细信息，请参阅配置 Monitor / OSD Interaction。

### 日志/调试

有时您可能会遇到 Ceph 需要修改日志记录输出和使用 Ceph 调试的问题。 有关日志轮换的详细信息，请参阅调试和日志记录。

### ceph.conf 示例

\[global\]
fsid \= \{cluster-id\}
mon initial members \= \{hostname\}\[, \{hostname\}\]
mon host \= \{ip-address\}\[, \{ip-address\}\]

#All clusters have a front\-side public network.
#If you have two NICs, you can configure a back side cluster 
#network for OSD object replication, heart beats, backfilling,
#recovery, etc.
public network \= \{network\}\[, \{network\}\]
#cluster network \= \{network\}\[, \{network\}\] 

#Clusters require authentication by default.
auth cluster required \= cephx
auth service required \= cephx
auth client required \= cephx

#Choose reasonable numbers for your journals, number of replicas
#and placement groups.
osd journal size \= \{n\}
osd pool default size \= \{n\}  # Write an object n times.
osd pool default min size \= \{n\} # Allow writing n copy in a degraded state.
osd pool default pg num \= \{n\}
osd pool default pgp num \= \{n\}

#Choose a reasonable crush leaf type.
#0 for a 1\-node cluster.
#1 for a multi node cluster in a single rack
#2 for a multi node, multi chassis cluster with multiple hosts in a chassis
#3 for a multi node cluster with hosts across racks, etc.
osd crush chooseleaf type \= \{n\}

### 运行多集群

使用 Ceph，您可以在同一硬件上运行多个 Ceph 存储集群。 与在具有不同 CRUSH 规则的同一群集上使用不同池相比，运行多个群集可提供更高级别的隔离。 单独的群集将具有单独的监视器，OSD 和元数据服务器进程。 使用默认设置运行 Ceph 时，默认群集名称为 ceph，这意味着您将在/ etc / ceph 默认目录中保存 Ceph 配置文件，文件名为 ceph.conf。

有关详细信息，请参阅 ceph-deploy new。 .. \_ceph-deploy new：../ ceph-deploy-new

运行多个群集时，必须为群集命名并使用群集名称保存 Ceph 配置文件。 例如，名为 openstack 的集群将在/ etc / ceph 缺省目录中具有文件名为 openstack.conf 的 Ceph 配置文件。

群集名称必须仅包含字母 a-z 和数字 0-9。

单独的集群意味着单独的数据磁盘和日志，它们不在集群之间共享。 cluster 元变量代表集群名称（即前面例子中的 openstack）。 各种设置使用 cluster 元变量，包括：

keyring  
admin socket  
log file  
pid file  
mon data  
mon cluster log file  
osd data  
osd journal  
mds data  
rgw data

创建默认目录或文件时，应在路径中的适当位置使用群集名称。 例如：

sudo mkdir /var/lib/ceph/osd/openstack-0
sudo mkdir /var/lib/ceph/mon/openstack-a

在同一主机上运行监视器时，应使用不同的端口。 默认情况下，监视器使用端口 6789.如果已使用端口 6789 使用监视器，请为其他群集使用不同的端口。

ceph -c \{cluster-name\}.conf health
ceph \-c openstack.conf health

## 网络设置

### 概述

网络配置对构建高性能 Ceph 存储来说相当重要。 Ceph 存储集群不会代表 Ceph 客户端执行请求路由或调度，相反， Ceph 客户端（如块设备、 CephFS 、 REST 网关）直接向 OSD 请求，然后 OSD 为客户端执行数据复制，也就是说复制和其它因素会额外增加集群网的负载。

我们的快速入门配置提供了一个简陋的 Ceph 配置文件，其中只设置了监视器 IP 地址和守护进程所在的主机名。如果没有配置集群网，那么 Ceph 假设你只有一个“公共网”。只用一个网可以运行 Ceph ，但是在大型集群里用单独的“集群”网可显著地提升性能。

我们建议用两个网络运营 Ceph 存储集群：一个公共网（前端）和一个集群网（后端）。为此，各节点得配备多个网卡

![](https://img2018.cnblogs.com/blog/1191664/201811/1191664-20181126103555230-182309917.png)

运营两个独立网络的考量主要有：

1.  性能： OSD 为客户端处理数据复制，复制多份时 OSD 间的网络负载势必会影响到客户端和 Ceph 集群的通讯，包括延时增加、产生性能问题；恢复和重均衡也会显著增加公共网延时。[  
    ](http://docs.ceph.org.cn/architecture#scalability-and-high-availability)
2.  安全： 大多数人都是良民，很少的一撮人喜欢折腾拒绝服务攻击（ DoS ）。当 OSD 间的流量失控时，归置组再也不能达到 active \+ clean 状态，这样用户就不能读写数据了。挫败此类攻击的一种好方法是维护一个完全独立的集群网，使之不能直连互联网；另外，请考虑用消息签名防止欺骗攻击。

### 防火墙

守护进程默认会绑定到 6800：7300 间的端口，你可以更改此范围。更改防火墙配置前先检查下 iptables 配置。  

sudo iptables -L

某些 Linux 发行版规矩拒绝除 SSH 之外所有网络接口的的所有入站请求。 例如：

REJECT all -- anywhere anywhere reject-with icmp-host-prohibited

你得先删掉公共网和集群网对应的这些规则，然后再增加安全保护规则。

监视器默认监听 6789 端口，而且监视器总是运行在公共网。按下例增加规则时，要把\{iface\}替换为公共网接口（如 eth0，eth1 等等），\{ip-address\}替换为 公共网 IP，\{netmask\}替换为公共网掩码。

sudo iptables -A INPUT -i \{iface\} -p tcp -s \{ip-address\}/\{netmask\} --dport 6789 -j ACCEPT

MDS 服务器会监听公共网 6800 以上的第一个可用端口。需要注意的是，这种行为是不确定的，所以如果你在同一主机上运行多个 OSD 或 MDS，或者在很短的时间内 重启了多个守护进程，它们会绑定更高的端口号;所以说你应该预先打开整个 6800-7300 端口区间。按下例增加规则时，要把\{iface\}替换为公共网接口（如 eth0 ，eth1 等等），\{ip-address\}替换为公共网 IP，\{netmask\}替换为公共网掩码。

sudo iptables -A INPUT -i \{iface\} -m multiport -p tcp -s \{ip-address\}/\{netmask\} --dports 6800:7300 -j ACCEPT

OSD 守护进程默认绑定从 6800 起的第一个可用端口，需要注意的是，这种行为是不确定的，所以如果你在同一主机上运行多个 OSD 或 MDS，或者在很短的时间内 重启了多个守护进程，它们会绑定更高的端口号。一主机上的各个 OSD 最多会用到 4 个端口：  
　　1.一个用于和客户端，监视器通讯;  
　　2.一个用于发送数据到其他 OSD;  
　　3.两个用于各个网卡上的心跳;

![](https://img2018.cnblogs.com/blog/1191664/201811/1191664-20181126104456037-902739347.png)

当某个守护进程失败并重启时没释放端口，重启后的进程就会监听新端口。你应该打开整个 6800-7300 端口区间，以应对这种可能性。

如果你分开了公共网和集群网，必须分别为之设置防火墙，因为客户端会通过公共网连接，而其他 OSD 会通过集群网连接。按下例增加规则时，要把\{iface\}替换为网 口（如 eth0，eth1 等等），\{ip-address\}替换为公共网或集群网 IP，\{netmask\}替换为公共网或集群网掩码。例如：

sudo iptables -A INPUT -i \{iface\}  -m multiport -p tcp -s \{ip-address\}/\{netmask\} --dports 6800:7300 -j ACCEPT

如果你的元数据服务器和 OSD 在同一节点上，可以合并公共网配置。

### Ceph 网络

Ceph 的网络配置要放到 \[global\] 段下。前述的 5 分钟快速入门提供了一个简陋的 Ceph 配置文件，它假设服务器和客户端都位于同一网段， Ceph 可以很好地适应这种情形。然而 Ceph 允许配置更精细的公共网，包括多 IP 和多掩码；也能用单独的集群网处理 OSD 心跳、对象复制、和恢复流量。不要混淆你配置的 IP 地址和客户端用来访问存储服务的公共网地址。典型的内网常常是 192.168.0.0 或 10.0.0.0 。

如果你给公共网或集群网配置了多个 IP 地址及子网掩码，这些子网必须能互通。另外要确保在防火墙上为各 IP 和子网开放了必要的端口。Ceph 用 CIDR 法表示子网，如 10.0.0.0/24。

配置完几个网络后，可以重启集群或挨个重启守护进程.Ceph 守护进程动态地绑定端口，所以更改网络配置后无需重启整个集群。

公共网络  
要配置公共网络，请将以下选项添加到 Ceph 配置文件的\[global\]部分。
```plain
\[global\]
        # ... elided configuration
        public network \= \{public-network/netmask\}
```
集群网络  
如果声明群集网络，OSD 将通过群集网络路由心跳，对象复制和恢复流量。 与使用单个网络相比，这可以提高性能。 要配置群集网络，请将以下选项添加到 Ceph 配置文件的\[global\]部分。
```plain
\[global\]
        # ... elided configuration
        cluster network \= \{cluster-network/netmask\}
```
我们希望无法从公共网络或 Internet 访问群集网络以增强安全性。

### Ceph Daemon

有一个网络配置是所有守护进程都要配的：各个守护进程都必须指定主机，Ceph 也要求指定监视器 IP 地址及端口。一些部署工具（如 ceph-deploy，Chef）会给你创建配置文件，如果它能胜任那就别设置这些值。主机选项是主机的短名，不是全资域名 FQDN，也不是 IP 地址。在命令行下输入主机名-s 获取主机名。
```plain
\[mon.a\]
        host \= \{hostname\}

        mon addr \= \{ip-address\}:6789 \[osd.0\]
        host \= \{hostname\}
```
您不必为守护程序设置主机 IP 地址。 如果您具有静态 IP 配置并且公共和集群网络都在运行，则 Ceph 配置文件可以为每个守护程序指定主机的 IP 地址。 要为守护程序设置静态 IP 地址，以下选项应出现在 ceph.conf 文件的守护程序实例部分中。
```plain
\[osd.0\]
        public addr \= \{host-public-ip-address\}
        cluster addr \= \{host-cluster-ip-address\}
```
单网卡 OSD，双网络集群

一般来说，我们不建议用单网卡 OSD 主机部署两个网络。然而这事可以实现，把公共地址选择配在\[osd.n\]段下即可强制 OSD 主机运行在公共网，其中 n 是其 OSD 号。另外，公共网和集群网必须互通，考虑到安全因素我们不建议这样做。

### 网络配置选项

网络配置选项不是必需的，Ceph 假设所有主机都运行于公共网，除非你特意配置了一个集群网。

  
公共网

公共网配置用于明确地为公共网定义 IP 地址和子网。你可以分配静态 IP 或用 public addr 覆盖 public network 选项。

public network
描述:公共网（前端）的 IP 地址和掩码（如 192.168.0.0/24 ），置于 \[global\] 下。多个子网用逗号分隔。 
类型:\{ip\-address\}/\{netmask\} \[, \{ip-address\}/\{netmask\}\] 
是否必需:No 
默认值:N/A 

public addr
描述:用于公共网（前端）的 IP 地址。适用于各守护进程。 
类型:IP 地址 
是否必需:No 
默认值:N/A 

集群网

集群网配置用来声明一个集群网，并明确地定义其 IP 地址和子网。你可以配置静态 IP 或为某 OSD 守护进程配置 cluster addr 以覆盖 cluster network 选项。

cluster network
描述:集群网（后端）的 IP 地址及掩码（如 10.0.0.0/24 ），置于 \[global\] 下。多个子网用逗号分隔。 
类型:\{ip\-address\}/\{netmask\} \[, \{ip-address\}/\{netmask\}\] 
是否必需:No 
默认值:N/A

cluster addr
描述:集群网（后端） IP 地址。置于各守护进程下。 
类型:Address 
是否必需:No 
默认值:N/A 

绑定

绑定选项用于设置 OSD 和 MDS 默认使用的端口范围，默认范围是 6800:7300 。确保防火墙开放了对应端口范围。

你也可以让 Ceph 守护进程绑定到 IPv6 地址。

ms bind port min
描述:OSD 或 MDS 可绑定的最小端口号。 
类型:32\-bit Integer 
默认值:6800 是否必需:No 

ms bind port max
描述:OSD 或 MDS 可绑定的最大端口号。 
类型:32\-bit Integer 
默认值:7300 是否必需:No. 

ms bind ipv6
描述:允许 Ceph 守护进程绑定 IPv6 地址。 
类型:Boolean 
默认值:false 是否必需:No 

主机

Ceph 配置文件里至少要写一个监视器、且每个监视器下都要配置 mon addr 选项；每个监视器、元数据服务器和 OSD 下都要配 host 选项。

mon addr
描述:\{hostname\}:\{port\} 条目列表，用以让客户端连接 Ceph 监视器。如果未设置， Ceph 查找 \[mon.\*\] 段。 
类型:String 
是否必需:No
默认值:N/A 

host
描述:主机名。此选项用于特定守护进程，如 \[osd.0\] 。 
类型:String 
是否必需:Yes, for daemon instances. 
默认值:localhost 

不要用 localhost 。在命令行下执行 hostname \-s 获取主机名（到第一个点，不是全资域名），并用于配置文件。用第三方部署工具时不要指定 host 选项，它会自行获取。

TCP

Ceph 默认禁用 TCP 缓冲。

ms tcp nodelay
描述:Ceph 用 ms tcp nodelay 使系统尽快（不缓冲）发送每个请求。禁用 Nagle 算法可增加吞吐量，但会引进延时。如果你遇到大量小包，可以禁用 ms tcp nodelay 试试。 
类型:Boolean 
是否必需:No 
默认值:true ms tcp rcvbuf
描述:网络套接字接收缓冲尺寸，默认禁用。 
类型:32\-bit Integer 
是否必需:No 
默认值:0 ms tcp read timeout
描述:如果一客户端或守护进程发送请求到另一个 Ceph 守护进程，且没有断开不再使用的连接，在 ms tcp read timeout 指定的秒数之后它将被标记为空闲。 
类型:Unsigned 64\-bit Integer 
是否必需:No 
默认值:900 15 minutes. 

## 认证设置

### 概述

cephx 协议已经默认开启。加密认证要耗费一定计算资源，但通常很低。如果您的客户端和服务器网络环境相当安全，而且认证的负面效应更大，你可以关闭它，通常不推荐您这么做。如果禁用了认证，就会有篡改客户端/服务器消息这样的中间人攻击风险，这会导致灾难性后果。

### 部署情景

部署 Ceph 集群有两种主要方案，这会影响您最初配置 Cephx 的方式。 Ceph 用户大多数第一次使用 ceph-deploy 来创建集群（最简单）。 对于使用其他部署工具（例如，Chef，Juju，Puppet 等）的集群，您将需要使用手动过程或配置部署工具来引导您的监视器。

* CEPH-DEPLOY

使用 ceph-deploy 部署集群时，您不必手动引导监视器或创建 client.admin 用户或密钥环。 您在 Storage Cluster 快速入门中执行的步骤将调用 ceph-deploy 为您执行此操作。

当您执行 ceph-deploy new \{initial-monitor（s）\}时，Ceph 将为您创建一个监视密钥环（仅用于引导监视器），它将为您生成一个初始 Ceph 配置文件，其中包含以下身份验证设置 ，表明 Ceph 默认启用身份验证：

auth\_cluster\_required = cephx
auth\_service\_required \= cephx
auth\_client\_required \= cephx

当您执行 ceph-deploy mon create-initial 时，Ceph 将引导初始监视器，检索包含 client.admin 用户密钥的 ceph.client.admin.keyring 文件。 此外，它还将检索密钥环，使 ceph-deploy 和 ceph-volume 实用程序能够准备和激活 OSD 和元数据服务器。

当您执行 ceph-deploy admin \{node-name\}时（注意：首先必须安装 Ceph），您将 Ceph 配置文件和 ceph.client.admin.keyring 推送到节点的/ etc / ceph 目录。 您将能够在该节点的命令行上以 root 身份执行 Ceph 管理功能。

* 手动部署

手动部署集群时，必须手动引导监视器并创建 client.admin 用户和密钥环。 要引导监视器，请按照 [Monitor Bootstrapping](http://docs.ceph.com/docs/master/install/manual-deployment#monitor-bootstrapping)中的步骤操作。 监视器引导的步骤是使用 Chef，Puppet，Juju 等第三方部署工具时必须执行的逻辑步骤。

### 启用/禁用 CEPHX

为监视器，OSD 和元数据服务器部署密钥时需启用 Cephx。 如果你只是打开/关闭 Cephx，你不必重复 bootstrapping 程序。

启用 Cephx

启用 cephx 后，Ceph 将在默认搜索路径（包括/etc/ceph/ceph.\$name.keyring）里查找密钥环。你可以在 Ceph 配置文件的\[global\]段里添加 keyring 选项来修改，但不推荐。

在禁用了 cephx 的集群上执行下面的步骤来启用它，如果你（或者部署工具）已经生成了密钥，你可以跳过相关的步骤。

1.创建 client.admin 密钥，并为客户端保存此密钥的副本：

ceph auth get-or-create client.admin mon 'allow \*' mds 'allow \*' osd 'allow \*' -o /etc/ceph/ceph.client.admin.keyring

警告：此命令会覆盖任何存在的/etc/ceph/client.admin.keyring 文件，如果部署工具已经完成此步骤，千万别再执行此命令。多加小心！

2.创建监视器集群所需的密钥环，并给它们生成密钥。

ceph-authtool --create-keyring /tmp/ceph.mon.keyring --gen-key -n mon. --cap mon 'allow \*'

3.把监视器密钥环复制到 ceph.mon.keyring 文件，再把此文件复制到各监视器的 mon 数据目录下。比如要把它复制给名为 ceph 集群的 mon.a，用此命令：

cp /tmp/ceph.mon.keyring /var/lib/ceph/mon/ceph-a/keyring

4.为每个 MGR 生成密钥，\{\$ id\}是 OSD 编号：

ceph auth get-or-create mgr.\{\$id\} mon 'allow profile mgr' mds 'allow \*' osd 'allow \*' -o /var/lib/ceph/mgr/ceph-\{\$id\}/keyring

5.为每个 OSD 生成密钥， \{\$id\} 是 MDS 的标识字母：

ceph auth get-or-create osd.\{\$id\} mon 'allow rwx' osd 'allow \*' -o /var/lib/ceph/osd/ceph-\{\$id\}/keyring

6.为每个 MDS 生成密钥， \{\$id\} 是 MDS 的标识字母：

ceph auth get-or-create mds.\{\$id\} mon 'allow rwx' osd 'allow \*' mds 'allow \*' mgr 'allow profile mds' -o /var/lib/ceph/mds/ceph-\{\$id\}/keyring

7.把以下配置加入 Ceph 配置文件的 \[global\] 段下以启用 cephx 认证：

auth cluster required = cephx
auth service required \= cephx
auth client required \= cephx

8.启动或重启 Ceph 集群

禁用 Cephx

下述步骤描述了如何禁用 Cephx。如果你的集群环境相对安全，你可以减免认证耗费的计算资源，然而我们不推荐。但是临时禁用认证会使安装，和/或排障更简单。

1.把下列配置加入 Ceph 配置文件的\[global\]段下即可禁用 cephx 认证：

auth cluster required = none
auth service required \= none
auth client required \= none

2.启动或重启 Ceph 集群

### 配置选项

 启动

auth cluster required
描述:如果启用了，集群守护进程（如 ceph\-mon 、 ceph-osd 和 ceph-mds ）间必须相互认证。可用选项有 cephx 或 none 。 
类型:String 
是否必需:No 
默认值:cephx. 

auth service required
描述:如果启用，客户端要访问 Ceph 服务的话，集群守护进程会要求它和集群认证。可用选项为 cephx 或 none 。 
类型:String 
是否必需:No 
默认值:cephx. 

auth client required
描述:如果启用，客户端会要求 Ceph 集群和它认证。可用选项为 cephx 或 none 。 
类型:String 
是否必需:No 
默认值:cephx. 

密钥

如果你的集群启用了认证， ceph 管理命令和客户端得有密钥才能访问集群。

给 ceph 管理命令和客户端提供密钥的最常用方法就是把密钥环放到 /etc/ceph ，通过 ceph-deploy 部署的 Cuttlefish 及更高版本，其文件名通常是 ceph.client.admin.keyring （或 \$cluster.client.admin.keyring ）。如果你的密钥环位于 /etc/ceph 下，就不需要在 Ceph 配置文件里指定 keyring 选项了。

我们建议把集群的密钥环复制到你执行管理命令的节点，它包含 client.admin 密钥。

你可以用 ceph-deploy admin 命令做此事，手动复制可执行此命令：

sudo scp \{user\}\@\{ceph-cluster-host\}:/etc/ceph/ceph.client.admin.keyring /etc/ceph/ceph.client.admin.keyring

确保给客户端上的 ceph.keyring 设置合理的权限位（如 chmod 644）。

你可以用 key 选项把密钥写在配置文件里（不推荐），或者用 keyfile 选项指定个路径。

keyring
描述:密钥环文件的路径。 
类型:String 
是否必需:No 
默认值:/etc/ceph/\$cluster.\$name.keyring,/etc/ceph/\$cluster.keyring,/etc/ceph/keyring,/etc/ceph/keyring.bin 

keyfile
描述:到密钥文件的路径，如一个只包含密钥的文件。 
类型:String 
是否必需:No 
默认值:None 

key
描述:密钥（密钥文本），最好别这样做。 
类型:String 
是否必需:No 
默认值:None 

DAEMON KEYRINGS  
管理用户或部署工具（例如，ceph-deploy）可以以与生成用户密钥环相同的方式生成守护进程密钥环。 默认情况下，Ceph 将守护进程密钥环存储在其数据目录中。 默认密钥环位置以及守护程序运行所需的功能如下所示。

ceph-mon
Location:          \$mon\_data/keyring
Capabilities:      mon 'allow \*' ceph\-osd
Location:          \$osd\_data/keyring
Capabilities:      mgr 'allow profile osd' mon 'allow profile osd' osd 'allow \*' ceph\-mds
Location:          \$mds\_data/keyring
Capabilities:      mds 'allow' mgr 'allow profile mds' mon 'allow profile mds' osd 'allow rwx' ceph\-mgr
Location:          \$mgr\_data/keyring
Capabilities:      mon 'allow profile mgr' mds 'allow \*' osd 'allow \*' radosgw
Location:          \$rgw\_data/keyring
Capabilities:      mon 'allow rwx' osd 'allow rwx' 

监视器密钥环（即 mon. ）包含一个密钥，但没有能力，且不是集群 auth 数据库的一部分。

守护进程数据目录位置默认格式如下：

/var/lib/ceph/\$type/\$cluster-\$id

例如， osd.12 的目录会是：

/var/lib/ceph/osd/ceph-12

你可以覆盖这些位置，但不推荐。

签名

在 Bobtail 及后续版本中， Ceph 会用开始认证时生成的会话密钥认证所有在线实体。然而 Argonaut 及之前版本不知道如何认证在线消息，为保持向后兼容性（如在同一个集群里运行 Bobtail 和 Argonaut ），消息签名默认是关闭的。如果你只运行 Bobtail 和后续版本，可以让 Ceph 要求签名。

像 Ceph 认证的其他部分一样，客户端和集群间的消息签名也能做到细粒度控制；而且能启用或禁用 Ceph 守护进程间的签名。

cephx require signatures
描述:若设置为 true ， Ceph 集群会要求客户端签名所有消息，包括集群内其他守护进程间的。 
类型:Boolean 
是否必需:No 
默认值:false cephx cluster require signatures
描述:若设置为 true ， Ceph 要求集群内所有守护进程签名相互之间的消息。 
类型:Boolean 
是否必需:No 
默认值:false cephx service require signatures
描述:若设置为 true ， Ceph 要求签名所有客户端和集群间的消息。 
类型:Boolean 
是否必需:No 
默认值:false cephx sign messages
描述:如果 Ceph 版本支持消息签名， Ceph 会签名所有消息以防欺骗。 
类型:Boolean 
默认值:true 

生存期

auth service ticket ttl  
描述:Ceph 存储集群发给客户端一个用于认证的票据时分配给这个票据的生存期。 
类型:Double 
默认值:60\*60 

## Monitor 设置

### 概述

理解如何配置 Ceph 监视器是构建可靠的 Ceph 存储集群的重要方面，任何 Ceph 集群都需要至少一个监视器。一个监视器通常相当一致，但是你可以增加，删除，或替换集群中的监视器

### 背景

监视器们维护着集群运行图的“主副本”，就是说客户端连到一个监视器并获取当前运行图就能确定所有监视器、 OSD 和元数据服务器的位置。 Ceph 客户端读写 OSD 或元数据服务器前，必须先连到一个监视器，靠当前集群运行图的副本和 CRUSH 算法，客户端能计算出任何对象的位置，故此客户端有能力直接连到 OSD ，这对 Ceph 的高伸缩性、高性能来说非常重要。监视器的主要角色是维护集群运行图的主副本，它也提供认证和日志记录服务。 Ceph 监视器们把监视器服务的所有更改写入一个单独的 Paxos 例程，然后 Paxos 以键/值方式存储所有变更以实现高度一致性。同步期间， Ceph 监视器能查询集群运行图的近期版本，它们通过操作键/值存储快照和迭代器（用 leveldb ）来进行存储级同步

![](https://img2018.cnblogs.com/blog/1191664/201811/1191664-20181127090427115-627338682.png)

自 0.58 版以来已弃用  
在 0.58 及更早版本中，Ceph 监视器每个服务用一个 Paxos 例程，并把运行图存储为文件。

### CLUSTER MAPS

集群运行图是多个图的组合，包括监视器图、 OSD 图、归置组图和元数据服务器图。集群运行图追踪几个重要事件：哪些进程在集群里（ in ）；哪些进程在集群里（ in ）是 up 且在运行、或 down ；归置组状态是 active 或 inactive 、 clean 或其他状态；和其他反映当前集群状态的信息，像总存储容量、和使用量。

当集群状态有明显变更时，如一 OSD 挂了、一归置组降级了等等，集群运行图会被更新以反映集群当前状态。另外，监视器也维护着集群的主要状态历史。监视器图、 OSD 图、归置组图和元数据服务器图各自维护着它们的运行图版本。我们把各图的版本称为一个 epoch 。

运营集群时，跟踪这些状态是系统管理任务的重要部分。

### MONITOR QUORUM

本文入门部分提供了一个简陋的 Ceph 配置文件，它提供了一个监视器用于测试。只用一个监视器集群可以良好地运行，然而单监视器是一个单故障点，生产集群要实现高可用性的话得配置多个监视器，这样单个监视器的失效才不会影响整个集群。

集群用多个监视器实现高可用性时，多个监视器用 Paxos 算法对主集群运行图达成一致，这里的一致要求大多数监视器都在运行且够成法定人数（如 1 个、 3 之 2 在运行、 5 之 3 、 6 之 4 等等）。

mon force quorum join 描述：强制监视器加入仲裁，即使它先前已从 MAP 中删除
类型：Boolean
默认值：false

### 一致性

你把监视器加进 Ceph 配置文件时，得注意一些架构问题， Ceph 发现集群内的其他监视器时对其有着严格的一致性要求。尽管如此， Ceph 客户端和其他 Ceph 守护进程用配置文件发现监视器，监视器却用监视器图（ monmap ）相互发现而非配置文件。

一个监视器发现集群内的其他监视器时总是参考 monmap 的本地副本，用 monmap 而非 Ceph 配置文件避免了可能损坏集群的错误（如 ceph.conf 中指定地址或端口的拼写错误）。正因为监视器把 monmap 用于发现、并共享于客户端和其他 Ceph 守护进程间， monmap 可严格地保证监视器的一致性是可靠的。

严格的一致性也适用于 monmap 的更新，因为关于监视器的任何更新、关于 monmap 的变更都是通过称为 Paxos 的分布式一致性算法传递的。监视器们必须就 monmap 的每次更新达成一致，以确保法定人数里的每个监视器 monmap 版本相同，如增加、删除一个监视器。 monmap 的更新是增量的，所以监视器们都有最新的一致版本，以及一系列之前版本。历史版本的存在允许一个落后的监视器跟上集群当前状态。

如果监视器通过配置文件而非 monmap 相互发现，这会引进其他风险，因为 Ceph 配置文件不是自动更新并分发的，监视器有可能不小心用了较老的配置文件，以致于不认识某监视器、放弃法定人数、或者产生一种 Paxos 不能确定当前系统状态的情形

### 初始化监视器

在大多数配置和部署案例中，部署 Ceph 的工具可以帮你生成一个监视器图来初始化监视器（如 ceph-deploy 等），一个监视器需要的选项：

* 文件系统标识符： fsid 是对象存储的唯一标识符。因为你可以在一套硬件上运行多个集群，所以在初始化监视器时必须指定对象存储的唯一标识符。部署工具通常可替你完成（如 ceph-deploy 会调用类似 uuidgen 的程序），但是你也可以手动指定 fsid 。
* 监视器标识符： 监视器标识符是分配给集群内各监视器的唯一 ID ，它是一个字母数字组合，为方便起见，标识符通常以字母顺序结尾（如 a 、 b 等等），可以设置于 Ceph 配置文件（如 \[mon.a\] 、 \[mon.b\] 等等）、部署工具、或 ceph 命令行工具。
* 密钥： 监视器必须有密钥。像 ceph-deploy 这样的部署工具通常会自动生成，也可以手动完成。

### 配置

要把配置应用到整个集群，把它们放到 \[global\] 下；要用于所有监视器，置于 \[mon\] 下；要用于某监视器，指定监视器例程，如 \[mon.a\] ）。按惯例，监视器例程用字母命名。

\[global\]

\[mon\]

\[mon.a\]

\[mon.b\]

\[mon.c\]

最小配置

Ceph 监视器的最简配置必须包括一主机名及其监视器地址，这些配置可置于 \[mon\] 下或某个监视器下。

\[mon\]
        mon host \= hostname1,hostname2,hostname3
        mon addr \= 10.0.0.10:6789,10.0.0.11:6789,10.0.0.12:6789

\[mon.a\]
        host \= hostname1
        mon addr \= 10.0.0.10:6789

这里的监视器最简配置假设部署工具会自动给你生成 fsid 和 mon. 密钥。一旦部署了 Ceph 集群，监视器 IP 地址不应该更改。然而，如果你决意要改，必须严格按照更改监视器 IP 地址来改。

客户端也可以使用 DNS SRV 记录找到监视器

集群 ID

每个 Ceph 存储集群都有一个唯一标识符（ fsid ）。如果指定了，它应该出现在配置文件的 \[global\] 段下。部署工具通常会生成 fsid 并存于监视器图，所以不一定会写入配置文件， fsid 使得在一套硬件上运行多个集群成为可能。

fsid
描述:集群 ID ，一集群一个。 
类型:UUID 
是否必需:Yes. 
默认值:无。若未指定，部署工具会生成。 

如果你用部署工具就不能设置

初始成员

我们建议在生产环境下最少部署 3 个监视器，以确保高可用性。运行多个监视器时，你可以指定为形成法定人数成员所需的初始监视器，这能减小集群上线时间。

\[mon\]
        mon initial members \= a,b,c

mon initial members
描述:集群启动时初始监视器的 ID ，若指定， Ceph 需要奇数个监视器来确定最初法定人数（如 3 ）。 
类型:String 
默认值:None 

数据

Ceph 提供 Ceph 监视器存储数据的默认路径。为了在生产 Ceph 存储集群中获得最佳性能，我们建议在 Ceph OSD 守护进程和 Ceph Monitor 在不同主机和驱动器上运行。由于 leveldb 使用 mmap（）来编写数据，Ceph Monitors 经常将内存中的数据刷新到磁盘，如果数据存储与 OSD 守护进程共存，则可能会干扰 Ceph OSD 守护进程工作负载。

在 Ceph 版本 0.58 及更早版本中，Ceph Monitors 将其数据存储在文件中。这种方法允许用户使用 ls 和 cat 等常用工具检查监控数据。但是，它没有提供强大的一致性。

在 Ceph 0.59 及后续版本中，监视器以键/值对存储数据。监视器需要 ACID 事务，数据存储的使用可防止监视器用损坏的版本进行恢复，除此之外，它允许在一个原子批量操作中进行多个修改操作。

一般来说我们不建议更改默认数据位置，如果要改，我们建议所有监视器统一配置，加到配置文件的 \[mon\] 下。

mon data
描述：监视器的数据位置。
类型：String
默认值：/var/lib/ceph/mon/\$cluster-\$id mon data size warn
描述：当监视器的数据存储超过 15GB 时，在群集日志中发出 HEALTH\_WARN。
类型：整型
默认值：15 \* 1024 \* 1024 \* 1024 \* mon data avail warn
描述：当监视器数据存储的可用磁盘空间小于或等于此百分比时，在群集日志中发出 HEALTH\_WARN。
类型：整型
默认值：30 mon data avail crit
描述：当监视器数据存储的可用磁盘空间小于或等于此百分比时，在群集日志中发出 HEALTH\_ERR。
类型：整型
默认值：5 mon warn on cache pools without hit sets
描述：如果缓存池未配置 hit\_set\_type 值，则在集群日志中发出 HEALTH\_WARN。有关详细信息，请参阅 hit\_set\_type。
类型：Boolean
默认值：true mon warn on crush straw calc version zero
描述：如果 CRUSH 的 straw\_calc\_version 为零，则在集群日志中发出 HEALTH\_WARN。有关详细信息，请参阅 CRUSH map tunables。
类型：Boolean
默认值：true mon warn on legacy crush tunables
描述：如果 CRUSH 可调参数太旧（早于 mon\_min\_crush\_required\_version），则在集群日志中发出 HEALTH\_WARN
类型：Boolean
默认值：true mon crush min required version
描述：群集所需的最小可调参数版本。有关详细信息，请参阅 CRUSH map tunables。
类型：String
默认值：firefly

mon warn on osd down out interval zero
描述：if mon osd down out interval is zero，则在集群日志中发出 HEALTH\_WARN。在 leader 上将此选项设置为零的行为与 noout 标志非常相似。在没有设置 noout 标志的情况下很难弄清楚集群出了什么问题但是现象差不多，所以我们在这种情况下报告一个警告。
类型：Boolean
默认值：true mon cache target full warn ratio
描述：cache\_target\_full 和 target\_max\_object 之间，我们开始警告
类型：float 默认值：0.66 mon health data update interval
描述：仲裁中的监视器与其对等方共享其健康状态的频率（以秒为单位）。 （负数禁用它）
类型：float 默认值：60 mon health to clog
描述：定期启用向群集日志发送运行状况摘要。
类型：Boolean
默认值：true mon health to clog tick interval
描述：监视器将健康摘要发送到群集日志的频率（以秒为单位）（非正数禁用它）。 如果当前运行状况摘要为空或与上次相同，则监视器不会将其发送到群集日志。
类型：整型
默认值：3600 mon health to clog interval
描述：监视器将健康摘要发送到群集日志的频率（以秒为单位）（非正数禁用它）。 无论摘要是否更改，Monitor 都将始终将摘要发送到群集日志。
类型：整型
默认值：60

存储容量

Ceph 存储集群利用率接近最大容量时（即 mon osd full ratio ），作为防止数据丢失的安全措施，它会阻止你读写 OSD 。因此，让生产集群用满可不是好事，因为牺牲了高可用性。 full ratio 默认值是 .95 或容量的 95\% 。对小型测试集群来说这是非常激进的设置。

Tip:监控集群时，要警惕和 nearfull 相关的警告。这意味着一些 OSD 的失败会导致临时服务中断，应该增加一些 OSD 来扩展存储容量。

在测试集群时，一个常见场景是：系统管理员从集群删除一个 OSD 、接着观察重均衡；然后继续删除其他 OSD ，直到集群达到占满率并锁死。我们建议，即使在测试集群里也要规划一点空闲容量用于保证高可用性。理想情况下，要做好这样的预案：一系列 OSD 失败后，短时间内不更换它们仍能恢复到 active + clean 状态。你也可以在 active + degraded 状态运行集群，但对正常使用来说并不好。

下图描述了一个简化的 Ceph 集群，它包含 33 个节点、每主机一个 OSD 、每 OSD 3TB 容量，所以这个小白鼠集群有 99TB 的实际容量，其 mon osd full ratio 为 .95 。如果它只剩余 5TB 容量，集群就不允许客户端再读写数据，所以它的运行容量是 95TB ，而非 99TB 。

![](https://img2018.cnblogs.com/blog/1191664/201811/1191664-20181127095500225-1199215238.png)

在这样的集群里，坏一或两个 OSD 很平常；一种罕见但可能发生的情形是一个机架的路由器或电源挂了，这会导致多个 OSD 同时离线（如 OSD 7-12 ），在这种情况下，你仍要力争保持集群可运行并达到 active + clean 状态，即使这意味着你得在短期内额外增加一些 OSD 及主机。如果集群利用率太高，在解决故障域期间也许不会丢数据，但很可能牺牲数据可用性，因为利用率超过了 full ratio 。故此，我们建议至少要粗略地规划下容量。

确定群集的两个数字：OSD 的数量和集群的总容量

如果将群集的总容量除以群集中的 OSD 数，则可以找到群集中 OSD 的平均平均容量。 考虑将该数字乘以您期望在正常操作期间同时失败的 OSD 数量（相对较小的数量）。 最后将群集的容量乘以全部比率，以达到最大运行容量; 然后，减去那些预期会故障的 OSD 从而计算出合理的 full ratio。 用更多数量的 OSD 故障（例如，一组 OSD）重复上述过程，以得到合理的 near full ratio。

以下设置仅适用于群集创建，然后存储在 OSDMap 中。
```plain
\[global\]


        mon osd full ratio \= .80 mon osd backfillfull ratio \= .75 mon osd nearfull ratio \= .70

mon osd full ratio
```
描述：OSD 被视为已满之前使用的磁盘空间百分比。
类型：float 默认值：0.95 mon osd backfillfull ratio
说明：在 OSD 被认为太满而无法 backfill 之前使用的磁盘空间百分比。
类型：float 默认值：0.90 mon osd nearfull ratio
描述：在 OSD 被认为接近满之前使用的磁盘空间百分比。
类型：float 默认值：0.85

如果一些 OSD 快满了，但其他的仍有足够空间，你可能配错 CRUSH 权重了。

这些设置仅适用于群集创建期间。 之后需要使用 ceph osd set-almostfull-ratio 和 ceph osd set-full-ratio 在 OSDMap 中进行更改

心跳

Ceph 监视器要求各 OSD 向它报告、并接收 OSD 们的邻居状态报告，以此来掌握集群。 Ceph 提供了监视器与 OSD 交互的合理默认值，然而你可以按需修改

监视器存储同步

当你用多个监视器支撑一个生产集群时，各监视器都要检查邻居是否有集群运行图的最新版本（如，邻居监视器的图有一或多个 epoch 版本高于当前监视器的最高版 epoch ），过一段时间，集群里的某个监视器可能落后于其它监视器太多而不得不离开法定人数，然后同步到集群当前状态，并重回法定人数。为了同步，监视器可能承担三种中的一种角色：  
　　1.Leader: Leader 是实现最新 Paxos 版本的第一个监视器。  
　　2.Provider: Provider 有最新集群运行图的监视器，但不是第一个实现最新版。  
　　3.Requester: Requester 落后于 leader ，重回法定人数前，必须同步以获取关于集群的最新信息。

有了这些角色区分， leader 就 可以给 provider 委派同步任务，这会避免同步请求压垮 leader 、影响性能。在下面的图示中， requester 已经知道它落后于其它监视器，然后向 leader 请求同步， leader 让它去和 provider 同步。

![](https://img2018.cnblogs.com/blog/1191664/201811/1191664-20181127101603877-310693997.png)

新监视器加入集群时有必要进行同步。在运行中，监视器会不定时收到集群运行图的更新，这就意味着 leader 和 provider 角色可能在监视器间变幻。如果这事发生在同步期间（如 provider 落后于 leader ）， provider 能终结和 requester 间的同步。

一旦同步完成， Ceph 需要修复整个集群，使归置组回到 active + clean 状态。

mon sync trim timeout
描述:    
类型:    Double
默认： 30.0  
  
mon sync heartbeat timeout
描述:    
类型:    Double
默认： 30.0  
 mon sync heartbeat interval
描述:    
类型:    Double
默认： 5.0  
 mon sync backoff timeout
描述:    
类型:    Double
默认： 30.0  
 mon sync timeout
描述:    Number of seconds the monitor will wait for the next update message from its sync provider before it gives up and bootstrap again.
类型:    Double
默认： 60.0  
 mon sync max retries
描述:    
类型:    Integer
默认： 5  
 mon sync max payload size
描述:    The maximum size for a sync payload \(in bytes\).
类型: 32\-bit Integer
默认： 1045676  
 paxos max join drift
描述:    在我们必须首先同步监控数据存储之前的最大 Paxos 迭代。 当监视器发现其对等体远远超过它时，它将首先与数据存储同步，然后再继续。 类型:    Integer
默认： 10  
 paxos stash full interval
描述:    多久（在提交中）存储 PaxosService 状态的完整副本。 当前此设置仅影响 mds，mon，auth 和 mgr PaxosServices。 类型:    Integer
默认： 25  
 paxos propose interval
描述:    Gather updates for this time interval before proposing a map update.
类型:    Double
默认： 1.0  
 paxos min
描述:    The minimum number of paxos states to keep around
类型:    Integer
默认： 500  
 paxos min wait 描述:    The minimum amount of time to gather updates after a period of inactivity.
类型:    Double
默认： 0.05  
 paxos trim min
描述:    Number of extra proposals tolerated before trimming
类型:    Integer
默认： 250  
 paxos trim max
描述:    The maximum number of extra proposals to trim at a time 类型:    Integer
默认： 500  
 paxos service trim min
描述:    The minimum amount of versions to trigger a trim \(0 disables it\)
类型:    Integer
默认： 250  
 paxos service trim max
描述:    The maximum amount of versions to trim during a single proposal \(0 disables it\)
类型:    Integer
默认： 500  
 mon max log epochs
描述:    The maximum amount of log epochs to trim during a single proposal
类型:    Integer
默认： 500  
 mon max pgmap epochs
描述:    The maximum amount of pgmap epochs to trim during a single proposal
类型:    Integer
默认： 500  
 mon mds force trim to
描述:    Force monitor to trim mdsmaps to this point \(0 disables it. dangerous, use with care\)
类型:    Integer
默认： 0  
 mon osd force trim to
描述:    Force monitor to trim osdmaps to this point, even if there is PGs not clean at the specified epoch \(0 disables it. dangerous, use with care\)
类型:    Integer
默认： 0  
 mon osd cache size
描述:    The size of osdmaps cache, not to rely on underlying store’s cache
类型:    Integer
默认： 10  
 mon election timeout
描述:    On election proposer, maximum waiting time for all ACKs in seconds.
类型:    Float
默认： 5  
 mon lease
描述:    The length \(in seconds\) of the lease on the monitor’s versions.
类型:    Float
默认： 5  
 mon lease renew interval factor
描述:    mon lease \* mon lease renew interval factor will be the interval for the Leader to renew the other monitor’s leases. The factor should be less than 1.0.
类型:    Float
默认： 0.6  
 mon lease ack timeout factor
描述:    The Leader will wait mon lease \* mon lease ack timeout factor for the Providers to acknowledge the lease extension.
类型:    Float
默认： 2.0  
 mon accept timeout factor
描述:    The Leader will wait mon lease \* mon accept timeout factor for the Requester\(s\) to accept a Paxos update.   
　　　　　　　　　　It is also used during the Paxos recovery phase for similar purposes.
类型:    Float
默认： 2.0  
 mon min osdmap epochs
描述:    Minimum number of OSD map epochs to keep at all times.
类型: 32\-bit Integer
默认： 500  
 mon max pgmap epochs
描述:    Maximum number of PG map epochs the monitor should keep.
类型: 32\-bit Integer
默认： 500  
  
mon max log epochs
描述:    Maximum number of Log epochs the monitor should keep.
类型: 32\-bit Integer
默认： 500

 时钟

Ceph 守护进程将关键消息传递给彼此，必须在守护进程达到超时阈值之前处理这些消息。 如果 Ceph 监视器中的时钟不同步，则可能导致许多异常。 例如：

1.守护进程忽略收到的消息（例如，时间戳过时）  
2.当没有及时收到消息时，超时/延迟触发超时。

你应该在所有监视器主机上安装 NTP 以确保监视器集群的时钟同步。

时钟漂移即使尚未造成损坏也能被 NTP 感知， Ceph 的时钟漂移或时钟偏差警告即使在 NTP 同步水平合理时也会被触发。提高时钟漂移值有时候尚可容忍， 然而很多因素（像载荷、网络延时、覆盖默认超时值和监控器存储同步选项）都能在不降低 Paxos 保证级别的情况下影响可接受的时钟漂移水平。

Ceph 提供了下列这些可调选项，让你自己琢磨可接受的值。

clock offset
描述:    时钟可以漂移多少，详情见 Clock.cc 。
类型:    Double
默认： 0 自 0.58 版以来已弃用。

mon tick interval
描述:    监视器的心跳间隔，单位为秒。
类型: 32\-bit Integer
默认： 5 mon clock drift allowed
描述:    监视器间允许的时钟漂移量
类型:    Float
默认：    .050 mon clock drift warn backoff
描述:    时钟偏移警告的退避指数。
类型:    Float
默认： 5 mon timecheck interval
描述:    和 leader 的时间偏移检查（时钟漂移检查）。单位为秒。
类型:    Float
默认： 300.0 mon timecheck skew interval
描述:    当 leader 存在 skew 时间时，以秒为单位的时间检查间隔（时钟漂移检查）。
类型:    Float
默认： 30.0

客户端

mon client hunt interval
描述:    客户端每 N 秒尝试一个新监视器，直到它建立连接 类型:    Double
默认： 3.0 mon client ping interval
描述:    客户端每 N 秒 ping 一次监视器。 类型:    Double
默认： 10.0 mon client max log entries per message
描述:    某监视器为每客户端生成的最大日志条数。
类型:    Integer
默认： 1000 mon client bytes
描述:    内存中允许存留的客户端消息数量（字节数）。 类型: 64\-bit Integer Unsigned
默认： 100ul \<\< 20

pool 设置

从版本 v0.94 开始，支持池标志，允许或禁止对池进行更改。

如果以这种方式配置，监视器也可以禁止删除池。

mon allow pool delete
描述:    If the monitors should allow pools to be removed. Regardless of what the pool flags say.
类型:    Boolean
默认： false osd pool default flag hashpspool
描述:    在新池上设置 hashpspool 标志
类型:    Boolean
默认： true osd pool default flag nodelete
描述:    在新池上设置 nodelete 标志。 防止以任何方式删除使用此标志的池。 类型:    Boolean
默认： false osd pool default flag nopgchange
描述:    在新池上设置 nopgchange 标志。 不允许为池更改 PG 的数量。 类型:    Boolean
默认： false osd pool default flag nosizechange
描述:    在新池上设置 nosizechange 标志。 不允许更改池的大小。
类型:    Boolean
默认： false

杂项

mon max osd
描述:    集群允许的最大 OSD 数量。 类型: 32\-bit Integer
默认： 10000 mon globalid prealloc
描述:    为集群和客户端预分配的全局 ID 数量。 类型: 32\-bit Integer
默认： 100 mon subscribe interval
描述:    同步的刷新间隔（秒），同步机制允许获取集群运行图和日志信息。 类型:    Double
默认： 86400 mon stat smooth intervals
描述:    Ceph 将平滑最后 N 个 PG 地图的统计数据。 类型:    Integer
默认： 2 mon probe timeout
描述:    监视器在 bootstrapping 之前等待查找 peers 对等体的秒数。 类型:    Double
默认： 2.0 mon daemon bytes
描述:   给 mds 和 OSD 的消息使用的内存空间（字节）。 类型: 64\-bit Integer Unsigned
默认： 400ul \<\< 20 mon max log entries per event
描述:    每个事件允许的最大日志条数。
类型:    Integer
默认： 4096 mon osd prime pg temp
描述:    Enables or disable priming the PGMap with the previous OSDs when an out OSD comes back into the cluster.   
With the true setting the clients will continue to use the previous OSDs until the newly in OSDs as that PG peered.
类型:    Boolean
默认： true mon osd prime pg temp max time 描述:    当 OSD 返回集群时，监视器应花费多少时间尝试填充 PGMap。 类型:    Float
默认： 0.5 mon osd prime pg temp max time estimate
描述:    Maximum estimate of time spent on each PG before we prime all PGs in parallel.
类型:    Float
默认： 0.25 mon osd allow primary affinity
描述:    允许在 osdmap 中设置 primary\_affinity。 类型:    Boolean
默认：    False

mon osd pool ec fast read
描述:    是否打开池上的快速读取。如果在创建时未指定 fast\_read，它将用作新创建的 erasure pool 的默认设置。 类型:    Boolean
默认：    False

mon mds skip sanity
描述:    Skip safety assertions on FSMap \(in case of bugs where we want to continue anyway\).   
Monitor terminates if the FSMap sanity check fails, but we can disable it by enabling this option.
类型:    Boolean
默认：    False

mon max mdsmap epochs
描述:    The maximum amount of mdsmap epochs to trim during a single proposal.
类型:    Integer
默认： 500 mon config key max entry size
描述:    config-key 条目的最大大小（以字节为单位）类型:    Integer
默认： 4096 mon scrub interval
描述:    How often \(in seconds\) the monitor scrub its store by comparing the stored checksums with the computed ones of all the stored keys.
类型:    Integer
默认： 3600\*24 mon scrub max keys
描述:    The maximum number of keys to scrub each time.
类型:    Integer
默认： 100 mon compact on start
描述:    Compact the database used as Ceph Monitor store on ceph\-mon start.   
A manual compaction helps to shrink the monitor database and improve the performance of it if the regular compaction fails to work.
类型:    Boolean
默认：    False

mon compact on bootstrap
描述:    Compact the database used as Ceph Monitor store on on bootstrap.   
Monitor starts probing each other for creating a quorum after bootstrap. If it times out before joining the quorum, it will start over and bootstrap itself again.
类型:    Boolean
默认：    False

mon compact on trim
描述:    Compact a certain prefix \(including paxos\) when we trim its old states.
类型:    Boolean
默认：    True

mon cpu threads
描述:    Number of threads for performing CPU intensive work on monitor.
类型:    Boolean
默认：    True

mon osd mapping pgs per chunk
描述:    We calculate the mapping from placement group to OSDs in chunks. This option specifies the number of placement groups per chunk.
类型:    Integer
默认： 4096 mon osd max split count
描述:    Largest number of PGs per “involved” OSD to let split create.   
When we increase the pg\_num of a pool, the placement groups will be split on all OSDs serving that pool. We want to avoid extreme multipliers on PG splits.
类型:    Integer
默认： 300 mon session timeout
描述:    Monitor will terminate inactive sessions stay idle over this time limit.
类型:    Integer
默认： 300

## 通过 DNS 查看操作监视器

 从版本 11.0.0 开始，RADOS 支持通过 DNS 查找监视器。

 这样，守护进程和客户端在其 ceph.conf 配置文件中不需要 mon 主机配置指令。

 使用 DNS SRV TCP 记录客户端可以查找监视器。

 这允许在客户端和监视器上进行较少的配置。使用 DNS 更新可以使客户端和守护程序了解监视器拓扑中的更改。

 默认情况下，客户端和守护程序将查找名为 ceph-mon 的 TCP 服务，该服务由 mon\_dns\_srv\_name 配置指令配置。

mon dns srv name
描述:    the service name used querying the DNS for the monitor hosts/addresses
类型:    String
默认：    ceph\-mon

## 心跳设置

### 概述

完成初始 Ceph 配置后，您可以部署并运行 Ceph。 当您执行诸如 ceph health 或 ceph \-s 之类的命令时，Ceph Monitor 会报告 Ceph 存储集群的当前状态。 Ceph Monitor 通过每个 Ceph OSD 守护进程自己的报告，以及从 Ceph OSD Daemons 接收有关其相邻 Ceph OSD 守护进程状态的报告，了解 Ceph 存储群集。 如果 Ceph Monitor 没有收到报告，或者它收到 Ceph 存储集群中的更改报告，Ceph Monitor 会更新 Ceph 集群映射的状态。

Ceph 为 Ceph Monitor / Ceph OSD Daemon 交互提供合理的默认设置。 但是，您可以覆盖默认值。 以下部分描述了 Ceph 监视器和 Ceph OSD 守护进程如何交互以监视 Ceph 存储群集。

### 心跳验证

各 OSD 每 6 秒会与其他 OSD 进行心跳检查，用 \[osd\] 下的 osd heartbeat interval 可更改此间隔、或运行时更改。如果一个 OSD 20 秒都没有心跳，集群就认为它 down 了，用 \[osd\] 下的 osd heartbeat grace 可更改宽限期、或者运行时更改。

![](https://img2018.cnblogs.com/blog/1191664/201811/1191664-20181127133523386-1744710090.png)

### 死亡 OSD 上报 

默认情况下，在 Ceph 监视器确认报告的 Ceph OSD 守护进程已关闭之前，需要来自不同主机的两个 Ceph OSD 守护进程向 Ceph 监视器报告另一个 Ceph OSD 守护进程已关闭。但是，所有报告故障的 OSD 都有可能存放在机架中，并且连接到另一个 OSD 时出现问题。为了避免这种误报，我们认为报告失败的对等体是整个群集中潜在的“子群集”的代理，同样具有类似的滞后性。显然不是所有情况都是这样，但有时会帮助我们优雅校正错误。 mon osd 报告子树级别用于通过 CRUSH 映射中的共同祖先类型将对等体分组到“子集群”中。默认情况下，只需要来自不同子树的两个报告来报告另一个 Ceph OSD 守护进程。你可以通过在 ceph 配置文件里的\[mon\]部分下添加 mon osd min down reporter 和 mon osd reporter subtree level 设置或在运行时设置值。

 ![](https://img2018.cnblogs.com/blog/1191664/201811/1191664-20181127134223342-1157057685.png)

### 报告互连失败

如果一 OSD 守护进程不能和配置文件中定义的任何 OSD 建立连接，它会每 30 秒向监视器索要一次最新集群运行图，你可以在\[osd\]下设置 osd mon heartbeat interval 来更改这个心跳间隔，或者运行时更改

![](https://img2018.cnblogs.com/blog/1191664/201811/1191664-20181127135346746-2070001453.png)

### 报告自己的状态

如果一 OSD 在 mon osd report timeout 时间内没向监视器报告过，监视器就认为它 down 了。OSD 守护进程会向监视器报告某些事件，如某次操作失败、归置组状态变更、 up\_thru 变更、或它将在 5 秒内启动。你可以设置 \[osd\] 下的 osd mon report interval min 来更改最小报告间隔，或在运行时更改。 OSD 守护进程每 120 秒会向监视器报告其状态，不论是否有值得报告的事件。在 \[osd\] 段下设置 osd mon report interval max 可更改 OSD 报告间隔，或运行时更改。

![](https://img2018.cnblogs.com/blog/1191664/201811/1191664-20181127135623185-1226237021.png)

### 配置 

心跳选项应该置于配置文件的 \[global\] 段下。

监视器选项

mon osd min up ratio
描述:    在把 OSD 标记为 down 前，保持处于 up 状态的 OSD 最小比例。
类型:    Double
默认：    .3 mon osd min in ratio
描述:    在把 OSD 标记为 out 前，保持处于 in 状态的 OSD 最小比例 类型:    Double
默认：    .75 mon osd laggy halflife
描述:    The number of seconds laggy estimates will decay.
类型:    Integer
默认： 60\*60 mon osd laggy weight
描述:    The weight for new samples in laggy estimation decay.
类型:    Double
默认： 0.3 mon osd laggy max interval
描述:    Maximum value of laggy\_interval in laggy estimations \(in seconds\).   
Monitor uses an adaptive approach to evaluate the laggy\_interval of a certain OSD. This value will be used to calculate the grace time for that OSD.
类型:    Integer
默认： 300 mon osd adjust heartbeat grace
描述:    If set to true, Ceph will scale based on laggy estimations.
类型:    Boolean
默认： true mon osd adjust down out interval
描述:    If set to true, Ceph will scaled based on laggy estimations.
类型:    Boolean
默认： true mon osd auto mark in 描述:    Ceph 将把任何启动中的 OSD 标记为在集群中（ in ）。 类型:    Boolean
默认： false mon osd auto mark auto out in 描述:    把正在启动、且被自动标记为 out 状态的 OSD 标记为 in 类型:    Boolean
默认： true mon osd auto mark new in 描述:    把正在启动的新 OSD 标记为 in 。 类型:    Boolean
默认： true mon osd down out interval
描述:    在 OSD 停止响应多少秒后把它标记为 down 且 out 。 类型: 32\-bit Integer
默认： 600 mon osd down out subtree limit
描述:    Ceph 不会自动标记的最小 CRUSH 单位类型。例如，如果设置为 host，如果 host 的所有 OSD 都关闭，Ceph 将不会自动标记这些 OSD。类型:    String
默认：    rack

mon osd report timeout
描述:    在声明无响应的 Ceph OSD 守护进程 down 之前的宽限期（以秒为单位）。 类型: 32\-bit Integer
默认： 900 mon osd min down reporters
描述:    报告 Ceph OSD 守护进程 down 所需的最小 Ceph OSD 守护进程数。
类型: 32\-bit Integer
默认： 2 mon osd reporter subtree level
描述:    In which level of parent bucket the reporters are counted.   
The OSDs send failure reports to monitor if they find its peer is not responsive. And monitor mark the reported OSD out and then down after a grace period.
类型:    String
默认：    host

OSD 选项

osd heartbeat address
描述:    OSD 用于心跳的网络地址 类型:    Address
默认：    The host address.

osd heartbeat interval
描述:    一个 OSD 探测它的邻居的间隔时间（秒） 类型: 32\-bit Integer
默认： 6 osd heartbeat grace
描述:    Ceph OSD 守护进程没有显示 Ceph 存储集群认为它已关闭的心跳所经过的时间。 必须在\[mon\]和\[osd\]或\[global\]部分中设置此设置，以便 MON 和 OSD 守护程序都可以读取它。 类型: 32\-bit Integer
默认： 20 osd mon heartbeat interval
描述:    OSD 没有邻居时多久探测一次监视器 类型: 32\-bit Integer
默认： 30 osd mon report interval
描述:    监视器允许 OSD 报告的最大间隔，超时将认为 OSD 挂了（ down ）。 类型: 32\-bit Integer
默认： 5 osd mon ack timeout
描述:    等待 Ceph Monitor 确认统计请求的秒数。 类型: 32\-bit Integer
默认： 30

## OSD 设置

### 概述

你可以通过配置文件调整 OSD ，仅靠默认值和极少的配置 OSD 守护进程就能运行。最简 OSD 配置需设置 osd journal size 和 host ，其他几乎都能用默认值。

Ceph 的 OSD 守护进程用递增的数字作标识，按惯例以 0 开始，如下：

osd.0 osd.1 osd.2

在配置文件里， \[osd\] 段下的配置适用于所有 OSD ；要添加针对特定 OSD 的选项（如 host ），把它放到那个 OSD 段下即可，如

\[osd\]
        osd journal size \= 5120 \[osd.0\]
        host \= osd-host-a

\[osd.1\]
        host \= osd-host-b

### 常规配置

下列选项可配置一 OSD 的唯一标识符、以及数据和日志的路径。 Ceph 部署脚本通常会自动生成 UUID 。我们不建议更改数据和日志的默认路径，因为这样会增加后续的排障难度。

日志尺寸应该大于期望的驱动器速度和 filestore max sync interval 之乘积的两倍；最常见的方法是为日志驱动器（通常是 SSD ）分区并挂载好，这样 Ceph 就可以用整个分区做日志。

osd uuid
描述:    OSD 的全局唯一标识符（ UUID ）。 类型:    UUID
默认：    The UUID.
Note:    osd uuid 适用于单个 OSD ， fsid 适用于整个集群。  
osd data
描述:    OSD 数据存储位置，你得创建并把数据盘挂载到其下。我们不推荐更改默认值。 类型:    String
默认： /var/lib/ceph/osd/\$cluster-\$id osd max write size
描述:    一次写入的最大尺寸，MB。 类型: 32\-bit Integer
默认： 90 osd max object size
描述:    一个 object 最大大小（字节）bytes.
类型: 32\-bit Unsigned Integer
默认：    128MB

osd client message size cap
描述:    内存里允许的最大客户端数据消息。 类型: 64\-bit Unsigned Integer
默认：    500MB default. 500\*1024L\*1024L osd class dir 描述:    RADOS 类插件的路径。 类型:    String
默认：    \$libdir/rados-classes

### 文件系统选项

Ceph 构建并安装文件系统用于 Ceph OSD

osd mkfs options \{fs-type\}
描述:    为 OSD 新建 \{fs-type\} 类型的文件系统时使用的选项。 类型:    String
Default for xfs: \-f -i 2048 Default for other file systems:
     \{empty string\}
For example::
osd mkfs options xfs \= -f -d agcount=24 osd mount options \{fs-type\}
描述:    挂载 \{fs-type\} 类型的文件系统作为 OSD 数据目录时所用的选项。 类型:    String
Default for xfs:
     rw,noatime,inode64
Default for other file systems:
     rw, noatime
For example::
osd mount options xfs = rw, noatime, inode64, logbufs=8

### 日志选项

默认情况下，Ceph 期望你把 OSD 日志存入以下路径

/var/lib/ceph/osd/\$cluster-\$id/journal

使用单一设备类型（例如，旋转驱动器）时，应该共同使用日志：逻辑卷（或分区）应与数据逻辑卷位于同一设备中。

当使用快速（SSD，NVMe）设备与较慢设备（如旋转驱动器）的混合时，将日志放在更快的设备上是有意义的，而数据完全占用较慢的设备。

默认的 osd 日志大小值是 5120（5GB），但它可以更大，在这种情况下需要在 ceph.conf 文件中设置：

osd journal
描述:    OSD 日志路径，可以是一个文件或块设备（ SSD 的一个分区）的路径。如果是文件，要先创建相应目录。我们建议用 osd data 以外的独立驱动器。 类型:    String
默认： /var/lib/ceph/osd/\$cluster-\$id/journal

osd journal size
描述:    日志大小（MB） 类型: 32\-bit Integer
默认： 5120

### 监视器 OSD 交互

Ceph OSD 守护进程检查对方的心跳并定期向监视器报告。 在许多情况下，Ceph 可以使用默认值。 但是，如果您的网络存在延迟问题，则可能需要采用更长的时间间隔。 有关心跳的详细讨论，请参阅心跳。

### 数据放置

有关详细信息，请参见 Pool＆PG Config Reference。

### SCRUBBING

除了为对象复制多个副本外，Ceph 还要洗刷归置组确认数据完整性。这种洗刷类似对象存储层的 fsck，对每个归置组，Ceph 生成一个所有对象的目录，并比对每个主对象及其副本以确保没有对象丢失或错配。轻微洗刷（每天）检查对象尺寸和属性，深层洗刷（每周）会读出数据并用校验和方法确认数据完整性。

洗刷对维护数据完整性很重要，但会影响性能;你可以用下列选项来增加或减少洗刷操作。

osd max scrubs
描述:    Ceph OSD 守护进程的最大同步清理操作数。 类型: 32\-bit Int
默认： 1 osd scrub begin hour
描述:    清理的下限时间 类型:    Integer in the range of 0 to 24 默认： 0 osd scrub end hour
描述:    可以执行预定清理时的上限时间。 与 osd scrub begin hour 一起定义了一个时间窗口，可以在其中进行擦洗。 但是，无论时间窗口是否允许，只要放置组的擦洗间隔超过 osd scrub max interval 都将进行擦洗。 默认： 24 osd scrub during recovery
描述:    在恢复期间允许擦洗。 将此设置为 false 将禁用在有活动恢复时安排新的清理（和深度清理）。 如果已经开始将继续执行。 这有助于减轻集群繁忙时上的负载。 类型:    Boolean
默认： true osd scrub thread timeout
描述:    The maximum time in seconds before timing out a scrub thread.
类型: 32\-bit Integer
默认： 60 osd scrub finalize thread timeout
描述:    The maximum time in seconds before timing out a scrub finalize thread.
类型: 32\-bit Integer
默认： 60\*10 osd scrub load threshold
描述:    标准化的最大负载。 当系统负载（由 getloadavg（）/online cpu numbers）高于此数字时，Ceph 不会擦除。 类型:    Float
默认： 0.5 osd scrub min interval
描述:    当 Ceph 存储集群负载较低时，擦除 Ceph OSD 守护程序的最小间隔（秒）。 类型:    Float
默认：    Once per day. 60\*60\*24 osd scrub max interval
描述:    无论群集负载如何，擦除 Ceph OSD 守护进程的最大间隔（秒）。 类型:    Float
默认：    Once per week. 7\*60\*60\*24 osd scrub chunk min
描述:    在单个操作期间要擦除的最小数量的对象存储块。 Ceph 在擦洗期间阻止写入单个块。 类型: 32\-bit Integer
默认： 5 osd scrub chunk max
描述:    单个操作期间要擦除的最大对象存储块数。 类型: 32\-bit Integer
默认： 25 osd scrub sleep 描述:    在擦洗下一组块之前休眠的时间。 增加此值将减慢整个清理操作，同时客户端操作受影响较小 类型:    Float
默认： 0 osd deep scrub interval
描述:    深度”清理的间隔（完全读取所有数据）。 osd scrub load threshold 不会影响此设置。 类型:    Float
默认：    Once per week. 60\*60\*24\*7 osd scrub interval randomize ratio
描述:    在给某一归置组调度下一个洗刷作业时，给 osd scrub min interval 增加个随机延时，这个延时是个小于 osd scrub min interval \* osd scrub interval randomized ratio 的随机值。  
　　　　  所以在实践中，这个默认设置会把洗刷操作随机地散布到允许的时间窗口内，即 \[1, 1.5\] \* osd scrub min interval 。 类型:    Float
默认： 0.5 osd deep scrub stride
描述:    深层洗刷时的读取尺寸
类型: 32\-bit Integer
默认： 512 KB. 524288

### 操作选项

osd op queue
描述：这设置了用于在 OSD 中优先化操作的队列类型。所有队列都具有严格的子队列，该队列在正常队列之前出列。
原始的 PrioritizedQueue（prio）使用令牌桶系统，当有足够的令牌时，它将首先使高优先级队列出列。如果没有足够的令牌可用，则队列将从低优先级出列到高优先级。
WeightedPriorityQueue（wpq）将所有优先级与其优先级相关联，以防止任何队列出现饥饿。如果少数 OSD 比其他 OSD 更加过载，WPQ 应该会有所帮助。
新的基于 OpClassQueue（mclock\_opclass）的 mClock 根据它们所属的类（recovery, scrub, snaptrim, client op, osd subop）对操作进行优先级排序。
并且，基于 ClientQueue（mclock\_client）的 mClock 还包含客户端标识符，以促进客户端之间的公平性。参阅 QoS Based on mClock。需要重启。
类型：String
有效选择：prio，wpq，mclock\_opclass，mclock\_client
默认值：PRIO

osd op queue cut off
描述：这将选择将哪些优先级操作发送到严格队列和普通队列。
设置为 low 将所有 replication 操作和更高级别的操作发送到 strict 队列，而设置为 high 将 replication acknowledgement 操作和更高级别的操作发送到 strict 队列。
如果群集中的一些 OSD 非常繁忙，将此设置为高，并将 osd op queue 设置中与 wpq 结合使用时，应该会有所帮助。
处理复制流量非常繁忙的 OSD 可能会在没有这些设置的情况下使主要客户端流量在这些 OSD 上匮乏。需要重启。
类型：String
有效选择:    low, high
默认值:    low

osd client op priority
描述：为客户端操作设置的优先级。它与 osd recovery op priority 关联。
类型：32 位整数
默认值：63 有效范围：1\-63 osd recovery op priority
描述：为恢复操作设置的优先级。它与 osd client op priority 关联。
类型：32 位整数
默认值：3 有效范围：1\-63 osd scrub priority
描述：为清理操作设置的优先级。它与 osd client op priority 相关。
类型：32 位整数
默认值：5 有效范围：1\-63 osd snap trim priority
描述：为 snap trim 操作设置的优先级。它与 osd client op priority 相关。
类型：32 位整数
默认值：5 有效范围：1\-63 osd op thread timeout
描述：Ceph OSD 守护进程操作线程超时（秒）。
类型：32 位整数
默认值：15 osd op complaint time 描述：在指定的秒数过后，操作 becomes complaint worthy。
类型：float 默认值：30 osd disk threads
描述：磁盘线程数，用于执行后台磁盘密集型 OSD 操作，例如 scrubbing 和 snap trimming。
类型：32 位整数
默认值：1 osd disk thread ioprio class
描述：警告：仅当 osd disk thread ioprio class 和 osd disk thread ioprio priority 都设置为非默认值时才会使用它。
ioprio\_set\(2\) I/O scheduling class 设置磁盘线程。
可接受的值是空字符串，be 或 rt。空闲类意味着磁盘线程的优先级低于 OSD 中的任何其他线程。这对于在忙于处理客户端操作的 OSD 上减慢擦除非常有用。
be 是默认值，与 OSD 中的所有其他线程具有相同的优先级。 rt 表示磁盘线程优先于 OSD 中的所有其他线程。
注意：仅适用于 Linux 内核 CFQ 调度程序。从 Jewel 版本开始磁盘 iothread 不再执行擦除，请参阅 osd priority options。
类型：String
默认值：空字符串

osd disk thread ioprio priority
说明：警告：仅当 osd disk thread ioprio class 和 osd disk thread ioprio priority 都设置为非默认值时才会使用它。
它设置磁盘线程的 ioprio\_set\(2\) I/O scheduling priority，范围从 0（最高）到 7（最低）。
如果给定主机上的所有 OSD 都处于空闲状态并且竞争 I / O（即由于控制器拥塞），则可以使用它将一个 OSD 的磁盘线程优先级降低到 7，以便优先级为 0 的另一个 OSD 可以具有优先级。 
注意：仅适用于 Linux 内核 CFQ 调度程序。
类型：整数，范围为 0 到 7，如果不使用为\-1。
默认值：\-1 osd op history size
描述：跟踪已完成操作的最大数量。
键入：32 位无符号整数
默认值：20 osd op history duration
描述：最早完成的操作跟踪。
键入：32 位无符号整数
默认值：600 osd op log threshold
描述：一次显示多少个操作日志。
类型：32 位整数
默认值：5

### 基于 MCLOCK 的 QOS

Ceph 对 mClock 的使用目前正处于试验阶段。

### 核心概念

Ceph 的 QoS 支持使用基于 dmClock 算法的排队调度器来实现。该算法按权重比例分配 Ceph 集群的 I / O 资源，并实施最小预留和最大限制的约束，使服务可以公平地竞争资源。目前，mclock\_opclass 操作队列将涉及 I / O 资源的 Ceph 服务划分为以下几类：

client op：客户端发出的 iops  
osd subop：主 OSD 发布的 iops  
snap trim：快照修剪相关请求  
pg recovery：与恢复相关的请求  
pg scrub：与擦洗相关的请求

并使用以下三组标记对资源进行分区。换句话说，每种服务类型的由三个标签控制：

reservation：为服务分配的最小 IOPS。  
limitation：为服务分配的最大 IOPS。  
weight：如果额外容量或系统超额订购，则按比例分配容量。

在 Ceph 运营中，评级为“cost”。并且为这些“成本”消耗分配用于服务各种服务的资源。因此，例如，只要需要，服务的预留越多，保证拥有的资源就越多。假设有两种服务：恢复和客户端操作：

恢复：（r：1，l：5，w：1）  
客户操作：（r：2，l：0，w：9）

上述设置确保恢复每秒服务的请求数不会超过 5 个，即使它需要服务，并且没有其他服务与之竞争。但是，如果客户端开始发出大量 I / O 请求，它们也不会耗尽所有 I / O 资源。只要有任何此类请求，就始终为恢复作业分配每秒 1 个请求。因此，即使在高负载的群集中，恢复作业也不会匮乏。与此同时，客户端操作系统可以享受更大部分的 I / O 资源，因为它的权重为“9”，而其竞争对手为“1”。对于客户端操作，它不受 limit setting 设置限制，因此如果没有正在进行恢复，它可以利用所有资源。

与 mclock\_opclass 一起，另一个名为 mclock\_client 的 mclock operation queue 可用。它根据类别划分操作，但也根据发出请求的客户端对它们进行划分。这不仅有助于管理在不同类别的操作上花费的资源分配，还有助于确保客户之间的公平性。

当前实现注意：当前的实验实现不强制执行限制值。作为第一个近似值，我们决定不阻止进入操作序列器的操作。

### MCLOCK 的细节

reservation 和 limit 值具有每秒请求单位。然而，weight 在技术上不具有单元并且 weight 是相对的。因此，如果一类请求的权重为 1 而权重为 9，那么后一类请求应该以 9 比 1 的比率执行。

即使权重没有单位，算法为请求分配权重，因此必须谨慎选择其值。如果权重为 W，则对于给定类别的请求，下一个请求将具有 1 / W 的权重标记加上先前的权重标记或当前时间，以较大者为准。这意味着如果 W 太大而 1 / W 太小，则可能永远不会分配计算的标签，因为它将获得当前时间的值。最终的教训是重量值不应该太大。它们应该在每秒预期服务的请求数量之下。

### CAVEATS

有一些因素可以减少 Ceph 中 mClock 操作队列的影响。首先，对 OSD 的请求按其放置组标识符进行分片。每个分片都有自己的 mClock 队列，这些队列既不会交互也不会在它们之间共享信息。可以使用配置选项 osd\_op\_num\_shards，osd\_op\_num\_shards\_hdd 和 osd\_op\_num\_shards\_ssd 来控制分片数。较少数量的分片会增加 mClock 队列的影响，但可能会产生其他有害影响。

其次，请求从操作队列传输到操作序列器，在操作序列器中执行真正的处理。操作队列是 mClock 所在的位置，mClock 确定要传输到操作序列器的下一个操作。操作序列器中允许的操作数是一个复杂的问题。一般来说，我们希望在序列器中保留足够的操作数，以便在等待磁盘和网络访问完成其他操作时，总是在某些操作上完成工作。另一方面，一旦操作转移到操作序列器，mClock 就不再能控制它。因此，为了最大化 mClock 的影响，我们希望尽可能少地在操作序列器中进行操作。

影响操作序列器中操作数的配置选项为 bluestore\_throttle\_bytes，bluestore\_throttle\_deferred\_bytes，bluestore\_throttle\_cost\_per\_io，bluestore\_throttle\_cost\_per\_io\_hdd 和 bluestore\_throttle\_cost\_per\_io\_ssd。

影响 mClock 算法影响的第三个因素是我们正在使用分布式系统，其中对多个 OSD 进行请求，并且每个 OSD 具有（可以具有）多个分片。然而，我们目前正在使用的 mClock 算法不是分布式的（dmClock 是 mClock 的分布式版本）。

目前，各种组织和个人正在尝试使用 mClock，我们希望您能在 ceph-devel 邮件列表中分享您对 mClock 和 dmClock 实验的体验。

osd push per object cost
描述：服务一个 push 操作的开销
类型：无符号整数
默认值：1000 osd recovery max chunk
描述：恢复操作可以携带的数据块的最大大小。
类型：无符号整数
默认值：8 MiB

osd op queue mclock client op res
描述:    客户端操作的 reservation
类型：float 默认值：1000.0 osd op queue mclock client op wgt
描述：客户端操作的权重。
类型：float 默认值：500.0 osd op queue mclock client op lim
描述：客户端操作的 limit。
类型：float 默认值：1000.0 osd op queue mclock osd subop res
描述：osd subop 的保留。
类型：float 默认值：1000.0 osd op queue mclock osd subop wgt
描述：osd subop 的权重。
类型：float 默认值：500.0 osd op queue mclock osd subop lim
描述：osd subop 的限制。
类型：float 默认值：0.0 osd op queue mclock snap res
描述：snap trimming 的 reservation 。
类型：float 默认值：0.0 osd op queue mclock snap wgt
描述：snap trimming 的权重。
类型：float 默认值：1.0 osd op queue mclock snap lim
描述：snap trimming 的限制。
类型：float 默认值：0.001 osd op queue mclock recov res
描述：    the reservation of recovery.
类型:    Float
默认值: 0.0 osd op queue mclock recov wgt
描述：    the weight of recovery.
类型:    Float
默认值: 1.0 osd op queue mclock recov lim
描述：    the limit of recovery.
类型:    Float
默认值: 0.001 osd op queue mclock scrub res
描述：    the reservation of scrub jobs.
类型:    Float
默认值: 0.0 osd op queue mclock scrub wgt
描述：    the weight of scrub jobs.
类型:    Float
默认值: 1.0 osd op queue mclock scrub lim
描述：    the limit of scrub jobs.
类型:    Float
默认值: 0.001

### BACKFILLING  

当集群新增或移除 OSD 时，按照 CRUSH 算法应该重新均衡集群，它会把一些归置组移出或移入多个 OSD 以回到均衡状态。归置组和对象的迁移会导致集群运营性能显著降低，为维持运营性能， Ceph 用 backfilling 来执行此迁移，它可以使得 Ceph 的回填操作优先级低于用户读写请求。

osd max backfills
描述：    每个 OSD 允许的最大回填数
类型： 64\-bit Unsigned Integer
默认值： 1 osd backfill scan min
描述：    每次回填的最小对象数目
类型： 32\-bit Integer
默认值： 64 osd backfill scan max
描述：    每次回填的最大对象数目
类型： 32\-bit Integer
默认值： 512 osd backfill retry interval
描述：    回填重试请求间隔 类型：    Double
默认值： 10.0

### OSD MAP

OSD 映射反映了在群集中运行的 OSD 守护进程。 随着时间的推移， map epochs 的数量增加。 Ceph 提供了一些设置，以确保 Ceph 在 OSD MAP 变大时表现良好。

osd map dedup
描述：    启用删除 OSD 映射中的重复项。
类型：    Boolean
默认值： true osd map cache size
描述：    缓存中保存的 OSD map 数目
类型： 32\-bit Integer
默认值： 500 osd map cache bl size
描述：    OSD 守护进程中内存中 OSD map 缓存的大小。
类型： 32\-bit Integer
默认值： 50 osd map cache bl inc size
描述：    OSD 守护进程中内存中 OSD 映射缓存增量尺寸。
类型： 32\-bit Integer
默认值： 100 osd map message max
描述：    每个 MOSDMap 图消息允许的最大条目数量。
类型： 32\-bit Integer
默认值： 100

### RECOVERY

当集群启动、或某 OSD 守护进程崩溃后重启时，此 OSD 开始与其它 OSD 们建立连接，这样才能正常工作。

如果某 OSD 崩溃并重生，通常会落后于其他 OSD ，也就是没有同归置组内最新版本的对象。这时， OSD 守护进程进入恢复模式并检索最新数据副本，并更新运行图。根据 OSD 挂的时间长短， OSD 的对象和归置组可能落后得厉害，另外，如果挂的是一个失效域（如一个机柜），多个 OSD 会同时重生，这样恢复时间更长、更耗资源。

为保持运营性能， Ceph 进行恢复时会限制恢复请求数、线程数、对象块尺寸，这样在降级状态下也能保持良好的性能

osd recovery delay start
描述：    对等关系建立完毕后， Ceph 开始对象恢复前等待的时间（秒）。
类型：    Float
默认值： 0 osd recovery max active
描述：    每个 OSD 一次处理的活跃恢复请求数量，增大此值能加速恢复，但它们会增加集群负载。
类型： 32\-bit Integer
默认值： 3 osd recovery max chunk
描述：    一次推送的数据块的最大尺寸。
类型： 64\-bit Unsigned Integer
默认值： 8 \<\< 20 osd recovery max single start
描述：    OSD 恢复时将重新启动的每个 OSD 的最大恢复操作数。
类型： 64\-bit Unsigned Integer
默认值： 1 osd recovery thread timeout
描述：    恢复现成超时时间
类型： 32\-bit Integer
默认值： 30 osd recover clone overlap
描述：    Preserves clone overlap during recovery. Should always be set to true.
类型：    Boolean
默认值： true osd recovery sleep 描述：    下次恢复或回填操作前的睡眠时间（以秒为单位）。增加此值将减慢恢复操作，同时客户端操作受影响较小。
类型：    Float
默认值： 0 osd recovery sleep hdd
描述：    下次恢复或硬盘回填操作之前的休眠时间（以秒为单位）。
类型：    Float
默认值： 0.1 osd recovery sleep ssd
描述：    下次恢复之前或回填 SSD 休眠的时间（以秒为单位）。
类型：    Float
默认值： 0 osd recovery sleep hybrid
描述：    当 osd 数据在 HDD 上并且 osd 日志在 SSD 上时，下一次恢复或回填操作之前的休眠时间（以秒为单位）。
类型：    Float
默认值： 0.025

### TIERING

osd agent max ops
描述：高速模式下每个分层代理的最大同时刷新操作数。
类型：32 位整数
默认值：4 osd agent max low ops
描述：低速模式下每个分层代理的最大同时刷新操作数。
类型：32 位整数
默认值：2

### 杂项

osd snap trim thread timeout
描述：    snap trim 线程超时时间
类型： 32\-bit Integer
默认值： 60\*60\*1 osd backlog thread timeout
描述：    backlog 线程超时时间
类型： 32\-bit Integer
默认值： 60\*60\*1 osd default notify timeout
描述：    OSD 默认通知超时（以秒为单位）。
类型： 32\-bit Unsigned Integer
默认值： 30 osd check for log corruption
描述：    检查日志文件是否损坏。计算消耗大。
类型：    Boolean
默认值： false osd remove thread timeout
描述：    remove OSD thread 超时时间
类型： 32\-bit Integer
默认值： 60\*60 osd command thread timeout
描述：    command thread 超时时间
类型： 32\-bit Integer
默认值： 10\*60 osd command max records
描述：    Limits the number of lost objects to return.
类型： 32\-bit Integer
默认值： 256 osd fast fail on connection refused
描述：    如果启用此选项，则连接的对等设备和 MON 会立即标记崩溃的 OSD（假设已崩溃的 OSD 主机存活）。禁用 restore，代价是在 I / O 操作中 OSD 崩溃时可能存在长 I / O 停顿。
类型：    Boolean
默认值： true

## BlueStore 设置

### 设备

BlueStore 管理一个，两个或（在某些情况下）三个存储设备。

在最简单的情况下，BlueStore 使用单个（主）存储设备。存储设备通常作为一个整体使用，BlueStore 直接占用完整设备。该主设备通常由数据目录中的块符号链接标识。

数据目录挂载成一个 tmpfs，它将填充（在启动时或 ceph-volume 激活它时）所有常用的 OSD 文件，其中包含有关 OSD 的信息，例如：其标识符，它所属的集群，以及它的私钥。

还可以使用两个额外的设备部署 BlueStore：

* WAL 设备（在数据目录中标识为 block.wal）可用于 BlueStore 的内部日志或预写日志。只有设备比主设备快（例如，当它在 SSD 上并且主设备是 HDD 时），使用 WAL 设备是有用的。
* 数据库设备（在数据目录中标识为 block.db）可用于存储 BlueStore 的内部元数据。 BlueStore（或者更确切地说，嵌入式 RocksDB）将在数据库设备上放置尽可能多的元数据以提高性能。如果数据库设备填满，元数据将写到主设备。同样，数据库设备要比主设备更快，则提供数据库设备是有帮助的。

如果只有少量快速存储可用（例如，小于 1GB），我们建议将其用作 WAL 设备。如果还有更多，配置数据库设备会更有意义。 BlueStore 日志将始终放在可用的最快设备上，因此使用数据库设备将提供与 WAL 设备相同的优势，同时还允许在其中存储其他元数据。

单个设备上配置 bluestore

ceph-volume lvm prepare --bluestore --data \<device>

指定 WAL 设备和/或数据库设备，

ceph-volume lvm prepare --bluestore --data \<device> --block.wal \<wal-device> --block.db \<db-device>

注意 \- data 可以是使用 vg / lv 表示法的逻辑卷。 其他设备可以是现有逻辑卷或 GPT 分区

### 部署

虽然有多种方法可以部署 Bluestore OSD，但这里有两个常见的用例，可以帮助阐明初始部署策略：

* BLOCK \(DATA\) ONLY

如果所有设备都是相同的类型，例如所有设备都是 HDD，并且没有快速设备来组合这些设备，那么仅使用此方法部署并且不将 block.db 或 block.wal 分开是有意义的。 对单个/ dev / sda 设备的 lvm 调用如下所示：

ceph-volume lvm create --bluestore --data /dev/sda

如果已经为每个设备创建了逻辑卷（1 个 LV 使用 100％的设备），则对名为 ceph-vg / block-lv 的 lv 的 lvm 调用如下所示：

ceph-volume lvm create --bluestore --data ceph-vg/block-lv

* BLOCK AND BLOCK.DB

如果混合使用快速和慢速设备（旋转和固态），建议将 block.db 放在速度更快的设备上，而块（数据）则放在较慢的设备上（旋转驱动器）。 block.db 的大小应该尽可能大，以避免性能损失。 ceph-volume 工具目前无法自动创建，因此需要手动创建卷组和逻辑卷。

对于下面的示例，假设有 4 个旋转驱动器（sda，sdb，sdc 和 sdd）和 1 个固态驱动器（sdx）。 首先创建卷组：

\$ vgcreate ceph-block-0 /dev/sda
\$ vgcreate ceph\-block-1 /dev/sdb
\$ vgcreate ceph\-block-2 /dev/sdc
\$ vgcreate ceph\-block-3 /dev/sdd

现在创建逻辑卷：

\$ lvcreate -l 100\%FREE -n block-0 ceph-block-0 \$ lvcreate \-l 100\%FREE -n block-1 ceph-block-1 \$ lvcreate \-l 100\%FREE -n block-2 ceph-block-2 \$ lvcreate \-l 100\%FREE -n block-3 ceph-block-3

我们正在为四个慢速旋转设备创建 4 个 OSD，因此假设/ dev / sdx 中有 200GB SSD，我们将创建 4 个逻辑卷，每个 50GB：

\$ vgcreate ceph-db-0 /dev/sdx
\$ lvcreate \-L 50GB -n db-0 ceph-db-0 \$ lvcreate \-L 50GB -n db-1 ceph-db-0 \$ lvcreate \-L 50GB -n db-2 ceph-db-0 \$ lvcreate \-L 50GB -n db-3 ceph-db-0

最后，使用 ceph-volume 创建 4 个 OSD：

\$ ceph-volume lvm create --bluestore --data ceph-block-0/block-0 --block.db ceph-db-0/db-0 \$ ceph\-volume lvm create --bluestore --data ceph-block-1/block-1 --block.db ceph-db-0/db-1 \$ ceph\-volume lvm create --bluestore --data ceph-block-2/block-2 --block.db ceph-db-0/db-2 \$ ceph\-volume lvm create --bluestore --data ceph-block-3/block-3 --block.db ceph-db-0/db-3

使用混合旋转和固态驱动器设置时，为 Bluestore 创建足够大的 block.db 逻辑卷非常重要。 通常，block.db 应具有尽可能大的逻辑卷。

建议 block.db 大小不小于块的 4％。 例如，如果块大小为 1TB，则 block.db 不应小于 40GB。

如果不使用快速和慢速设备的混合，则不需要为 block.db（或 block.wal）创建单独的逻辑卷。 Bluestore 将在块空间内自动管理这些内容。

### 缓存自动调节

当 tc\_malloc 配置为内存分配器并且启用了 bluestore\_cache\_autotune 设置时，可以将 Bluestore 配置为自动调整其缓存大小。

默认情况下，此选项当前已启用。 Bluestore 将尝试通过 osd\_memory\_target 配置选项将 OSD 堆内存使用量保持在指定的目标大小。 这是一种尽力而为的算法，缓存的收缩率不会小于 osd\_memory\_cache\_min 指定的数量。 高速缓存比率基于优先级的层次来选择。 如果不提供优先级信息，则将 bluestore\_cache\_meta\_ratio 和 bluestore\_cache\_kv\_ratio 选项用作回退。

bluestore\_cache\_autotune
描述：    在遵循最小值的同时自动调整分配给不同 bluestore 缓存的比率。
类型：    Boolean
是否必须：    Yes
默认值    True

osd\_memory\_target
描述：    当 tcmalloc 可用且启用了缓存自动调整时，将尝试将这么多字节映射到内存中。
注意：这可能与进程的 RSS 内存使用不完全匹配。虽然进程映射的堆内存总量通常应该接近此目标，但无法保证内核实际上将回收未映射的内存。
在最初的开发过程中，发现一些内核导致 OSD 的 RSS 内存超过映射内存高达 20％。
然而，假设当存在大量内存压力时，内核通常可能更积极地回收未映射的内存。
类型：    Unsigned Integer
是否必须：    Yes
默认值 4294967296 bluestore\_cache\_autotune\_chunk\_size
描述：    启用高速缓存自动调节时分配给高速缓存的块大小（以字节为单位）。当 autotuner 将内存分配给不同的缓存时，它将以 chunk 的形式分配内存。  
这样做是为了避免在堆大小或自动调整的高速缓存比率有轻微波动时 evictions
类型：    Unsigned Integer
是否必须：    No
默认值 33554432 bluestore\_cache\_autotune\_interval
描述：    启用高速缓存自动调节后重新平衡的的间隔。将间隔设置得太小会导致 CPU 使用率过高和性能下降。
类型：    Float
是否必须：    No
默认值 5 osd\_memory\_base
描述：    启用 tcmalloc 和缓存自动调整时，估计 OSD 所需的最小内存量（以字节为单位）。这用于帮助自动调整器估计高速缓存的预期聚合内存消耗。
类型：    Unsigned Interger
是否必须：    No
默认值 805306368 osd\_memory\_expected\_fragmentation
描述：    启用 tcmalloc 和缓存自动调整时，估计内存碎片的百分比。这用于帮助自动调整器估计高速缓存的预期聚合内存消耗。
类型：    Float
是否必须：    No
默认值 0.15 osd\_memory\_cache\_min
描述：    启用 tcmalloc 和缓存自动调整时，设置用于缓存的最小内存量。注意：将此值设置得太低会导致明显的缓存抖动。
类型：    Unsigned Integer
是否必须：    No
默认值 134217728 osd\_memory\_cache\_resize\_interval
描述：    启用 tcmalloc 和缓存自动调整时，调整缓存大小间隔（秒）。此设置更改 bluestore 可用于缓存的总内存量。注意：将间隔设置得太小会导致内存分配器抖动并降低性能。
类型：    Float
是否必须：    No
默认值 1

### 手动调节缓存

BlueStore 缓存的每个 OSD 消耗的内存量由 bluestore\_cache\_size 配置选项决定。如果未设置该配置选项（即，保持为 0），则根据是否将 HDD 或 SSD 用于主设备（由 bluestore\_cache\_size\_ssd 和 bluestore\_cache\_size\_hdd 配置选项设置），使用不同的默认值。

BlueStore 和 Ceph OSD 的其余部分目前最好能够地严格预算内存。除了配置的高速缓存大小之外，还有 OSD 本身消耗的内存，并且通常由于内存碎片和其他分配器开销而产生一些开销。

配置的高速缓存内存预算可以通过几种不同的方式使用：

* Key/Value 元数据（即 RocksDB 的内部缓存）
* BlueStore 元数据
* BlueStore 数据（即最近读取或写入的对象数据）

高速缓存内存使用情况由以下选项控制：bluestore\_cache\_meta\_ratio，bluestore\_cache\_kv\_ratio 和 bluestore\_cache\_kv\_max。专用于数据的缓存部分是 1.0 减去 meta 和 kv 比率。专用于 kv 元数据的内存（RocksDB 缓存）由 bluestore\_cache\_kv\_max 限制。

bluestore\_cache\_size
描述：    BlueStore 将用于其缓存的内存量。如果为零，则将使用 bluestore\_cache\_size\_hdd 或 bluestore\_cache\_size\_ssd。
类型：    Unsigned Integer
是否必须：    Yes
默认值 0 bluestore\_cache\_size\_hdd
描述：    当由 HDD 支持时，BlueStore 将用于其缓存的默认内存量。
类型：    Unsigned Integer
是否必须：    Yes
默认值 1 \* 1024 \* 1024 \* 1024 \(1 GB\)

bluestore\_cache\_size\_ssd
描述：    当 SSD 支持时，BlueStore 将用于其缓存的默认内存量。
类型：    Unsigned Integer
是否必须：    Yes
默认值 3 \* 1024 \* 1024 \* 1024 \(3 GB\)

bluestore\_cache\_meta\_ratio
描述：    专用于元数据的缓存比率。
类型：    Floating point
是否必须：    Yes
默认值    .01 bluestore\_cache\_kv\_ratio
描述：    专用于键/值数据的缓存比率（rocksdb）。
类型：    Floating point
是否必须：    Yes
默认值    .99 bluestore\_cache\_kv\_max
描述：    用于键/值数据（rocksdb）的最大缓存量。
类型：    Unsigned Integer
是否必须：    Yes
默认值 512 \* 1024\*1024 \(512 MB\)

### 校验

BlueStore 校验所有写入磁盘的元数据和数据。元数据校验和由 RocksDB 处理并使用 crc32c。数据校验和由 BlueStore 完成，可以使用 crc32c，xxhash32 或 xxhash64。默认值为 crc32c，取值适合大多数用途。

完整数据校验和确实增加了 BlueStore 必须存储和管理的元数据量。在可能的情况下，例如，当客户端指示数据被顺序写入和读取时，BlueStore 将校验更大的块，但在许多情况下，它必须为每 4 千字节数据块存储校验和值（通常为 4 个字节）。

通过将校验和截断为两个或一个字节，可以使用较小的校验和值，从而减少元数据开销。权衡的是，随着校验和越小，检测不到随机错误的概率越高，从大约 32 位（4 字节）校验的四十亿分之一到 16 位（ 2 字节）校验的 1/65536，和 8 位（1 字节）校验的 1/256。通过选择 crc32c\_16 或 crc32c\_8 作为校验和算法，可以使用较小的校验和值。

校验和算法可以通过每个池的 csum\_type 属性或 global config 选项设置。例如

ceph osd pool set \<pool-name> csum\_type \<algorithm>

bluestore\_csum\_type
描述：要使用的默认校验和算法。
类型：String
要求：有
有效设置：none，crc32c，crc32c\_16，crc32c\_8，xxhash32，xxhash64
默认值：crc32c

### 内联压缩

BlueStore 内联压缩支持 snappy，zlib 和 lz4。lz4 压缩插件在官方发行版中不是分布式版本。

BlueStore 中的数据是否被压缩是由压缩模式和与写入操作相关的任何提示的组合决定的。压缩模式可以是：

* none：从不压缩数据。
* passive：除非写入操作具有可压缩的提示集，否则不要压缩数据。
* aggressive：压缩数据，除非写入操作具有不可压缩的提示集。
* force：尝试压缩数据，无论如何。

有关可压缩和不可压缩 IO 提示的更多信息，请参阅[`rados_set_alloc_hint()`](http://docs.ceph.com/docs/master/rados/api/librados/#c.rados_set_alloc_hint "rados_set_alloc_hint").

请注意，无论模式如何，如果数据块的大小未充分减小，则不会使用它，并且将存储未压缩的原始数据。例如，如果 bluestore compression required ratio 设置为.7，则压缩数据必须是原始大小（或更小）的 70％。

compression mode, compression algorithm, compression required ratio, min blob size, and max blob size 可以通过每个存储池属性或 global config 选项设置。池属性可以设置为：

ceph osd pool set \<pool-name> compression\_algorithm \<algorithm> ceph osd pool set \<pool-name> compression\_mode \<mode> ceph osd pool set \<pool-name> compression\_required\_ratio \<ratio> ceph osd pool set \<pool-name> compression\_min\_blob\_size \<size> ceph osd pool set \<pool-name> compression\_max\_blob\_size \<size>

bluestore compression algorithm
描述：    如果未设置每个存储池的 compression\_algorithm 属性，则使用默认压缩（如果有）。由于在压缩少量数据时 CPU 负担较高，因此不建议对 bluestore 使用 zstd。
类型：    String
是否必须：    No
有效值：    lz4, snappy, zlib, zstd
默认值    snappy

bluestore compression mode
描述：    如果池的 compression\_mode 属性未设置，将使用默认模式
类型：    String
是否必须：    No
有效值：    none, passive, aggressive, force
默认值    none

bluestore compression required ratio
描述：    压缩比率必须达到这个值才进行压缩
类型：    Floating point
是否必须：    No
默认值    .875 bluestore compression min blob size
描述：    比这个还小的 chunk 不进行压缩.池设置 compression\_min\_blob\_size 覆盖这个值.
类型：    Unsigned Integer
是否必须：    No
默认值 0 bluestore compression min blob size hdd
描述：    旋转设备最小 blob 大小
类型：    Unsigned Integer
是否必须：    No
默认值    128K

bluestore compression min blob size ssd
描述：    SSD 最小 blob 大小
类型：    Unsigned Integer
是否必须：    No
默认值    8K

bluestore compression max blob size
描述：    大于此尺寸的 chunk 会被分割成小块再尽心压缩，池属性 compression\_max\_blob\_size 设置覆盖此值
类型：    Unsigned Integer
是否必须：    No
默认值 0 bluestore compression max blob size hdd
描述：    旋转设备最大 blob 尺寸
类型：    Unsigned Integer
是否必须：    No
默认值    512K

bluestore compression max blob size ssd
描述：    SSD 最大 blob 尺寸
类型：    Unsigned Integer
是否必须：    No
默认值    64K

### SPDK 使用

如果要将 NVME SSD 用于 SPDK 驱动程序，则需要准备好系统。 有关详细信息，请参阅[SPDK document](http://www.spdk.io/doc/getting_started.html#getting_started_examples)。

SPDK 提供了一个自动配置设备的脚本。 用户可以以 root 身份运行脚本：

\$ sudo src/spdk/scripts/setup.sh

然后，您需要在此指定 NVMe 设备的设备选择器，并为 bluestore\_block\_path 指定“spdk：”前缀。例如，用户可以找到 Intel PCIe SSD 的设备选择器：

\$ lspci -mm -n -D -d 8086:0953

设备选择器的形式为 DDDD:BB:DD.FF 或 DDDD.BB.DD.FF，然后设置：

bluestore block path = spdk:0000:01:00.0

其中 0000:01:00.0 是上面 lspci 命令输出中找到的设备选择器。

如果要为每个节点运行多个 SPDK 实例，则必须指定每个实例将使用的 dpdk 内存大小（以 MB 为单位），以确保每个实例使用自己的 dpdk 内存

在大多数情况下，我们只需要一个设备用作 data，db，db wal。 我们需要确认以下配置：

bluestore\_block\_db\_path = "" bluestore\_block\_db\_size \= 0 bluestore\_block\_wal\_path \= "" bluestore\_block\_wal\_size \= 0

否则，当前实现将符号文件设置为内核文件系统位置，并使用内核驱动程序发出 DB/WAL IO。

## FileStore 设置

filestore debug omap check
描述:　　  打开对同步检查过程的调试。代价很高，仅用于调试。 
类型:　　  Boolean 
是否必需:  No 
默认值:　　0 

### 扩展属性

扩展属性（ XATTR ）是配置里的重要部分。一些文件系统对 XATTR 字节数有限制，另外在某些情况下文件系统存储 XATTR 的速度不如其他方法。下面的选项让你用独立于文件系统的存储方法，或许能提升性能。

Ceph 扩展属性用底层文件系统的 XATTR （如果没有尺寸限制）存储为 inline xattr 。如果有限制，如 ext4 限制为 4KB ，达到 filestore max inline xattr size 或 filestore max inline xattrs 阀值时一些 XATTR 将存储为键/值数据库（也叫 omap ）。

filestore max inline xattr size
描述：    每个对象存储在文件系统中的 XATTR 的最大大小（即 XFS，btrfs，ext4 等）。不应该大于文件系统可以处理的大小。默认值 0 表示使用特定于底层文件系统的值。
类型：    Unsigned 32\-bit Integer
是否必须：    No
默认值： 0 filestore max inline xattr size xfs
描述：    存储在 XFS 文件系统中的 XATTR 的最大大小。仅在 filestore max inline xattr size \== 0 时使用
类型：    Unsigned 32\-bit Integer
是否必须：    No
默认值： 65536 filestore max inline xattr size btrfs
描述：    存储在 btrfs 文件系统中的 XATTR 的最大大小。仅在 filestore max inline xattr size \== 0 时使用。
类型：    Unsigned 32\-bit Integer
是否必须：    No
默认值： 2048 filestore max inline xattr size other
描述：    存储在其他文件系统中的 XATTR 的最大大小。仅在 filestore max inline xattr size \== 0 时使用。
类型：    Unsigned 32\-bit Integer
是否必须：    No
默认值： 512 filestore max inline xattrs
描述：    每个对象的文件系统中存储的最大 XATTR 数。默认值 0 表示使用特定于底层文件系统的值。
类型： 32\-bit Integer
是否必须：    No
默认值： 0 filestore max inline xattrs xfs
描述：    每个对象存储在 XFS 文件系统中的最大 XATTR 数。仅在 filestore max inline xattrs \== 0 时使用。
类型： 32\-bit Integer
是否必须：    No
默认值： 10 filestore max inline xattrs btrfs
描述：    每个对象存储在 btrfs 文件系统中的最大 XATTR 数。仅在 filestore max inline xattrs \== 0 时使用。
类型： 32\-bit Integer
是否必须：    No
默认值： 10 filestore max inline xattrs other
描述：    每个对象存储在其他文件系统中的最大 XATTR 数。仅在 filestore max inline xattrs \== 0 时使用。
类型： 32\-bit Integer
是否必须：    No
默认值： 2

### 同步间隔

filestore 需要周期性地静默写入、同步文件系统，这创建了一个提交点，然后就能释放相应的日志条目了。较大的同步频率可减小执行同步的时间及保存在日志里的数据量；较小的频率使得后端的文件系统能优化归并较小的数据和元数据写入，因此可能使同步更有效。

filestore max sync interval
描述: 同步 filestore 的最大间隔秒数。 
类型: Double 
是否必需: No 
默认值: 5 filestore min sync interval
描述: 同步 filestore 的最小间隔秒数。 
类型: Double 
是否必需: No 
默认值: .01 

### 回写器

filestore 回写器强制使用 sync file range 来写出大块数据，这样处理有望减小最终同步的代价。实践中，禁用“ filestore 回写器”有时候能提升性能。

filestore flusher
描述:启用 filestore 回写器。 
类型:Boolean 
是否必需:No 
默认值:false Deprecated since version v.65.

filestore flusher max fds
描述:设置回写器的最大文件描述符数量。 
类型:Integer 
是否必需:No 
默认值:512 Deprecated since version v.65.

filestore sync flush
描述:启用同步回写器。 
类型:Boolean 
是否必需:No 
默认值:false Deprecated since version v.65.

filestore fsync flushes journal data
描述:文件系统同步时也回写日志数据。 
类型:Boolean 
是否必需:No 
默认值:false 

### 队列

filestore queue max ops
描述：    文件存储操作接受的最大并发数，超过此设置的请求会被阻塞。
类型：    Integer
是否必须：    No. 对性能影响最小
默认值： 50 filestore queue max bytes
描述：    一次操作的最大字节数
类型：    Integer
是否必须：    No
默认值： 100 \<\< 20

### 超时

filestore op threads
描述：    允许并行操作文件系统的最大线程数 类型：    Integer
是否必须：    No
默认值： 2 filestore op thread timeout
描述：    文件系统操作线程超时 \(秒\).
类型：    Integer
是否必须：    No
默认值： 60 filestore op thread suicide timeout
描述：    commit 操作超时时间（秒），超时将取消提交 类型：    Integer
是否必须：    No
默认值： 180

### B-TREE FILESYSTEM

filestore btrfs snap
描述：    对 btrfs filestore 启用快照功能。
类型：    Boolean
是否必须：    No. Only used for btrfs.
默认值： true filestore btrfs clone range
描述：    允许 btrfs filestore 克隆操作排队。
类型：    Boolean
是否必须：    No. Only used for btrfs.
默认值： true

### 日志

filestore journal parallel
描述：    允许并行记日志，对 btrfs 默认开。
类型：    Boolean
是否必须：    No
默认值： false filestore journal writeahead
描述：    允许预写日志，对 xfs 默认开。
类型：    Boolean
是否必须：    No
默认值： false

### 杂项

filestore merge threshold
描述：    并入父目录前，子目录内的最小文件数。注：负值表示禁用子目录合并功能。
类型：    Integer
是否必须：    No
默认值： \-10 filestore split multiple
描述：    \(filestore\_split\_multiple \* abs\(filestore\_merge\_threshold\) + \(rand\(\) \% filestore\_split\_rand\_factor\)\) \* 16 是分割为子目录前某目录内的最大文件数
类型：    Integer
是否必须：    No
默认值： 2 filestore split rand factor
描述：    添加到拆分阈值的随机因子，以避免一次发生太多文件存储拆分。有关详细信息，请参阅 filestore split multiple。  
这只能在现有的 osd 离线时通过 ceph-objectstore-tool 的 apply-layout-settings 命令更改。
类型：    Unsigned 32\-bit Integer
是否必须：    No
默认值： 20 filestore update to
描述：    限制文件存储自动升级到指定版本。
类型：    Integer
是否必须：    No
默认值： 1000 filestore blackhole
描述：    丢弃任何讨论中的事务。
类型：    Boolean
是否必须：    No
默认值： false filestore dump file 描述：    存储事务转储的文件。
类型：    Boolean
是否必须：    No
默认值： false filestore kill at
描述：    在第 n 次机会后注入失败
类型：    String
是否必须：    No
默认值： false filestore fail eio
描述：    eio 失败/崩溃。
类型：    Boolean
是否必须：    No
默认值： true

## 日志设置

Ceph 的 OSD 使用日志的原因有二：速度和一致性。

* 速度： 日志使得 OSD 可以快速地提交小块数据的写入， Ceph 把小片、随机 IO 依次写入日志，这样，后端文件系统就有可能归并写入动作，并最终提升并发承载力。因此，使用 OSD 日志能展现出优秀的突发写性能，实际上数据还没有写入 OSD ，因为文件系统把它们捕捉到了日志。
* 一致性： Ceph 的 OSD 守护进程需要一个能保证原子操作的文件系统接口。 OSD 把一个操作的描述写入日志，然后把操作应用到文件系统，这使得原子更新一个对象（例如归置组元数据）。每隔一段 filestore max sync interval 和 filestore min sync interval 之间的时间， OSD 停止写入、把日志同步到文件系统，这样允许 OSD 修整日志里的操作并重用空间。若失败， OSD 从上个同步点开始重放日志。

OSD 守护进程支持下面的日志选项：

journal dio
描述：    启用 direct i/o。需要将 journal block align 设置为 true。
类型：    Boolean
是否必须：    Yes when using aio.
默认值： true journal aio
Changed in version 0.61: Cuttlefish
描述：    使用 libaio 异步写日志. Requires journal dio 设为 true.
类型：    Boolean
是否必须：    No.
默认值：    Version 0.61 and later, true. Version 0.60 and earlier, false.

journal block align
描述：    块对齐写. dio and aio 需要.
类型：    Boolean
是否必须：    Yes when using dio and aio.
默认值： true journal max write bytes
描述：    一次写入日志的最大尺寸
类型：    Integer
是否必须：    No
默认值： 10 \<\< 20 journal max write entries
描述：    一次写入日志的最大条目
类型：    Integer
是否必须：    No
默认值： 100 journal queue max ops
描述：    队列里允许的最大操作数
类型：    Integer
是否必须：    No
默认值： 500 journal queue max bytes
描述：    队列一次操作允许的最大尺寸
类型：    Integer
是否必须：    No
默认值： 10 \<\< 20 journal align min size
描述：    当负载大于指定最小值时对齐
类型：    Integer
是否必须：    No
默认值： 64 \<\< 10 journal zero on create
描述：    文件存储在 mkfs 期间用 0 填充整个日志。
类型：    Boolean
是否必须：    No
默认值： false

## Pool，PG 和 CRUSH 设置

当你创建存储池并给它设置归置组数量时如果你没指定，Ceph 就用默认值。我们建议更改某些默认值，特别是存储池的副本数和默认归置组数量，可以在运行 pool 命令的时候设置这些值。你也可以把配置写入 Ceph 配置文件的 \[global\] 段来覆盖默认值。

 
```plain
\[global\]

<<<<<<< HEAD
    # By default, Ceph makes 3 replicas of objects. If you want to make four
=======
    # By default, Ceph makes 3 replicas of objects. If you want to make fourplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplain
>>>>>>> 0eb6d915945e4d84c1a59a646f299c232fef70af
    # copies of an object the default value--a primary copy and three replica
    # copies\--reset the default values as shown in 'osd pool default size'.
    # If you want to allow Ceph to write a lesser number of copies in a degraded
    # state, set 'osd pool default min size' to a number less than the
    # 'osd pool default size' value.

    osd pool default size \= 3  # Write an object 3 times.
    osd pool default min size \= 2 # Allow writing two copies in a degraded state.

    # Ensure you have a realistic number of placement groups. We recommend
    # approximately 100 per OSD. E.g., total number of OSDs multiplied by 100 # divided by the number of replicas \(i.e., osd pool default size\). So for # 10 OSDs and osd pool default size = 4, we'd recommend approximately
    # \(100 \* 10\) / 4 = 250.

    osd pool default pg num \= 250 osd pool default pgp num \= 250
```
 

mon max pool pg num
描述：    每个池的最大放置组数。
类型：    Integer
默认： 65536 mon pg create interval
描述：    在同一个 Ceph OSD 守护进程中创建 PG 间隔秒数。
类型：    Float
默认： 30.0 mon pg stuck threshold
描述：    多长时间无响应的 PG 才认为它卡住了
类型： 32\-bit Integer
默认： 300 mon pg min inactive
描述：    如果 PG 的数量保持非活动状态超过 mon\_pg\_stuck\_threshold 设置，则在群集日志中发出 HEALTH\_ERR。非正数意味着禁用，永远不会进入 ERR。
类型：    Integer
默认： 1 mon pg warn min per osd
描述：    如果每个（in）OSD 的平均 PG 数低于此数，则在群集日志中发出 HEALTH\_WARN。 （非正数会禁用此功能）
类型：    Integer
默认： 30 mon pg warn max per osd
描述：    如果每个（in）OSD 的平均 PG 数高于此数，则在群集日志中发出 HEALTH\_WARN。 （非正数会禁用此功能）
类型：    Integer
默认： 300 mon pg warn min objects
描述：    如果集群中的对象总数低于此数量时不警告
类型：    Integer
默认： 1000 mon pg warn min pool objects
描述：    存储池对象数目低于此数量时不警告
类型：    Integer
默认： 1000 mon pg check down all threshold
描述：    当检查所有 PG 的时候，down OSD 的比例不低于这个比例
类型：    Float
默认： 0.5 mon pg warn max object skew
描述：    如果某个池的平均对象数目大于 mon pg warn max object skew 乘以整个池的平均对象数目，则在集群日志中发出 HEALTH\_WARN。 （非正数会禁用此功能）
类型：    Float
默认： 10 mon delta reset interval
描述：    在我们将 pg delta 重置为 0 之前不活动的秒数。我们跟踪每个池的已用空间的增量，例如，这会让我们更容易理解恢复的进度或缓存的性能层。但是，如果某个池没有报告任何活动，我们只需重置该池的增量历史记录。
类型：    Integer
默认： 10 mon osd max op age
描述：    在我们 get concerned 之前的最大操作时间（使其成为 2 的幂）。如果请求被阻止超过此限制，将发出 HEALTH\_WARN。
类型：    Float
默认： 32.0 osd pg bits
描述：    每个 Ceph OSD 守护进程给 PG 的 bit 数。
类型： 32\-bit Integer
默认： 6 osd pgp bits
描述：    每个 Ceph OSD 守护进程给 PGPs 的 bit 数。 
类型： 32\-bit Integer
默认： 6 osd crush chooseleaf type
描述：    CRUSH 规则中用于 chooseleaf 的存储桶类型。使用序数排名而不是名称。
类型： 32\-bit Integer
默认： 1. 通常是包含一个或多个 Ceph OSD 守护进程的 host

osd crush initial weight
描述：    新添加的 osds 进入 crushmap 的初始权重
类型：    Double
默认：    以 TB 为单位的容量大小为权重

osd pool default crush rule
描述：    创建复制池时使用的默认 CRUSH 规则。
类型： 8\-bit Integer
默认： \-1 表示“选择具有最低数字 ID 的规则并使用该规则”。这是为了在没有规则 0 的情况下使池创建工作。

osd pool erasure code stripe unit
描述：    设置纠删池的对象条带块的默认大小（以字节为单位）。大小为 S 的每个对象将被存储为 N 个条带，每个数据块接收条带单元字节。 每个条带将被单独编码/解码。纠删配置文件中的 stripe\_unit 设置可以覆盖此选项。
类型：    Unsigned 32\-bit Integer
默认： 4096 osd pool default size
描述：    设置池中对象的副本数。默认值同样用于 ceph osd pool set \{pool\-name\} size \{size\}
类型： 32\-bit Integer
默认： 3 osd pool default min size
描述：    设置池中对象的最小写入副本数，以确认对客户端的写入操作。如果不满足最小值，Ceph 将不会确认写入客户端。此设置指示降级模式下运行时最少有多少副本数量。
类型： 32\-bit Integer
默认：    0 表示没有特定的最小值。如果为 0，则最小值为 size \- \(size / 2\).

osd pool default pg num
描述：    池的默认 PG 数
类型： 32\-bit Integer
默认： 8 osd pool default pgp num
描述：    池的放置的默认 pgp 数。 PG 和 PGP 应该相等。
类型： 32\-bit Integer
默认： 8 osd pool default flags
描述：    新池的默认标志。
类型： 32\-bit Integer
默认： 0 osd max pgls
描述：    The maximum number of placement groups to list. A client requesting a large number can tie up the Ceph OSD Daemon.
类型：    Unsigned 64\-bit Integer
默认： 1024 Note:    默认就好

osd min pg log entries
描述：    修剪日志文件时要维护的最小放置组日志数。
类型： 32\-bit Int Unsigned
默认： 1000 osd default data pool replay window
描述：    OSD 等待客户端重放请求的时间（以秒为单位）
类型： 32\-bit Integer
默认： 45 osd max pg per osd hard ratio
描述：    在 OSD 拒绝创建新 PG 之前，群集允许的每个 OSD 的 PG 数量的比率。如果服务的 PG 数超过 osd max pg per osd hard ratio \* mon max pg per osd，OSD 将停止创建新的 PG。
类型：    Float
默认： 2


## 消息设置

### 通用设置

ms tcp nodelay
描述：    在 messenger tcp 会话上禁用 nagle 算法。
类型：    Boolean
是否必须： No
默认： true ms initial backoff
描述：    出错时重连的初始等待时间
类型：    Double
是否必须： No
默认：    .2 ms max backoff
描述：    出错重连时等待的最大时间
类型：    Double
是否必须： No
默认： 15.0 ms nocrc
描述：    禁用网络消息的 crc 校验， CPU 不足时可提升性能
类型：    Boolean
是否必须： No
默认： false ms die on bad msg
描述：    调试选项，无需配置
类型：    Boolean
是否必须： No
默认： false ms dispatch throttle bytes
描述：    Throttles 等待分派的消息的阈值。
类型： 64\-bit Unsigned Integer
是否必须： No
默认： 100 \<\< 20 ms bind ipv6
描述：    如果想让守护进程绑定到 IPv6 地址而非 IPv4 就得启用（如果你指定了守护进程或集群 IP 就不必要了）
类型：    Boolean
是否必须： No
默认： false ms rwthread stack bytes
描述：    堆栈尺寸调试选项，不要配置.
类型： 64\-bit Unsigned Integer
是否必须： No
默认： 1024 \<\< 10 ms tcp read timeout
描述：    控制信使在关闭空闲连接之前等待的时间（以秒为单位）。
类型： 64\-bit Unsigned Integer
是否必须： No
默认： 900 ms inject socket failures
描述：    调试选项，无需配置
类型： 64\-bit Unsigned Integer
是否必须： No
默认： 0

### ASYNC MESSENGER OPTIONS

ms async transport type
描述：    Async Messenger 使用的传输类型。可以是 posix，dpdk 或 rdma。 Posix 使用标准 TCP / IP 网络，是默认设置。其他运输可能是实验性的，支持可能有限。
类型：    String
是否必须： No
默认：    posix

ms async op threads
描述：    每个 Async Messenger 实例使用的初始工作线程数。应该至少等于副本的最大数，但如果您的 CPU 核心数量不足和/或您在单个服务器上托管了大量 OSD，则可以减少它。
类型： 64\-bit Unsigned Integer
是否必须： No
默认： 3 ms async max op threads
描述：    每个 Async Messenger 实例使用的最大工作线程数。当机器具有有限的 CPU 数量时设置为较低的值，而当 CPU 未充分利用时设置为较高的值（即，在 I / O 操作期间，一个或多个 CPU 始终处于 100％负载状态）
类型： 64\-bit Unsigned Integer
是否必须： No
默认： 5 ms async set affinity
描述：    设置为 true 以将 Async Messenger 工作程序绑定到特定 CPU 核心。
类型：    Boolean
是否必须： No
默认： true ms async affinity cores
描述：    当 ms async set affinity 为 true 时，此字符串指定 Async Messenger 工作程序如何绑定到 CPU 核心。  
例如，"0,2"将 workers ＃1 和＃2 分别绑定到 CPU 核心＃0 和＃2。注意：手动设置关联时，请确保不将 workers 分配给作为超线程或类似技术的效果而创建的虚拟 CPU 处理器，因为它们比常规 CPU 核心慢。
类型：    String
是否必须： No
默认：    \(empty\)

ms async send inline
描述：    直接从生成消息的线程发送消息，而不是从 Async Messenger 线程排队和发送。已知此选项会降低具有大量 CPU 内核的系统的性能，因此默认情况下禁用此选项。
类型：    Boolean
是否必须： No
默认： false
 

## 常规设置

fsid
  描述：    文件系统 ID，每集群一个。
  类型：    UUID
  是否必须： No.
  默认：    N/A. 通常由部署工具生成。

admin socket
  描述：    在某个守护进程上执行管理命令的套接字，不管 Ceph 监视器团体是否已建立。
  类型：    String
  是否必须： No
  默认： /var/run/ceph/\$cluster-\$name.asok

pid file 
  描述：    mon、osd、mds 将把它们的 PID 写入此文件，其名为 /var/run/\$cluster/\$type.\$id.pid 。  
  如名为 Ceph 的集群，其 ID 为 a 的 mon 进程将创建 /var/run/ceph/mon.a.pid 。如果是正常停止的，pid file 就会被守护进程删除；如果进程未进入后台运行（即启动时加了 -f 或 -d 选项），它就不会创建 pid file 。
  类型：    String
  是否必须： No
  默认：    No

chdir
  描述：    Ceph 进程一旦启动、运行就进入这个目录，默认推荐 / 类型：    String
  是否必须： No
  默认： / max open files
  描述：    如果设置了， Ceph 存储集群启动时会设置操作系统的 max open fds （即文件描述符最大允许值），这有助于防止耗尽文件描述符。
  类型： 64\-bit Integer
  是否必须： No
  默认： 0 
fatal signal handlers
  描述：    如果设置了，将安装 SEGV 、 ABRT 、 BUS 、 ILL 、 FPE 、 XCPU 、 XFSZ 、 SYS 信号处理器，用于产生有用的日志信息。
  类型：    Boolean
  默认： true
  
## 原文链接
[CEPH 集群操作入门--配置 - 陆小呆 - 博客园](https://www.cnblogs.com/luxiaodai/p/10006036.html#_lab2_1_14)