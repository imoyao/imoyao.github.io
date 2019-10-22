---
title: Ceph 管理系统对比
date: 2019-10-22 11:12:35
tags:
- Ceph
- 存储
---
本文主要在[Ceph 开源管理监控平台分析](http://www.hl10502.com/2017/03/30/ceph-web-manage/)基础上做一点补充。

## 现状
Ceph 的开源管理监控平台有如 VSM（三年前最后更新，read-only），InkScope，Calamari,[Suse-enterprise-storage](https://www.suse.com/zh-cn/products/suse-enterprise-storage/)等;
## VSM
[VSM | Virtual Storage Manager](https://github.com/intel/virtual-storage-manager)
### 官网
[virtual-storage-manager](https://01.org/zh/virtual-storage-manager)

### 技术选型
基于 Django 开发
## inkScope
[inkScope](https://github.com/inkscope/inkscope)
### 介绍
Inscope 搭建的主要组件:

- inkscope-common   
包含 inkscope 的默认配置文件以及其他进程(cephprobe,sysprobe)启动所需的依赖文件，所有相关节点都需要安装。
- inkscope-admviz   
包含 inkscope 的 web 控制台文件，含接口和界面，仅需要安装一个，该节点（管理节点）上同时需要按安装 flask 和 mongodb
- inkscope-cephrestapi  
用于安装启动 ceph RESTful api 的脚本，仅需要安装在提供 api 接口的节点上，即 mon 节点。
- inkscope-cephprobe    
用于安装启动 cephprobe 的脚本(整个集群只需一个)，安装在 mon 节点，脚本主要实现：获取 Ceph 集群的一些信息，并使用端口（5000）提供服务，将数据存入 mongodb 数据库中。
- inkscope-sysprobe         
安装用于所有 mon 和 osd 的 sysprobe 所需要脚本，即所有节点均安装，实现获取节点设备资源信息如：CPU、内存、磁盘等等。
### 搭建
[Centos7.2：搭建 Ceph 管理系统 Inscope](https://blog.csdn.net/je930502/article/details/50812014)
[Ceph web 管理/监控平台 Inkscope 部署](https://gtcsq.readthedocs.io/en/latest/others/inkscope_install.html)
[开源 Ceph 管理平台 Inkscope 部署手册](http://cloud.51cto.com/art/201507/486005_all.htm)
### 技术选型
PHP（？）、Flask、MongoDB、AngularJS 

## Calamari
[calamari](https://github.com/ceph/calamari)

### 介绍
Calamari 包含的组件主要有 calamari-server、romana、salt-minion、salt-master、diamond。

这些模块各自的作用：

- calamari-server   
这个是提供一个与集群进行交互，并且自己封装了一个自己的 API，做集中管理的地方，这个只需要在集群当中的某一台机器上安装，也可以独立安装

- romana    
就是原来的 calamari-client，这个叫 client,其实是一个 web 的界面，这个叫 calamari-web 更好，现在已经更名为 romana，这个也是只需要在集群当中的某一台机器上安装，也可以独立安装，这个需要跟 calamari-server 安装在一台机器上

- salt-master   
是一个远程管理的工具，可以批量的管理其他的机器，可以对安装了 salt-minion 的机器进行管理，在集群当中，这个也是跟 calamari-server 安装在一起的

- salt-minion   
是安装在集群的所有节点上的，这个是接收 salt-master 的指令对集群的机器进行操作，并且反馈一些信息到 salt-master 上

- diamond   
这个是系统的监控信息的收集控件，提供集群的硬件信息的监控和集群的信息的监控，数据是发送到 romana 的机器上的，是由 romana 上的 carbon 来收取数据并存储到机器当中的数据库当中的
- Graphite      
图形显示工具，其中 carbon 用来收集数据，whisper 是针对其专门开发的数据库，用来持久化数据，graphite-web 借助 django、apache 等提供 web 服务，从而用浏览器可以图形化展示数据。

Calamari 为 Ceph 的运维和管理提供了一个统一的平台，而且用户还可以基于这个平台扩展自己的存储管理产品，但同时也存在着不足和需要改进的地方。

1. Calamari 还不能完成 Ceph deploy 所实现的部署功能，这是它最大一个不足；Fuel 可以完成部署功能，并且可以选择 Ceph server 的数据盘和日志盘以及定制默认的备份数等，所以 Calamari + Fuel 可以来实现一个完成的基于 Ceph 的部署和管理工具。
2. Calamari 提供的管理功能太少，用户无法只使用它来运维一个 Ceph 环境。
3. 用户可以基于 Calamari 开发自己的 Ceph 管理软件，UI 部分可以修改 calamari_clients 的页面，也可也单独实现一套自己的 UI 基于 calamari_rest 和 Graphite_web，后端的功能的监控部分可以扩展 diamond 的 collector 实现，管理 Ceph 的功能可以扩展 rest api，cthulhu，salt 等来实现。

### 搭建
[calamari：基于 web 页面的 ceph 系统监控管理工具安装](https://blog.csdn.net/hit1944/article/details/38752717)
[ceph 监控管理平台 calamari](https://blog.51cto.com/linuxww/1944963)
### 技术选型
Django

## ceph-dash
[ceph-dash](https://github.com/Crapworks/ceph-dash)
### 技术选型
Flask
## 横向对比
[ceph-days-sf2015](http://de.slideshare.net/Inktank_Ceph/07-ceph-days-sf2015-paul-evans-static)
### 对比背景
![](/images/img_20191022163356.jpg)
### 管理
![management](/images/img_20191022164343.jpg)
### 监控
![monitor](/images/img_20191022164348.jpg)
### 概览
![VSM](/images/img_20191022164357.jpg)    
![inkScope](/images/img_20191022164353.jpg)    
![Calamari](/images/img_20191022164326.jpg)    
![ceph-dash](/images/img_20191022173026.jpg)    
## 一种声音
> 从 ceph 社区 qq 群看过去，总会有一些运维或者开发询问哪种 ceph 管理平台方便好用，然后就开始对比 inkscope、vsm、calamari。其实这些都不是重点，重点是看看 github 上的这些项目已经 long long ago 不更新代码了，也就是说软件的生命周期走到了尽头，没有更新和扩展。想想群里的兄弟在生产环境上用这些软件，最后是什么结果。。。况且大部分公司都是一两个码农在搬砖，投入到开发这三个监控平台上也不现实。
>
>大部分生产环境都是用 cli 对 ceph 进行管理，所以生产环境对 ceph 的管理需求不大。在监控上，ustack 之前的文档提过了一套监控方案。建议关注一下https://prometheus.io/项目。前台集成 grafana，运维人员根据自己实际需求，DIY 监控面板，配合后端 exporters 很小的开发量，实现监控任意指标。报警方面 prometheus 也有自己的解决方案。联邦机制的实现可以使监控平台横向扩展。目前很多公司的生产环境都在用此方案。考虑到大规模运营，后续还需要 ELK 等工具的帮助。

[关于 ceph 监控管理平台的一点个人观点](https://my.oschina.net/yangfanlinux/blog/783756)

## 相关博客 
[zphj1987](http://www.zphj1987.com/)