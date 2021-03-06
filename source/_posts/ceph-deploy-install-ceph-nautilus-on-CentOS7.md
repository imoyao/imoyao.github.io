---
title: CentOS7 部署 nautilus 版 CEPH（使用 ceph-deploy）
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
此步请自行完成；
    此步配置之后需要保证：
    1. 开机网络自启；
    2. 各节点之间的网络连通性（`ping {hostname}`）
2. 添加 CEPH 的 yum 源
国内使用阿里源加快下载
```bash
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
添加 EPEL 的阿里镜像源
```bash
wget -O /etc/yum.repos.d/epel.repo http://mirrors.aliyun.com/repo/epel-7.repo
```

或者手动编辑

```bash
vim /etc/yum.repos.d/epel-7.repo
```
直接写入
```plain
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
```
4. 更新源并安装 ceph-deploy
```bash
sudo yum update
sudo yum install ceph-deploy -y
```
5. 安装 NTP
```bash
sudo yum install ntp ntpdate ntp-doc -y
```
配置 ntp 服务（此步省略）
6. 安装 SSH 服务
```bash
sudo yum install openssh-server -y
```
7. 修改 host
```bash
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

{%note warning %}
**注意**
- 各节点都要创建该用户；
- 不要使用 ceph 作为部署用户的用户名；
- 用户必须赋权 root 用户；
{%endnote %}

1. 创建用户
```plain
# 本例中使用 cephadm
sudo useradd -d /home/cephadm -m cephadm 
sudo passwd cephadm
```
2. sudo 赋权
```plain
echo "cephadm ALL = (root) NOPASSWD:ALL"  > /etc/sudoers.d/cephadm
sudo chmod 0440 /etc/sudoers.d/cephadm
```

更多信息参阅官方文档 [Preflight Checklist — Ceph Documentation](https://ceph.readthedocs.io/en/latest/install/ceph-deploy/quick-start-preflight/#create-a-ceph-deploy-user)

---

### 配置节点
 修改两个子节点的网络
{%note warning %}
如果使用克隆虚拟机，请注意一定要修改 MAC 地址绑定
[虚拟机克隆以及 IP，MAC 地址的修改_运维_进击的菜鸟-CSDN 博客](https://blog.csdn.net/lp102811/article/details/80204321)
{% endnote %}
注意：以下操作只在 admin-node 节点执行即可；
1. 切换到 cephadm 用户
```bash
su cephadm
```
2. 建立 admin-node 节点到两个子节点的 ssh 互信
```shell
# 生成密钥（一路回车）
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
注意：免密登录比较重要，如果是测试环境，可以直接使用 root 用户的话，上面指令改为`ssh-copy-id root@node1`去建立互信关系。
4. 此步为建议步骤
编辑`~/.ssh/config`，防止每次使用 cephadm 用户执行操作时手动输入，如果你有安全方面的顾虑，也可以执行时再输入。
```plain
Host node1
   Hostname node1
   User cephadm
Host node2
   Hostname node2
   User cephadm
Host node3
   Hostname node3
   User cephadm
```
其中 Host 后面跟你的部署的节点的 hostname，User 后面跟刚才新建的用户名（本例中即 cephadm）

### 防火墙端口

你可以选择直接关闭防火墙，也可以选择开放防火墙端口。以下以开放防火墙端口为例：

1. 在 monitor 节点
```bash
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

### TTY
使用`sudo visudo`打开`sudoers`文件（注意不要用编辑器打开而是使用专用命令），定位到`Defaults requiretty`设置，修改为 `Defaults:ceph !requiretty`

### 设置 SELINUX 为 Permissive
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
### 注意
1. 以后执行 ceph-deploy 的指令都应该在该目录下进行；
2. 请不要使用 sudo 调用 ceph-deploy；如果你以其他用户身份进行部署操作，不要以 root 身份运行它，因为它不会发出远程主机上所需的 sudo 命令。
{% endnote %}

### 清除环境
```plain
ceph-deploy purge node1 node2
ceph-deploy purgedata node1 node2
ceph-deploy forgetkeys
rm ceph.* -rf
```
{%note warning%}
#### 报错
```plain
Bad owner or permissions on /home/cephadm/.ssh/config
[ceph_deploy][ERROR ] RuntimeError: connecting to host: cnode1 resulted in errors: HostNotFound cnode1
```
#### 解决
确认节点开机？确认是以 cephadm 用户登录？之后执行：
```bash
chmod 600 /home/cephadm/.ssh/config
```
然后重复执行上一步。
{%endnote%}
此步骤会清除节点之间的 ceph 环境，相当于初始化一个全新的安装环境。

### 初始化
1. 在`my-cluster`管理节点执行创建部署节点
指定的节点名称为 hostname, fqdn 或者 hostname:fqdn，如果不了解 FQDN 的含义可以参考：
[关于 hostname 和 fqdn 的区别和获取及设置 - 邹天得 - 博客园](https://www.cnblogs.com/videring/articles/7025867.html)
本例中管理节点`hostname`为 admin-node，此处应该为你执行 ceph-deploy 操作的节点 hostname。
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
{%note warning%}
遇到报错
```plain
Traceback (most recent call last):
  File "/usr/bin/ceph-deploy", line 18, in <module>
    from ceph_deploy.cli import main
  File "/usr/lib/python2.7/site-packages/ceph_deploy/cli.py", line 1, in <module>
    import pkg_resources
ImportError: No module named pkg_resources
```
安装`distribute`。如果国内源太慢，可以参考此文[Python 换源操作 | 别院牧志](https://www.masantu.com/wiki/%E6%8D%A2%E6%BA%90/pip/)
```bash
# 如果没有安装pip，先安装pip
yum install python-pip 
pip install distribute
```
或者参考此处：[python - No module named pkg_resources - Stack Overflow](https://stackoverflow.com/questions/7446187/no-module-named-pkg-resources)
{%endnote%}
2. 修改集群配置
```shell
vi ceph.conf
```
如果有多个网络接口，需要在 Ceph 配置文件的`[global]`一节下添加`public network`设置，这也是官网建议我们的配置。具体参见[Network Configuration Reference — Ceph Documentation](https://docs.ceph.com/docs/nautilus/rados/configuration/network-config-ref/)
```plain
[global]
fsid = 52420c57-bf82-4ca9-9184-a38e2fab427e
mon_initial_members = admin-node
mon_host = 172.18.1.101
auth_cluster_required = cephx
auth_service_required = cephx
auth_client_required = cephx
osd pool default size = 2  #增加默认副本数为 2
public network = 172.18.1.0/24 # 添加整个子网段
```
如果使用 ipv6 网络，则追加如下内容
```bash
echo ms bind ipv6 = true >> ceph.conf
```

### 安装 ceph
admin-node 节点执行，ceph-deploy 自动去各节点安装 ceph 环境
```plain
ceph-deploy install admin-node node1 node2
```
---

#### 报错处理

{%note danger %}
1. 网络不通
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
我使用 a 方案时候重启网络`systemctl restart network`发现域名解析配置文件已经被修改了。鄙人不擅长网络。
此外，如果使用非 root 用户部署，一定要保证部署用户（本例中的 cephadm）可以正常 sudo！
2. 重新配置 epel.repo
进入`/etc/yum.repos.d`中删除`epel.repo`和`epel-testing.repo`重新安装
{% endnote %}
---
{%note info %}
本人在实践时发现默认安装最新稳定版本 ceph，而假如需要安装指定小版本的 ceph，可以参考[此文](/blog/2020-03-16/ceph-deploy-install-a-specific-minor-version-ceph/)。
{% endnote %}
执行到上面的时候可能会遇到报错，一定要耐心排查保证没有`ERROR`之后再进行下一步！

### 初始化 monitor 节点并收集所有密钥
```shell
ceph-deploy mon create-initial
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
在创建 mgr 节点的时候遇到显示`HostNotFound`错误，使用`vi /etc/sysconfig/network`修改 hostname 之后保证与上文中`/etc/hosts`配置相同，重新运行即可。

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
{%note warning%}
今天重新部署遇到报错：
```plain
ceph -s
[errno 2] error connecting to the cluster
```
现象描述：不加 sudo 执行下面的指令显示受限，加 sudo 之后可以获取到 ceph 的状态，很奇怪，暂时没有找到解决办法。
```bash
sudo ceph --connect-timeout=25 --cluster=ceph --admin-daemon=/var/run/ceph/ceph-mon.cnode0.asok mon_status
```
{%endnote %}
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
所以需要覆写配置，正常操作的时候不需要添加该选项。
注意`--overwrite-conf`指令必须紧跟在后面，而不能写在配置文件后面！
{% endnote %}

> 其中`create`是`prepare`和`active`的合并操作，下面是该命令的解释：
> `ceph-deploy osd prepare HOST:DISK[:JOURNAL] [HOST:DISK[:JOURNAL]……]`
> 为 osd 准备一个目录/磁盘。它会检查是否超过 MAX PIDs,读取 bootstrap-osd 的 key 或者写一个（如果没有找到的话），然后它会使用 ceph-disk 的 prepare 命令来准备磁盘、日志，并且把 OSD 部署到指定的主机上。
> `ceph-deploy osd active HOST:DISK[:JOURNAL] [HOST:DISK[:JOURNAL]……]`
> 激活上一步的 OSD。实际上它会调用 ceph-disk 的 active 命令，这个时候 OSD 会 up and in。
> `ceph-deploy osd create HOST:DISK[:JOURNAL] [HOST:DISK[:JOURNAL]……]`
> 上面两个命令的综合。

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
{% note info %}
**注意：**
如果 zap 磁盘失败，确认磁盘是否之前已经做过 LUN，如果是，需要删除 LV，VG，PV，之后再进行添加 osd 的操作。
{% endnote %}
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

----

## 启用 dashboard

1. 在所有的 mgr 节点安装 dashbaord
```bash
yum install ceph-mgr-dashboard -y
```
2. 重启 mgr 功能
```bash
ceph mgr module disable dashboard
ceph mgr module enable dashboard
```
3. 生成并安装自签名的证书
```bash
ceph dashboard create-self-signed-cert
```

4. 创建一个 dashboard 登录用户名密码
```bash
ceph dashboard ac-user-create admin admin administrator 
```
5. 查看服务访问方式
```bash
ceph mgr services
```
返回结果
```plain
{
    "dashboard": "https://cnode0:8443/"
}
```
6. 打开防火墙指定端口（8443）
```plain
firewall-cmd --zone=public --add-port=8443/tcp --permanent >/dev/null 2>&1
firewall-cmd --reload >/dev/null 2>&1
```
7. 访问浏览器
![dashboard](/images/ceph-dashboard.png)

## 开启 Object Gateway 管理功能

```plain
1、创建rgw用户
# radosgw-admin user info --uid=user01
2、提供Dashboard证书
# ceph dashboard set-rgw-api-access-key $access_key
# ceph dashboard set-rgw-api-secret-key $secret_key
3、配置rgw主机名和端口
# ceph dashboard set-rgw-api-host 192.168.25.224
4、刷新web页面
```

以下内容是从别人博客复制的，没有验证。

---

## 安装 grafana
1. 配置 yum 源文件
建议使用清华源：[grafana | 镜像站使用帮助 | 清华大学开源软件镜像站 | Tsinghua Open Source Mirror](https://mirror.tuna.tsinghua.edu.cn/help/grafana/)
```bash
vim /etc/yum.repos.d/grafana.repo
```
```plain
[grafana]
name=grafana
baseurl=https://mirrors.tuna.tsinghua.edu.cn/grafana/yum/rpm
repo_gpgcheck=0
enabled=1
gpgcheck=0
```
2. 通过 yum 命令安装 grafana
```bash
yum -y install grafana
```
3.启动 grafana 并设为开机自启
```bash
systemctl start grafana-server.service 
systemctl enable grafana-server.service
```

## 安装 promethus
1. 下载安装包，
下载地址：`https://prometheus.io/download/`
2. 解压压缩包
```bash
tar fvxz prometheus-2.14.0.linux-amd64.tar.gz
```
3. 将解压后的目录改名
```bash
mv prometheus-2.14.0.linux-amd64 /opt/prometheus
```
4. 查看 promethus 版本
```bash
./prometheus --version
```
```plain
prometheus, version 2.14.0 (branch: HEAD, revision: edeb7a44cbf745f1d8be4ea6f215e79e651bfe19)
  build user:       root@df2327081015
  build date:       20191111-14:27:12
  go version:       go1.13.4

```
5. 配置系统服务启动
```bash
vim /etc/systemd/system/prometheus.service
```
```plain
[Unit]
Description=Prometheus Monitoring System
Documentation=Prometheus Monitoring System

[Service]
ExecStart=/opt/prometheus/prometheus \
  --config.file /opt/prometheus/prometheus.yml \
  --web.listen-address=:9090

[Install]
WantedBy=multi-user.target
```
6、加载系统服务
```bash
systemctl daemon-reload
```
7、启动服务和添加开机自启动
```bash
systemctl start prometheus
systemctl enable prometheus
```

## ceph mgr prometheus 插件配置

```bash
ceph mgr module enable prometheus
netstat -nltp | grep mgr 检查端口
curl 127.0.0.1:9283/metrics  测试返回值
```

## 配置 promethus

1、在 scrape\_configs: 配置项下添加

```plain
vim prometheus.yml
- job_name: 'ceph_cluster'
    honor_labels: true
    scrape_interval: 5s
    static_configs:
      - targets: ['192.168.25.224:9283']
        labels:
          instance: ceph
          
```

2、重启 promethus 服务

```plain
systemctl restart prometheus
```

3、检查 prometheus 服务器中是否添加成功

```plain
# 浏览器-》 http://x.x.x.x:9090 -》status -》Targets
```

## 配置 grafana

1. 浏览器登录 grafana 管理界面  
2. 添加 data sources，点击 configuration--》data sources  
3. 添加 dashboard，点击 HOME--》find dashboard on grafana.com  
4. 搜索 ceph 的 dashboard  
5. 点击 HOME--》Import dashboard, 选择合适的 dashboard，记录编号

## 参考资料
- [Preflight Checklist — Ceph Documentation](https://docs.ceph.com/en/nautilus/start/quick-start-preflight/)
- [Storage Cluster Quick Start — Ceph Documentation](https://docs.ceph.com/en/nautilus/start/quick-ceph-deploy/)
- [Quick Guide to Install and Configure Ceph Cluster on CentOS 7](https://www.linuxtechi.com/install-configure-ceph-cluster-centos-7/)
- [单机版 Ceph 环境部署，Linux 平台 - 知乎](https://zhuanlan.zhihu.com/p/67832892)
- [初试 Centos7 上 Ceph 存储集群搭建_运维_哎_小羊的博客-CSDN 博客](https://blog.csdn.net/aixiaoyang168/article/details/78788703)
- [ceph-deploy – Ceph deployment tool — Ceph Documentation](https://docs.ceph.com/en/latest/man/8/ceph-deploy/)
- [ceph-deploy 命令详解_运维_ns2250225-CSDN 博客](https://blog.csdn.net/ns2250225/article/details/69978355)
- [全网最详细的 Ceph14.2.5 集群部署及配置文件详解，快来看看吧-博客园](https://www.cnblogs.com/passzhang/p/12151835.html)
- [Ceph 文件系统-全网最炫酷的 Ceph Dashboard 页面和 Ceph 监控-博客园](https://www.cnblogs.com/passzhang/p/12179816.html)