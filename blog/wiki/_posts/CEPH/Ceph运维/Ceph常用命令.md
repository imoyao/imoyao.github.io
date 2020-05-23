---
title: first-wiki
toc: true
date: 2020-05-23 11:02:28
tags:
categories:
---
#### 集群信息

```shell
# 集群健康状态
ceph health detail

# 当前集群状态
ceph -s

# 集群存储空间
ceph df

# 集群实时运行状态
ceph -w

# 认证用户
ceph auth list

# 

```

#### mon 信息

```shell
# mon状态
ceph mon stat

# 选举状态
ceph quorum_status

# 映射信息
ceph mon dump

# 删除mon
ceph mon remove mon.c

# 获取当前mon map
ceph mon getmap -o mon.map

# 查看文件中的mon map
monmaptool --print mon.map

# 注入mon map到新节点
ceph-mon -i mon.d --inject-monmap mon.map


```

