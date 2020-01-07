---
title: 在搭建 Hexo 中遇到的问题记录
date: 2017-11-18 13:12:12
cover: https://d33wubrfki0l68.cloudfront.net/6657ba50e702d84afb32fe846bed54fba1a77add/827ae/logo.svg
tags:
- HOWTO
- Hexo
- 博客优化
categories:
- 教程记录
---

在网络上搜索一天多才磕磕绊绊搭建好这个博客，⁄(⁄ ⁄•⁄ω⁄•⁄ ⁄)⁄ 现在把过程中遇到的坑记录一下，希望可以给之后的同学们带来帮助。
<!--more-->

## npm 包管理安装太慢怎么办

- 临时使用
```shell
 npm --registry https://registry.npm.taobao.org install express
```
- 持久使用(更换源链接为淘宝源)
```shell
npm config set registry https://registry.npm.taobao.org
# 配置后可通过下面方式来验证是否成功
npm config get registry
# 或者
npm info express
```
- 通过 cnpm 使用
```plain
npm install -g cnpm --registry=https://registry.npm.taobao.org
# 使用
cnpm install expresstall express
```

还可以参考下面这个工具:

[nrm —— 快速切换 NPM 源 （附带测速功能）](https://segmentfault.com/a/1190000000473869)

## 我有两台电脑/换电脑后如何重新发布博客

使用 Github 的 branch 功能建立两个分支，（如：master 和 hexo）设置 hexo 分支为默认分支，然后将博客后台配置文件全部`push`到该分支。master 端为使用`hexo d`命令发布分支。

**注：**master 分支不能当作他用，只能作为 hexo 发布之后使用。

可以参考下面链接配置
[Hexo 博客从一台电脑迁移到其他电脑 - 简书](http://www.jianshu.com/p/beb8d611340a)

## 如何设置腾讯公益为 404 页面

以下是知乎网友给出的回答：

> 直接在 source 根目录下创建自己的`404.html`即可。~~但是自定义 404 页面仅对绑定顶级域名的项目才起作用。~~

经我试验并不一定要绑定顶级域名才可以，使用官方给出的方案设置后并不能实现错误页 页面跳转到我们设置的 404 页面。
以下来自 github 网友在 issues 中的解释：
> 你的站点(编注：二级域名即 Github)启用了 https，腾讯公益 404 的脚本是 http 协议，因此这段脚本被阻止了。

解决的方法是将页面里的 script 换成如下：

```javascript
  <script type="text/plain" src="http://www.qq.com/404/search_children.js" charset="utf-8" homePageUrl="/" homePageName="回到我的主页"></script>
  <script src="https://qzone.qq.com/gy/404/data.js" charset="utf-8"></script>
  <script src="https://qzone.qq.com/gy/404/page.js" charset="utf-8"></script>
```
经试验该方法还是会出现问题，使用 F12 审查元素出现报错信息。最后使用以下方案解决该问题:

[使腾讯 404 公益页面支持 HTTPS](https://eason-yang.com/2016/08/06/set-tencent-lostchild-404-page-for-ssl/)

目前存在问题：页面会有一个卡顿加载的过程，该页面没有适配移动端。

## Next 主题文章页如何设置多标签

在文章发布页（MARKDOWN 文件顶部）添加如下字段:

```plain
title: 在搭建Hexo中遇到的问题记录
# 标签（注意短横杠后的空格）
tags:
- HOWTO
- Hexo
- Hexo-Next
- etc.
author: imoyao
```
## 如何给博客文章页添加音乐

可以用音乐网站的外链，但是一般外链是`<iframe>`，据说这个方法影响网站的 SEO。

下面我就隆重介绍一款 `HTML5` 音乐播放器——`Aplayer`。需要用到`hexo-tag-aplayer`插件。

切换到本地 Hexo 目录，运行：
```shell
npm install hexo-tag-aplayer@2.0.1
```
添加音频语法如下：

```plain
#This is a example.
{% raw %}

{% aplayer "平凡之路" "朴树" "https://xxx.com/%E5%B9%B3%E5%87%A1%E4%B9%8B%E8%B7%AF.mp3" "https://xxx.com/1.jpg" "autoplay" %}
就会出现你想要的音乐啦。

{% aplayer "蓝莲花" "许巍" "http://oh6j8wijn.bkt.clouddn.com/%E8%93%9D%E8%8E%B2%E8%8A%B1.mp3" "http://oh6j8wijn.bkt.clouddn.com/133107859321201106e3c3ede9a13305.jpeg" "autoplay" %}`

{% endraw %}

```
如果你想加入歌单，更多参数的配置可以参照[插件](https://github.com/MoePlayer/hexo-tag-aplayer)的使用说明。

## TODO
`material` 主题填坑

## 参考链接
1. [开始使用 - NexT 使用文档 ](http://theme-next.iissnan.com/getting-started.html)
2. [GitHub+Hexo 搭建个人网站详细教程](https://zhuanlan.zhihu.com/p/26625249)
2. [hexo添加音乐、high一下及一些坑 | tc9011's](http://tc9011.com/2016/12/24/hexo%E6%B7%BB%E5%8A%A0%E9%9F%B3%E4%B9%90%E3%80%81high%E4%B8%80%E4%B8%8B%E5%8F%8A%E4%B8%80%E4%BA%9B%E5%9D%91/)
