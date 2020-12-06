---
title: CentOS7 安装 Octopus 版 CEPH（使用 cephadm）
date: 2020-03-22 16:38:42
tags:
- CEPH
- 环境搭建
- CentOS7
top: 2
reward: true
cover: /images/logos/ceph-logo.svg
categories:
- 工作日常
subtitle: 正所谓“江上代有才人出，各领风骚数百年。”，从 Octopus 版开始 ceph-deploy 不再被作为官方推荐的部署 ceph 集群的工具（Nautilus 版仍然支持），取而代之的是新秀 cephadm。使用开源产品最重要的是跟上社区节奏，本文以官方文档为基础实践了 ceph 集群的部署流程。
---
## 版本信息
- 系统信息
    ```plain
    [root@cepho ~]# uname -r
    3.10.0-957.el7.x86_64
    [root@cepho ~]# cat /etc/system-release
    CentOS Linux release 7.6.1810 (Core) 
    ```
- Python3 版本
    ```plain
    [root@cepho ~]# python3 -V
    Python 3.8.2
    ```
    生产环境中我们没有必要追求最新，安装 3.6 版本即可。当然如果你追求最新，那么就用最新的也好。
- Docker 信息
    ```plain
    [root@cepho ~]# docker --version
    Docker version 19.03.8, build afacb8b
    ```
- CEPH 版本
 ```shell
 ceph --version
 ceph version 15.1.1 (4536217610b4c55c08a293e67f5ae1f1129190be) octopus (rc)
 ```
因为系统安装的是普通版本而不是最小安装，所以 ntp、lvm 管理工具等默认已经安装。

## 介绍
Cephadm 通过 SSH 从管理守护程序连接到主机来部署和管理 Ceph 群集，以添加、删除或更新 Ceph 守护程序的容器。它不依赖于外部配置或编排工具，如 Ansible、Rook 或 Salt。

Cephadm 管理 Ceph 群集的整个生命周期。它首先在单个节点（一个`monitor`和一个`mgr`）上引导一个最简的 Ceph 群集，然后使用业务流程接口（后续命令（“day 2” commands））扩展群集以包括所有主机并预配所有 Ceph 守护进程和服务。这可以通过 Ceph 命令行接口 （CLI） 或 dashboard  （GUI） 执行完成。

## 发展动向
目前 cephadm 仍然在进一步开发，功能正在有条不紊地进行着，使用 cephadm 是一个差强人意的选择。
以下组件的 Cephadm 管理目前得到良好支持：

- Monitors
- Managers
- OSDs
- CephFS 文件系统
- rbd-mirror

以下组件正在使用 cephadm，但文档并不像我们希望的那么完整，而且在不久的将来使用可能会有一些变化：

- RGW
- dmcrypt Osds

Cephadm 对以下功能的支持仍在开发中：

- NFS
- iSCSI

如果遇到问题，您始终可以使用：
```bash
ceph orch pause
```
或使用如下指令完全关闭 cephadm：
```bash
ceph orch set backend ''
ceph mgr module disable cephadm
```

## 安装 cephadm
- 下载 cephadm 并赋权
```plain
curl --silent --remote-name --location https://github.com/ceph/ceph/raw/octopus/src/cephadm/cephadm
chmod +x cephadm
```
- 添加源信息，指定为 Octopus 版本
```shell
./cephadm add-repo --release octopus
./cephadm install
```
此时会更新 repo 信息
```plain
./cephadm add-repo --release octopus
INFO:root:Writing repo to /etc/yum.repos.d/ceph.repo...
INFO:cephadm:Enabling EPEL...
```
验证：
```plain
[root@cepho yum.repos.d]# ll -t
total 48
```
更新前：
```plain
# before
total 36
-rw-r--r--. 1 root root  413 Mar 15 12:36 ceph.repo
-rw-r--r--. 1 root root 1664 Nov 23  2018 CentOS-Base.repo
-rw-r--r--. 1 root root 1309 Nov 23  2018 CentOS-CR.repo
-rw-r--r--. 1 root root  649 Nov 23  2018 CentOS-Debuginfo.repo
-rw-r--r--. 1 root root  314 Nov 23  2018 CentOS-fasttrack.repo
-rw-r--r--. 1 root root  630 Nov 23  2018 CentOS-Media.repo
-rw-r--r--. 1 root root 1331 Nov 23  2018 CentOS-Sources.repo
-rw-r--r--. 1 root root 5701 Nov 23  2018 CentOS-Vault.repo

```
更新后
```plain
# after
-rw-r--r--. 1 root root  477 Mar 22 17:33 ceph.repo
-rw-r--r--. 1 root root 2424 Oct 19 05:57 docker-ce.repo
-rw-r--r--. 1 root root 1050 Sep 18  2019 epel.repo
-rw-r--r--. 1 root root 1149 Sep 18  2019 epel-testing.repo
-rw-r--r--. 1 root root 1664 Nov 23  2018 CentOS-Base.repo
-rw-r--r--. 1 root root 1309 Nov 23  2018 CentOS-CR.repo
-rw-r--r--. 1 root root  649 Nov 23  2018 CentOS-Debuginfo.repo
-rw-r--r--. 1 root root  314 Nov 23  2018 CentOS-fasttrack.repo
-rw-r--r--. 1 root root  630 Nov 23  2018 CentOS-Media.repo
-rw-r--r--. 1 root root 1331 Nov 23  2018 CentOS-Sources.repo
-rw-r--r--. 1 root root 5701 Nov 23  2018 CentOS-Vault.repo
```
其中前三行即是更新之后的源信息。
{%note info no-icon%}
### 报错处理
1. 没有装 Python3
    执行第一条指令*可能*报错
    ```plain
    ./cephadm add-repo --release octopus
    -bash: ./cephadm: /usr/bin/python3: bad interpreter: No such file or directory
    ```
    这是因为系统中缺少 Python3 支持，所以要安装 Python3，关于 Python3 的安装可以参考此处👇
    1. [Python3 环境搭建 | 菜鸟教程](https://www.runoob.com/python3/python3-install.html) 
    2. [安装 Python 所需依赖环境 - 寒爵 - 博客园](https://www.cnblogs.com/Jimc/p/10218062.html) 
    安装之后验证：
    ```shell
    python3 -V
    ```
    返回版本信息：
    ```plain
    Python 3.8.2
    ```
2. 没有装 podman/docker
    ```plain
    Unable to locate any of ['podman', 'docker']
    ```
    安装 Docker 参考[CentOS Docker 安装 | 菜鸟教程](https://www.runoob.com/docker/centos-docker-install.html)
    验证
    ```plain
    docker --version
    Docker version 19.03.8, build afacb8b
    ```
    {%endnote%}

- 安装 cephadm
    ```plain
    ./cephadm install
    ```
    ```plain
    INFO:cephadm:Installing packages ['cephadm']...
    ```
- 验证 cephadm 安装完成
    ```plain
    which cephadm
    ```
    ```plain
    /usr/sbin/cephadm
    ```

## 引导新集群
你需要知道用于群集的第一个监视器守护程序的 IP 地址。 通常，这是第一台主机的 IP。 如果存在多个网络和接口，请确保选择任何可供访问 Ceph 群集的主机访问的网络和接口。
```plain
mkdir -p /etc/ceph
```
```plain
cephadm bootstrap --mon-ip *<mon-ip>*   # 此处指定moniter地址
```
{% note warning %}
**TODO**
注意，此处指定为 ssh 登录的 ip 时一直提示端口占用，且 mon 进程一直启不来，后来改成另一个节点之后可以正常部署，需要查阅更多资料确认！
{% endnote %}

```shell
cephadm bootstrap --mon-ip 172.18.1.128
```
```plain
INFO:cephadm:Using recent ceph image ceph/daemon-base:latest
INFO:cephadm:Verifying podman|docker is present...  # 验证podman|docker
INFO:cephadm:Verifying lvm2 is present...           # 验证lvm2
INFO:cephadm:Verifying time synchronization is in place... # 验证时间同步
INFO:cephadm:Unit chronyd.service is enabled and running        # chronyd
INFO:cephadm:Repeating the final host check...
INFO:cephadm:podman|docker (/usr/bin/docker) is present
INFO:cephadm:systemctl is present
INFO:cephadm:lvcreate is present
INFO:cephadm:Unit chronyd.service is enabled and running
INFO:cephadm:Host looks OK
INFO:root:Cluster fsid: d0d73402-6c28-11ea-8165-00505625d3e6    # 生成集群fsid
INFO:cephadm:Verifying IP 172.18.1.128 port 3300 ...
INFO:cephadm:Verifying IP 172.18.1.128 port 6789 ...            # 验证端口
INFO:cephadm:Pulling latest ceph/daemon-base:latest container...
INFO:cephadm:Extracting ceph user uid/gid from container image...   # pull容器
INFO:cephadm:Creating initial keys...
INFO:cephadm:Creating initial monmap...                     # 初始化keys、monmap
INFO:cephadm:Creating mon...
INFO:cephadm:Waiting for mon to start...
INFO:cephadm:Waiting for mon...                                # 创建并启动mon
INFO:cephadm:Assimilating anything we can from ceph.conf...
INFO:cephadm:Generating new minimal ceph.conf...                # 生成配置
INFO:cephadm:Restarting the monitor...                      
INFO:cephadm:Creating mgr...                                    # 创建mgr
INFO:cephadm:Non-zero exit code 1 from /usr/bin/firewall-cmd --permanent --query-service ceph
INFO:cephadm:/usr/bin/firewall-cmd:stdout no
INFO:cephadm:Enabling firewalld service ceph in current zone...
INFO:cephadm:Non-zero exit code 1 from /usr/bin/firewall-cmd --permanent --query-port 8080/tcp
INFO:cephadm:/usr/bin/firewall-cmd:stdout no
INFO:cephadm:Enabling firewalld port 8080/tcp in current zone...
INFO:cephadm:Non-zero exit code 1 from /usr/bin/firewall-cmd --permanent --query-port 8443/tcp
INFO:cephadm:/usr/bin/firewall-cmd:stdout no
INFO:cephadm:Enabling firewalld port 8443/tcp in current zone...
INFO:cephadm:Non-zero exit code 1 from /usr/bin/firewall-cmd --permanent --query-port 9283/tcp
INFO:cephadm:/usr/bin/firewall-cmd:stdout no
INFO:cephadm:Enabling firewalld port 9283/tcp in current zone...        # 打开防火墙端口
INFO:cephadm:Wrote keyring to ceph.client.admin.keyring
INFO:cephadm:Wrote config to ceph.conf
INFO:cephadm:Waiting for mgr to start...
INFO:cephadm:Waiting for mgr...
INFO:cephadm:mgr not available, waiting (1/10)...
……
INFO:cephadm:mgr not available, waiting (5/10)...
INFO:cephadm:Enabling cephadm module...
INFO:cephadm:Waiting for the mgr to restart...                          # 重启mgr
INFO:cephadm:Waiting for Mgr epoch 5...
INFO:cephadm:Setting orchestrator backend to cephadm...
INFO:cephadm:Generating ssh key...
INFO:cephadm:Wrote public SSH key to to ceph.pub
INFO:cephadm:Adding key to root@localhost's authorized_keys...
INFO:cephadm:Adding host cepho...
INFO:cephadm:Deploying mon service with default placement...
INFO:cephadm:Deploying mgr service with default placement...
INFO:cephadm:Deploying crash service with default placement...
INFO:cephadm:Enabling the dashboard module...
INFO:cephadm:Waiting for the mgr to restart...
INFO:cephadm:Waiting for Mgr epoch 9...
INFO:cephadm:Generating a dashboard self-signed certificate...      # 初始化dashboard
INFO:cephadm:Creating initial admin user...
INFO:cephadm:Fetching dashboard port number...
INFO:cephadm:Ceph Dashboard is now available at:

	     URL: https://cepho:8443/
	    User: admin
	Password: tkl507cgh3                                            # 初始密码，默认登录之后需要修改

INFO:cephadm:You can access the Ceph CLI with:

	sudo /usr/sbin/cephadm shell --fsid d0d73402-6c28-11ea-8165-00505625d3e6 -c ceph.conf -k ceph.client.admin.keyring

INFO:cephadm:Please consider enabling telemetry to help improve Ceph:

	ceph telemetry on

For more information see:

	https://docs.ceph.com/docs/master/mgr/telemetry/

INFO:cephadm:Bootstrap complete.
```
该命令会做以下操作：

- 在本地主机上为集群创建`mon`和`mgr`守护程序。

- 为 Ceph 集群生成一个新的 SSH 密钥，并将其添加到`root`用户的`/root/.ssh/authorized_keys`文件中。

- 将与新集群通信所需的最小配置文件写入`/etc/ceph/ceph.conf`。

- 将`client.admin`管理（特权！）秘密密钥的副本写入`/etc/ceph/ceph.client.admin.keyring`。

- 将公共密钥的副本写入`/etc/ceph/ceph.pub`。

{%note info%}
**注意**： 执行上述命令会去 docker 上面拉取最新的`ceph/daemon-base`，国内需要换源。具体操作如下：
1. 编辑或新建配置文件：
 ```shell
 vi /etc/docker/daemon.json
 ```
 写入：
 ```plain
{
"registry-mirrors" : [
    "http://ovfftd6p.mirror.aliyuncs.com",
    "http://registry.docker-cn.com",
    "http://docker.mirrors.ustc.edu.cn",
    "http://hub-mirror.c.163.com"
],
"insecure-registries" : [
    "registry.docker-cn.com",
    "docker.mirrors.ustc.edu.cn"
],
"debug" : true,
"experimental" : true
}
```
2. 重启 docker 服务
    ```plain
    systemctl restart docker
    ```
3. 手动拉取镜像
 ```shell
 docker pull ceph/daemon-base
 ```
由于本人第一次使用 docker，所以一些表述可能存在问题。
{% endnote %}
### 访问 dashboard
![overview](/images/Ceph-dashboard-overview.png)
![Ceph-dashboard](/images/Ceph-dashboard-host.png)

默认的引导行为适用于绝大多数用户。 请参阅以下有关选项对某些用户可能有用的一些，或运行 `cephadm bootstrap -h` 以查看所有可用选项：

- 方便起见，Bootstrap 会将访问新集群所需的文件写到`/etc/ceph`中，以便主机本身安装的任何 Ceph 软件包（例如，访问命令行界面）都可以轻松找到它们。

 但是，使用`cephadm`部署的守护程序容器根本不需要`/etc/ceph`。 使用`--output-dir *directory>*`选项将它们放在不同的目录（如.<当前目录>）中，避免与同一主机上的现有 Ceph 配置（`cephadm`或其他）之间的潜在冲突。

- 我们可以将任何初始 Ceph 配置选项传递到新集群，方法是将它们放置在标准`ini`样式的配置文件中，并使用`--config * <config-file> *`选项。

### 使能 CEPH CLI
ceph 官方建议启用对 ceph 命令的轻松访问，我们有以下途径可以实现：
- 调用 cephadm shell 命令启动容器中的 bash
    ```plain
    sudo /usr/sbin/cephadm shell --fsid d0d73402-6c28-11ea-8165-00505625d3e6 -c ceph.conf -k ceph.client.admin.keyring
    ```
    其中的`fsid`可以在上一条返回信息中找到，或者在`ceph.conf`中进行查看。
    ```plain
    INFO:cephadm:Using recent ceph image ceph/daemon-base:latest
    ```
- 安装 ceph-common 包，包含了`ceph`, `rbd`, `mount.ceph` (用于挂载 CephFS 文件系统)等；
    ```shell
    cephadm add-repo --release octopus          # 此处会更新源，如果需要使用国内源请不要执行
    yum install ceph-common # 此处官网暂为cephadm install xxx，但是我执行之后报错，所以修改。
    ```
- 调用`ceph`命令查看集群状态
    ```plain
    ceph -s
    cluster:
        id:     d0d73402-6c28-11ea-8165-00505625d3e6
        health: HEALTH_WARN
                Reduced data availability: 1 pg inactive
                OSD count 0 < osd_pool_default_size 3

    services:
        mon: 1 daemons, quorum cepho (age 20m)
        mgr: cepho.lgqcve(active, since 18m)
        osd: 0 osds: 0 up, 0 in

    data:
        pools:   1 pools, 1 pgs
        objects: 0 objects, 0 B
        usage:   0 B used, 0 B / 0 B avail
        pgs:     100.000% pgs unknown
                1 unknown
    ```
- 在`cephadm shell`中查看集群健康信息
    ```plain
    [ceph: root@cepho /]# ceph health
    HEALTH_WARN Reduced data availability: 1 pg inactive; OSD count 0 < osd_pool_default_size 3
    ```

---
TODO:以下待验证

### 集群添加新节点
1. 在新的节点拷贝认证`ssh key`认证密钥
在 bash 中执行
```plain
ssh-copy-id -f -i ceph.pub root@*<new-host>*    # 新节点的hostname
```
2. 告诉新节点是集群的一部分
在 cephadm shell 中执行
```plain
ceph orch host add *newhost*
```

## 参考链接
- [Deploying a new Ceph cluster — Ceph Documentation](https://docs.ceph.com/en/latest/cephadm/)