---
title: CentOS7 安装 nautilus 版 CEPH（使用 ceph-deploy）
date: 2020-03-15 12:37:35
tags:
- CEPH
- 环境搭建
- CentOS7
cover: https://i1.wp.com/ceph.io/wp-content/uploads/2019/03/nautilus.svg_.png
categories:
- 工作日常
subtitle: 人生苦短，不要把时间浪费在重复性工作上。本文主要以 ceph-deploy 为例实践了 ceph 集群的部署流程。
---
## 引言
项目开发中准备基于 ceph-mgr 中的 dashboard 做二次开发，本文主要记录搭建 ceph 环境的过程。
### 环境说明
节点配置中参考官网搭建示例，基于实体机内存状况限制，使用三节点最小节点配置，具体如下：
![ceph 节点组成说明](/images/ceph-1.png)
## 前期准备
1. 配置网络为静态 ip
简略
2. 添加 CEPH 的 yum 源
```plain
vim /etc/yum.repos.d/ceph.repo
```
```plain
[Ceph]
name=Ceph packages for $basearch
baseurl=http://mirrors.aliyun.com/ceph/rpm-nautilus/el7/$basearch
enabled=1
gpgcheck=0
type=rpm-md

[Ceph-noarch]
name=Ceph noarch packages
baseurl=http://mirrors.aliyun.com/ceph/rpm-nautilus/el7/noarch
enabled=1
gpgcheck=0
type=rpm-md

[ceph-source]
name=Ceph source packages
baseurl=http://mirrors.aliyun.com/ceph/rpm-nautilus/el7/SRPMS
enabled=1
gpgcheck=0
type=rpm-md
```
3. 更新 epel.repo
国内使用阿里源加快下载
 ```plain
wget -O /etc/yum.repos.d/epel.repo http://mirrors.aliyun.com/repo/epel-7.repo
# 或者直接写入
[epel]
name=Extra Packages for Enterprise Linux 7 - $basearch
baseurl=http://mirrors.aliyun.com/epel/7/$basearch
failovermethod=priority
enabled=1
gpgcheck=0
gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-EPEL-7

[epel-debuginfo]
name=Extra Packages for Enterprise Linux 7 - $basearch - Debug
baseurl=http://mirrors.aliyun.com/epel/7/$basearch/debug
failovermethod=priority
enabled=0
gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-EPEL-7
gpgcheck=0

[epel-source]
name=Extra Packages for Enterprise Linux 7 - $basearch - Source
baseurl=http://mirrors.aliyun.com/epel/7/SRPMS
failovermethod=priority
enabled=0
gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-EPEL-7
gpgcheck=0
```plain
4. 更新源并安装 ceph-deploy
```plain
sudo yum update
sudo yum install ceph-deploy
```
5. 安装 NTP
```plain
sudo yum install ntp ntpdate ntp-doc
```
6. 安装 SSH 服务
```plain
sudo yum install openssh-server
```
7. 修改 host
```shell
vi /etc/hosts
```
```plain
127.0.0.1   localhost localhost.localdomain localhost4 localhost4.localdomain4
::1         localhost localhost.localdomain localhost6 localhost6.localdomain6
172.18.1.101 admin-node
172.18.1.102 node1
172.18.1.103 node2
```

### 创建 CEPH DEPLOY 用户（以 cephadm 为例）
1. 创建用户
```plain
# 本例中使用 cephadm
sudo useradd -d /home/cephadm -m cephadm 
sudo passwd cephadm
```
2. sudo 赋权
```plain
echo "cephadm ALL = (root) NOPASSWD:ALL" | sudo tee /etc/sudoers.d/cephadm
sudo chmod 0440 /etc/sudoers.d/cephadm
```
3. tty
使用 sudo visudo 定位`Defaults requiretty`配置修改为`Defaults:ceph !requiretty`或者直接注释掉；
---

### 配置节点
1. 修改两个子节点的网络
{%note warning %}
如果使用克隆虚拟机，请注意一定要修改 MAC 地址绑定
[虚拟机克隆以及 IP，MAC 地址的修改_运维_进击的菜鸟-CSDN 博客](https://blog.csdn.net/lp102811/article/details/80204321)
{% endnote %}
注意：以下操作只在 admin-node 节点执行
2. 建立 admin-node 节点到两个子节点的 ssh 互信
```shell
# 生成密钥，
ssh-keygen
# 拷贝
ssh-copy-id cephadm@node1
ssh-copy-id cephadm@node2
```
3. 验证免密登录
```plain
ssh node1 
ssh node2
```

### 防火墙
1. 在 monitor 节点
```plain
sudo firewall-cmd --zone=public --add-service=ceph-mon --permanent
```
2. 在 OSDs 和 MDSs 节点
```plain
sudo firewall-cmd --zone=public --add-service=ceph --permanent
```
3. 配置立即生效
```plain
sudo firewall-cmd --reload
```
4. 设置 SELINUX 为 Permissive
```plain
sudo setenforce 0
```

## 创建集群
在管理节点上创建一个目录，以维护 ceph-deploy 为集群生成的配置文件和密钥。
```plain
mkdir my-cluster
cd my-cluster
```
{% note warning%}
请不要使用 sudo 调用 ceph-deploy；如果你以其他用户身份登录，不要以 root 身份运行它，因为它不会发出远程主机上所需的 sudo 命令。
{% endnote %}
### 清除环境
```plain
ceph-deploy purge node1 node2
ceph-deploy purgedata node1 node2
ceph-deploy forgetkeys
rm ceph.* -rf
```

### 初始化
1. 在`my-cluster`节点执行创建 mon 节点
```plain
ceph-deploy new admin-node
```
输出如下:
```plain
ll
total 12
-rw-r--r--. 1 root root  200 Mar 15 16:33 ceph.conf
-rw-r--r--. 1 root root 3014 Mar 15 16:33 ceph-deploy-ceph.log
-rw-------. 1 root root   73 Mar 15 16:33 ceph.mon.keyring
```
2. 修改集群配置
```shell
vi ceph.conf
```
```plain
[global]
fsid = 52420c57-bf82-4ca9-9184-a38e2fab427e
mon_initial_members = admin-node
mon_host = 172.18.1.101
auth_cluster_required = cephx
auth_service_required = cephx
auth_client_required = cephx
osd pool default size = 2  #增加默认副本数为 2
```

### 安装 ceph
admin-node 节点执行，ceph-deploy 自动去各节点安装 ceph 环境
```plain
ceph-deploy install admin-node node1 node2
```
---
{%note info %}
执行上述报错
```plain
# 太长省略
[admin-node][WARNIN]             yum-config-manager --save --setopt=<repoid>.skip_if_unavailable=true
[admin-node][WARNIN] 
[admin-node][WARNIN] Cannot find a valid baseurl for repo: base/7/x86_64
[admin-node][ERROR ] RuntimeError: command returned non-zero exit status: 1
[ceph_deploy][ERROR ] RuntimeError: Failed to execute command: yum -y install epel-release
```
遇到此错误，先排查网络是否联通（`ping www.baidu.com`），如果不通，则修改网络，否则，添加 DNS 解析配置；
参见：
- [用 yum 安装软件提示 cannot find a valid baseurl for repo:base/7/x86_64 的解决方法 - 简书](https://www.jianshu.com/p/50f0fb206cf7)
- [小白解决 CENTOS7 错误:Cannot find a valid baseurl for repo: base/7/x86_6 - 林诺欧巴 - 博客园](https://www.cnblogs.com/linnuo/p/6257204.html)  
上面的方法提供了两种方案：a):直接修改网卡配置；b):修改 `cat /etc/resolv.conf`
我使用 a 方案时候重启网络`systemctl restart network`发现域名解析配置文件已经被修改了。本人不擅长网络相关，见笑。
{% endnote %}
---
{%note info %}
本人在实践时发现默认安装最新稳定版本 ceph，而假如需要安装指定小版本的 ceph，可以参考[此文](/blog/2020-03-16/ceph-deploy-install-a-specific-minor-version-ceph/)。
{% endnote %}
执行到上面的时候可能会遇到报错，一定要耐心排查保证没有`ERROR`之后再进行下一步！
### 初始化 monitor 节点并收集所有密钥
```shell
$ ceph-deploy mon create-initial
```
此时目录下文件为
```plain
total 44
-rw-------. 1 root root   113 Mar 15 19:36 ceph.bootstrap-mds.keyring
-rw-------. 1 root root   113 Mar 15 19:36 ceph.bootstrap-mgr.keyring
-rw-------. 1 root root   113 Mar 15 19:36 ceph.bootstrap-osd.keyring
-rw-------. 1 root root   113 Mar 15 19:36 ceph.bootstrap-rgw.keyring
-rw-------. 1 root root   151 Mar 15 19:36 ceph.client.admin.keyring
-rw-r--r--. 1 root root   226 Mar 15 18:27 ceph.conf
-rw-r--r--. 1 root root 16137 Mar 15 19:36 ceph-deploy-ceph.log
-rw-------. 1 root root    73 Mar 15 18:26 ceph.mon.keyring
```
### 部署 manager 守护线程
这是 nautilus 版新加进程，此处创建 mgr 主要是为了后续 ceph-dashboard 使用。
```shell
ceph-deploy mgr create admin-node
```
---
{%note danger %}
在创建 mgr 节点的时候遇到显示`HostNotFound`错误，使用`vi /etc/sysconfig/network`修改 hostname 之后保证与上文中`\etc\hosts`配置相同，重新运行即可。

```shell
[ceph_deploy.mgr][DEBUG ] Deploying mgr, cluster ceph hosts node1:node1
ssh: connect to host node1 port 22: Connection timed out
[ceph_deploy.mgr][ERROR ] connecting to host: node1 resulted in errors: HostNotFound node1
[ceph_deploy][ERROR ] GenericError: Failed to create 1 MGRs

```
{% endnote%}
### 查看 ceph 工作状态
```shell
ceph -s
```
```plain
  cluster:
    id:     91c3049f-7500-4840-beaf-e57ab240d1d5
    health: HEALTH_OK
 
  services:
    mon: 1 daemons, quorum admin-node (age 98m)
    mgr: admin-node(active, since 5s)
    osd: 0 osds: 0 up, 0 in
 
  data:
    pools:   0 pools, 0 pgs
    objects: 0 objects, 0 B
    usage:   0 B used, 0 B / 0 B avail
    pgs:     
```
此时，集群已经部署成功，但是还没有存储节点，`革命尚未成功，同志仍需努力`。
### 添加 OSD 节点
1. 获取集群节点可用磁盘列表
```shell
ceph-deploy disk list node1 node2
```
```plain
[ceph_deploy.conf][DEBUG ] found configuration file at: /root/.cephdeploy.conf
[ceph_deploy.cli][INFO  ] Invoked (2.0.1): /usr/bin/ceph-deploy disk list node1 node2
[ceph_deploy.cli][INFO  ] ceph-deploy options:
[ceph_deploy.cli][INFO  ]  username                      : None
[ceph_deploy.cli][INFO  ]  verbose                       : False
[ceph_deploy.cli][INFO  ]  debug                         : False
[ceph_deploy.cli][INFO  ]  overwrite_conf                : False
[ceph_deploy.cli][INFO  ]  subcommand                    : list
[ceph_deploy.cli][INFO  ]  quiet                         : False
[ceph_deploy.cli][INFO  ]  cd_conf                       : <ceph_deploy.conf.cephdeploy.Conf instance at 0x7f8d2e53be60>
[ceph_deploy.cli][INFO  ]  cluster                       : ceph
[ceph_deploy.cli][INFO  ]  host                          : ['node1', 'node2']
[ceph_deploy.cli][INFO  ]  func                          : <function disk at 0x7f8d2e99e320>
[ceph_deploy.cli][INFO  ]  ceph_conf                     : None
[ceph_deploy.cli][INFO  ]  default_release               : False
[node1][DEBUG ] connection detected need for sudo
[node1][DEBUG ] connected to host: node1 
[node1][DEBUG ] detect platform information from remote host
[node1][DEBUG ] detect machine type
[node1][DEBUG ] find the location of an executable
[node1][INFO  ] Running command: sudo fdisk -l
[node1][INFO  ] Disk /dev/sda: 21.5 GB, 21474836480 bytes, 41943040 sectors
[node1][INFO  ] Disk /dev/mapper/centos-root: 18.2 GB, 18249416704 bytes, 35643392 sectors
[node1][INFO  ] Disk /dev/mapper/centos-swap: 2147 MB, 2147483648 bytes, 4194304 sectors
[node2][DEBUG ] connection detected need for sudo
[node2][DEBUG ] connected to host: node2 
[node2][DEBUG ] detect platform information from remote host
[node2][DEBUG ] detect machine type
[node2][DEBUG ] find the location of an executable
[node2][INFO  ] Running command: sudo fdisk -l
[node2][INFO  ] Disk /dev/sda: 21.5 GB, 21474836480 bytes, 41943040 sectors
[node2][INFO  ] Disk /dev/mapper/centos-root: 18.2 GB, 18249416704 bytes, 35643392 sectors
[node2][INFO  ] Disk /dev/mapper/centos-swap: 2147 MB, 2147483648 bytes, 4194304 sectors
```
2. 添加磁盘（可选）
除了系统盘没有可用磁盘！因为我们使用的是虚拟机，可以在 osd 节点直接手动创建一个磁盘，之后查看磁盘如下：
```shell
ceph-deploy disk list node1 node2
```
```plain
[ceph_deploy.conf][DEBUG ] found configuration file at: /root/.cephdeploy.conf
[ceph_deploy.cli][INFO  ] Invoked (2.0.1): /usr/bin/ceph-deploy disk list node1 node2
[ceph_deploy.cli][INFO  ] ceph-deploy options:
[ceph_deploy.cli][INFO  ]  username                      : None
[ceph_deploy.cli][INFO  ]  verbose                       : False
[ceph_deploy.cli][INFO  ]  debug                         : False
[ceph_deploy.cli][INFO  ]  overwrite_conf                : False
[ceph_deploy.cli][INFO  ]  subcommand                    : list
[ceph_deploy.cli][INFO  ]  quiet                         : False
[ceph_deploy.cli][INFO  ]  cd_conf                       : <ceph_deploy.conf.cephdeploy.Conf instance at 0x7fd5f2a89ef0>
[ceph_deploy.cli][INFO  ]  cluster                       : ceph
[ceph_deploy.cli][INFO  ]  host                          : ['node1', 'node2']
[ceph_deploy.cli][INFO  ]  func                          : <function disk at 0x7fd5f2eeb320>
[ceph_deploy.cli][INFO  ]  ceph_conf                     : None
[ceph_deploy.cli][INFO  ]  default_release               : False
[node1][DEBUG ] connection detected need for sudo
[node1][DEBUG ] connected to host: node1 
[node1][DEBUG ] detect platform information from remote host
[node1][DEBUG ] detect machine type
[node1][DEBUG ] find the location of an executable
[node1][INFO  ] Running command: sudo fdisk -l
[node1][INFO  ] Disk /dev/sda: 21.5 GB, 21474836480 bytes, 41943040 sectors
[node1][INFO  ] Disk /dev/sdb: 5368 MB, 5368709120 bytes, 10485760 sectors
[node1][INFO  ] Disk /dev/mapper/centos-root: 18.2 GB, 18249416704 bytes, 35643392 sectors
[node1][INFO  ] Disk /dev/mapper/centos-swap: 2147 MB, 2147483648 bytes, 4194304 sectors
[node2][DEBUG ] connection detected need for sudo
[node2][DEBUG ] connected to host: node2 
[node2][DEBUG ] detect platform information from remote host
[node2][DEBUG ] detect machine type
[node2][DEBUG ] find the location of an executable
[node2][INFO  ] Running command: sudo fdisk -l
[node2][INFO  ] Disk /dev/sda: 21.5 GB, 21474836480 bytes, 41943040 sectors
[node2][INFO  ] Disk /dev/sdb: 8589 MB, 8589934592 bytes, 16777216 sectors
[node2][INFO  ] Disk /dev/mapper/centos-root: 18.2 GB, 18249416704 bytes, 35643392 sectors
[node2][INFO  ] Disk /dev/mapper/centos-swap: 2147 MB, 2147483648 bytes, 4194304 sectors
```
{% note warning%}
进行下面操作时请确保你的磁盘没有被使用且不包含任何个人重要数据。
{% endnote %}
3. 擦除磁盘的分区表和内容
```shell
ceph-deploy disk zap node1 /dev/sdb
```
```plain
[ceph_deploy.conf][DEBUG ] found configuration file at: /root/.cephdeploy.conf
[ceph_deploy.cli][INFO  ] Invoked (2.0.1): /usr/bin/ceph-deploy disk zap node1 /dev/sdb
[ceph_deploy.cli][INFO  ] ceph-deploy options:
[ceph_deploy.cli][INFO  ]  username                      : None
[ceph_deploy.cli][INFO  ]  verbose                       : False
[ceph_deploy.cli][INFO  ]  debug                         : False
[ceph_deploy.cli][INFO  ]  overwrite_conf                : False
[ceph_deploy.cli][INFO  ]  subcommand                    : zap
[ceph_deploy.cli][INFO  ]  quiet                         : False
[ceph_deploy.cli][INFO  ]  cd_conf                       : <ceph_deploy.conf.cephdeploy.Conf instance at 0x7f509bdcbef0>
[ceph_deploy.cli][INFO  ]  cluster                       : ceph
[ceph_deploy.cli][INFO  ]  host                          : node1
[ceph_deploy.cli][INFO  ]  func                          : <function disk at 0x7f509c22d320>
[ceph_deploy.cli][INFO  ]  ceph_conf                     : None
[ceph_deploy.cli][INFO  ]  default_release               : False
[ceph_deploy.cli][INFO  ]  disk                          : ['/dev/sdb']
[ceph_deploy.osd][DEBUG ] zapping /dev/sdb on node1
[node1][DEBUG ] connection detected need for sudo
[node1][DEBUG ] connected to host: node1 
[node1][DEBUG ] detect platform information from remote host
[node1][DEBUG ] detect machine type
[node1][DEBUG ] find the location of an executable
[ceph_deploy.osd][INFO  ] Distro info: CentOS Linux 7.6.1810 Core
[node1][DEBUG ] zeroing last few blocks of device
[node1][DEBUG ] find the location of an executable
[node1][INFO  ] Running command: sudo /usr/sbin/ceph-volume lvm zap /dev/sdb
[node1][WARNIN] --> Zapping: /dev/sdb
[node1][WARNIN] --> --destroy was not specified, but zapping a whole device will remove the partition table
[node1][WARNIN] Running command: /bin/dd if=/dev/zero of=/dev/sdb bs=1M count=10
[node1][WARNIN] --> Zapping successful for: <Raw Device: /dev/sdb>
```
4. 将磁盘作为 OSD 使用
```shell
ceph-deploy --overwrite-conf osd create --data /dev/sdb node1
```
{% note info%}
上面的`--overwrite-conf`是因为遇到报错：
```shell
[ceph_deploy.osd][ERROR ] RuntimeError: config file /etc/ceph/ceph.conf exists with different content; use --overwrite-conf to overwrite
[ceph_deploy][ERROR ] GenericError: Failed to create 1 OSDs
```
所以覆写配置，正常操作的时候不需要添加该选项。
{% endnote %}

    其中`create`是`prepare`和`active`的合并操作，下面是该命令的解释：
    
    > `ceph-deploy osd prepare HOST:DISK[:JOURNAL] [HOST:DISK[:JOURNAL]……]`
    为 osd 准备一个目录/磁盘。它会检查是否超过 MAX PIDs,读取 bootstrap-osd 的 key 或者写一个（如果没有找到的话），然后它会使用 ceph-disk 的 prepare 命令来准备磁盘、日志，并且把 OSD 部署到指定的主机上。
    >
    > `ceph-deploy osd active HOST:DISK[:JOURNAL] [HOST:DISK[:JOURNAL]……]`
    激活上一步的 OSD。实际上它会调用 ceph-disk 的 active 命令，这个时候 OSD 会 up and in。
    >
    > `ceph-deploy osd create HOST:DISK[:JOURNAL] [HOST:DISK[:JOURNAL]……]`
    上两个命令的综合。
    
    返回结果如下：
    ```plain
    [ceph_deploy.conf][DEBUG ] found configuration file at: /root/.cephdeploy.conf
    [ceph_deploy.cli][INFO  ] Invoked (2.0.1): /usr/bin/ceph-deploy --overwrite-conf osd create --data /dev/sdb node1
    [ceph_deploy.cli][INFO  ] ceph-deploy options:
    [ceph_deploy.cli][INFO  ]  verbose                       : False
    [ceph_deploy.cli][INFO  ]  bluestore                     : None
    [ceph_deploy.cli][INFO  ]  cd_conf                       : <ceph_deploy.conf.cephdeploy.Conf instance at 0x7fa5b902af80>
    [ceph_deploy.cli][INFO  ]  cluster                       : ceph
    [ceph_deploy.cli][INFO  ]  fs_type                       : xfs
    [ceph_deploy.cli][INFO  ]  block_wal                     : None
    [ceph_deploy.cli][INFO  ]  default_release               : False
    [ceph_deploy.cli][INFO  ]  username                      : None
    [ceph_deploy.cli][INFO  ]  journal                       : None
    [ceph_deploy.cli][INFO  ]  subcommand                    : create
    [ceph_deploy.cli][INFO  ]  host                          : node1
    [ceph_deploy.cli][INFO  ]  filestore                     : None
    [ceph_deploy.cli][INFO  ]  func                          : <function osd at 0x7fa5b94882a8>
    [ceph_deploy.cli][INFO  ]  ceph_conf                     : None
    [ceph_deploy.cli][INFO  ]  zap_disk                      : False
    [ceph_deploy.cli][INFO  ]  data                          : /dev/sdb
    [ceph_deploy.cli][INFO  ]  block_db                      : None
    [ceph_deploy.cli][INFO  ]  dmcrypt                       : False
    [ceph_deploy.cli][INFO  ]  overwrite_conf                : True
    [ceph_deploy.cli][INFO  ]  dmcrypt_key_dir               : /etc/ceph/dmcrypt-keys
    [ceph_deploy.cli][INFO  ]  quiet                         : False
    [ceph_deploy.cli][INFO  ]  debug                         : False
    [ceph_deploy.osd][DEBUG ] Creating OSD on cluster ceph with data device /dev/sdb
    [node1][DEBUG ] connection detected need for sudo
    [node1][DEBUG ] connected to host: node1
    [node1][DEBUG ] detect platform information from remote host
    [node1][DEBUG ] detect machine type
    [node1][DEBUG ] find the location of an executable
    [ceph_deploy.osd][INFO  ] Distro info: CentOS Linux 7.6.1810 Core
    [ceph_deploy.osd][DEBUG ] Deploying osd to node1
    [node1][DEBUG ] write cluster configuration to /etc/ceph/{cluster}.conf
    [node1][DEBUG ] find the location of an executable
    [node1][INFO  ] Running command: sudo /usr/sbin/ceph-volume --cluster ceph lvm create --bluestore --data /dev/sdb
    [node1][WARNIN] Running command: /bin/ceph-authtool --gen-print-key
    [node1][WARNIN] Running command: /bin/ceph --cluster ceph --name client.bootstrap-osd --keyring /var/lib/ceph/bootstrap-osd/ceph.keyring -i - osd new 0e40ac48-72bf-42b7-b1d0-8c7d4ed3a1d5
    [node1][WARNIN] Running command: /usr/sbin/vgcreate -s 1G --force --yes ceph-54716551-34cf-47e3-8f6f-81cce6973a81 /dev/sdb
    [node1][WARNIN]  stdout: Physical volume "/dev/sdb" successfully created.
    [node1][WARNIN]  stdout: Volume group "ceph-54716551-34cf-47e3-8f6f-81cce6973a81" successfully created
    [node1][WARNIN] Running command: /usr/sbin/lvcreate --yes -l 100%FREE -n osd-block-0e40ac48-72bf-42b7-b1d0-8c7d4ed3a1d5 ceph-54716551-34cf-47e3-8f6f-81cce6973a81
    [node1][WARNIN]  stdout: Logical volume "osd-block-0e40ac48-72bf-42b7-b1d0-8c7d4ed3a1d5" created.
    [node1][WARNIN] Running command: /bin/ceph-authtool --gen-print-key
    [node1][WARNIN] Running command: /bin/mount -t tmpfs tmpfs /var/lib/ceph/osd/ceph-0
    [node1][WARNIN] Running command: /usr/sbin/restorecon /var/lib/ceph/osd/ceph-0
    [node1][WARNIN] Running command: /bin/chown -h ceph:ceph /dev/ceph-54716551-34cf-47e3-8f6f-81cce6973a81/osd-block-0e40ac48-72bf-42b7-b1d0-8c7d4ed3a1d5
    [node1][WARNIN] Running command: /bin/chown -R ceph:ceph /dev/dm-2
    [node1][WARNIN] Running command: /bin/ln -s /dev/ceph-54716551-34cf-47e3-8f6f-81cce6973a81/osd-block-0e40ac48-72bf-42b7-b1d0-8c7d4ed3a1d5 /var/lib/ceph/osd/ceph-0/block
    [node1][WARNIN] Running command: /bin/ceph --cluster ceph --name client.bootstrap-osd --keyring /var/lib/ceph/bootstrap-osd/ceph.keyring mon getmap -o /var/lib/ceph/osd/ceph-0/activate.monmap
    [node1][WARNIN]  stderr: 2020-03-18 21:22:24.155 7f50487fa700 -1 auth: unable to find a keyring on /etc/ceph/ceph.client.bootstrap-osd.keyring,/etc/ceph/ceph.keyring,/etc/ceph/keyring,/etc/ceph/keyring.bin,: (2) No such file or directory
    [node1][WARNIN] 2020-03-18 21:22:24.155 7f50487fa700 -1 AuthRegistry(0x7f5040064e08) no keyring found at /etc/ceph/ceph.client.bootstrap-osd.keyring,/etc/ceph/ceph.keyring,/etc/ceph/keyring,/etc/ceph/keyring.bin,, disabling cephx
    [node1][WARNIN]  stderr: got monmap epoch 1
    [node1][WARNIN] Running command: /bin/ceph-authtool /var/lib/ceph/osd/ceph-0/keyring --create-keyring --name osd.0 --add-key AQCMIHJeddtiNhAAqZHUd554bkav2bT85my+3A==
    [node1][WARNIN]  stdout: creating /var/lib/ceph/osd/ceph-0/keyring
    [node1][WARNIN] added entity osd.0 auth(key=AQCMIHJeddtiNhAAqZHUd554bkav2bT85my+3A==)
    [node1][WARNIN] Running command: /bin/chown -R ceph:ceph /var/lib/ceph/osd/ceph-0/keyring
    [node1][WARNIN] Running command: /bin/chown -R ceph:ceph /var/lib/ceph/osd/ceph-0/
    [node1][WARNIN] Running command: /bin/ceph-osd --cluster ceph --osd-objectstore bluestore --mkfs -i 0 --monmap /var/lib/ceph/osd/ceph-0/activate.monmap --keyfile - --osd-data /var/lib/ceph/osd/ceph-0/ --osd-uuid 0e40ac48-72bf-42b7-b1d0-8c7d4ed3a1d5 --setuser ceph --setgroup ceph
    [node1][WARNIN] --> ceph-volume lvm prepare successful for: /dev/sdb
    [node1][WARNIN] Running command: /bin/chown -R ceph:ceph /var/lib/ceph/osd/ceph-0
    [node1][WARNIN] Running command: /bin/ceph-bluestore-tool --cluster=ceph prime-osd-dir --dev /dev/ceph-54716551-34cf-47e3-8f6f-81cce6973a81/osd-block-0e40ac48-72bf-42b7-b1d0-8c7d4ed3a1d5 --path /var/lib/ceph/osd/ceph-0 --no-mon-config
    [node1][WARNIN] Running command: /bin/ln -snf /dev/ceph-54716551-34cf-47e3-8f6f-81cce6973a81/osd-block-0e40ac48-72bf-42b7-b1d0-8c7d4ed3a1d5 /var/lib/ceph/osd/ceph-0/block
    [node1][WARNIN] Running command: /bin/chown -h ceph:ceph /var/lib/ceph/osd/ceph-0/block
    [node1][WARNIN] Running command: /bin/chown -R ceph:ceph /dev/dm-2
    [node1][WARNIN] Running command: /bin/chown -R ceph:ceph /var/lib/ceph/osd/ceph-0
    [node1][WARNIN] Running command: /bin/systemctl enable ceph-volume@lvm-0-0e40ac48-72bf-42b7-b1d0-8c7d4ed3a1d5
    [node1][WARNIN]  stderr: Created symlink from /etc/systemd/system/multi-user.target.wants/ceph-volume@lvm-0-0e40ac48-72bf-42b7-b1d0-8c7d4ed3a1d5.service to /usr/lib/systemd/system/ceph-volume@.service.
    [node1][WARNIN] Running command: /bin/systemctl enable --runtime ceph-osd@0
    [node1][WARNIN]  stderr: Created symlink from /run/systemd/system/ceph-osd.target.wants/ceph-osd@0.service to /usr/lib/systemd/system/ceph-osd@.service.
    [node1][WARNIN] Running command: /bin/systemctl start ceph-osd@0
    [node1][WARNIN] --> ceph-volume lvm activate successful for osd ID: 0
    [node1][WARNIN] --> ceph-volume lvm create successful for: /dev/sdb
    [node1][INFO  ] checking OSD status...
    [node1][DEBUG ] find the location of an executable
    [node1][INFO  ] Running command: sudo /bin/ceph --cluster=ceph osd stat --format=json
    [ceph_deploy.osd][DEBUG ] Host node1 is now ready for osd use.
    ```
    阅读最后一行信息，我们知道 node1 作为 osd 节点被添加进去了。
5. 查看集群状态
```shell
ceph -s
```
返回结果如下：
```plain
cluster:
id:     e32088fc-a761-4aab-b221-fb56d42371dc
health: HEALTH_WARN         # 提示 osd 节点少于预设
        2 daemons have recently crashed
        OSD count 1 < osd_pool_default_size 2

services:
mon: 1 daemons, quorum admin-node (age 3h)
mgr: admin-node(active, since 26m)
osd: 1 osds: 1 up (since 7m), 1 in (since 7m)

data:
pools:   0 pools, 0 pgs
objects: 0 objects, 0 B
usage:   1.0 GiB used, 3.0 GiB / 4 GiB avail
pgs:
```
至此，单个的 OSD 节点添加成功。
但是因为我们在[3.2 节](#%E5%88%9D%E5%A7%8B%E5%8C%96)的配置中添加了`osd pool default size = 2`配置，所以会显示 warning 信息。我们可以重复上面步骤添加 node2 为另一个 OSD 节点之后再次查看集群健康状态：
```shell
ceph health
```
```plain
HEALTH_OK
```
至此，ceph 环境搭建完毕！

## 参考资料
- [Preflight Checklist — Ceph Documentation](https://docs.ceph.com/docs/nautilus/start/quick-start-preflight/)
- [Storage Cluster Quick Start — Ceph Documentation](https://docs.ceph.com/docs/nautilus/start/quick-ceph-deploy/)
- [Quick Guide to Install and Configure Ceph Cluster on CentOS 7](https://www.linuxtechi.com/install-configure-ceph-cluster-centos-7/)
- [单机版 Ceph 环境部署，Linux 平台 - 知乎](https://zhuanlan.zhihu.com/p/67832892)
- [初试 Centos7 上 Ceph 存储集群搭建_运维_哎_小羊的博客-CSDN 博客](https://blog.csdn.net/aixiaoyang168/article/details/78788703)
- [ceph-deploy – Ceph deployment tool — Ceph Documentation](https://docs.ceph.com/docs/nautilus/man/8/ceph-deploy/)
- [ceph-deploy 命令详解_运维_ns2250225-CSDN 博客](https://blog.csdn.net/ns2250225/article/details/69978355)
- [全网最详细的 Ceph14.2.5 集群部署及配置文件详解，快来看看吧-博客园](https://www.cnblogs.com/passzhang/p/12151835.html)
- [Ceph 文件系统-全网最炫酷的 Ceph Dashboard 页面和 Ceph 监控-博客园](https://www.cnblogs.com/passzhang/p/12179816.html)