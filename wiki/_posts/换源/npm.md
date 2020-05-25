---
title: npm 安装及换源
toc: true
date: 2020-05-25 18:21:46
tags:
- Git

---

## 安装 node

1.  更新源

```bash
curl --silent --location https://rpm.nodesource.com/setup_10.x | sudo bash -
```

2. 安装 node

```bash
sudo yum -y install nodejs
```

### 注意

1. 如果以上步骤不能安装 最新版 node，执行以下命令后再执行第二步：

   ```bash
   sudo yum clean all
   ```

2. 如果存在多个 nodesoucre，执行以下命令删除，然后重新执行第一第二步：

   ```bash
   sudo rm -fv /etc/yum.repos.d/nodesource*
   ```

## 换源

### 通过 config 命令

```bash
npm config set registry https://registry.npm.taobao.org npm info underscore 
```

（如果上面配置正确这个命令会有字符串 response）

### 命令行指定

```bash
npm --registry https://registry.npm.taobao.org info underscore
```

### 编辑 `~/.npmrc`加入下面内容

```bash
registry = https://registry.npm.taobao.org
```

### 使用 nrm 管理 registry 地址

1. 下载 nrm

   ```bash
   npm install -g nrm
   ```
2. 添加 registry 地址

   ```bash
   nrm add npm http://registry.npmjs.org
   nrm add taobao https://registry.npm.taobao.org
   ```

3. 切换 npm registry 地址

   ```bash
   nrm use taobao
   nrm use npm
   ```

## 参考链接

[CentOS yum 安装 node.js](https://www.cnblogs.com/royfans/p/10405329.html)

[设置 npm 的 registry - 简书](https://www.jianshu.com/p/0e80d8a355a8)

