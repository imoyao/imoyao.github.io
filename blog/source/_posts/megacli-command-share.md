---
title: 磁盘阵列控制卡（RAID卡）MegaCli常用管理命令汇总
date: 2017-11-20 15:02:45
tags:
- RAID
- Linux
- MegaCli
- 存储
categories:
- 教程记录
---
在进行存储相关开发时肯定要创建磁盘阵列，本文主要记录 RAID 卡管理工具`MegaCli`的使用。
<!--more-->
## 查询篇

- 显示BBU状态信息    
```shell
MegaCli -AdpBbuCmd -GetBbuStatus –aALL 
``` 
- 显示BBU容量信息    
```shell
MegaCli -AdpBbuCmd -GetBbuCapacityInfo –aALL 
```
- 显示BBU设计参数    
```shell
MegaCli -AdpBbuCmd -GetBbuDesignInfo –aALL
```
- 显示当前BBU属性   
```shell
MegaCli -AdpBbuCmd -GetBbuProperties –aALL 
```
- 查看充电状态    
```shell
MegaCli -AdpBbuCmd -GetBbuStatus -aALL |grep "Charger Status" 
```
- 查看充电进度百分比     
```shell
MegaCli -AdpBbuCmd -GetBbuStatus -aALL |grep "Relative State of Charge"
```
- 查看所有物理磁盘信息     
```shell
MegaCli -PDList -aALL
```
- 显示所有逻辑磁盘组信息     
```shell
MegaCli -LDInfo -LALL –aAll
```
- 查看物理磁盘重建进度(重要)
```shell
MegaCli -PDRbld -ShowProg -PhysDrv [1:5] -a0 
```
- 查看适配器个数    
```shell
MegaCli –adpCount 
```
- 查看适配器时间     
```shell
MegaCli -AdpGetTime –aALL
```
- 显示所有适配器信息    
```shell
MegaCli -AdpAllInfo –aAll 
```
<br>

- 显示RAID卡型号，RAID设置，Disk相关信息      
```shell
MegaCli -cfgdsply –aALL 
```
- 查询RAID阵列个数    
```shell
MegaCli -cfgdsply -aALL |grep "Number of DISK GROUPS:"
``` 
- 查看Cache 策略设置    
```shell
MegaCli -cfgdsply -aALL |grep Polic
```
- 查看磁盘缓存策略 
```shell
# L---->[VD num or ALL] a---->[Adapter num or ALL]
MegaCli -LDGetProp -Cache -L0 -a0
# or 
MegaCli -LDGetProp -DskCache -LALL -aALL
```
- 查看物理磁盘重建进度
```shell 
MegaCli -PDRbld -ShowProg -PhysDrv [1:5] -a0
```
- 查看Megacli的log
```shell
MegaCli -FwTermLog dsply -a0 > adp2.log
```
## 设置篇

### 创建/删除阵列
```shell
# 创建一个 RAID5 阵列，由物理盘 2,3,4 构成，该阵列的热备盘是物理盘 5 
MegaCli -CfgLdAdd -r5 [1:2,1:3,1:4] WB Direct -Hsp[1:5] –a0 
# 创建阵列，不指定热备 
MegaCli -CfgLdAdd -r5 [1:2,1:3,1:4] WB Direct –a0 
# 删除阵列 
MegaCli -CfgLdDel -L1 –a0 
# 在线添加磁盘 
# 重建逻辑磁盘组 1 , RAID 级别是5，添加物理磁盘号 1:4。
MegaCli -LDRecon -Start -r5 -Add -PhysDrv[1:4] -L1 -a0 
```

**注：**重建完后，新添加的物理磁盘会自动处于重建(同步)状态，这个时候 `fdisk -l`是看不到阵列的空间变大的，只有在系统重启后才能看见。 

### 查看阵列初始化信息 

- 阵列创建完后，会有一个初始化同步块的过程，可以查看其进度。 
```shell
MegaCli -LDInit -ShowProg -LALL -aALL 
# or 以动态可视化文字界面显示 
MegaCli -LDInit -ProgDsply -LALL –aALL 
```
- 查看阵列后台初始化进度
```shell
MegaCli -LDBI -ShowProg -LALL -aALL 
# or 以动态可视化文字界面显示 
MegaCli -LDBI -ProgDsply -LALL -aALL 
```
### 设置磁盘缓存策略 

缓存策略解释：
代码|含义
---|---
WT|(Write through)
WB|(Write back)
NORA|(No read ahead) 
RA|(Read ahead) 
ADRA|(Adaptive read ahead) 
Cached|-- 
Direct|-- 
eg：
```shell
MegaCli -LDSetProp WT|WB|NORA|RA|ADRA -L0 -a0 
# or 
MegaCli -LDSetProp -Cached|-Direct -L0 -a0 
# or 
- enable / disable disk cache 
MegaCli -LDSetProp -EnDskCache|-DisDskCache -L0 -a0
```
### 热备管理

- 创建热备 
```shell
# [1:5]---->[E:S]

# 指定第 5 块盘作为全局热备
MegaCli -PDHSP -Set [-EnclAffinity] [-nonRevertible] -PhysDrv[1:5] -a0 
# eg：
MegaCli -PDHSP   -Set   -Dedicated  -Array0  -physdrv[E:S] -a0
# 为某个阵列指定专用热备 
MegaCli -PDHSP -Set [-Dedicated [-Array1]] [-EnclAffinity] [-nonRevertible] -PhysDrv[1:5] -a0 
```
- 删除热备
```shell
MegaCli -PDHSP -rmv -PhysDrv[1:5] -a0 
```
- 将某块物理盘下线/上线 
```shell
# 下线
MegaCli -PDOffline -PhysDrv [1:4] -a0 
# 上线
MegaCli -PDOnline -PhysDrv [1:4] -a0 
```

**注：**如果直接删除RAID而不操作热备，其局部热备会变为全局热备，而不是删除。


## 管理篇

- 点亮指定硬盘（定位）
```shell
MegaCli -PdLocate -start -physdrv[252:2] -a0
```
- 查看RAID阵列中掉线的盘
```shell
MegaCli -pdgetmissing -a0
```
- 替换坏掉的模块
```shell
MegaCli -pdreplacemissing -physdrv[12:10] -Array5 -row0 -a0
```
- 手动开启rebuid
```shell
MegaCli -pdrbld -start -physdrv[12:10] -a0
```
- 查看Megacli的log
```shell
MegaCli -FwTermLog dsply -a0 > adp2.log
```
- 关闭Rebuild
```shell
MegaCli -AdpAutoRbld -Dsbl -a0
```
- 设置rebuild的速率
```shell
MegaCli -AdpSetProp RebuildRate -30 -a0
```

### foreign 管理

创建 RAID 前, 需要检测是否具有`foreign`配置, 如果有但此时不需要保留 RAID 时需要清除 RAID 的 `foreign`状态。

- 检测是否具有 `foreign` 配置
```shell
MegaCli -PDlist -aALL | grep "Foreign State"  
```
- 将标注为 `Foreign` 磁盘标注为`unconfigrue good`
```shell
MegaCli -PDMakeGood -PhysDrv[32:5] -a0  
```
- 清除 `foreign` 配置
```shell
MegaCli -CfgForeign -Scan -a0  
```
**注**：一般以上两条都要执行才能清除 `foreign` 状态

## 其他

磁盘状态 State 
```shell
("Failed", "Online, Spun Up", "Online, Spun Down", "Unconfigured(bad)", "Unconfigured(good), Spun down", "Hotspare, Spun down", "Hotspare, Spun up" or "not Online")
```

## Unsolve
- 扩展 RAID（加盘）
```shell
MegaCli -LDRecon -Start -r1 -Add -PhysDrv[252:1] -L1 -a0                                     
# 报错
Failed to Start Reconstruction of Virtual Drive.

FW error description: 
 The requested command has invalid arguments.  

Exit Code: 0x03
```
[参见这里1](http://en.community.dell.com/support-forums/servers/f/956/t/19531272)

## 参考资料
1. [DELL磁盘阵列控制卡（RAID卡）MegaCli常用管理命令汇总](http://zh.community.dell.com/techcenter/b/weblog/archive/2013/03/07/megacli-command-share)
2. [Linux下查看Raid磁盘阵列信息的方法](http://www.ha97.com/4073.html)
3. [Megacli 常用命令](http://www.mamicode.com/info-detail-860128.html)
  