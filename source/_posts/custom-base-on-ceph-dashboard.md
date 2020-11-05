---
title: 基于CEPH的dashboard的二次开发
date: 2019-12-13 11:13:57
tags:
- CEPH
categories:
---
## 前言
{% note info %}
本文为个人记录之用，不对大多数用户具有参考价值。
{% endnote %}
## 分布式集群管理系统
项目以`ceph-14.2.5`版本代码中的`src/pybind/mgr/dashboard`为基础通过二次开发以实现Ceph分布式管理系统。

![overview](/images/ceph-dashboard.png)

## 开发环境搭建

### 前端
```shell
# 安装npm
yum install npm
```
查看`npm`与`nodejs`的版本，如果`nodejs`低于`8.9.0`版本，则升级之：

```shell
# 配置国内源
npm config set registry https://registry.npm.taobao.org
# 安装node版本管理工具'n'
npm install -g n
# 升级到`8.9`版本的`node`
n 8.9.0
```
**注意**：以`Linux`为开发环境安装前端依赖进行演示：
切换到`/usr/share/ceph/mgr/dashboard/frontend` 目录：
``` shell
# 此处可见官方../HACKING.rst 文档说明
# install dependencies
cnpm install
# serve with hot reload at localhost:9000
npm start
```
之后，如果使用默认配置，则访问`http://localhost:4200/`进行开发。

## 项目目录结构
```shell
tree -L 3 -I "node_modules|*.pyc|*.pyo" 
```
```sh
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
## 发布历史

TODO

## 更多  
首先阅读[HACKING.rst](./HACKING.rst)文档，然后阅读[文档目录](docs/)了解更多。
