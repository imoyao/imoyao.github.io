---
title: 打造个人图床
toc: true
date: 2020-05-23 12:27:56
tags: 博客
---

寻求一种直接、有效、方便、免费（尽量或者很实惠）的图床方案。
![二者不可兼得](/images/20180915163013.gif)

## 域名备案、实名认证

~~### 又拍云~~
需要域名备案
~~### 七牛云~~
1. https 图片外链收费
2. 需要域名备案

## 阿里云 OSS

阿里云 OSS 计费由四个部分组成: 存储费用 + 流量费用 + 请求费用 + 数据处理费用

3. jsDelivr
```plain
//图片上床到Github仓库的地址
https://github.com/Longxr/PicStored/tree/master/blog/xxx.png

//jsdelivr链接地址
https://cdn.jsdelivr.net/gh/Longxr/PicStored/blog/xxx.png

```
## 解决方案
1. 博客尽量少加图片
2. 尽量将图片放在博客目录下，不使用图床
3. 对于不重要的图片，可以使用免费图床
4. 可以购买一些付费的专门的图床服务
## 小白用户

[Image Upload - SM.MS - Simple Free Image Hosting](https://sm.ms/)
> 5 MB max per file. 10 files max per request.

## 开发者
[0xDkd/auxpi: 🍭 集合多家 API 的新一代图床](https://github.com/0xDkd/auxpi)

## 软件

### GoodSync vs freefilesync
关于备份，有两个极优秀的软件我不得不提——Macrium Reflect 和 GoodSync。如果说 Macrium 为我提供了整套的系统以及磁盘备份的解决方案，那么 GoodSync 可以说是只要有正在运行的系统（他也可以运行在 U 盘里）存在，它可以解决任何的备份、同步、传输需求。

它支持任意（可以非本机，可以在内网，可以是云存储）文件夹到任意文件夹备份与同步。

同时它还支持自动执行同步、备份功能，通过检测文件夹的变动，所以它可以满足我上述的两个需求。
[文件同步工具 GoodSync 限免又来了，这货到底有什么用？ - 小众软件](https://www.appinn.com/goodsync-2019/)

### [Molunerfinn/PicGo: A simple & beautiful tool for pictures uploading built by vue-cli-electron-builder](https://github.com/Molunerfinn/PicGo)

## 实现思路
1. 借助 GoodSync（待验证）实现主站（域名下）、博客、wiki 中的图片备份到 static 目录；
2. 图床目录中的图片全部进行压缩；
3. 将 post 中的图片链接替换为 jsDelivr；
	- [ ] 实现头图替换（大图实在太慢了）
	- [ ] 内页是否替换？

## 参考链接
[嗯，图片就交给它了 - 少数派](https://sspai.com/post/40499)
[更换博客图床 - 简书](https://www.jianshu.com/p/2b14396a6eb2)
[可能是最佳的免费图床 | 斯是陋室，惟吾德馨](https://yi-yun.github.io/%E5%9B%BE%E5%BA%8A%E7%9A%84%E9%80%89%E6%8B%A9/)
[博客图床迁移记](https://glumes.com/post/life/blog-image-migrate/)
[markdown 博客图床上传的艰辛之路 | 洞香春](https://wdd.js.org/the-hard-way-of-markdown-insert-images.html)
[博客图床最佳解决方案 | 嘟嘟独立博客](http://tengj.top/2019/08/18/tuchuang/)
[各位 v 友，你们博客的图床都采用什么方案啊 - V2EX](https://v2ex.com/t/551634)
