---
title: Hexo 主题 Butterfly 自定义之路
tags:
  - Hexo
  - Butterfly
cover: /images/krzysztof-niewolny-f8JYQPq45uI-unsplash.jpg
categories:
  - 博客个性化
date: 2020-01-06 21:32:01
reward: true
subtitle: 生命不息，折腾不止
---
本文主要针对 hexo-theme-butterfly 主题进行了个性化自定义，并对修改内容做了简单介绍。
<!--more-->
{%note no-icon%}
原作者文档👉 [hexo-theme-butterfly 安装文档](https://demo.jerryc.me/)
{%endnote%}
## 已完成

### 美化

#### svg 背景

使用 [SVG 编辑器](https://c.runoob.com/more/svgeditor/) 修改
- footer 背景
```plain
- var footer_img =  theme.footer_bg.footer_img
      - var footer_bg = theme.footer_bg.enable == false ? '' : `background-image: url(${footer_img})`
      - var is_bg = theme.footer_bg.enable == false ? 'color' : 'photo'
```
- 友链头像 404 默认图
- 评论区背景图

#### page 背景图
 在原作者的基础上添加了修改 books 页面 bg 的 strict，不得不说作者真的很细心。
 ```jade
if theme.douban_background.enable
    if is_current('/movies/', [strict])
      - var source = theme.movie_background
    if is_current('/books/', [strict])
      - var source = theme.book_background
    if source
      - var bg_img = `background-image: url(${source})`
      #web_bg(data-type='photo' style=bg_img)
 ```
#### 网站 logo
```jade
    //更换文字为logo图片
  //a#site-name.blog_title(href=url_for('/')) #[=config.title]
  a#site-name.blog_title(href=url_for('/'))
    - var site_logo = theme.site_logo
    - var site_patch = `background: url(${site_logo})`
    span.site-logo(style=site_patch)
```
```styl
//网站换为图片之后加样式
    .site-logo
      display: inline-block;
      vertical-align: middle;
      width: 150px;
      height: 40px
      background-size: cover!important;
```

#### 表格美化

|姓名|年龄|性别|民族|
|:---:|:---|---:|:---:|
|张三丰|100|男|汉族|
|张翠山|35|男|汉族|
|殷素素|33|女|汉族|
|张无忌|12|男|汉族|
|赵敏|12|女|蒙古族|
|小昭|12|女|波斯人|

参考 [Hexo 下表格的美化和优化](https://hexo.imydl.tech/archives/6742.html)

### 新增

#### 标签外挂
- [x] ~~参考`Next`[主题外挂](https://hexo-theme-next.netlify.com/docs/tag-plugins/)~~
参见[此处](https://vuejs.org/v2/cookbook/serverless-blog.html) note 挂件；
建议阅读[標籤外掛(Tag Plugins) | Butterfly](https://demo.jerryc.me/posts/2df239ce/)
`gallery`已经实现需求，所以没有必要实现了。
{% gallery %} 

![](https://images.unsplash.com/photo-1578028076641-ef1d08387c14?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=1350&q=80) 

![](https://images.unsplash.com/photo-1557244056-ac3033d17d9a?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=634&q=80) 

![](https://i0.hippopx.com/photos/121/457/241/girls-the-scenery-wallpaper-7f97112750013868bc5bcc249f13e27d.jpg) 

![](https://cdn.jsdelivr.net/gh/masantu/statics/images/p458733229.jpg) 

![](https://picjumbo.com/wp-content/uploads/iphone-free-stock-photos-2210x3315.jpg) 
![](https://images.unsplash.com/photo-1529245814698-dd66c442bfef?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=1350&q=80) 
{% endgallery %}

#### 用户状态
- [x] 用户卡片页显示个人工作状态（支持 fa 和 emoji 😀）
头像 hover 事件修改
参考此处实现[头像不翻转，鼠标 hover 放大](https://vwin.github.io/2018/08/02/Hexo-Next%E4%B8%BB%E9%A2%98%E5%A4%B4%E5%83%8F%E6%97%8B%E8%BD%AC/)
```styl
.card-info
    img
      display: inline-block
      width: 110px
      height: 110px
      border-radius: 70px
      vertical-align: top
      margin: 0 auto
      webkit-transition: 1.4s all
      moz-transition: 1.4s all
      ms-transition: 1.4s all
      transition: 1.4s all

      &:hover
        background-color: $avatar-bg
        webkit-transform: rotate(360deg) scale(1.1)
        moz-transform: rotate(360deg) scale(1.1)
        ms-transform: rotate(360deg) scale(1.1)
        transform: rotate(360deg) scale(1.1)
```

#### footer 页面
- [x] 添加 badge
```pug
#/Butterfly/layout/includes/footer.pug
```

#### iframe 实现 [豆瓣书影音](/douban/) 页面
```html
<!--用户名替换为自己的豆瓣id-->
<div id="iframe">
    <iframe height="100%" src="https://m.douban.com/people/imoyao/subject_profile" sandbox="allow-forms allow-scripts allow-same-origin allow-popups"></iframe>
</div>
```
#### 实现 Netlify CMS 管理
使用[Hexo Netlify CMS](https://github.com/jiangtj/hexo-netlify-cms)实现
参考[将 Hexo 静态博客部署到 Netlify | reuixiy](https://io-oi.me/tech/deploy-static-site-to-netlify/)

#### 吐个槽
- [x] 侧边栏添加吐个槽，用户可以进行反馈

### 改进

#### 文章页 sidebar 图标
- [x] 更换另外一种图标，同时 hover 变成显眼按钮

#### 个人信息
- [x] 图标显示风格左右旋转而不是上下颠倒

#### 赞赏
鉴于国人现实经济状况，只有在`font-matter`中添加`reward: true`才会打开赞赏功能；
```jade
// themes/Butterfly/layout/post.pug
if theme.reward.enable && page.reward
```
#### page 页侧边栏
- [x] 不要展示只看一次就可以的信息（如网站概览，公告等）
- [x] 只在首页显示公告和网站概览；跳到对应页时，侧边栏不显示对应 card（避免信息重复）；
```plain
layout/includes/widget/index.pug
```
#### 文章页结束语
```jade
  //结束语分割线
    .divider.divider-horizontal.divider-with-text-center(role='separator')
      span.divider-inner-text=theme.divider_text
```

## TODO

### 原作者废弃
- [x] 文章 front matter: hide 支持

### 新增

#### 首页添加描述卡
- [x] 自述页面
- ~~music~~
- ~~video~~

#### 添加 logos 页面存放网站 logo 等个人信息
参考
- [Ceph Logos - Ceph](https://ceph.io/logos/)
- [The Python Logo | Python Software Foundation](https://www.python.org/community/logos/)

#### page 页
- [x] 增加正文结束分割线，可以自定义分割线文字内容；
- [x] 修改 books、movies 页面的背景，更加沉浸式；
    TODO:暂时页面 id 重复未解决

### 侧边栏
- [x] 给友链页面中的朋友栏增加首页友链卡；
- [x] 侧边栏只显示 20 条 tag，剩余的访问 tag 页面才能看到；
- [x] [豆瓣历史](/douban/)页面不显示侧边栏；
```jade
      //douban 页面特殊处理
  else if page.type === 'douban'
    article#page.no-aside-page
      .article-container!= page.content
```

### 摘要
- [x] 目前的摘要功能应该是我没有配置好，感觉没有生效；
```jade
 - var specific_desc = article.description || article.subtitle || article.excerpt
      if specific_desc
        .content!= specific_desc
      else if theme.auto_excerpt && theme.auto_excerpt.enable
        - const content = strip_html(article.content)
        - let expert = content.substring(0, theme.auto_excerpt.length) 
        - content.length > theme.auto_excerpt.length ? expert += ' ...' : ''
        .content!= expert
```
> 因为主题 UI 的关系，主页文章节选只支持自动节选和文章页 description。优先选择自动节选。
> 在 butterfly.yml 里可以开启 auto_excerpt 的选项，你的文章将会在自动截取部分显示在主页。（默认显示 150 个字）。
```ymal
 auto_excerpt: 
 enable: true 
 length: 150
```

### 编辑直达
- [ ] 首页增加 [后台管理](https://imoyao.netlify.com/admin/#/) navbar；
- [ ] 文章页添加编辑按钮（？）；
    参考主题 [wzpan/hexo-theme-freemind: Most powerful bootstrap theme for hexo.](https://github.com/wzpan/hexo-theme-freemind) 实现

### 暗色模式
- [x] 一些自定义样式修改；

### 简化部署
在站点配置文件中修改远程部署仓库信息如下：
```yml
deploy:
  type: git
  repo:
    github: https://github.com/imoyao/imoyao.github.io.git
    gitee: https://gitee.com/imoyao/imoyao.git
```
其中地址修改为你的仓库的地址。具体说明见[此处](https://blog.csdn.net/tsvico/article/details/80629452)；同时还可以将代码推送到两个仓库中，参考[此处](https://www.jianshu.com/p/747e2bb71775)：
```bash
git remote set-url --add origin {你的 gitee 项目地址}
```
（当然我们也可以手动点击 gitee 网页上的同步按钮强制从 github 上更新）