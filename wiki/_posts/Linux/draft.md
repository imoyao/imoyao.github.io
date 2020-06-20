---
title: TODO，其他暂时无法归类
toc: true
date: 2020-05-23 12:27:56
tags: 
- 存储
---
## 不重启扫描磁盘
```bash
echo '- - -' > /sys/class/scsi_host/host0/scan  # 有几个host就扫面几个，除非找到已加磁盘
```