## 手动配置ansible_runner_service
安装Python3
安装gcc
yum install -y gcc python3-devel libffi-devel openssl-devel 
### 添加环境变量
```
export PATH=/usr/local/bin:$PATH
```
### 开放 9090 端口
```
firewall-cmd --zone=public --add-port=9090/tcp --permanent
```
### 配置国内源加速
```
vi .pip/pip.conf 
```
写入：
```
[global]
timeout = 300
index-url = https://pypi.tuna.tsinghua.edu.cn/simple
[install]
trusted-host = tsinghua.edu.cn
```
### 加虚拟盘

echo '- - -' > /sys/class/scsi_host/host0/scan
### 装包
pip3 install -r requirements.txt

sudo python3 setup.py install --record installed_files --single-version-externally-managed

ansible_runner_service

## 遇到的问题

1. ansible 版本不对

装对应版本之后如果还不对，则删除playbook版本校验功能。

2. 提示 dashboard_admin_password 密码没有设置

[[ ceph-validate ] fail when dashboard_admin_password and/or grafana_admin_password are not set · Issue #59 · red-hat-storage/cockpit-ceph-installer](https://github.com/red-hat-storage/cockpit-ceph-installer/issues/59)

['AnsibleUndefinedVariable: ''grafana_admin_password'' is undefined' · Issue #5080 · ceph/ceph-ansible](https://github.com/ceph/ceph-ansible/issues/5080)
可以手动修改playbook配置
```
[root@cephnode1 group_vars]# vi /usr/share/ceph-ansible/group_vars/all.yml

---
ceph_origin: repository
ceph_repository: custom
ceph_custom_repo: http://10.10.1.8/ceph
ceph_stable_release: nautilus
ceph_version_num: 14
cluster_network: 100.0.0.0/8
containerized_deployment: false
dashboard_enabled: true
ip_version: ipv4
monitor_address_block: 100.0.0.0/8
public_network: 10.0.0.0/8
dashboard_admin_user: admin
dashboard_admin_password: admin
grafana_admin_user: admin
grafana_admin_password: admin

```


```
---
ceph_conf_overrides:
  global:
    osd_crush_chooseleaf_type: 0
    osd_pool_default_size: 1
ceph_origin: repository
ceph_repository: community
ceph_mirror: http://10.10.1.8/ceph
ceph_stable_release: nautilus
ceph_version_num: 14
cluster_network: 100.0.0.0/8
containerized_deployment: true
dashboard_enabled: true
docker_pull_timeout: 600s
ip_version: ipv4
monitor_address_block: 100.0.0.0/8
public_network: 10.0.0.0/8
dashboard_admin_user: admin
dashboard_admin_password: admin
grafana_admin_user: admin
grafana_admin_password: admin

```

---
ceph_conf_overrides:
  global:
    osd_crush_chooseleaf_type: 0
    osd_pool_default_size: 1
ceph_origin: repository
ceph_repository: community
ceph_mirror: http://10.10.1.8/ceph
ceph_stable_release: nautilus
ceph_version_num: 14
cluster_network: 100.0.0.0/8
containerized_deployment: true
dashboard_enabled: true
docker_pull_timeout: 600s
ip_version: ipv4
monitor_address_block: 100.0.0.0/8
public_network: 10.0.0.0/8



ceph_origin: repository
ceph_repository: community
ceph_stable_release: nautilus
ceph_version_num: 14
ceph_mirror: http://10.10.1.8/ceph
public_network: 10.0.0.0/8
cluster_network: 100.0.0.0/8
dashboard_enabled: true
docker_pull_timeout: 600s
ip_version: ipv4
monitor_address_block: 100.0.0.0/8
public_network: 10.0.0.0/8

dashboard_enabled: true
dashboard_admin_user: admin
dashboard_admin_password: admin
grafana_admin_user: admin
grafana_admin_password: admin



[Stucked on waiting for the monitor(s) to form the quorum... when executing add-mon.yml · Issue #4634 · ceph/ceph-ansible](https://github.com/ceph/ceph-ansible/issues/4634)