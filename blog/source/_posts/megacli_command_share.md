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
进行存储开发时需要创建磁盘阵列，本文主要记录 RAID 卡管理工具`MegaCli`的使用。需要注意的是，目前该管理工具因为商业收购已经被官方“弃坑”，`StorCLI`作为后继者整合了`LSI`和原来`3ware`的产品支持，兼容`MegaCLI`命令的同时更加简洁，参阅[此篇](https://imoyao.github.io/blog/2017-12-27/storcli_command_share/)。
<!--more-->

## 巡读

```shell
#立即激活
MegaCli -adppr -enblauto -a0
#设置成手动模式，需要用MegaCli -adppr -start –a0 来激活
MegaCli -adppr -enblman -a0
#查看巡读的模式，本次巡读结束与下一次开始巡读的间隔，当前状态等信息
MegaCli -adppr -info -a0
#查看巡读的进度
MegaCli -fwtermlog -dsply -a0
#结束巡读，在巡读过程中，多次运用MegaCli -adppr -stop -a0或MegaCli -adppr -start -a0会使叠代数增加，此时可能不能开始或结束巡读，用MegaCli -adppr -dsbl -a0来禁止巡读，重新开始。
MegaCli -adppr -stop -a0
#设置本次巡读结束与下一次巡读开始的时间间隔，默认是168小时，当val=0时, 本次巡读结束后，立即开始下一次巡读
MegaCli -adppr -setdelay val -a0
#巡读时是否纠正媒介错误
MegaCli -AdpSetProp -PrCorrectUncfgdAreas -val -a0
#设置定时巡读 yyyymmdd hh，具体含义如下：20120108 16表示2012年01月08日16点
MegaCli -AdpPR -SetStartTime yyyymmdd hh -a0
```

## cc校验

- 立即开始cc校验

```shell
#L0表示Target ID 为0的raid组
MegaCli -ldcc -start -L0 –a0
#如果没有完全初始化或后台初始化
#The virtual disk has not been initialized、 Running a consistency check may result in inconsistent messages in the log
#可以强行cc校验
MegaCli -ldcc -start -force –L0 –a0
#显示当前cc校验的进度
MegaCli -ldcc -progdsply -L0 -a0
#关掉当前的cc校验
MegaCli -ldcc -abort -L0 -a0
```

- 计划cc校验
如果模式为disable(MegaCli -adpccsched -info -a0来查看)，则下一次开始时间为07/28/2135, 02:00:00，状态为 Stopped，延期为168个小时;
只有模式为Sequential和Concurrent模式时，才可以设定定期时间，所以要首先设定模式;
如果模式为Sequential时，所有虚拟磁盘组顺序进行cc校验;
如果模式为Concurrent时，所有虚拟磁盘组同时进行cc校验;
```shell
#设定CC模式
MegaCli -adpccsched -modeconc -a0
#或者
MegaCli -adpccsched -modeseq -a0
#然后设定开始时间
MegaCli -adpccsched setstarttime 20101122 18 -a0
#设置本次cc校验结束和下次cc校验开始的时间间隔
MegaCli -adpccsched -setdelay 2 -a0
#禁止计划cc校验
MegaCli -AdpCcSched -dsbl -a0
#设置错误发生时放弃cc校验
MegaCli -adpsetprop -AbortCC -1 -a0
#查看cc校验的事件日志
MegaCli -AdpEventLog -GetCCIncon –f filename –L0 –a0
#如果设置延期时间为0，本次cc校验结束后，下一次cc校验会立即开始
```

## 快速初始化和完全初始化
快速初始化值是往raid组的前8M和后8M写0
```shell
#快速初始化
MegaCli -LDInit -start –L0 -a0
#完全初始化
MegaCli -LDInit -start -full –L0 -a0
#显示初始化的进度
MegaCli -LDInit -progdsply -L0 -a0
#结束完全初始化
MegaCli -LDInit -abort -L0 -a0
```

## 后台初始化
Raid5 需要5个数据盘才可以后台初始化(5个盘中不包含热备盘)
后台初始化是创建raid后5分钟开始的(好像有时不是这样的)
后台初始化和cc校验不同的地方是，后台初始化可以自动开始
改变后台初始化率时，需要停止后台初始化，否则没有效果
```shell
#禁止后台初始化
MegaCli -LDBI -dsbl -L0 -a0
#结束正在进行的后台初始化
MegaCli -LDBI -abort -L0 -a0
#查看后台初始化的设置
MegaCli -LDBI -getsetting -L0 -a0
#显示后台初始化进度
MegaCli -LDBI -progdsply -L0 -a0
```

## copyback

```shell
#开启或禁用copyback
MegaCli -AdpSetProp –CopyBackDsbl -0 -a0 (开启)
#显示copyback设置情况
MegaCli –AdpGetProp -CopyBackDsbl –a0
```
当设置copyback为enable时，拔出坏盘，换上一个UNCONF的新盘，先用热备盘进行重建，然后进行copyback操作，如果copyback为disable时，不进行copyback操作，可以设定copyback为enable，然后用MegaCli -PDCpyBk -Start -PhysDrv[E0:S0,E1:S1] –a0开始copyback操作，其中[E0：S0]是raid组中的磁盘(源盘)，而[E1：S1]不是raid组中的磁盘(目的盘)

当某个盘出现第一个smart错误时，可以在这个盘和热备盘之间进行copyback操作，热备盘作为目的盘，完成了copyback操作时，smart错误盘才标记为failed状态。
```shell
#如果在copyback时，raid组删除，目的盘回到热备盘状态或Unconfigured Good
MegaCli -AdpGetProp SMARTCpyBkEnbl -a0
```

## 日志
```shell
#查看所有的information日志
MegaCli -adpalilog -a0
#查看固件调试日志(固件终端日志)
MegaCli -fwtermlog -dsply -a0
#查看raid卡日志
MegaCli -adpeventlog -getevents -f filename -a0
#清除日志
MegaCli -AdpEventLog -Clear –a0
```

## raid5扩容
```shell
#raid5的扩容
MegaCli -LDRecon -Start -r5 -Add -Physdrv[E0:S0] -L0 -a0
#查看扩容的进度
MegaCli -LDRecon -progdsply -L0 –a0
```

## 级别迁移
```shell
在迁移过程中，转换前的raid的一个盘下线，转换前raid的所有盘都下线
支持的类型 RAID 0 to RAID 1，RAID 0 to RAID 5，RAID 0 to RAID 6，RAID 1 to RAID 0，RAID 1 to RAID 5，RAID 1 to RAID 6，RAID 5 to RAID 0，RAID 5 to RAID 6，RAID 6 to RAID 0，RAID 6 to RAID 5
#建立了三个盘的raid 0
MegaCli -cfgldadd -r0[117:1,117:3,117:11] -a0
#增加一个盘[117:14],转换到raid5
MegaCli -ldrecon -start -r5 -add -physdrv[117:14] -l0 -a0
```

## 升级ROM
```shell
#从低版本到高版本升级
MegaCli -adpfwflash -f x.rom -a0
#从高版本到低版本降级
#加上noverchk忽略版本的检查，升级以后需要重启才生效
MegaCli -adpfwflash -f x.rom -noverchk -a0
```

## 连接方式

Raid对内有两个接口，即connector0和connector1。得到连接器的状态;
 MegaCli -adpgetconnectormode -connector0 -a0 
如果连接器的模式为internal时，jbod的磁盘全部看不到，如果连接器的模式为external时，主柜上的磁盘全部看不到;

## 外来配置
```shell
#扫描外来配置的个数
MegaCli -cfgforeign -scan -a0
#查看当前的磁盘在normal时的位置
MegaCli -cfgforeign -preview -a0
#来导入配置，恢复虚拟磁盘组
MegaCli -cfgforeign -import -a0
#清除外来配置
MegaCli -cfgforeign -clear -a0
#显示出现外来配置(磁盘插入的顺序)的过程
MegaCli -cfgforeign -dsply -a0
```

## 物理磁盘的处理
```shell
#磁盘的状态由FAULTY变成CONF
MegaCli -PDMakeGood -PhysDrv[E0:S0] –a0
#磁盘上线
MegaCli -PDOnline -PhysDrv[E0:S0,E1:S1,...] –a0
#磁盘下线
#failed状态的盘可以下线，然后用MegaCli -pdmarkmissing -physdrv[E0:S0] -a0让磁盘踢盘，让其他的UNCONF状态的磁盘来替代这个盘MegaCli -PdReplaceMissing -physdrv[E0:S0] -arrayA, -rowB -a0
MegaCli -PDOffline -PhysDrv[E0:S0,E1:S1,...] –a0 
#此时磁盘处于Spun down状态，如果用此磁盘来建立raid，则磁盘的状态自动变成Spun Up
MegaCli -PdPrpRmv -physdrv[E0:S0] –a0
#清除单个磁盘
MegaCli -pdclear -start -physdrv[E:S] -a0
#设置热备盘的节电策略
MegaCli -AdpSetProp –DsblSpinDownHSP -val –a0
#设置空闲盘的节电策略
MegaCli -AdpSetProp –EnblSpinDownUnConfigDrvs -val –a0
#获取所有磁盘的详细信息
MegaCli -PDList –a0
#获取单个盘的详细信息
MegaCli -pdInfo -PhysDrv[E0:S0] –a0
```

## Adpsetprop设置属性
```shell
RebuildRate ，PatrolReadRate，BgiRate，CCRate，ReconRate，表示进行重建，巡读，后台初始化，cc校验，扩容等所占有的系统资源率，提高速度
CoercionMode(强制模式)，分成三种形式，None，128M，1G，当为1G时，每个磁盘比没有设置的时减少了1G的空间;
PredFailPollInterval，轮询预测失败的时间间隔。Predictive Failure Count就是smart错误;
MaintainPdFailHistoryEnbl 保存坏盘的历史记录。当为enable时，当一个盘掉线并重新上线。需要清除配置信息，添加为热备盘才可以重建当为disable时。当一个盘掉线并重新上线，自动重建;
#设置Cluster模式，目前不支持，只能设置为disbale
MegaCli -AdpSetProp ClusterEnable -0 -a0
#设置jbod模式，针对raid0有效，对单个盘读写，即先写第一个盘，写满了在写第二个盘。MegaCli -PDMakeJBOD -physdrv[E0:S0,E1:S1] -a0 可以设置jbod模式(目前不支持)
MegaCli -AdpSetProp -EnableJBOD -1 -a0
#让设备驱动暴露enclosure devices
MegaCli -AdpSetProp ExposeEnclDevicesEnbl -1 -a0
```

## NCQ

Native Command Queuing (NCQ)对硬盘的读写命令的顺序进行优化。带NCQ技术的硬盘在接到读写指令后，会根据指令对访问地址进行重新排序。比如根据指令，硬盘需要访问330扇区、980扇区、340扇区，由于数据在磁盘上分布位置不同，普通硬盘只会按部就班地依次访问。而NCQ硬盘对指令进行优化排列之后，就可以先读取330扇区，接着读取340扇区，然后再读取980扇区。这样做的好处就是减少了磁头臂来回移动的时间，使数据读取更有效，同时有效地延长了硬盘的使用寿命。
```shell
#显示NCQ的设置情况
MegaCli -adpgetprop -NCQdsply -a0
#设置开启NCQ
MegaCli -adpsetprop -NCQenbl -a0
#关闭NCQ
MegaCli -adpsetprop -NCQdsbl -a0
```

## 添加和移除热备盘
```shell
#添加局部热备盘，其中array0表示第0个raid
MegaCli -PDHSP -Set -Dedicated -Array0 -physdrv[E:S] -a0
#添加全局热备盘
MegaCli -pdhsp -set -physdrv[E:S] -a0
#移除全局和热备局部热备
MegaCli -pdhsp -rmv -physdrv[E:S] -a0
```

## 重建
```shell
#查看重建的进度
MegaCli -PDRbld -progdsply -physdrv[E:S] -a0
#调快重建的速度
MegaCli -AdpSetProp RebuildRate -val -a0
#设置自动重建，当一个盘坏掉时，热备盘可以自动重建，代替坏的盘
MegaCli -AdpAutoRbld -Enbl -a0
#手动开始重建，E0:S0表示坏的盘
MegaCli -PDRbld -Start -PhysDrv [E0:S0] -a0
```

## 恢复出厂设置
```shell
#恢复出厂的默认配置
MegaCli -AdpFacDefSet –a0
```

## 告警
```shell
#临时关闭，重启又变成开启
MegaCli -AdpSetProp -AlarmSilence –a0
#永久关闭，重启后还是关闭
MegaCli -AdpSetProp -AlarmDsbl –a0
#开启
MegaCli -AdpSetProp -Alarmenbl –a0
#查看告警的状态
MegaCli -AdpgetProp -Alarmdsply –a0
```

## 配置相关
```shell
#可以查看一组磁盘上的多个raid的配置
MegaCli -CfgDsply -a0
#保存配置文件
MegaCli -CfgSave -f filename -a0
#导入配置文件，Raid组的配置文件放在最后，放在每个磁盘的最后512M，主要包含数据从哪里开始写的配置和用来Migration 的swap文件
MegaCli -CfgRestore -f filename -a0
#启动时恢复外来配置
MegaCli -AdpSetProp -AutoEnhancedImportEnbl -a0
#验证配置文件和文件的内容
MegaCli -AdpSetVerify -f fileName -a0
```

## RAID卡相关
```shell
#查看raid的配置信息
MegaCli -adpallinfo -a0
#关闭raid卡
MegaCli -adpShutDown -a0
#获取raid的时间
MegaCli -adpGetTime -a0
#对raid进行诊断
MegaCli -AdpDiag val -a0
#设置负载均衡，Raid卡对终端设备采用多路径访问，一半的设备通过一条路径，另一半的设备通过另一条路径，一条途径有盘插入和移除时，启动负载平衡，避免设备有重用
MegaCli -AdpSetProp –LoadBalanceMode -val –a0
#获取raid卡的个数
MegaCli –adpCount
#获取pci信息
MegaCli -AdpGetPciInfo -a0
#Raid卡的在线重置，fw重置raid卡控制器芯片
MegaCli -AdpSetProp DisableOCR -val -a0
#显示raid卡，系统等的一些简单信息
MegaCli -ShowSummary -f filename -a0
#显示每个phy的错误数
MegaCli -PhyErrorCounters -a0
```

## Enclosure的信息
```shell
#查看机柜的相关信息
MegaCli -encinfo -a0
#查看机柜的状态
MegaCli -encstatus -a0
```

## BIOS相关
```shell
#在启动时要按任意键才可以启动这种情况设置这个参数。但是首先要确保 bios 处于 enable 状态。通过 MegaCli -AdpBIOS -dsply -a0可以查看。如果不是，先用MegaCli -AdpBIOS -enbl -a0来设置
MegaCli –AdpBIOS –BE –a0
#把当前的Raid组作为启动
MegaCli –AdpBootDrive -set -L0 -a0
```

## 背板相关
```shell
#如果背板 disable 时，会自动的去检测背板
MegaCli -AdpSetProp -AutoDetectBackPlaneDsbl -val –a0
```

## 启动时上电
```shell
#设置一次上电的磁盘的个数
MegaCli -AdpSetProp SpinupDriveCount -val -a0
#设置上电的延迟时间
MegaCli -AdpSetProp SpinupDelay -val -a0
```

## 刷新缓存

```shell
#刷新raid卡缓存
MegaCli -AdpCacheFlush –a0
#刷缓存的时间间隔
MegaCli -AdpSetProp CacheFlushInterval –val –a0
```

## 让硬盘LED灯闪烁

```shell
#开启blink
MegaCli -AdpSetProp UseDiskActivityforLocate -1 -a0
#让硬盘LED灯闪烁
MegaCli -PdLocate -start –physdrv[E:S] -a0
#停掉硬盘LED灯
MegaCli -PdLocate -stopt –physdrv[E:S] -a0
```

## 电池告警

```shell
MegaCli -AdpSetProp BatWarnDsbl -val -a0
```

## 纠错码相关

```shell
#设置纠错码漏桶的字节数
MegaCli -AdpSetProp EccBucketSize -val -a0
```
## 后台初始化，完全初始化，cc校验，巡读等之间的关系

后台初始化和完全初始化，cc校验时不能进行巡读;
巡读时可以后台初始化和完全初始化，此时巡读结束;;
在后台初始化和cc校验时，不能开始完全初始化;
扩容时不能建raid，不能添加热备盘;
rebuild的优先级高于copyback;

## RAID 的创建与删除
- 创建raid 0，1，5，6

```shell
#MegaCli -CfgLdAdd -rX[E0:S0,E1:S1,...] [WT|WB] [NORA|RA|ADRA] [Direct|Cached] [CachedBadBBU|NoCachedBadBBU] [-szXXX [-szYYY ...]] [-strpszM] [-Hsp[E0:S0,...]] [-AfterLdX] [-Force]|[FDE|CtrlBased] -a0 可以设置写模式(wt，wb)，读模式(ra，nora，adra)，缓存模式(direct，cached)，大小(sz)，条块大小(strpszM)等。比如1000G，只用指定盘的一部分(sz1000G)，设置条块的大小strpsz(设置为16k，则为strpsz16)
MegaCli -cfgldadd -r5[117:1,117:3,117:11] -wb -ra -cached -cachedbadbbu -force -a0
```

- 创建raid 10，50，60

```shell
#MegaCli -CfgSpanAdd -rX-Array0[E0:S0,E1:S1] -Array1[E0:S0,E1:S1] [-ArrayX[E0:S0,E1:S1] ...] [WT|WB] [NORA|RA|ADRA] [Direct|Cached] [CachedBadBBU| NoCachedBadBBU] [-szXXX[-szYYY ...]][-strpszM][-AfterLdX][-Force] |[FDE|CtrlBased] -aN
MegaCli -CfgSpanAdd -r10 -Array0[245:0,245:1] Array1[245:2,245:3] -WB -RA -Cached -Cachedbadbbu -a0
```
- 批量创建raid0

```shell
#把每个槽位的磁盘都创建为只有一个盘的raid0
MegaCli -CfgEachDskRaid0 -wb -ra -cached -cachedbadbbu -a0
#把所有的空闲盘都加入到raid中
MegaCli -CfgAllFreeDrv -r5 -SATAOnly -wb -ra -cached -cachedbadbbu -a0
```

- 删除raid组

```shell
#清除所有的raid组的配置
MegaCli -cfgclr -a0
#删除指定的raid组(Target Id: 0)的raid组
MegaCli -cfglddel -L0 -a0
```

## 设置RAID组的属性

```shell
#设置raid组的名字
MegaCli -ldsetprop -name dg -L0 -a0
#设置访问策略为读写，MegaCli -ldsetprop -blocked -L0 -a0设置访问策略为阻塞，此时raid组的设备不可以访问，fdisk -l不能发现设备
MegaCli -ldsetprop -rw -L0 -a0
#设置写策略为wt(直写)，直接写入到硬盘上，然后再返回。wb模式是写入到缓存中就返回，设置wb模式写速度有显著的改善，提高到12倍
MegaCli -ldsetprop -wt -L0 -a0
#设置读策略为ra(预先读出一定的数据)，还有nora模式，ra模式读可以提高到2倍左右
MegaCli -ldsetprop -ra -L0 -a0 
#设置缓存策略为cached
MegaCli -ldsetprop -cached -L0 -a0
#开启磁盘的缓存，对写速度有一定的提高(1.4倍)
MegaCli -ldsetprop -endskcache -L0 -a0
```
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

|代码|含义|
|:------|:--------------|
|WT    | (Write through)|
|WB    |(Write back)|
|NORA  |(No read ahead) |
|RA    |(Read ahead) |
|ADRA  |(Adaptive read ahead) |
|Cached|-    |
|Direct|-    |

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

## Unsolved
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

- [官方资源下载-broadcom](https://www.broadcom.com/site-search?q=megacli)
- [Dell – PERC/LSI MegaCLI – How to install](https://techedemic.com/2014/08/07/dell-perclsi-megacli-how-to-install/)
- [LSIMegaRAIDSAS](https://hwraid.le-vert.net/wiki/LSIMegaRAIDSAS#a3.1.megactl)
- [DELL磁盘阵列控制卡（RAID卡）MegaCli常用管理命令汇总](http://zh.community.dell.com/techcenter/b/weblog/archive/2013/03/07/megacli-command-share)
- [MegaCli命令总结 - CSDN博客](http://blog.csdn.net/heart_2011/article/details/7254404)
- [Linux下查看Raid磁盘阵列信息的方法](http://www.ha97.com/4073.html)
- [Megacli 常用命令](http://www.mamicode.com/info-detail-860128.html)
  