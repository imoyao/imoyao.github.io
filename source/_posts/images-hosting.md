---
title: 免费个人博客图床解决方案
toc: true
tags: 
- 博客
- 图床
- 软件
categories:
  - 善用佳软
date: 2020-12-06 10:52:09
---
## 前言
写博客的时候需要引用很多图片，一种常见的方式是在仓库中新建一个目录然后引用。但是这样的话在网页查看时会有点慢。所以本文试图寻求一种直接、有效、方便、免费（尽量或者很实惠）的图床方案。

![鱼和熊掌，不可兼得](https://cdn.jsdelivr.net/gh/masantu/statics@master/images/20180915163013.gif)

## 自建图床

本方案针对可接受备案（实名认证）及付费用户。

### ~~又拍云~~
需要域名备案

### ~~七牛云~~
1. https 图片外链收费
2. 需要域名备案

### 阿里云 OSS

阿里云 OSS 计费由四个部分组成: 存储费用 + 流量费用 + 请求费用 + 数据处理费用

## 免费图床

### sm.ms
[Image Upload - SM.MS - Simple Free Image Hosting](https://sm.ms/)
 > 5 MB max per file. 10 files max per request.

### [聚合图床 - 免费无限图片上传](https://www.superbed.cn/)
 > 单图最大5M，1000个文件

限制条件[见此](https://www.superbed.cn/vip)

### [路过图床 - 免费图片上传, 专业图片外链, 免费公共图床](https://imgchr.com/)
 > 全球CDN加速, 支持外链, 原图保存, 最大单张支持10 MB

限制条件[服务条款 - 路过图床](https://imgchr.com/page/tos)

### 图床测试

为了实验上述免费图床的有效性，我分别上传了一张图片以供测试。如果他们的服务可用，则可以在下方看到图片被正常加载。如果只是临时使用，可以点击图片直达使用。

[![路过图床](https://s3.ax1x.com/2020/12/06/DXaxFs.jpg)](https://imgchr.com/i/DXaxFs)

[![聚合图床](https://pic.downk.cc/item/5fcc7602394ac5237839e4bf.jpg)](https://www.superbed.cn/)

[![Image Upload - SM.MS - Simple Free Image Hosting](https://i.loli.net/2020/12/06/ZODeJTQL7vpSBaW.jpg)](https://sm.ms/)

[![图壳](https://static01.imgkr.com/temp/77df24ba89314c24bff7750f10b4d187.jpg)](https://imgkr.com/)

[![postimages](https://i.postimg.cc/tRNvCQQR/image.jpg)](https://postimages.org/)

### 开发者
[0xDkd/auxpi: 🍭 集合多家 API 的新一代图床](https://github.com/0xDkd/auxpi)
[staugur/picbed: 基于Flask的Web自建图床，支持存储到又拍云、七牛云、阿里云OSS、腾讯云COS、GitHub、Gitee](https://github.com/staugur/picbed)

## 免费

### 服务提供商 jsDelivr
```javascript
// load any GitHub release, commit, or branch

// note: we recommend using npm for projects that support it

https://cdn.jsdelivr.net/gh/user/repo@version/file
```
比如，我们在用户名（imoyao）下创建仓库（statics），则分支（master/main）下的文件（file_path_with_name）可以通过CDN获取。
```plain
//图片上床到Github仓库的地址
https://github.com/{imoyao}/{statics}/tree/{master}/{file_path_with_name}

//jsdelivr链接地址
https://cdn.jsdelivr.net/gh/{imoyao}/{statics}@{master}/{file_path_with_name}
```
## 解决方案

### 实现思路
1. 借助 GoodSync/freefilesync（待验证）实现主站、博客、wiki 中的图片备份到 static 目录；
2. 图床目录中的图片全部进行无损压缩；
3. 将 post 中的图片链接替换为 jsDelivr；

### 文件夹同步软件

#### GoodSync vs freefilesync

> 关于备份，有两个极优秀的软件我不得不提——Macrium Reflect 和 GoodSync。如果说 Macrium 为我提供了整套的系统以及磁盘备份的解决方案，那么 GoodSync 可以说是只要有正在运行的系统（它也可以运行在 U 盘里）存在，它可以解决任何的备份、同步、传输需求。
>
>它支持任意（可以非本机，可以在内网，可以是云存储）文件夹到任意文件夹备份与同步。
>
>同时它还支持自动执行同步、备份功能，通过检测文件夹的变动，所以它可以满足我上述的两个需求。

参考阅读[文件同步工具 GoodSync 限免又来了，这货到底有什么用？ - 小众软件](https://www.appinn.com/goodsync-2019/)

最终选择：[FreeFileSync](https://freefilesync.org/download.php)

![配置自定义规则](https://cdn.jsdelivr.net/gh/masantu/statics/images/20201206160024.png)

{% note warning %}

**注意**

同步配置时选择*自定义*，上方选择可能出现的情形，下方选择当出现配置情形时需要做的动作，最好不要把右侧镜像目录的图片删除。如果对自己的配置不确定，请保证回收站可用的同时对处理逻辑进行测试！
{% endnote %}

使用教程：[强大的备份软件FreeFileSync - 知乎](https://zhuanlan.zhihu.com/p/140026821)

### 剪切图片直接上传仓库
使用 PicGo直接上传仓库，参见：[Molunerfinn/PicGo: A simple & beautiful tool for pictures uploading built by vue-cli-electron-builder](https://github.com/Molunerfinn/PicGo)

### 定期对图片进行无损压缩
按需查找：[TinyPNG – Third-Party Solutions](https://tinypng.com/third-party)
插件版：[TinyPNG Image Optimizer - IntelliJ IDEs | JetBrains](https://plugins.jetbrains.com/plugin/11573-tinypng-image-optimizer)
更多参见：[有没有一个批量压缩图片软件？ - 知乎](https://www.zhihu.com/question/20432364)
Github Action[Tinify Image Action · Actions · GitHub Marketplace](https://github.com/marketplace/actions/tinify-image-action)

### 图片去重
使用[DoubleKiller - Download [english] (Big Bang enterprises)](http://www.bigbangenterprises.de/en/doublekiller/download.htm)对上传Github仓库的图片进行去重。
[寻找一款清理电脑中重复文件的软件? - 知乎](https://www.zhihu.com/question/35069783)

### 视频
视频文件较大，我们不要上传到 Github 仓库中，直接使用视频图床即可。
参见：[图床 - 图片上传, 外链, 高清原图, 永久免费, 支持视频上传](http://imgbed.cn/)

## 其他
1. 博客尽量少加图片
2. 尽量将图片放在博客目录下，不使用图床
3. 对于不重要的图片，可以使用免费图床
4. 可以购买一些付费的专门的图床服务

## 参考链接
[嗯，图片就交给它了 - 少数派](https://sspai.com/post/40499)
[无需注册、打开即用，这 8 个免费好用的图床工具值得一试 - 少数派](https://sspai.com/post/55032)
[更换博客图床 - 简书](https://www.jianshu.com/p/2b14396a6eb2)
[可能是最佳的免费图床 | 斯是陋室，惟吾德馨](https://yi-yun.github.io/%E5%9B%BE%E5%BA%8A%E7%9A%84%E9%80%89%E6%8B%A9/)
[博客图床迁移记](https://glumes.com/post/life/blog-image-migrate/)
[markdown 博客图床上传的艰辛之路 | 洞香春](https://wdd.js.org/the-hard-way-of-markdown-insert-images.html)
[博客图床最佳解决方案 | 嘟嘟独立博客](http://tengj.top/2019/08/18/tuchuang/)
[各位 v 友，你们博客的图床都采用什么方案啊 - V2EX](https://v2ex.com/t/551634)
