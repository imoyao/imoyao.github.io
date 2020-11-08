---
title: 基于 CEPH 的 dashboard 的二次开发
date: 2019-12-13 11:13:57
tags:
- CEPH
categories:
- 工作日常
cover: /images/logos/ceph-logo.svg
---
{% note info %}
本文为个人记录之用，不对大多数用户具有参考价值。
{% endnote %}

## 前言
项目以`ceph-14.2.5`版本代码中的 [ceph/src/pybind/mgr/dashboard· ceph/ceph](https://github.com/ceph/ceph/tree/master/src/pybind/mgr/dashboard) 为基础通过二次开发以实现 Ceph 分布式管理系统。

![Dashboard](/images/ceph-dashboard.png)

## 开发环境搭建

### 前端
1. 安装 npm 工具
```shell
# 安装npm
yum install npm
```
2. 安装 node 环境
```shell
# 配置国内源
npm config set registry https://registry.npm.taobao.org
# 安装node版本管理工具'node'
npm install -g n
# 升级到`8.9`版本的`node`
n 8.9.0
```
查看`npm`与`nodejs`的版本，如果`nodejs`低于`8.9.0`版本，则升级之。
**注意**：以`Linux`为开发环境安装前端依赖进行演示：
切换到`/usr/share/ceph/mgr/dashboard/frontend` 目录：
此处可见官方[Ceph Dashboard Developer Documentation — Ceph Documentation](https://docs.ceph.com/en/latest/dev/developer_guide/dash-devel/)文档说明。
3. 安装依赖
``` shell
# 此处可见官方../HACKING.rst 文档说明
# install dependencies
npm install
```
可以以`node-sass`安装成功为参考标志，如果报错，请删除 node_modules 目录之后重试。
```shell
#报错清除缓存
npm cache verify
```
4. 安装成功之后，修改代理配置
```shell
# 代理配置
mv proxy.conf.json.sample proxy.conf.json
```
一个可参考的配置内容为：
```plain
{
  "/api/": {
    "target": "http://localhost:8080",  # 服务端口和运行地址需要根据情况配置，注意http和https必须分清
    "secure": false,
    "logLevel": "debug"
  },
  "/ui-api/": {
    "target": "http://localhost:8080",
    "secure": false,
    "logLevel": "debug"
  }
}

```
6. 运行前端服务
```shell
npm start
```
之后，如果使用默认配置，则访问`http://localhost:4200/`进行开发，外部网络访问，替换为服务所属机器的 ip 即可。

### 后端
1. 安装 pip
2. 安装 python 依赖
```shell
pip install requirements.txt -r
```
3. 配置并启动 ODSP 作为一个服务
```shell
systemctl start odspd
```

## 功能展示
{% gallery %}
![节点信息展示](/images/ceph-dash/Estor-host-info.png)
![磁盘（批量）点灯](/images/ceph-dash/Snipaste_2020-11-06_14-49-46.png)
![节点远程管理（开、关机，用户、网络管理）](/images/ceph-dash/Snipaste_2020-11-06_14-50-44.png)
![系统工具：时间展示和DNS修改及展示](/images/ceph-dash/Snipaste_2020-11-06_14-58-33.png)
{% endgallery %}

## 项目目录结构
```shell
tree -L 3 -I "node_modules|*.pyc|*.pyo" 
```
```plain
.
├── awsauth.py
├── controllers     # 后端Python
│   ├── auth.py
│   ├── cephfs.py
│   ├── cluster_configuration.py
│   ├── docs.py
│   ├── erasure_code_profile.py
│   ├── grafana.py
│   ├── health.py
│   ├── home.py
│   ├── host.py
│   ├── __init__.py
│   ├── iscsi.py
│   ├── logging.py
│   ├── logs.py
│   ├── mgr_modules.py
│   ├── monitor.py
│   ├── nfsganesha.py
│   ├── osd.py
│   ├── perf_counters.py
│   ├── pool.py
│   ├── prometheus.py
│   ├── rbd_mirroring.py
│   ├── rbd.py
│   ├── rgw.py
│   ├── role.py
│   ├── saml2.py
│   ├── settings.py
│   ├── summary.py
│   ├── task.py
│   └── user.py
├── exceptions.py
├── frontend            # 前端
│   ├── angular.json
│   ├── dist
│   │   └── en-US
│   ├── e2e
│   │   ├── block
│   │   ├── cluster
│   │   ├── filesystems
│   │   ├── helper.po.ts
│   │   ├── nfs
│   │   ├── pools
│   │   └── tsconfig.e2e.json
│   ├── environment.build.js
│   ├── html-linter.config.json
│   ├── i18n.config.json
│   ├── nodejs-8.9.4-1nodesource.x86_64.rpm
│   ├── package.json
│   ├── package-lock.json
│   ├── protractor.conf.js
│   ├── proxy.conf.json.sample
│   ├── src                # 静态src
│   │   ├── app
│   │   ├── assets
│   │   ├── defaults.scss
│   │   ├── environments
│   │   ├── favicon.ico
│   │   ├── index.html
│   │   ├── jestGlobalMocks.ts
│   │   ├── locale
│   │   ├── main.ts
│   │   ├── polyfills.ts
│   │   ├── setupJest.ts
│   │   ├── styles
│   │   ├── styles.scss
│   │   ├── testing
│   │   ├── tsconfig.app.json
│   │   ├── tsconfig.spec.json
│   │   ├── typings.d.ts
│   │   ├── unit-test-configuration.ts.sample
│   │   ├── vendor.overrides.scss
│   │   └── vendor.variables.scss
│   ├── tsconfig.json
│   └── tslint.json
├── grafana.py
├── HACKING.rst
├── __init__.py
├── module.py       # 必需
├── plugins
│   ├── feature_toggles.py
│   ├── __init__.py
│   ├── interfaces.py
│   ├── lru_cache.py
│   ├── pluggy.py
│   └── ttl_cache.py
├── README.rst
├── requirements-py27.txt       # python依赖
├── requirements-py3.txt
├── requirements.txt
├── rest_client.py
├── run-backend-api-request.sh
├── run-backend-api-tests.sh
├── run-backend-rook-api-request.sh
├── run-frontend-e2e-tests.sh
├── run-frontend-unittests.sh
├── run-tox.sh
├── security.py
├── services
│   ├── access_control.py
│   ├── auth.py
│   ├── cephfs.py
│   ├── ceph_service.py
│   ├── cephx.py
│   ├── exception.py
│   ├── ganesha.py
│   ├── __init__.py
│   ├── iscsi_client.py
│   ├── iscsi_cli.py
│   ├── iscsi_config.py
│   ├── orchestrator.py
│   ├── rbd.py
│   ├── rgw_client.py
│   ├── sso.py
│   └── tcmu_service.py
├── settings.py
├── tests           # 单元测试代码
│   ├── helper.py
│   ├── __init__.py
|   |—— # 省略
│   └── test_tools.py
├── tools.py
└── tox.ini

```

## 问题记录

### 集群配置
启用`mgr restful`之后，访问`https://node_addr:8003/config/cluster`获取集群配置信息，之后可以访问具体名称，获得配置详情；

### 如何添加`controller`
参见[HACKING.rst](https://docs.ceph.com/en/latest/dev/developer_guide/dash-devel/)

继承`BaseController`之后使用 `@Controller`,`@ApiController` 或者`@UiApiController` ，三者的区别是：
`@ApiController` 和 `@UiApiController` 是`@Controller`的特殊化。

`@ApiController` 应该用在提供类 API 接口，而`@UiApiController`应该被用于非公用的 API，其他接口使用`@Controller`

一般来说，我们只需要实现`@Controller`和`@ApiController` 即可。

`@Endpoint` 用于暴露接口的方法实现，它可以接收很多参数，比如请求方法，查询参数等；
***注***：对于集群管理时，我们把 node 信息直接传输到 url 中，或许是一个好办法，参考：`@Endpoint(path="/{date}/latency")`处代码。

而继承`RESTController`默认返回`json`格式数据。它是一个简化并使用`collection`整合数据的抽象层，将方法名、请求类型和状态码进行映射。具体映射关系见文档表格。

### 调试
模块编写完成，重启服务，看是否会有模块未找到，服务导入等报错
```shell
ceph mgr module disable dashboard
ceph mgr module enable dashboard
ceph dashboard create-self-signed-cert
```
也可以查看日志，查找可能的报错信息。

#### 查看日志

通过该文件可以查看`mgr`中的报错信息，暂时未找到 logger.info()写入 log 中的信息（是否需要配置？）
```shell
tailf /var/log/ceph/ceph-mgr.node1.log
```
```python
from ..module import cherrypy
cherrypy.log('---------', json.dumps(update_info))     # 必须是str
```
### MDS 状态

[元数据服务器](https://my.oschina.net/myspaceNUAA/blog/500136)
[CEPH-MDS – CEPH 元数据服务器守护进程](http://docs.ceph.org.cn/man/8/ceph-mds/)

### 需要安装的工具、依赖

- 获取磁盘`SN`号码
```shell
yum install hdparm
```

### 时间配置
集群部署的时候脚本中应该有配置 NTP 的操作，步骤参见：[NTP](https://access.redhat.com/documentation/en-us/red_hat_ceph_storage/1.2.3/html/installation_guide_for_rhel_x86_64/pre-installation-requirements#ntp)  
不再支持手动输入时间配置
1. 直接设置集群内部机器为 ntp 服务器，其他指向该机器；
2. 给定 ip 或域名地址，如果是集群网段的，则直接返回提示不支持，否则，所有指向该地址。
{% note warning %}
**注意**
根据下面这篇文章的观点，在集群起来之后再去调节 ntp 服务被认为是会严重影响集群业务的操作，如果一定要调整，也可能会耗时很久！
[深度解析 CephX 原理—调节 NTP 时钟的困境 | 开心鬼](http://hackerain.me/2019/12/15/ceph/cephx.html)
{% endnote %}

[监视器配置参考](http://docs.ceph.org.cn/rados/configuration/mon-config-ref/)
   
### mon 状态
- [Understanding Monitor Status](https://access.redhat.com/documentation/en-us/red_hat_ceph_storage/3/html/troubleshooting_guide/troubleshooting-monitors#understanding-monitor-status)
- [Troubleshooting Monitors — Ceph Documentation](https://docs.ceph.com/docs/nautilus/rados/troubleshooting/troubleshooting-mon/)
#### 在法定之内 in quorum
`ceph daemon mon.node X mon_status`两种 state， leader 或者 peon；
如果 leader down 之后，调用可以看到原来的 state 为`peon`的会变为`probing`，如果可以实现仲裁，则`rank`最小者变为 leader；
#### 超出法定人数 out quorum/新加入的节点
状态可能为 探测（probing）, 选举（electing） 或者 synchronizing

- [mon.X is down (out of quorum)](https://access.redhat.com/documentation/en-us/red_hat_ceph_storage/3/html/troubleshooting_guide/troubleshooting-monitors#monitor-is-out-of-quorum)

## 发布历史

### vN1.0.1（2020-07-03）

#### 集群主机

##### mon/mgr
节点发现：
1. 单节点添加
2. 多节点添加
3. 局域网段添加
节点删除

##### 远程管理
1. 节点远程开机、关机、重启；
2. 修改远程操作用户用户名、密码；
3. 网络配置（ip、掩码、网关。

##### 磁盘展示及定位
磁盘盘位查看、（批量）定位及取消定位；

##### 系统工具
1. 设置 ntp 服务器
2. 设置 DNS

##### License
license 添加、删除、更新

##### OSD
osd 新建：osd 添加（类型配置）、添加-WAL devices DB devices，加密
OSD 编辑：洗刷、深度洗刷、设置权重、标记、销毁、清除

##### 日志
集群日志管理、审计日志、日志打包下载

##### 存储池
存储池新建、编辑、删除

##### 块设备
- 映像
新建、编辑、复制、删除，移除回收站、容量调节
- 镜像
- ISCSI-target
- ISCSI-网关

##### 对象网关
守护进程创建、更新、删除

## 更多  
首先阅读[HACKING.rst](./HACKING.rst)文档，然后阅读[文档目录](docs/)了解更多。
同事写的备忘录：[有道云笔记](https://note.youdao.com/ynoteshare1/index.html?id=550ed97b36101aab178afe9081cd52ee)
