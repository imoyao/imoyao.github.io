---
title: Hexo 主题 Butterfly 自定义之路
tags:
  - Hexo
  - Butterfly
cover: /images/krzysztof-niewolny-f8JYQPq45uI-unsplash.jpg
categories:
  - 博客美化
date: 2020-01-06 21:32:01
reward: true
---
{%note no-icon%}
原作者文档👉 [hexo-theme-butterfly 安装文档](https://jerryc.me/posts/21cfbf15/)
{%endnote%}
## 已改进

### svg 背景

使用 [SVG 编辑器](https://c.runoob.com/more/svgeditor/) 修改 footer、友链头像 404、评论区背景图；

### 表格美化

|姓名|年龄|性别|民族|
|:---:|:---|---:|:---:|
|张三丰|100|男|汉族|
|张翠山|35|男|汉族|
|殷素素|33|女|汉族|
|张无忌|12|男|汉族|
|赵敏|12|女|蒙古族|
|小昭|12|女|波斯人|

参考 [Hexo 下表格的美化和优化](https://hexo.imydl.tech/archives/6742.html)

### 文章
~~- [ ]参考`Next`[主题外挂](https://hexo-theme-next.netlify.com/docs/tag-plugins/)~~
`gallery`已经实现需求，所以没有必要实现了。
{% gallery %} 

![](https://images.unsplash.com/photo-1557244056-ac3033d17d9a?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=634&q=80) 

![](https://cdn.jsdelivr.net/gh/masantu/statics/image/p458733229.jpg) 

![](https://picjumbo.com/wp-content/uploads/iphone-free-stock-photos-2210x3315.jpg) 
![](https://images.unsplash.com/photo-1529245814698-dd66c442bfef?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=1350&q=80) 
{% endgallery %}

#### 状态
- [x] 用户卡片页显示个人工作状态（支持 fa 和 emoji 😀）

#### footer 页面
- [x] 添加 badge

#### 背景图
 在原作者的基础上添加了修改 books 页面 bg 的 strict，不得不说作者真的很细心了。
 ```jade
 else if is_current('/books/', [strict])
  - var top_img = theme.books_img || theme.default_top_img
 ```
#### 赞赏
鉴于国人现实经济状况，只有在`font-matter`中添加`reward: true`才会打开赞赏功能；
```jade
// themes/Butterfly/layout/post.pug
if theme.reward.enable && page.reward
```
 
### 实现 Netlify CMS 管理
使用[Hexo Netlify CMS](https://github.com/jiangtj/hexo-netlify-cms)实现
参考[将 Hexo 静态博客部署到 Netlify | reuixiy](https://io-oi.me/tech/deploy-static-site-to-netlify/)

#### page 页侧边栏
- [x] 不要展示只看一次就可以的信息（如网站概览，公告等）
{% note success %}
只在首页显示公告和网站概览；跳到对应页时，侧边栏不显示对应 card（避免信息重复）；
{%endnote%}

## TODO

### 新增

#### 首页添加描述卡
- [x] self introduce
- ~~music~~
- ~~video~~

#### page 背景图
- [x] 修改 books、movies 页面的背景，更加沉浸式;
    TODO:暂时页面 id 重复未解决

#### 编辑直达
- [ ] 首页增加 [后台管理](https://imoyao.netlify.com/admin/#/) navbar
- [ ] 文章页添加编辑按钮(?)