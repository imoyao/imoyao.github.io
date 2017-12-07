创建vdisk的时候出现以下问题

MegaCli -CfgLdAdd -r0[17:6] -a0
Adapter 0: Configure Adapter Failed
FW error description:
The current operation is not allowed because the controller has data in cache for offline or missing virtual drives.
Exit Code: 0x54

解决方法:
MegaCli -GetPreservedCacheList -a0
MegaCli -DiscardPreservedCache -L6 -a0
效果如下:
>MegaCli  -GetPreservedCacheList -a0
Adapter #0
Virtual Drive(Target ID 06): Missing.
Exit Code: 0x00
>MegaCli -DiscardPreservedCache -L6 -a0
Adapter #0
Virtual Drive(Target ID 06): Preserved Cache Data Cleared.
Exit Code: 0x00

新换硬盘状态是JBOD状态，导致创建vdisk失败
MegaCli -CfgLdAdd -r0[21:7] -a0
The specified physical disk does not have the appropriate attributes to complete the requested command.
Exit Code: 0x26
查看硬盘JBOD状态

MegaCli -PDList -a0|less|grep JBOD
新换硬盘状态是JBOD状态，导致创建vdisk失败
解决方法:

>MegaCli -PDMakeGood -PhysDrv[21:7] -force -a0

Adapter: 0: EnclId  -21 SlotId  -7 state changed to Unconfigured  -Good.
Exit Code: 0x00
>MegaCli -CfgLdAdd -r0[21:7] -a0

Adapter 0: Created VD 8
Adapter 0: Configured the Adapter!!
Exit Code: 0x00
 MegaCli 管理工具清理Cache异常报错，不能清理Cache
>MegaCli -DiscardPreservedCache -L5 -a0

Adapter #0
Segmentation fault
设置RAID卡cache策略
查看RAID cache状态
>MegaCli -LDGetProp -Cache -Lall -a0

Adapter 0  -VD 0(target id: 0): Cache Policy:WriteThrough, ReadAdaptive, Direct, No Write Cache if bad BBU
Adapter 0  -VD 1(target id: 1): Cache Policy:WriteThrough, ReadAdaptive, Direct, No Write Cache if bad BBU
Adapter 0  -VD 2(target id: 2): Cache Policy:WriteBack, ReadAdaptive, Direct, Write Cache OK if bad BBU
Exit Code: 0x00
设置RAID卡cache策略
>MegaCli -LDSetProp ForcedWB -L2 -a0

Set Write Policy to Forced WriteBack on Adapter 0, VD 2 (target id: 2) success
Exit Code: 0x00
cache 策略如果在RAID卡电池出现问题的时候，强制设为ForcedWB的情况下面，存在很多风险，当机器挂了或者断电的情况下面，cache中的数据就没法刷回磁盘，这样就存在数据丢失的情况。 这是一种牺牲安全换取性能的做法，不值得推荐。

参考来源：

- [RAID 常見操作速查一 - FPs](http://fangpeishi.com/raid_cheatsheet1.html#Adaptec系列坏盘)
- [DELL磁盘阵列控制卡(RAID)管理工具-MegaCli常用指令参考-FreeOA](http://www.freeoa.net/osuport/sysadmin/linux-dell-raid-tool-megacli-cmd-ref_1408.html)
