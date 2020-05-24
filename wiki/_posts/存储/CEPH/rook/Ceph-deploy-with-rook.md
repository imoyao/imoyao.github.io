
## 版本信息
所采用版本为`Rook version v1.2`；

### Prerequisites

#### 前提

> Kubernetes 版本 V1.11+

> ```shell
> modprobe rbd
> ```

> ```shell
> # 新版本以ceph-volume为存储介质管理工具，基于lvm实现管理，替换老的工具ceph-disk；
> yum install -y lvm2
> ```

> 参数调整
>
> ```shell
> # pid max
> sysctl -w kernel.pid_max=4194303
> # 通过数据预读并且记载到随机访问内存方式提高磁盘读操作
> echo "8192" > /sys/block/${盘符}/queue/read_ahead_kb
> # I/O Scheduler
> echo "deadline" > /sys/block/${普通盘符}/queue/scheduler
> echo "noop" > /sys/block/${ssd盘符}/queue/scheduler
> ```

#### 安装包

```shell
git clone --single-branch --branch release-1.2 https://github.com/rook/rook.git
```

#### 节点标签及污点

```shell
kubectl label nodes $CEPH_NODE role=storage-node
kubectl taint nodes $CEPH_NODE storage-node=:NoSchedule
```

#### 准备镜像

```shell
# cluster
ceph/ceph:v14.2.9
# operator
rook/ceph:v1.2.7
# csi-ceph
quay.io/cephcsi/cephcsi:v2.0.0
# csi-registrar
quay.io/k8scsi/csi-node-driver-registrar:v1.2.0
# csi-resizer
quay.io/k8scsi/csi-resizer:v0.4.0
# csi-provisioner
quay.io/k8scsi/csi-provisioner:v1.4.0
# csi-snapshotter
quay.io/k8scsi/csi-snapshotter:v1.2.2
# csi-attacher
quay.io/k8scsi/csi-attacher:v2.1.0
```

### Installation

#### 个性化配置

```shell
cd rook/cluster/examples/kubernetes/ceph
vim cluster.yaml
```

```yaml
apiVersion: ceph.rook.io/v1
kind: CephCluster
metadata:
  name: rook-ceph
  namespace: rook-ceph
spec:
  cephVersion:
    image: ceph/ceph:v14.2.9
    allowUnsupported: false
  dataDirHostPath: /var/lib/rook
  skipUpgradeChecks: false
  continueUpgradeAfterChecksEvenIfNotHealthy: false
  mon:
    count: 3
    allowMultiplePerNode: false
  # mgr:
    # modules:
    # Several modules should not need to be included in this list. The "dashboard" and "monitoring" modules
    # are already enabled by other settings in the cluster CR and the "rook" module is always enabled.
    # - name: pg_autoscaler
    #   enabled: true
  # enable the ceph dashboard for viewing cluster status
  dashboard:
    enabled: true
    # serve the dashboard under a subpath (useful when you are accessing the dashboard via a reverse proxy)
    # urlPrefix: /ceph-dashboard
    # serve the dashboard at the given port.
    # port: 8443
    # serve the dashboard using SSL
    ssl: true
  # enable prometheus alerting for cluster
  monitoring:
    # requires Prometheus to be pre-installed
    enabled: false
    rulesNamespace: rook-ceph
  network:
    # toggle to use hostNetwork
    hostNetwork: false
  rbdMirroring:
    # The number of daemons that will perform the rbd mirroring.
    # rbd mirroring must be configured with "rbd mirror" from the rook toolbox.
    workers: 0
  # enable the crash collector for ceph daemon crash collection
  crashCollector:
    disable: false
  placement:
    all:
      nodeAffinity:
        requiredDuringSchedulingIgnoredDuringExecution:
          nodeSelectorTerms:
          - matchExpressions:
            - key: role
              operator: In
              values:
              - storage-node
      podAffinity:
      podAntiAffinity:
      tolerations:
      - key: storage-node
        operator: Exists
# The above placement information can also be specified for mon, osd, and mgr components
#    mon:
# Monitor deployments may contain an anti-affinity rule for avoiding monitor
# collocation on the same node. This is a required rule when host network is used
# or when AllowMultiplePerNode is false. Otherwise this anti-affinity rule is a
# preferred rule with weight: 50.
#    osd:
#    mgr:
  annotations:
#    all:
#    mon:
#    osd:
# If no mgr annotations are set, prometheus scrape annotations will be set by default.
#   mgr:
  resources:
# The requests and limits set here, allow the mgr pod to use half of one CPU core and 1 gigabyte of memory
# 此处修改组件的资源配置
    mgr:
      limits:
        cpu: "500m"
        memory: "1024Mi"
      requests:
        cpu: "500m"
        memory: "1024Mi"
# The above example requests/limits can also be added to the mon and osd components
    mon:
# osd内存配置每个至少2G
    osd:
#    prepareosd:
#    crashcollector:
  # The option to automatically remove OSDs that are out and are safe to destroy.
  removeOSDsIfOutAndSafeToRemove: false
#  priorityClassNames:
#    all: rook-ceph-default-priority-class
#    mon: rook-ceph-mon-priority-class
#    osd: rook-ceph-osd-priority-class
#    mgr: rook-ceph-mgr-priority-class
  storage: # cluster level storage configuration and selection
    useAllNodes: false
    useAllDevices: false
    #deviceFilter:
    config:
       storeType: bluestore
       metadataDevice: "md0" # 修改为ssd盘符
      # databaseSizeMB: "1024" # uncomment if the disks are smaller than 100 GB
      # journalSizeMB: "1024"  # uncomment if the disks are 20 GB or smaller
       osdsPerDevice: "1" # this value can be overridden at the node or device level
      # encryptedDevice: "true" # the default value for this option is "false"
# Cluster level list of directories to use for filestore-based OSD storage. If uncomment, this example would create an OSD under the dataDirHostPath.
    #directories:
    #- path: /var/lib/rook
# 此处修改存储节点相关信息及磁盘配置
    nodes:
    - name: "172.17.4.201"
      devices: 
      - name: "sdb" # 裸设备盘符,多个设备罗列
      - name: "nvme01" # 性能较好的磁盘,单个设备需要多个osd
        config:
          osdsPerDevice: "5"
      config: # 此处配置会覆盖上面的全局配置,需与上保持一致,或针对节点定制
        storeType: bluestore
        metadataDevice: "md0" # 修改为ssd盘符
#    - name: "172.17.4.301"
#      deviceFilter: "^sd."
  disruptionManagement:
    managePodBudgets: false
    osdMaintenanceTimeout: 30
    manageMachineDisruptionBudgets: false
    machineDisruptionBudgetNamespace: openshift-machine-api
```

> 注意：资源配置参照https://docs.ceph.com/docs/master/start/hardware-recommendations/

#### 执行安装

```shell
cd rook/cluster/examples/kubernetes/ceph
# create the common resources
kubectl create -f common.yaml
# create the Operator deployment
kubectl create -f operator.yaml
# create Ceph storage cluster
kubectl create -f cluster.yaml
```

#### 创建 toolbox

```shell
kubectl create -f toolbox.yaml
```

#### 创建 dashboard

```shell
# 按需求选择
kubectl create -f [dashboard-external-http.yaml | dashboard-external-https.yaml | dashboard-ingress-https.yaml | dashboard-loadbalancer.yaml]
```

#### 创建块存储

*Kubernetes 使用*

```shell
# 根据需求修改pool name、RBD image format、RBD image features等
kubectl create -f csi/rbd/storageclass.yaml
# 创建pvc
kubectl create -f csi/rbd/pvc.yaml
```

*非 Kubernetes 使用*

```shell
# 根据需求修改pool name，pg、pgp可后续通过toolbox手动调整
kubectl create -f pool.yaml
# img通过toolbox手动创建
```

#### 创建文件系统

*Kubernetes 使用*

```shell
# 根据需求修改fs name、调度亲和及mds资源分配
kubectl create -f filesystem.yaml
kubectl create -f csi/cephfs/storageclass.yaml
kubectl create -f csi/cephfs/pvc.yaml
```

*非 Kubernetes 使用*

```shell
# 根据需求修改fs name、调度亲和及mds资源分配
kubectl create -f filesystem.yaml
```

### Cleaning up a Cluster

*Delete the Block and File artifacts*

```shell
kubectl delete -f ../wordpress.yaml
kubectl delete -f ../mysql.yaml
kubectl delete -n rook-ceph cephblockpool replicapool
kubectl delete storageclass rook-ceph-block
kubectl delete -f csi/cephfs/kube-registry.yaml
kubectl delete storageclass csi-cephfs
```

*Delete the CephCluster CRD*

```shell
kubectl -n rook-ceph delete cephcluster rook-ceph
```

*Delete the Operator and related Resources*

```shell
kubectl delete -f operator.yaml
kubectl delete -f common.yaml
```

*Delete the data on hosts*

```shell
#!/usr/bin/env bash
DISK="/dev/sdb"
# Zap the disk to a fresh, usable state (zap-all is important, b/c MBR has to be clean)
# You will have to run this step for all disks.
sgdisk --zap-all $DISK

# These steps only have to be run once on each node
# If rook sets up osds using ceph-volume, teardown leaves some devices mapped that lock the disks.
ls /dev/mapper/ceph-* | xargs -I% -- dmsetup remove %
# ceph-volume setup can leave ceph-<UUID> directories in /dev (unnecessary clutter)
rm -rf /dev/ceph-*
```

*clean up `dataDirHostPath`*

```shell
rm -rf /var/lib/rook
```
## 参考资料

[官方文档](https://rook.github.io/docs/rook/v1.2/)