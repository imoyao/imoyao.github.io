---
title: Pool-deletion-is-disabled-by-the-mon_allow_pool_delete-configuration-setting
date: 2020-04-13 11:47:08
tags:
categories:
---

如果使用 ceph-deploy，编辑配置文件添加
[mon]
mon_allow_pool_delete = true
推送配置到各节点（执行一条即可，推荐 2）
ceph-deploy --overwrite-conf admin node1 node2
ceph-deploy --overwrite-conf config push
推送后查看配置
cat /etc/ceph/ceph.conf
[global]
fsid = fecaf014-622f-4b42-b24a-8cfc4146dea4
mon_initial_members = node1
mon_host = 10.10.15.60
auth_cluster_required = cephx
auth_service_required = cephx
auth_client_required = cephx
osd pool default size = 2
public network = 10.10.15.0/24
[mon]
mon_allow_pool_delete = true	# 此条信息


另一种方案：

ceph tell mon.* injectargs --mon-allow-pool-delete=true
mon.node1: injectargs:mon_allow_pool_delete = 'true'
mon.node2: injectargs:mon_allow_pool_delete = 'true'

[root@node1 ~]# ceph osd pool delete pool1 pool1 --yes-i-really-really-mean-it
pool 'pool1' removed

ceph daemon /var/run/ceph/ceph-mon.$(hostname -s).asok config show | grep mon_allow_pool_delete
    "mon_allow_pool_delete": "false",

[root@node1 ~]# ceph-conf --name mon.$(hostname -s) --show-config-value admin_socket
/var/run/ceph/ceph-mon.node1.asok

[root@node1 ~]# ceph tell mon.node1 injectargs '--mon_allow_pool_delete=true'
injectargs:mon_allow_pool_delete = 'true'

[root@node1 ~]#  ceph daemon /var/run/ceph/ceph-mon.$(hostname -s).asok config show | grep mon_allow_pool_delete
    "mon_allow_pool_delete": "true",

systemctl list-units --type=service|grep ceph

  ceph-crash.service                 loaded active running Ceph crash dump collector
  ceph-mgr@node1.service             loaded active running Ceph cluster manager daemon
  ceph-mon@node1.service             loaded active running Ceph cluster monitor daemon
  ceph-osd@0.service                 loaded active running Ceph object storage daemon osd.0
  ceph-osd@1.service                 loaded active running Ceph object storage daemon osd.1
● ceph-radosgw@rgw.node1.service     loaded failed failed  Ceph rados gateway

重新执行删除操作
ceph osd pool delete {pool-name} [{pool-name} --yes-i-really-really-mean-it]
[root@node1 ~]# ceph osd pool delete Storpool_test Storpool_test --yes-i-really-really-mean-it
pool 'Storpool_test' removed

## 参考链接
- [DELETE A POOL](https://docs.ceph.com/docs/nautilus/rados/operations/pools/#delete-a-pool)

- [ceph (luminous 版) pool 管理 - 程序园](http://www.voidcn.com/article/p-bxwpgcfi-bqy.html)