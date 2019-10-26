---
title: ceph-calamari 安装记录
date: 2019-10-23 16:44:31
tags:
- 安装
- Calamari
---
## 克隆源码
```bash
mkdir /tmp/calamari-repo
cd /tmp/calamari-repo 
git clone https://github.com/ceph/calamari.git
git clone https://github.com/ceph/Diamond.git 
git clone https://github.com/ceph/calamari-clients.git
```
## 构建 calamari server 的 rpm 包

## 生成diamond安装包
```bash
cd ../Diamond
git checkout origin/calamari
yum install rpm-build -y
make rpm
```
将diamond-<version>.noarch.rpm复制到所有的ceph服务器，执行安装：
```bash
cd dist/
# 方案1
yum install python-configobj
rpm -ivh diamond-<version>.noarch.rpm
# 方案2
yum localinstall diamond-3.4.67-0.noarch.rpm
```
## 安装salt-minion
在所有的ceph服务器上安装salt-minion
```bash
yum install salt-minion
```
创建/etc/salt/minion.d/calamari.conf，内容为：
master: {fqdn}
{fqdn}对应calamari服务器的域名。
启动salt-minion服务：

# service salt-minion restart

## 参考链接
- [安装部署Ceph Calamari](https://www.cnblogs.com/gaohong/p/4669524.html)