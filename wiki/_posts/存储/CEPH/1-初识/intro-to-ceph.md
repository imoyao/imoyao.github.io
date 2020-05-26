---
title: 初识 Ceph 组件
date: 2020-03-17 21:10:17
subtitle: CEPH，你到底有几个好妹妹？🧐
tags:
- CEPH
cover: /images/logos/ceph-logo.svg
---
无论是要向云平台提供 Ceph 对象存储和/或 Ceph 块设备服务，部署 Ceph 文件系统还是出于其他目的使用 Ceph，一切 Ceph 存储集群的部署工作都要从设置每个 Ceph 节点，网络和 Ceph 存储集群开始。 一个 Ceph 存储群集至少需要一个`Ceph Monitor`、`Ceph Manager`和`Ceph OSD`（对象存储守护进程）。 如果需要运行 Ceph 文件系统客户端，还需要`Ceph Metadata Server`。
- Ceph 监视器（Monitors）
Ceph 监视器（ceph-mon）维护集群状态的映射，包括监视器（mon）映射，管理器（mgr）映射，OSD 映射，MDS 映射和 CRUSH 映射。 这些映射是 Ceph 守护程序相互协调群集状态所需的关键要素。 监视器还负责管理守护进程和客户端之间的身份验证。 通常至少需要**三个**监视器节点才能实现冗余和高可用性。注意，多个 Monitor 的信息需要强一致性，因此要求 Monitor 节点之间的系统时间是一致的，并且网络延时要低。
- 管理器（Managers）
Ceph Manager 守护程序（ceph-mgr）负责跟踪运行时的指标和 Ceph 集群的当前状态，包括存储利用率、当前性能指标和系统负载。Ceph Manager 守护程序还托管基于 python 的模块以管理和暴露 Ceph 集群信息，包括 Web 端的`Ceph Dashboard`和 REST API。 通常，至少需要**两个**管理器才能实现高可用性。
- Ceph 对象存储设备（Object Storage Device|OSDs）
Ceph OSD(对象存储守护进程，Ceph - OSD)用于存储数据，处理数据复制、恢复、再平衡，并通过检查其他 Ceph OSD 守护进程的心跳来为 Ceph 监视器和管理器提供一些监视信息。通常需要至少**3 个**Ceph OSD 才能实现冗余和高可用性。
- Ceph 元数据服务器(MDS、Ceph-MDS)
Ceph 元数据服务器存储代表 Ceph 文件系统（Ceph FS）的元数据。（亦即：Ceph 块设备存储和 Ceph 对象存储不使用 MDS）。Ceph 元数据服务器允许 POSIX 文件系统用户执行基本命令(如 ls、find 等)，而不会给 Ceph 存储集群带来巨大的负担。
Ceph 将数据作为对象存储在逻辑存储池（VG）中。 使用`CRUSH算法`，Ceph 计算哪个放置组应包含该对象，并进一步计算哪个 Ceph OSD 守护程序应存储该放置组。 CRUSH 算法使 Ceph 存储集群能够动态扩展，重新平衡和恢复。
- 对象网关（ceph-radosgw）
Ceph 对象网关节点上运行 Ceph RADOS 网关守护程序（ceph-radosgw）。它是一个构建在 librados 之上的对象存储接口，也是一个为应用程序提供 Ceph 存储集群的 RESTful 网关。Ceph 对象网关支持两个接口：S3 和 OpenStack Swift。
## 网站记录
[twt 企业 IT 交流平台 - talkwithtrend，企业 IT 技术社区，帮助您融入同行](http://www.talkwithtrend.com/)
---
## 建议最低硬件配置
{% raw %}

<table class="docutils align-default">
<thead>
<tr class="row-odd"><th class="head"><p>Process</p></th>
<th class="head"><p>Criteria</p></th>
<th class="head"><p>Minimum Recommended</p></th>
</tr>
</thead>
<tbody>
<tr class="row-even"><td rowspan="5"><p><code class="docutils literal notranslate"><span class="pre">ceph-osd</span></code></p></td>
<td><p>Processor</p></td>
<td><ul class="simple">
<li><p>1x 64-bit AMD-64</p></li>
<li><p>1x 32-bit ARM dual-core or better</p></li>
</ul>
</td>
</tr>
<tr class="row-odd"><td><p>RAM</p></td>
<td><p>~1GB for 1TB of storage per daemon</p></td>
</tr>
<tr class="row-even"><td><p>Volume Storage</p></td>
<td><p>1x storage drive per daemon</p></td>
</tr>
<tr class="row-odd"><td><p>Journal</p></td>
<td><p>1x SSD partition per daemon (optional)</p></td>
</tr>
<tr class="row-even"><td><p>Network</p></td>
<td><p>2x 1GB Ethernet NICs</p></td>
</tr>
<tr class="row-odd"><td rowspan="4"><p><code class="docutils literal notranslate"><span class="pre">ceph-mon</span></code></p></td>
<td><p>Processor</p></td>
<td><ul class="simple">
<li><p>1x 64-bit AMD-64</p></li>
<li><p>1x 32-bit ARM dual-core or better</p></li>
</ul>
</td>
</tr>
<tr class="row-even"><td><p>RAM</p></td>
<td><p>1 GB per daemon</p></td>
</tr>
<tr class="row-odd"><td><p>Disk Space</p></td>
<td><p>10 GB per daemon</p></td>
</tr>
<tr class="row-even"><td><p>Network</p></td>
<td><p>2x 1GB Ethernet NICs</p></td>
</tr>
<tr class="row-odd"><td rowspan="4"><p><code class="docutils literal notranslate"><span class="pre">ceph-mds</span></code></p></td>
<td><p>Processor</p></td>
<td><ul class="simple">
<li><p>1x 64-bit AMD-64 quad-core</p></li>
<li><p>1x 32-bit ARM quad-core</p></li>
</ul>
</td>
</tr>
<tr class="row-even"><td><p>RAM</p></td>
<td><p>1 GB minimum per daemon</p></td>
</tr>
<tr class="row-odd"><td><p>Disk Space</p></td>
<td><p>1 MB per daemon</p></td>
</tr>
<tr class="row-even"><td><p>Network</p></td>
<td><p>2x 1GB Ethernet NICs</p></td>
</tr>
</tbody>
</table>
{% endraw %}

## 参考链接
- [Intro to Ceph — Ceph Documentation](https://docs.ceph.com/docs/master/start/intro/)
- [Ceph Glossary — Ceph Documentation](https://ceph.readthedocs.io/en/latest/glossary/)
- [Hardware Recommendations — Ceph Documentation](https://docs.ceph.com/docs/master/start/hardware-recommendations/#data-storage)
- [Ceph 使用的最佳实践](https://www.ibm.com/developerworks/cn/opensource/os-ceph-active-active-data-center-and-best-practices/index.html)