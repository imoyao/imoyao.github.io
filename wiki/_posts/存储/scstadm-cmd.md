---
title: scstadmin 命令汇总
toc: true
date: 2019-05-26 12:27:56
tags: 
- SCST
- 存储
---

1> iscsi-scst 基本配置
1.1>创建
scstadmin -add_target iqn.2015:storage.vdisk1 -driver iscsi //创建 target
scstadmin -add_group ESX -driver iscsi -target iqn.2015:storage.vdisk1 //添加主机组
scstadmin -open_dev disk01 -handler vdisk_blockio -attributes filename=/dev/VolGroup00/lv_01 // 建立虚拟磁盘与后端磁盘映射
scstadmin -add_lun 0 -driver iscsi -target iqn.2015:storage.vdisk1 -device disk01            //虚拟磁盘添加至主机组
scstadmin -add_init iqn.2015:vcenterserver  -driver iscsi -target  iqn.2015:storage.vdisk1 -group ESX // 添加客户端到主机组
scstadmin -enable_target iqn.2015:storage.vdisk1 -driver iscsi  //使能 target
scstadmin -set_drv_attr iscsi -attributes enabled=1 //使能虚拟磁盘属性设置
scstadmin -set_tgt_attr iqn.2015:storage.vdisk1 -driver iscsi -attributes allowed_portal=10.10.10.184 //建立 target 与网卡映射关系，通过多次执行此命令实现多路径存储端支持；
scstadmin -write_config /etc/scst.conf  //保存配置文件


1.2>修改/删除
scstadmin -close_dev disk01 -handler vdisk_blockio  //删除虚拟磁盘与后端磁盘的映射
scstadmin -rem_target iqn.2015:storage.vdisk1 -driver iscsi  //删除 target
scstadmin -rem_group ESX -driver iscsi -target iqn.2015:storage.vdisk1  //删除主机组
scstadmin -rem_init iqn.2015:vcenterserver -driver iscsi -target iqn.2015:storage.vdisk1 -group ESX  //删除主机组中指定客户端
scstadmin -clear_init -driver iscsi -target iqn.2015:storage.vdisk1 -group ESX  //删除组中的所有客户端
scstadmin -rem_lun 0 -driver iscsi -target iqn.2015:storage.vdisk1           //虚拟磁盘删除从指定主机组
scstadmin -disable_target iqn.2015:storage.vdisk1 -driver iscsi  //停止 target
scstadmin -clear_config -force //清理配置文件

1.3> 查看信息
scstadmin -list_device  //查看所有虚拟块设备
scstadmin -list_target  //查看所有 taget
scstadmin -list_tgt_attr iqn.2015:storage.vdisk1 -driver iscsi  //查看指定 target 属性
scstadmin -list_sessions  //查看 target 与 init 之间的会话信息

2> fc-target 基本配置

scstadmin -add_group ESX -driver qla2x00t -target 21:00:00:24:ff:5c:aa:15  //target 添加组
scstadmin -open_dev disk01 -handler vdisk_blockio -attributes filename=/dev/vg_raid5/thin_scst  //建立虚拟磁盘与物理盘的映射关系
scstadmin -add_lun 0 -driver qla2x00t -target 21:00:00:24:ff:5c:aa:14 -device disk01  //添加虚拟磁盘到 target
scstadmin -enable_target 21:00:00:24:ff:5c:aa:15 -driver qla2x00t  //使能 target
其他配置与 iscsi 都是类似的；只是 FC 采用 WWN 号标识 target 和 init；

单控 fc 配置
scstadmin -open_dev disk01 -handler vdisk_fileio -attributes filename=/dev/sdb
scstadmin -add_lun 0 -driver qla2x00t -target 21:00:00:24:ff:91:8e:8a -device disk01
scstadmin -add_group group1 -driver qla2x00t -target 21:00:00:24:ff:91:8e:8a
scstadmin -enable_target 21:00:00:24:ff:91:8e:8a -driver qla2x00t
scstadmin -write_conf /etc/scst.conf

双控 fc 配置
scstadmin -open_dev t11_l10_6142 -handler vdisk_fileio -attributes filename=/dev/StorPool11/SANLun10 -no_lip
scstadmin -add_lun 0 -driver qla2x00t -target 21:00:00:24:ff:91:8e:8a -device t11_l10_6142 -no_lip 
scstadmin -add_group group1 -driver qla2x00t -target 21:00:00:24:ff:91:8e:8a -no_lip 
scstadmin -enable_target 21:00:00:24:ff:91:8e:8a -driver qla2x00t
scstadmin -write_conf /etc/scst.conf

重新连接服务器端：echo 1 >> /sys/class/fc_hsot/host1/issue_lip

scstadmin -add_lun 6 -driver qla2x00t -target 21:00:00:24:ff:3d:be:21 -device sdg_1111
scstadmin -add_lun 6 -driver qla2x00t -target 21:00:00:24:ff:3d:be:20 -device sdg_1111
scstadmin -add_lun 6 -driver qla2x00t -target 21:00:00:24:ff:34:9b:bd -device sdg_1111
scstadmin -add_lun 6 -driver qla2x00t -target 21:00:00:24:ff:34:9b:bc -device sdg_1111

multipath -F 关闭多路径（也就是关闭聚合）
multipath -v3 生成多路径（聚合）
multipath -ll 查看多路径
如果有多路径的话，最好聚合，使用聚合后的盘；


iscsiadmin 的命令汇总

1、查看 iscsi 的存储：iscsiadm -m discovery -t st -p ISCSI_IP
2、查看 iscsi 发现记录：iscsiadm -m node
3、删除 iscsi 发现记录：iscsiadm -m node -o delete -T LUN_NAME -p ISCSI_IP
4、登陆 iscsi 存储：iscsiadm -m node -T LUN_NAME -p ISCSI_IP -l
5、登出 iscsi 存储：iscsiadm -m node -T LUN_NAME -p ISCSI_IP -u
6、显示会话情况：iscsiadm -m session