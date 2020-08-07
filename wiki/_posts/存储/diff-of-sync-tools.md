---
title: 各种同步工具之间的差异| DRBD vs SCP vs rsync vs mirror
toc: true
date: 2020-08-07 12:27:56
tags: 
- 存储
- 工具
- Linux
---
## DRBD
用于块级别设备之间的同步。
## SCP
待续
## rsync
待续

> [DRBD](https://www.linbit.com/drbd/) operates on block device level. This makes it useful for synchronizing systems that are under heavy load. Lsyncd on the other hand does not require you to change block devices and/or mount points, allows you to change uid/gid of the transferred files, separates the receiver through the one-way nature of rsync. DRBD is likely the better option if you are syncing databases.

[GlusterFS](http://www.gluster.org/) and [BindFS](http://bindfs.org/) use a FUSE-Filesystem to interject kernel/userspace filesystem events.

[Mirror](https://github.com/stephenh/mirror) is an asynchronous synchronisation tool that takes use of the inotify notifications much like Lsyncd. The main differences are: it is developed specifically for master-master use, thus running on a daemon on both systems, uses its own transportation layer instead of rsync and is Java instead of Lsyncd’s C core with Lua scripting.

## 参考链接
[Lsyncd - Live Syncing (Mirror) Daemon](https://axkibe.github.io/lsyncd/)
[How does `scp` differ from `rsync`? - Stack Overflow](https://stackoverflow.com/questions/20244585/how-does-scp-differ-from-rsync)