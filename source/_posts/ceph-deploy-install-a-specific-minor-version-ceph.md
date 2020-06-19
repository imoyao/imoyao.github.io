title: 如何使用 ceph-deploy 部署一个指定版本号的 ceph 集群
tags:
  - CEPH
  - ceph-deploy
  - CentOS7
  - 环境搭建
reward: true
date: 2020-03-16 14:09:20
cover: /images/logos/ceph-logo.svg
categories:
- 工作日常
---

## 前言
在 [上文](/blog/2020-03-15/ceph-deploy-install-ceph-nautilus-on-CentOS7/) 中我们使用 ceph-deploy 搭建 ceph 集群。而当前版本 ceph-deploy 不支持用户指定小版本号，使用`--release`只支持安装最新稳定版。当然我们可以手动搭建，但是操作下来耗时且容易出错，毕竟~~人生苦短（我太懒了）~~。
## 版本信息
1. 系统版本
```plain
[root@admin-node my-cluster]# cat /etc/system-release
CentOS Linux release 7.6.1810 (Core) 
[root@admin-node my-cluster]# uname -a
Linux admin-node 3.10.0-957.el7.x86_64 #1 SMP Thu Nov 8 23:39:32 UTC 2018 x86_64 x86_64 x86_64 GNU/Linux
```
2. ceph 版本
```plain
[root@admin-node my-cluster]# ceph -v
ceph version 14.2.5 (ad5bd132e1492173c85fda2cc863152730b16a92) nautilus (stable)
```

## 在本地配置离线存储库

### 安装网络服务

1. 安装 ngix
```plain
yum install epel-release -y
yum install nginx -y
```
2. 打开 nginx
```plain
systemctl start nginx
systemctl enable nginx
systemctl status nginx
```
3. 添加防火墙规则
```plain
firewall-cmd --zone=public --permanent --add-service=http
firewall-cmd --zone=public --permanent --add-service=https
firewall-cmd --reload
```

### 创建本地镜像源

1. 安装必需工具
```plain
yum install createrepo yum-utils wget -y
```
2. 创建镜像源文件夹
```plain
mkdir -p /var/www/html/repos/{SRPMS,x86_64,noarch}
```
3. 下载相应软件包
可以手动在以下 3 个链接中下载各自架构下的相应软件包
```plain
https://download.ceph.com/rpm-nautilus/el7/SRPMS/
https://download.ceph.com/rpm-nautilus/el7/noarch/
https://download.ceph.com/rpm-nautilus/el7/x86_64/
```
另外，我们也可以从阿里云的镜像源链接`http://mirrors.aliyun.com/ceph/`下载（国内用户你懂的）
```plain
wget https://mirrors.aliyun.com/ceph/rpm-nautilus/el7/x86_64/ceph-14.2.5-0.el7.x86_64.rpm
wget https://mirrors.aliyun.com/ceph/rpm-nautilus/el7/x86_64/ceph-14.2.5-0.el7.x86_64.rpm
wget https://mirrors.aliyun.com/ceph/rpm-nautilus/el7/x86_64/ceph-base-14.2.5-0.el7.x86_64.rpm
wget https://mirrors.aliyun.com/ceph/rpm-nautilus/el7/x86_64/ceph-common-14.2.5-0.el7.x86_64.rpm
wget https://mirrors.aliyun.com/ceph/rpm-nautilus/el7/x86_64/ceph-debuginfo-14.2.5-0.el7.x86_64.rpm
wget https://mirrors.aliyun.com/ceph/rpm-nautilus/el7/x86_64/ceph-fuse-14.2.5-0.el7.x86_64.rpm
wget https://mirrors.aliyun.com/ceph/rpm-nautilus/el7/x86_64/ceph-mds-14.2.5-0.el7.x86_64.rpm
wget https://mirrors.aliyun.com/ceph/rpm-nautilus/el7/x86_64/ceph-mgr-14.2.5-0.el7.x86_64.rpm
wget https://mirrors.aliyun.com/ceph/rpm-nautilus/el7/x86_64/ceph-mon-14.2.5-0.el7.x86_64.rpm
wget https://mirrors.aliyun.com/ceph/rpm-nautilus/el7/x86_64/ceph-osd-14.2.5-0.el7.x86_64.rpm
wget https://mirrors.aliyun.com/ceph/rpm-nautilus/el7/x86_64/ceph-radosgw-14.2.5-0.el7.x86_64.rpm
wget https://mirrors.aliyun.com/ceph/rpm-nautilus/el7/x86_64/ceph-resource-agents-14.2.5-0.el7.x86_64.rpm
wget https://mirrors.aliyun.com/ceph/rpm-nautilus/el7/x86_64/ceph-selinux-14.2.5-0.el7.x86_64.rpm
wget https://mirrors.aliyun.com/ceph/rpm-nautilus/el7/x86_64/ceph-test-14.2.5-0.el7.x86_64.rpm
wget https://mirrors.aliyun.com/ceph/rpm-nautilus/el7/x86_64/cephfs-java-14.2.5-0.el7.x86_64.rpm
wget https://mirrors.aliyun.com/ceph/rpm-nautilus/el7/x86_64/libcephfs-devel-14.2.5-0.el7.x86_64.rpm
wget https://mirrors.aliyun.com/ceph/rpm-nautilus/el7/x86_64/libcephfs2-14.2.5-0.el7.x86_64.rpm
wget https://mirrors.aliyun.com/ceph/rpm-nautilus/el7/x86_64/libcephfs_jni-devel-14.2.5-0.el7.x86_64.rpm
wget https://mirrors.aliyun.com/ceph/rpm-nautilus/el7/x86_64/libcephfs_jni1-14.2.5-0.el7.x86_64.rpm
wget https://mirrors.aliyun.com/ceph/rpm-nautilus/el7/x86_64/librados-devel-14.2.5-0.el7.x86_64.rpm
wget https://mirrors.aliyun.com/ceph/rpm-nautilus/el7/x86_64/librados2-14.2.5-0.el7.x86_64.rpm
wget https://mirrors.aliyun.com/ceph/rpm-nautilus/el7/x86_64/libradosstriper-devel-14.2.5-0.el7.x86_64.rpm
wget https://mirrors.aliyun.com/ceph/rpm-nautilus/el7/x86_64/libradosstriper1-14.2.5-0.el7.x86_64.rpm
wget https://mirrors.aliyun.com/ceph/rpm-nautilus/el7/x86_64/librbd-devel-14.2.5-0.el7.x86_64.rpm
wget https://mirrors.aliyun.com/ceph/rpm-nautilus/el7/x86_64/librbd1-14.2.5-0.el7.x86_64.rpm
wget https://mirrors.aliyun.com/ceph/rpm-nautilus/el7/x86_64/librgw-devel-14.2.5-0.el7.x86_64.rpm
wget https://mirrors.aliyun.com/ceph/rpm-nautilus/el7/x86_64/librgw2-14.2.5-0.el7.x86_64.rpm
wget https://mirrors.aliyun.com/ceph/rpm-nautilus/el7/x86_64/python-ceph-compat-14.2.5-0.el7.x86_64.rpm
wget https://mirrors.aliyun.com/ceph/rpm-nautilus/el7/x86_64/python-cephfs-14.2.5-0.el7.x86_64.rpm
wget https://mirrors.aliyun.com/ceph/rpm-nautilus/el7/x86_64/python-rados-14.2.5-0.el7.x86_64.rpm
wget https://mirrors.aliyun.com/ceph/rpm-nautilus/el7/x86_64/python-rbd-14.2.5-0.el7.x86_64.rpm
wget https://mirrors.aliyun.com/ceph/rpm-nautilus/el7/x86_64/python-rgw-14.2.5-0.el7.x86_64.rpm
wget https://mirrors.aliyun.com/ceph/rpm-nautilus/el7/x86_64/python34-ceph-argparse-14.2.5-0.el7.x86_64.rpm
wget https://mirrors.aliyun.com/ceph/rpm-nautilus/el7/x86_64/python34-cephfs-14.2.5-0.el7.x86_64.rpm
wget https://mirrors.aliyun.com/ceph/rpm-nautilus/el7/x86_64/python34-rados-14.2.5-0.el7.x86_64.rpm
wget https://mirrors.aliyun.com/ceph/rpm-nautilus/el7/x86_64/python34-rbd-14.2.5-0.el7.x86_64.rpm
wget https://mirrors.aliyun.com/ceph/rpm-nautilus/el7/x86_64/python34-rgw-14.2.5-0.el7.x86_64.rpm
wget https://mirrors.aliyun.com/ceph/rpm-nautilus/el7/x86_64/rados-objclass-devel-14.2.5-0.el7.x86_64.rpm
wget https://mirrors.aliyun.com/ceph/rpm-nautilus/el7/x86_64/rbd-fuse-14.2.5-0.el7.x86_64.rpm
wget https://mirrors.aliyun.com/ceph/rpm-nautilus/el7/x86_64/rbd-mirror-14.2.5-0.el7.x86_64.rpm
wget https://mirrors.aliyun.com/ceph/rpm-nautilus/el7/x86_64/rbd-nbd-14.2.5-0.el7.x86_64.rpm
wget http://mirrors.aliyun.com/ceph/rpm-nautilus/el7/x86_64/python-ceph-argparse-14.2.5-0.el7.x86_64.rpm
wget https://mirrors.aliyun.com/ceph/rpm-nautilus/el7/noarch/ceph-deploy-2.0.0-0.noarch.rpm
```
4. 执行镜像源创建
```plain
createrepo -v /var/www/html/repos/SRPMS/
createrepo -v /var/www/html/repos/x86_64/
createrepo -v /var/www/html/repos/noarch/
```
5. 修改 Nginx 配置
```plain
vi /etc/nginx/conf.d/repos.conf
```
```plain
server {
        listen   80;
        server_name  172.18.1.101;	# 修改此处为本机地址
        root   /var/www/html/repos;
        location / {
                index  index.php index.html index.htm;
                autoindex on;	#enable listing of directory index
        }
}

```
6. 重新启动 nginx，然后再次访问本地源测试
```plain
systemctl restart nginx
```
![upload successful](/images/pasted-0.png)

## 安装 Ceph
1. 声明本地仓库
```plain
vi/etc/yum.repos.d/ceph.repo
```
```plain
[ceph]
name=Ceph packages for $basearch
baseurl=http://172.18.1.101/x86_64/		# 注意此处ip为镜像源的ip
enabled=1
priority=2
gpgcheck=0
gpgkey=https://download.ceph.com/keys/release.asc

[ceph-noarch]
name=Ceph noarch packages
baseurl=http://172.18.1.101/noarch
enabled=1
priority=2
gpgcheck=0
gpgkey=https://download.ceph.com/keys/release.asc

[ceph-source]
name=Ceph source packages
baseurl=http://172.18.1.101/SRPMS
enabled=0
priority=2
gpgcheck=0
gpgkey=https://download.ceph.com/keys/release.asc
EOF
```
2. 然后像[往常一样](/blog/2020-03-15/ceph-deploy-install-ceph-nautilus-on-CentOS7/)进行 ceph 部署
```plain
yum -y install ceph-deploy
```
3. 转到使用 `ceph-deploy` 安装的步骤，我们将使用 **--repo-url** 替换命令
```plain
ceph-deploy install --repo-url http://172.18.1.101/ ceph1 ceph2 ceph3
```
4. 安装完成后，再次检查`ceph version`版本
```plain
[node2][DEBUG ] 
[node2][DEBUG ] Complete!
[node2][INFO  ] Running command: sudo ceph --version
[node2][DEBUG ] ceph version 14.2.5 (ad5bd132e1492173c85fda2cc863152730b16a92) nautilus (stable)
[root@admin-node x86_64]# ceph -v
ceph version 14.2.5 (ad5bd132e1492173c85fda2cc863152730b16a92) nautilus (stable)
```
## 本地镜像安装
1. 下载源文件到本地
```plain
mkdir ceph-mirror
cd ceph-mirror

yum install --downloadonly --downloaddir=. ceph
yum install --downloadonly --downloaddir=. yum-plugin-priorities

```
2. 对文件进行删选
仅保留我们需要的版本的 rpm 文件，其余的删除（否则同步会很耗时）

3. 使用`--local-mirror`指定使用本地镜像安装
```plain
ceph-deploy install --local-mirror {/opt/ceph-mirror/rpm-nautilus/el7/} node1 nodex
```
后面一次跟的指令为本地 mirror 所在路径、节点 hostname（多个或一个）

### 问题定位
同步时同步文件报内存不足
```plain
[cdnode1][INFO  ] syncing file: aarch64/ceph-debuginfo-14.2.2-0.el7.aarch64.rpm
[ceph_deploy][ERROR ] Traceback (most recent call last):
[ceph_deploy][ERROR ]   File "/usr/lib/python2.7/site-packages/ceph_deploy/util/decorators.py", line 69, in newfunc

# 太长省略
[ceph_deploy][ERROR ]     return _Serializer().save(obj)
[ceph_deploy][ERROR ]   File "/usr/lib/python2.7/site-packages/ceph_deploy/lib/vendor/remoto/lib/vendor/execnet/gateway_base.py", line 1312, in save
[ceph_deploy][ERROR ]     return type(streamlist[0])().join(streamlist)
[ceph_deploy][ERROR ] MemoryError
[ceph_deploy][ERROR ] 
Error in sys.exitfunc:

```
分析了一下，这个文件大概 2G 大小，如果直接 rsync 的话会导致内存爆炸，所以我的处理办法是删除`ceph-debuginfo`这个文件，后续有问题再装。

## 总结	
 `ceph-deploy` 可以通过三种指定方式部署 ceph,分别为`ceph-deploy install --release`（用于指定大版本号如`nautilus`）、`ceph-deploy install --testing`(用于最新开发版本)和`ceph-deploy install --dev`（用于指定分支或者 tag）,起初我以为`--dev`可以满足我指定版本号的需求，后来一顿操作发现报错:
```plain
[ceph_deploy.hosts.centos.install][DEBUG ] fetching repo information from: https://shaman.ceph.com/api/repos/ceph/14.5.2/latest/centos/7/repo/?arch=x86_64
[ceph_deploy.util.net][ERROR ] repository might not be available yet
[ceph_deploy][ERROR ] RuntimeError: HTTP Error 504: Gateway Timeout, failed to fetch https://shaman.ceph.com/api/repos/ceph/14.5.2/latest/centos/7/repo/?arch=x86_64
```
访问`https://shaman.ceph.com/api/repos/ceph`发现可用库里根本没有对应版本。通过阅读[install — ceph-deploy 2.0.2 documentation](https://docs.ceph.com/ceph-deploy/docs/install.html#behind-firewall)我们知道可以指定 `--repo-url`搭配`--gpg-url`使用指定源链接的方式指定本地源安装。此外，使用`--local-mirrors`指定本地源的方式也可以参考。参见[install — ceph-deploy 2.0.2 documentation](https://docs.ceph.com/ceph-deploy/docs/install.html#local-mirrors)。

本文通过搭建本地镜像源然后指定的方式间接完成了 ceph 集群的安装。

## 参考链接
- [install — ceph-deploy 2.0.2 documentation](https://docs.ceph.com/ceph-deploy/docs/install.html#install)
- [ceph-deploy-specific-version.md at thaonguyenvan/notes-storage](https://github.com/thaonguyenvan/notes-storage/blob/51e6eeb02c34767ad84d350c2462bdccc179c35c/ceph/setup/ceph-deploy-specific-version.md)

