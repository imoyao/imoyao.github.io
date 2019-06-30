---
title: Storcli 常用管理命令汇总
date: 2017-12-27 11:38:45
tags:
- RAID
- Linux
- Storcli
- 存储
categories:
- 教程记录
---
目前`LSI RAID`卡使用的配置工具主要有：`Megaraid Storage Manager`（MSM，图形环境）、`MegaCLI`（字符界面）、`StorCLI`（字符界面）。其中`StorCLI`作为`MegaCLI`后继者整合了`LSI`和原来`3ware`的产品支持，兼容`MegaCLI`命令的同时更加简洁。[前面的文章](https://imoyao.github.io/blog/2017-11-20/megacli_command_share/)记录了`MegaCli`常用管理命令，本篇主要记录`StorCLI`的使用。

<!--more-->

## 安装`Storcli`

### Ubuntu

```shell
unzip ul_avago_storcli_1.18.11_anyos.zip
dpkg -i storcli_all_os/Ubuntu/storcli_1.18.11_all.deb
dpkg -l | grep -i storcli
```
### Centos

```shell
unzip ul_avago_storcli_1.18.11_anyos.zip
rpm -ivh storcli_all_os/Linux/storcli-1.18.11-1.noarch.rpm
rpm -qi storcli
ln -s /opt/MegaRAID/storcli/storcli64 /usr/local/bin/storcli
```

### ESXi 5.5 & ESXi 6.0

```shell
unzip ul_avago_storcli_1.18.11_anyos.zip
esxcli software vib install -v=vmware-esx-storcli-1.21.06.vib --no-sig-check
ln -s /opt/lsi/storcli/storcli /sbin/storcli
storcli -V
```
## `storcli`使用

专有名词解释：

`/cx, /vx` 表示 `Controller/Virtual Drive Number`.

`/ex, /sx`表示 `Enclosure/Slot ID`.

`VD`表示 `Virtual Drive`.

要输出`json`格式的返回,在命令行最后添加`J`.


- 固件升级

```shell
storcli /cx download file=/path/to/firmware.rom
```

- 查看控制器和配置信息

```shell
storcli /cx show all
```
- 使用激活码激活特性(如 CacheCade, FastPath,...)

```shell
storcli /cx set aso key=AAAAAAAABBBBBBBBCCCCCCCC
```
- 查看现有硬盘及其状态的信息 (IDs,...)

```shell
storcli /cx /eall /sall show (all)
```

返回结果

```shell
Controller = 0
Status = Success
Description = Show Drive Information Succeeded.

Drive Information :
=================
-----------------------------------------------------------------------------
EID:Slt DID State DG     Size Intf Med SED PI SeSz Model                  Sp
-----------------------------------------------------------------------------
252:0     1 Onln   1 3.637 TB SATA HDD N   N  512B WDC WD4000FYYZ-03UL1B3 U
252:1     3 Onln   1 3.637 TB SATA HDD N   N  512B WDC WD4000FYYZ-03UL1B3 U
......
252:6    85 Onln   0 3.637 TB SATA HDD N   N  512B WDC WD4000FYYZ-03UL1B3 U
252:7     2 UGood  - 3.637 TB SATA HDD N   N  512B WDC WD4000FYYZ-03UL1B3 D
-----------------------------------------------------------------------------


EID-Enclosure Device ID|Slt-Slot No.|DID-Device ID|DG-DriveGroup
DHS-Dedicated Hot Spare|UGood-Unconfigured Good|GHS-Global Hotspare
UBad-Unconfigured Bad|Onln-Online|Offln-Offline|Intf-Interface
Med-Media Type|SED-Self Encryptive Drive|PI-Protection Info
SeSz-Sector Size|Sp-Spun|U-Up|D-Down|T-Transition|F-Foreign
UGUnsp-Unsupported|UGShld-UnConfigured shielded|HSPShld-Hotspare shielded
CFShld-Configured shielded|Cpybck-CopyBack|CBShld-Copyback Shielded
```

- 现有虚拟硬盘及其状态的信息

```shell
storcli /cx /vall show (all)
```
- 查看当前所有重建的状态

```shell
storcli /cx /eall /sall show rebuild
```
## 创建/初始化 `raid`

- `shell`创建`VD`

```shell
storcli /cx add vd type=[RAID0(r0)|RAID1(r1)|...] drives=[EnclosureID:SlotID|:SlotID-SlotID|:SlotID,SlotID]
#more
storcli /cx add vd type=raid[0|1|5|6|00|10|50|60(r0|r1|...)] [Size=<VD1_Sz>,<VD2_Sz>,..|all] [name=<VDNAME1>,..] drives=e:s|e:s-x,y;e:s-x,y,z [PDperArray=x] [SED] [pdcache=on|off|default] [pi] [DimmerSwitch(ds)=default|automatic(auto)|none|maximum(max)|MaximumWithoutCaching(maxnocache)] [wt|wb] [nora|ra] [direct|cached] [CachedBadBBU|NoCachedBadBBU][cachevd] [Strip=<8|16|32|64|128|256|1024>] [AfterVd=X] [Spares = [e:]s|[e:]s-x|[e:]s-x,y] [force][ExclusiveAccess]
```
示例:

```shell
# 使用硬盘0-2创建raid1
storcli /cx add vd type=r1 drives=252:0-2
# 创建 raid5,write-bakc,read-ahead
storcli /cx add vd type=raid5  size=all names=VD1 drives=32:2-7 wb ra
# 创建 raid10/50/60,必须设定PDperArray参数,write-bakc,read-ahead
storcli /cx add vd type=raid10 size=all names=VD1 drives=32:2-7 PDperArray=2 wb ra
```
- `shell`之初始化`VD`

```plain
storcli /cx/vx start init (force)
```
- 监视初始化进度

```shell
storcli /cx/vx show init
```

- `shell`之移除`VD`

```shell
storcli /cx/vx del (force)
```

## 缓存加速

- `shell`之创建`CacheCade`设备（SSD 缓存加速）

```shell
storcli /cx add vd cc type=r[0,1,10] drives=[EnclosureID:SlotID|:SlotID-SlotID|:SlotID,SlotID]  WT|WB (assignvds=0,1,2)
```
示例:

```shell
storcli /c0 add vd cc type=r1 drives=252:2-3 WB
```
- `shell`之`CacheCade`激活/停用

```shell
storcli /cx/[vx|vall] set ssdCaching=[on|off]
```
示例:

```shell
storcli /c0/v1 set ssdCaching=on
```
- `shell`之移除`CacheCade`

```shell
storcli /cx/vx del cc
```

## 误插拔设备合并

如果不正确地移除设备并重新连接到 RAID 控制器，它将被识别为 UBAD(Unconfigured Bad)。

```shell
storcli /c0 /eall /sall show
```
此时的返回结果：

```shell
Controller = 0
Status = Success
Description = Show Drive Information Succeeded.

Drive Information :
=================

-------------------------------------------------------------------------------
EID:Slt DID State DG       Size Intf Med SED PI SeSz Model                  Sp 
-------------------------------------------------------------------------------
252:0     7 Onln   0  465.25 GB SATA HDD N   N  512B WDC WD5003ABYX-01WERA1 U  
252:1     6 Onln   1  465.25 GB SATA HDD N   N  512B WDC WD5003ABYX-01WERA1 U  
252:2     5 UGood  -  465.25 GB SATA HDD N   N  512B WDC WD5003ABYX-01WERA1 U  
252:3     4 UBad   - 223.062 GB SATA SSD N   N  512B INTEL SSDSC2CW240A3    U  
-------------------------------------------------------------------------------
......
```
此时`252:3`必需置为`UGOOD`

- `UBad`置为`UGOOD`

```shell
storcli /cx /ex /sx set good
```
返回结果

```shell
Controller = 0
Status = Success
Description = Show Drive Information Succeeded.

Drive Information :
=================
-------------------------------------------------------------------------------
EID:Slt DID State DG       Size Intf Med SED PI SeSz Model                  Sp 
-------------------------------------------------------------------------------
252:0     7 Onln   0  465.25 GB SATA HDD N   N  512B WDC WD5003ABYX-01WERA1 U  
252:1     6 Onln   1  465.25 GB SATA HDD N   N  512B WDC WD5003ABYX-01WERA1 U  
252:2     5 UGood  -  465.25 GB SATA HDD N   N  512B WDC WD5003ABYX-01WERA1 U  
252:3     4 UGood  F 223.062 GB SATA SSD N   N  512B INTEL SSDSC2CW240A3    U  
-------------------------------------------------------------------------------
```
- `foreign`管理

此时硬盘为`foreign`状态

```shell
storcli /cx /fall show
```
返回结果

```shell
Controller = 0
Status = Success
Description = Operation on foreign configuration Succeeded

FOREIGN CONFIGURATION :
=====================
----------------------------------------
DG EID:Slot Type State       Size NoVDs 
----------------------------------------
 0 -        Cac0 Frgn  223.062 GB     1 
----------------------------------------

NoVDs - Number of VDs in disk group|DG - Diskgroup
Total foreign drive groups = 1
```
现在它可以重新包含在配置中

```shell
storcli /cx /fall import
```
如果设备是 RAID 的一部分，则会自动执行重建（请参阅概述中的状态：Rbld）。 可用以下命令监视进度：

```shell
storcli /cx /ex /sx show rebuild
```

## 其他

```shell
# 查看VD健康状态等,获取到坏盘的E:S编号,然后查看对应盘的SN
storcli /c0 /vall show [all]
storcli /c0 /eX /sY show all |grep SN
# 查看阵列卡
storcli show ctrlcount
# 查看 virtual disk 0 @controlor 0
storcli /cx /v0 show
# 查看 Controlor-0, Enclosure-7, Slot-7的磁盘信息
storcli /cx/e252/s7 show all
# 查看报警信息
storcli /cx show alarm
# 关闭beep蜂鸣器报警
storcli /cx set alarm=<on|off|silence>
# 定位磁盘仓位
storcli /c0/e8/s2 start/stop locate
```
## 参考来源

- [官方相关资源下载-broadcom](https://www.broadcom.com/site-search?q=storcli)
- [StorCLI 官方手册下载](https://docs.broadcom.com/docs-and-downloads/raid-controllers/raid-controllers-common-files/StorCLI_RefMan_revf.pdf)
- [StorCLI _Thomas-Krenn](https://www.thomas-krenn.com/en/wiki/StorCLI)
- [STORCLI-wiki（个人博主维护）](https://www.xargs.cn/doku.php/lsi:storcli%E6%89%8B%E5%86%8C)

