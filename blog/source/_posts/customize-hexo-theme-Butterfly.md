title: Hexo 主题 Butterfly 自定义之路
tags:
  - Hexo
  - Butterfly
cover: >-
  https://d33wubrfki0l68.cloudfront.net/6657ba50e702d84afb32fe846bed54fba1a77add/827ae/logo.svg
categories:
  - 博客美化
date: 2020-01-06 21:32:01
---
## 改进

### svg 背景

使用 [SVG 编辑器](https://c.runoob.com/more/svgeditor/) 修改 footer、评论区背景图；

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
- [ ] 参考`Next`主题外挂
 [tag-plugins](https://hexo-theme-next.netlify.com/docs/tag-plugins/)

### 实现 Netlify CMS 管理

使用[Hexo Netlify CMS](https://github.com/jiangtj/hexo-netlify-cms)实现

参考[将 Hexo 静态博客部署到 Netlify | reuixiy](https://io-oi.me/tech/deploy-static-site-to-netlify/)

#### page 页侧边栏
- [x] 不要展示只看一次就可以的信息（如网站概览，公告等）

## TODO

### 新增

#### 首页添加描述卡
- self introduce
- music
- video

#### 状态
- [ ] 用户卡片页显示个人状态

#### 编辑直达
- [ ] 首页增加 [后台管理](https://imoyao.netlify.com/admin/#/) navbar
- [ ] 文章页添加编辑按钮(?)
