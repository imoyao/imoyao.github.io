---
title: Hexo 主题 Butterfly 自定义之路
date: 2020-01-06 21:32:01
tags:
- Hexo
- Butterfly
cover: https://d33wubrfki0l68.cloudfront.net/6657ba50e702d84afb32fe846bed54fba1a77add/827ae/logo.svg
---

## svg背景

使用[SVG 编辑器](https://c.runoob.com/more/svgeditor/)修改footer、评论区背景图；

## 插入视频
```
<video src="/media/Dream-It-Possible.mp4" controls="controls" style="max-width: 100%; display: block; margin-left: auto; margin-right: auto;"> Your browser does not support the video tag. </video>
```
## TODO

## 首页添加描述卡

- self introduce
- music
- video

## page 页侧边栏

不要展示只看一次就可以的信息

### 插件

使用第三方插件 `hexo-wordcount` 被 `hexo-symbols-count-time` 所取代，因为 `hexo-symbols-count-time` 没有任何外部 `nodejs` 依赖、也没有会导致生成站点时的性能问题 language filter。

### 表格美化

参考[Hexo下表格的美化和优化](https://hexo.imydl.tech/archives/6742.html)

|姓名|年龄|性别|民族|
|:---:|:---|---:|:---:|
|张三丰|100|男|汉族|
|张翠山|35|男|汉族|
|殷素素|33|女|汉族|
|张无忌|12|男|汉族|
|赵敏|12|女|蒙古族|
|小昭|12|女|波斯人|
