---
title: CentOS7 下源码安装 DRBD
date: 2018-01-11 10:43:17
tags:
- DRBD
- Linux
- CentOS
categories:
- 教程记录
toc: true
---
最近开发中又要用到`DRBD`做远程复制的功能，网上搜到很多都是`yum`安装的办法，这里记录一下源码安装的办法。
<!--more-->

## 准备工作

### 关闭防火墙

```shell
systemctl disable firewalld
systemctl stop firewalld
```

### 关闭 SELinux

```shell
sed -i -e "s/=enforcing/=disabled/g" /etc/selinux/config
setenforce 0 
```

### 安装依赖

```shell
yum -y update 
yum -y install gcc make automake autoconf libxslt libxslt-devel flex rpm-build wget
```

**注意：** 安装`kernel-devel`一定要和`uname -r`获取结果一致。

```shell
rpm -q kernel-devel
uname -r

# 3.10.0-327.el7.x86_64
```

返回的内核版本应当一致，否则建议用本地源安装`kernel-devel`。
		
## 下载/解压源码

```shell
官方地址：https://www.linbit.com/en/drbd-community/drbd-download/
旧版本：http://www.linbit.com/en/drbd-community/old-releases/
MORE：http://www.linbit.com/www.linbit.com/downloads/drbd/
```

**注意：** 在`DRBD 8.4.3`(?)以上版本，对`drbd`和`utils`做了拆分，需要分别进行下载。

```shell
wget https://xxx.tar.gz
```

当然，如果需要你也可以通过我的分享下载编译好的`rpm`包（示例版本）：

> 链接:  https://pan.baidu.com/s/1huncgDI       密码:  b41i

### 解压下载的两个`tar`包

```shell
tar -zxvf drbd-8.*.tar.gz
tar -zxvf drbd-utils-*.tar.gz
```
## 编译`rpm`

### 创建构建`DRBD`需要的目录

```shell
mkdir -p rpmbuild/{BUILD,BUILDROOT,RPMS,SOURCES,SPECS,SRPMS}
```
### 编译`DRBD`

#### 制作 `rpm` 包

```shell
cd drbd-8.4.5/
make clean
make km-rpm KDIR=/usr/src/kernels/`uname -r`/       # 启用内核模块 自动识别内核版本    
# 返回：
# You have now:
# /root/rpmbuild/RPMS/x86_64/drbd-km-3.10.0_693.11.6.el7.x86_64-8.4.5-1.x86_64.rpm
# /root/rpmbuild/RPMS/x86_64/drbd-km-debuginfo-8.4.5-1.x86_64.rpmmakeinsta
```
---

#### 直接编译安装

```shell
## drbd模块

cd drbd
make
make install
lsmod|grep drbd
cp drbd.ko /lib/modules/`uname -r`/kernel/lib/

## 安装模块
modprobe drbd
## 验证drbd模块是否加载（部分系统默认有该模块）
lsmod|grep drbd

# drbd                  364858  0
# libcrc32c              12644  4 xfs,drbd,nf_nat,nf_conntrack
```
---

### 编译 drbd-utils 组件

```shell
cd ../../drbd-utils-8.9.0/   
./configure
make rpm
# 返回：
###
+ exit 0
You have now:
/root/rpmbuild/RPMS/x86_64/drbd-km-3.10.0_693.11.6.el7.x86_64-8.4.5-1.x86_64.rpm
/root/rpmbuild/RPMS/x86_64/drbd-km-debuginfo-8.4.5-1.x86_64.rpm
/root/rpmbuild/RPMS/x86_64/drbd-8.9.0-1.el7.centos.x86_64.rpm
/root/rpmbuild/RPMS/x86_64/drbd-utils-8.9.0-1.el7.centos.x86_64.rpm
/root/rpmbuild/RPMS/x86_64/drbd-xen-8.9.0-1.el7.centos.x86_64.rpm
/root/rpmbuild/RPMS/x86_64/drbd-udev-8.9.0-1.el7.centos.x86_64.rpm
/root/rpmbuild/RPMS/x86_64/drbd-pacemaker-8.9.0-1.el7.centos.x86_64.rpm
/root/rpmbuild/RPMS/x86_64/drbd-bash-completion-8.9.0-1.el7.centos.x86_64.rpm
/root/rpmbuild/RPMS/x86_64/drbd-debuginfo-8.9.0-1.el7.centos.x86_64.rpm
###
```

此时有可能提示错误如下：

```shell
/usr/bin/xsltproc \
        --xinclude \
        http://docbook.sourceforge.net/release/xsl/current/manpages/docbook.xsl drbdsetup.xml
error : Operation in progress
warning: failed to load external entity "http://docbook.sourceforge.net/release/xsl/current/manpages/docbook.xsl"
cannot parse http://docbook.sourceforge.net/release/xsl/current/manpages/docbook.xsl
make[1]: *** [drbdsetup.8] Error 4
```
提示有一个地址文件没能找到，解决方法：

```shell
yum -y install docbook-style-xsl
```

TODO: 此处暂未找到别的解决方法，欢迎读者留言。

## 安装

### 安装编译生成的文件

```shell
cd /root/rpmbuild/RPMS/x86_64/
rpm -ivh drbd-* --force
```
### 加载模块（参见分割线部分）

```shell
modprobe drbd

```
## 验证安装结果

```shell
lsmod|grep drbd
# 返回（`depends` 可能略有不同）：
# drbd                  373375  4
# libcrc32c              12644  2 xfs,drbd

drbd-overview  
 
# 以下两者返回稍有不同    
cat /proc/drbd
drbdadm -V
# 返回

DRBDADM_BUILDTAG=GIT-hash:\ 79677f4***7ca6b99929\ build\ by\ root@imoyao\,\ 2018-01-06\ 14:25:03
DRBDADM_API_VERSION=1
DRBD_KERNEL_VERSION_CODE=0x080405
DRBDADM_VERSION_CODE=0x080900
DRBDADM_VERSION=8.9.0
```
## 参考来源

- [CentOS 7 : DRBD : Install : Server World](https://www.server-world.info/en/note?os=CentOS_7&p=drbd&f=1)

- [CentOS 安装配置 DRBD – WTF Daily Blog](http://blog.topspeedsnail.com/archives/8381)

- [CentOS 下实现 Heartbeat+DRBD+MySQL 双机热备硬件故障自动切换高可用(HA)方案 | 三木的人生——3mu.me](http://www.3mu.me/centos%E4%B8%8B%E5%AE%9E%E7%8E%B0heartbeatdrbdmysql%E5%8F%8C%E6%9C%BA%E7%83%AD%E5%A4%87%E7%A1%AC%E4%BB%B6%E6%95%85%E9%9A%9C%E8%87%AA%E5%8A%A8%E5%88%87%E6%8D%A2%E9%AB%98%E5%8F%AF%E7%94%A8ha/#respond)