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

## 生成 diamond 安装包
```bash
cd ../Diamond
git checkout origin/calamari
yum install rpm-build -y
make rpm
```
将 diamond-<version>.noarch.rpm 复制到所有的 ceph 服务器，执行安装：
```bash
cd dist/
# 方案1
yum install python-configobj
rpm -ivh diamond-<version>.noarch.rpm
# 方案2
yum localinstall diamond-3.4.67-0.noarch.rpm
```
## 安装 salt-minion
在所有的 ceph 服务器上安装 salt-minion
```bash
yum install salt-minion
```
创建`/etc/salt/minion.d/calamari.conf`，内容为：
master: {SERVER NODE HOSTNAME}
{SERVER NODE HOSTNAME}对应 calamari 服务器的域名。
启动 salt-minion 服务：
```shell
service salt-minion restart
```
## 问题记录
### Ceph servers are connected to Calamari, but no Ceph cluster has been created yet
安装完成之后，首页出现如下提示：

![New-Calamari-Installation](/images/snipaste_20191106_133550.jpg)  
```shell
This appears to be the first time you have started Calamari and there are no clusters currently configured.

*some* Ceph servers are connected to Calamari, but no Ceph cluster has been
created yet. Please use ceph-deploy to create a cluster; please see the
Inktank Ceph Enterprise documentation for more details.
```
具体[见此处](https://github.com/ceph/calamari/issues/518)    
#### 解决办法
- 执行`salt '*' ceph.get_heartbeats`，返回如下:
```shell
node2:
    The minion function caused an exception: Traceback (most recent call last):
      File "/usr/lib/python2.7/site-packages/salt/minion.py", line 1200, in _thread_return
        return_data = func(*args, **kwargs)
      File "/var/cache/salt/minion/extmods/modules/ceph.py", line 534, in get_heartbeats
        service_data = service_status(filename)
      File "/var/cache/salt/minion/extmods/modules/ceph.py", line 593, in service_status
        fsid = json.loads(admin_socket(socket_path, ['status'], 'json'))['cluster_fsid']
    KeyError: 'cluster_fsid'
…… # It is same.
    The minion function caused an exception: Traceback (most recent call last):
      File "/usr/lib/python2.7/site-packages/salt/minion.py", line 1200, in _thread_return
        return_data = func(*args, **kwargs)
      File "/var/cache/salt/minion/extmods/modules/ceph.py", line 534, in get_heartbeats
        service_data = service_status(filename)
      File "/var/cache/salt/minion/extmods/modules/ceph.py", line 593, in service_status
        fsid = json.loads(admin_socket(socket_path, ['status'], 'json'))['cluster_fsid']
    KeyError: 'cluster_fsid'

```
- 修改代码`AdminSocketError ` 为 ` (AdminSocketError,KeyError)`：
```python
try:
    fsid = json.loads(admin_socket(socket_path, ['status'], 'json'))['cluster_fsid']
except (AdminSocketError,KeyError):  # 此处也可以直接使用 Exception
    # older osd/mds daemons don't support 'status'; try our best
   pass             # 此处代码不变
```
**注意**: 在`admin`节点，代码可能在 `/opt/calamari/salt/salt/_modules/ceph.py` 而在其他节点，代码可能在`/var/cache/salt/minion/extmods/modules/ceph.py`。
-  在`admin`节点执行`salt "*" saltutil.sync_all`或者`systemctl restart salt-minion`，返回:
```shell
node3:
    ----------
    beacons:
    grains:
    modules:
    output:
    renderers:
    returners:
    sdb:
    states:
    utils:
……
node2:
    ----------
    beacons:
    grains:
    modules:
    output:
    renderers:
    returners:
    sdb:
    states:
    utils:
```
- 然后，在`admin`节点执行`salt '*' ceph.get_heartbeats`，返回:
```shell
node2:
    |_
      ----------
      boot_time:
          1573005001
      ceph_version:
          2:13.2.6-0.el7
      services:
          ----------
          ceph-mgr.node2:
              ----------
              cluster:
                  ceph
              fsid:
                  47071b01-394e-4a62-bb2d-cfe3c19637f7
              id:
                  node2
              status:
                  None
              type:
                  mgr
              version:
                  13.2.6
          ceph-osd.0:
              ----------
              cluster:
                  ceph
              fsid:
                  47071b01-394e-4a62-bb2d-cfe3c19637f7
              id:
                  0
              status:
                  None
              type:
                  osd
              version:
                  13.2.6
    |_
      ----------
……
```
- 访问页面，获取到如此显示  
![500_error](/images/snipaste_20191106_102957.jpg)   
### 500 错误，请联系管理员
[此处](https://tracker.ceph.com/issues/13476)有关于该问题的描述。
- 查看calamari 日志
```shell
tailf /var/log/calamari/calamari.log 
```
获取到以下错误：
```shell
2019-11-05 21:02:19,605 - metric_access - django.request No graphite data for ceph.cluster.47071b01-394e-4a62-bb2d-cfe3c19637f7.df.total_used_bytes
2019-11-05 21:02:19,606 - metric_access - django.request No graphite data for ceph.cluster.47071b01-394e-4a62-bb2d-cfe3c19637f7.df.total_used
2019-11-05 21:02:19,606 - metric_access - django.request No graphite data for ceph.cluster.47071b01-394e-4a62-bb2d-cfe3c19637f7.df.total_space
2019-11-05 21:02:19,607 - metric_access - django.request No graphite data for ceph.cluster.47071b01-394e-4a62-bb2d-cfe3c19637f7.df.total_avail
2019-11-05 21:02:19,608 - ERROR - django.request Internal Server Error: /api/v1/cluster/47071b01-394e-4a62-bb2d-cfe3c19637f7/space
Traceback (most recent call last):
  File "/opt/calamari/venv/lib/python2.7/site-packages/django/core/handlers/base.py", line 115, in get_response
    response = callback(request, *callback_args, **callback_kwargs)
  File "/opt/calamari/venv/lib/python2.7/site-packages/rest_framework/viewsets.py", line 78, in view
    return self.dispatch(request, *args, **kwargs)
  File "/opt/calamari/venv/lib/python2.7/site-packages/calamari_rest_api-0.1-py2.7.egg/calamari_rest/views/rpc_view.py", line 94, in dispatch
    self.client.close()
  File "/opt/calamari/venv/lib/python2.7/site-packages/zerorpc/core.py", line 293, in close
    SocketBase.close(self)
  File "/opt/calamari/venv/lib/python2.7/site-packages/zerorpc/socket.py", line 37, in close
    self._events.close()
  File "/opt/calamari/venv/lib/python2.7/site-packages/zerorpc/events.py", line 198, in close
    self._send.close()
  File "/opt/calamari/venv/lib/python2.7/site-packages/zerorpc/events.py", line 50, in close
    self._send_task.kill()
  File "/opt/calamari/venv/lib/python2.7/site-packages/gevent/greenlet.py", line 235, in kill
    waiter.get()
  File "/opt/calamari/venv/lib/python2.7/site-packages/gevent/hub.py", line 575, in get
    return self.hub.switch()
  File "/opt/calamari/venv/lib/python2.7/site-packages/gevent/hub.py", line 338, in switch
    return greenlet.switch(self)
LostRemote: Lost remote after 10s heartbeat

------

2019-11-05 23:59:43,586 - ERROR - django.request Internal Server Error: /api/v1/cluster/47071b01-394e-4a62-bb2d-cfe3c19637f7/health_counters
Traceback (most recent call last):
  File "/opt/calamari/venv/lib/python2.7/site-packages/django/core/handlers/base.py", line 115, in get_response
    response = callback(request, *callback_args, **callback_kwargs)
  File "/opt/calamari/venv/lib/python2.7/site-packages/rest_framework/viewsets.py", line 78, in view
    return self.dispatch(request, *args, **kwargs)
  File "/opt/calamari/venv/lib/python2.7/site-packages/calamari_rest_api-0.1-py2.7.egg/calamari_rest/views/rpc_view.py", line 91, in dispatch
    return super(RPCViewSet, self).dispatch(request, *args, **kwargs)
  File "/opt/calamari/venv/lib/python2.7/site-packages/django/views/decorators/csrf.py", line 77, in wrapped_view
    return view_func(*args, **kwargs)
  File "/opt/calamari/venv/lib/python2.7/site-packages/rest_framework/views.py", line 399, in dispatch
    response = self.handle_exception(exc)
  File "/opt/calamari/venv/lib/python2.7/site-packages/calamari_rest_api-0.1-py2.7.egg/calamari_rest/views/rpc_view.py", line 108, in handle_exception
    return super(RPCViewSet, self).handle_exception(exc)
  File "/opt/calamari/venv/lib/python2.7/site-packages/rest_framework/views.py", line 396, in dispatch
    response = handler(request, *args, **kwargs)
  File "/opt/calamari/venv/lib/python2.7/site-packages/calamari_rest_api-0.1-py2.7.egg/calamari_rest/views/v1.py", line 315, in get
    counters = self.generate(osd_data, mds_data, mon_status, pg_summary)
  File "/opt/calamari/venv/lib/python2.7/site-packages/calamari_rest_api-0.1-py2.7.egg/calamari_rest/views/v1.py", line 167, in generate
    'mds': cls._calculate_mds_counters(mds_map),
  File "/opt/calamari/venv/lib/python2.7/site-packages/calamari_rest_api-0.1-py2.7.egg/calamari_rest/views/v1.py", line 295, in _calculate_mds_counters
    up = len(mds_map['up'])
TypeError: 'NoneType' object has no attribute '__getitem__'

--------

2019-11-06 00:00:53,567 - ERROR - django.request Internal Server Error: /api/v1/cluster/47071b01-394e-4a62-bb2d-cfe3c19637f7/osd
Traceback (most recent call last):
  File "/opt/calamari/venv/lib/python2.7/site-packages/django/core/handlers/base.py", line 115, in get_response
    response = callback(request, *callback_args, **callback_kwargs)
  File "/opt/calamari/venv/lib/python2.7/site-packages/rest_framework/viewsets.py", line 78, in view
    return self.dispatch(request, *args, **kwargs)
  File "/opt/calamari/venv/lib/python2.7/site-packages/calamari_rest_api-0.1-py2.7.egg/calamari_rest/views/rpc_view.py", line 91, in dispatch
    return super(RPCViewSet, self).dispatch(request, *args, **kwargs)
  File "/opt/calamari/venv/lib/python2.7/site-packages/django/views/decorators/csrf.py", line 77, in wrapped_view
    return view_func(*args, **kwargs)
  File "/opt/calamari/venv/lib/python2.7/site-packages/rest_framework/views.py", line 399, in dispatch
    response = self.handle_exception(exc)
  File "/opt/calamari/venv/lib/python2.7/site-packages/calamari_rest_api-0.1-py2.7.egg/calamari_rest/views/rpc_view.py", line 108, in handle_exception
    return super(RPCViewSet, self).handle_exception(exc)
  File "/opt/calamari/venv/lib/python2.7/site-packages/rest_framework/views.py", line 396, in dispatch
    response = handler(request, *args, **kwargs)
  File "/opt/calamari/venv/lib/python2.7/site-packages/calamari_rest_api-0.1-py2.7.egg/calamari_rest/views/v1.py", line 417, in get
    osds, osds_by_pg_state = self.generate(pg_summary, osd_map, server_info, servers)
  File "/opt/calamari/venv/lib/python2.7/site-packages/calamari_rest_api-0.1-py2.7.egg/calamari_rest/views/v1.py", line 365, in generate
    for pool_id, osds in osd_map.osds_by_pool.items():
  File "/opt/calamari/venv/lib/python2.7/site-packages/calamari_common-0.1-py2.7.egg/calamari_common/util.py", line 8, in wrapper
    rv = function(*args)
  File "/opt/calamari/venv/lib/python2.7/site-packages/calamari_common-0.1-py2.7.egg/calamari_common/types.py", line 206, in osds_by_pool
    for rule in [r for r in self.data['crush']['rules'] if r['ruleset'] == pool['crush_ruleset']]:
KeyError: 'crush_ruleset'
2019-11-06 00:00:54,566 - metric_access - django.request No graphite data for ceph.cluster.47071b01-394e-4a62-bb2d-cfe3c19637f7.pool.1.num_objects
```
查看 `cthulhu` 日志
```shell
tailf /var/log/calamari/cthulhu.log
```
返回如下：
```shell
2019-11-05 22:05:31,371 - WARNING - cthulhu Ignoring event salt/job/20191105220531366943/ret/node1
2019-11-05 22:05:31,371 - WARNING - cthulhu.request_collection on_completion: unknown jid 20191105220531366943, return: None
2019-11-05 22:05:38,283 - WARNING - cthulhu.request_collection on_completion: unknown jid 20191105220538277178, return: None
2019-11-05 22:05:38,283 - WARNING - cthulhu Ignoring event salt/job/20191105220538277178/ret/node3
2019-11-05 22:05:38,383 - WARNING - cthulhu Ignoring event salt/job/20191105220538379133/ret/node2
2019-11-05 22:05:38,384 - WARNING - cthulhu.request_collection on_completion: unknown jid 20191105220538379133, return: None
2019-11-05 22:05:41,384 - WARNING - cthulhu Abandoning fetch for mds_map started at 2019-11-06 03:05:31.344465+00:00
2019-11-05 22:05:41,385 - ERROR - cthulhu Exception handling message with tag ceph/cluster/47071b01-394e-4a62-bb2d-cfe3c19637f7
Traceback (most recent call last):
  File "/opt/calamari/venv/lib/python2.7/site-packages/calamari_cthulhu-0.1-py2.7.egg/cthulhu/manager/cluster_monitor.py", line 244, in _run
    self.on_heartbeat(data['id'], data['data'])
  File "/opt/calamari/venv/lib/python2.7/site-packages/calamari_cthulhu-0.1-py2.7.egg/cthulhu/gevent_util.py", line 35, in wrapped
    return func(*args, **kwargs)
  File "/opt/calamari/venv/lib/python2.7/site-packages/calamari_cthulhu-0.1-py2.7.egg/cthulhu/manager/cluster_monitor.py", line 346, in on_heartbeat
    cluster_data['versions'][sync_type.str])
  File "/opt/calamari/venv/lib/python2.7/site-packages/calamari_cthulhu-0.1-py2.7.egg/cthulhu/manager/cluster_monitor.py", line 99, in on_version
    self.fetch(reported_by, sync_type)
  File "/opt/calamari/venv/lib/python2.7/site-packages/calamari_cthulhu-0.1-py2.7.egg/cthulhu/manager/cluster_monitor.py", line 109, in fetch
    client = LocalClient(config.get('cthulhu', 'salt_config_path'))
  File "/usr/lib/python2.7/site-packages/salt/client/__init__.py", line 126, in __init__
    self.opts = salt.config.client_config(c_path)
  File "/usr/lib/python2.7/site-packages/salt/config.py", line 2203, in client_config
  File "/usr/lib/python2.7/site-packages/salt/utils/xdg.py", line 13, in xdg_config_dir
  File "/opt/calamari/venv/lib64/python2.7/posixpath.py", line 269, in expanduser
KeyError: 'getpwuid(): uid not found: 0'
```
## 参考链接
- [安装部署 Ceph Calamari](https://www.cnblogs.com/gaohong/p/4669524.html)
- [在CentOS 7 安装Calamari](https://www.cnblogs.com/flytor/p/11425135.html)