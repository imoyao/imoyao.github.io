---
title: 如何将代码打patch？
date: 2020-11-04 17:57:53
tags:
- 开源
categories:
---
## 前言
在基于开源项目做二次开发的时候，我们可能会在某一个版本号上开始，然后做开发。当开发进行一段时间之后，远程上面的代码可能已经和我们的代码大相径庭了，这个时候想要合并就会变得相对比较困难，所以在此记录一下流程。
## 工作流
一般来说，我们二次开发时会先拉取分支作为本地仓库，即第一次git init的内容

## 生成patch文件
```
git format-patch 703ae2b80580e1xxx3f718d428572b50
```
## 应用patch

```shell
git am patches/0002-1.-2.-disk-host.get-api-3.-4.-utils-5.-conf.patch
git apply patches/0002-1.-2.-disk-host.get-api-3.-4.-utils-5.-conf.patch --reject
git status | grep rej
git add .
git am --resolved
git log
```
## 参考链接
[ git 打补丁方法总结_JT的专栏-CSDN博客](https://blog.csdn.net/sinat_20059415/article/details/80598347)