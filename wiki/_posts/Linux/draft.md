
## 不重启扫描磁盘
```bash
echo '- - -' > /sys/class/scsi_host/host0/scan  # 有几个host就扫面几个，除非找到已加磁盘
```