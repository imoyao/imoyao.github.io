---
title: 我的开源博客 idealyard 心路历程及其他
date: 2019-06-17T12:25:06.000Z
tags:
  - 博客
  - Flask
  - 开源
categories:
- Projects
- IdealYard
cover: /images/nathan-anderson-XxyzpjYNY8k-unsplash.jpg
reward: true
---
今天（2019-09-12）基本完成了博客系统—— [IdealYard](https://github.com/imoyao/idealyard) 的雏形，当然，这距离臻于完美还有很长的路要走。但正所谓不怕走不到头，就怕一直不敢出发。虽然是个不起眼的项目，但是从无到有也消耗了不少精力，所以有必要做个简单记录。
## 缘起
一切缘起，都要从丘处机路过牛家村的那个下午说起……   
早就想动手搭建一个属于自己的博客项目，但是作为一名出色的国家一级退堂鼓表演家，总是找各种理由，一直未能计划成型落实。最后，终于在 G 小姐的鼓舞下开始着手编码了。
![不试试，怎么知道自己做不到呢？](/images/wx_img_20190910153859.jpg)

## 技术选型

因为主要开发语言是 Python，而目前 Python 社区已经发出公告将在 2020 年初停止 Python2 的维护。因此，选择使用 Python3 作为基本版本支持。在 [框架选择](/blog/2019-06-05/Flask-vs-webpy/) 问题上，虽然之前主要使用 Web.py 开发，但鉴于 Web.py 目前的维护现状和社区活跃度，所以选择更受开发者青睐的 Flask 作为后端 web 开发框架；此外，使用到 Celery 做一些耗时请求异步处理，如注册验证邮件发送和博客数据库备份（由于时间关系暂时未做）。而前端则使用目前热门的框架 Vue 和 Element-UI 来构建。

## 心路历程
虽然 Python2 与 Python3 之间有语法区别，但是基本用法方面也没有到“学习一种新语言”的地步，所以还算顺利。而 Flask 作为“一次一滴”的轻型框架，在刚开始的时候学习每一个子模块的使用感觉有点繁琐，用过几个之后感觉也挺顺利并逐渐喜欢上了这种理念。

前端方面呢，由于之前一直使用 `jQuery` 操作 DOM，所以一开始并不习惯这种 `MVVM` 设计模式，尤其是对生命周期的理解不够到位。话说回来，目前来说也还是有很多地方理解不够透彻，但是基本能够实现功能并简单优化。当然，道路是崎岖的，比如在使用 `axios` 发送请求连接前后端的时候，就出现了一些问题，尤其是在认证环节耗费了不少时间。其实是一个很细微的点，但是因为周围的同事都没有这方面的开发经验，所以一个人琢磨还是花费了不少的时间。

回首看来，没有打败你的最终都会让你更加强大，不过在第一次面对这些问题的时候还真是有点找不到北。

## 预览

<iframe class="bilibili" src="https://xbeibeix.com/api/bilibili/biliplayer/?url=BV11v411v76q" scrolling="no" border="0" frameborder="no" framespacing="0" allowfullscreen="true"> </iframe>

如果上方无法打开，请访问下方链接。

<iframe class="bilibili" src="//player.bilibili.com/player.html?aid=244176193&bvid=BV11v411v76q&cid=221300555&page=1&high_quality=1" scrolling="no" border="0" frameborder="no" framespacing="0" allowfullscreen="true"> </iframe>

## 交流
1. 技术问题请尽量使用[Issues · imoyao/idealyard](https://github.com/imoyao/idealyard/issues)提问回馈社区，参阅：[Issue #15 · imoyao/idealyard](https://github.com/imoyao/idealyard/issues/15)
2. 在网友的提议下建立了 QQ 群，群号：613922612。但是请注意：该项目为单纯开源，本人并不靠此盈利（有自己的砖要搬），在可预见的未来也**没有可能**投入到为大家答疑解惑中去。所以该群的目的更多是建立一个小白之间互相交流的途径。如果可能，请在公开场合讨论你的问题而不是简单地抛出截图等待答案。

![QQ 群扫码关注](https://cdn.jsdelivr.net/gh/imoyao/idealyard@master/document/src/idealyard-qq-group.png)

{%raw%}
<a target="_blank" href="https://qm.qq.com/cgi-bin/qm/qr?k=Em75uvDaupjSZzL-Y_C9FqzzFUUPiBAA&jump_from=webapi"><img border="0" src="//pub.idqqimg.com/wpa/images/group.png" alt="脚踏实地，仰望星空" title="Flask 交流群"></a>
{%endraw%}

3. 友善、友善、友善。网络一线牵，珍惜这段缘。请务必和善、诚恳地对待其他同学。

## 展望
目前基本完成了一个博客的完整功能，但是其实还有很多的小 Bug 需要解决。而且在开发的过程中又产生了一些新想法，还需要自己抽时间落地。具体请阅读 [我的博客 idealyard 待办事项记录](/blog/2019-08-29/blog-idealyard-TODO/)。

## 参考
本博客在编写过程中主要参考链接和书目有：
- [Element 官方文档](https://element.eleme.cn/#/zh-CN/component)
- [Vue 官方文档](https://cn.vuejs.org/v2/guide/index.html)
- [《Flask Web 开发实战》](https://book.douban.com/subject/30310340/)

{% blockquote 彭端淑,为学一首示子侄 %}
天下事有难易乎？为之，则难者亦易矣；不为，则易者亦难矣。人之为学有难易乎？学之，则难者亦易矣；不学，则易者亦难矣。
吾资之昏，不逮人也，吾材之庸，不逮人也；旦旦而学之，久而不怠焉，迄乎成，而亦不知其昏与庸也。吾资之聪，倍人也，吾材之敏，倍人也；屏弃而不用，其与昏与庸无以异也。圣人之道，卒于鲁也传之。然则昏庸聪敏之用，岂有常哉？
蜀之鄙有二僧：其一贫，其一富。贫者语于富者曰：“吾欲之南海，何如？”富者曰：“子何恃而往？”曰：“吾一瓶一钵足矣。”富者曰：“吾数年来欲买舟而下，犹未能也。子何恃而往！”越明年，贫者自南海还，以告富者，富者有惭色。
西蜀之去南海，不知几千里也，僧富者不能至而贫者至焉。人之立志，顾不如蜀鄙之僧哉？是故聪与敏，可恃而不可恃也；自恃其聪与敏而不学者，自败者也。昏与庸，可限而不可限也；不自限其昏与庸，而力学不倦者，自力者也。
{% endblockquote %}
