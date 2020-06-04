---
title: Yum 常见操作记录
toc: true
date: 2020-05-23 18:21:46
tags:
- Linux
- Yum

---

## 配置
默认yum下载的包保存在`/var/cache/yum`，也可以在 /etc/yum.conf 指定：
```plain
cachedir=/var/cache/yum # 存放目录
keepcache=1 # 1为保存 0为不保存
metadata_expire=90m # 过期时间
```

## 只下载不安装包

1. 安装`yum-downloadonly`或 `yum-plugin-downloadonly` 软件包
```bash
yum install yum-plugin-downloadonly
```
说明：`yum-downloadonly`是yum的一个插件，使得yum可以从RHN或者yum的仓库只下载包而不安装。

2. 安装完成后，查看`/etc/yum/pluginconf.d/downloadonly.conf` 配置文件的内容，确认这个插件已经启用：
```bash
vim /etc/yum/pluginconf.d/downloadonly.conf
```
```plain
[main] 
enabled=1
```
举例，从yum源下载lrzsz软件包
```bash
yum install --downloadonly lrzsz
```

### 自定义下载路径
默认下载保存的位是`/var/cache/yum/{RepositoryName}/packages/`目录。可以使用yum的参数`–downloaddir`来指定自定义的路径。与
`–downloadonly` 参数一块使用。
```bash
yum install --downloadonly --downloaddir=/download lrzsz
```
参见：[Yum只下载不安装包_运维_mini_xiang的博客-CSDN博客](https://blog.csdn.net/mini_xiang/article/details/53070321)
