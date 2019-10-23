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
## 构建calamari server的rpm包
