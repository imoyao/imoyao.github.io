---
title: Hexo 同时使用两种主题（博客与wiki页面实现统一管理）
toc: true
date: 2020-05-23 11:02:28
tags:
- Hexo
- wiki
- 博客
categories:
- 博客个性化
---

## 缘起
想在博客系统的基础上搭建一个 [wiki系统](/wiki) ，用于实现一些知识体系的积累。当然可以通过创建两个hexo仓库分别用于渲染博客页面（主题一）和wiki页面（主题二）；但是每次进行知识管理的时候就要切换不同的仓库目录，而且部分文件可能产生冗余（如：npm install 产生的node_modules），所以本文实践利用一个hexo仓库内渲染生成使用不同theme生成主页和wiki页面，以实现一次部署和统一管理。

## TL;DR
[使用代替配置文件-配置 | Hexo](https://hexo.io/zh-cn/docs/configuration#%E4%BD%BF%E7%94%A8%E4%BB%A3%E6%9B%BF%E9%85%8D%E7%BD%AE%E6%96%87%E4%BB%B6)
```
hexo --help
Global Options:
  --config  Specify config file instead of using _config.yml 
```
root目录下有两个config文件，默认使用`_config.yml`，用`hexo --config config_wiki.yml g`命令渲染`wiki`页面至`/public/wiki/`，同时设置点击主页面`wiki`导航栏后自动跳转到`public/wiki/`。

## 修改步骤

1. 更改原主页面的theme的config文件，增加navbar类别（不同主题设置字段不同）；
```
Wiki: /wiki/
```
2.  为了避免在修改wiki配置时影响到主页面，将root目录下的`_config.yml`文件（即站点配置文件），复制并重命名为`_config_wiki.yml`，以下修改均指此文件。

3.  安装hexo的[Wikitten](https://github.com/zthxxx/hexo-theme-Wikitten)主题，将其作为wiki页面的theme；
```
cd your-hexo-directory
git clone https://github.com/zthxxx/hexo-theme-Wikitten.git themes/Wikitten
```
此外，你也可以选用其他风格wiki主题，如：[wzpan/hexo-theme-wixo: A wiki theme for Hexo.](https://github.com/wzpan/hexo-theme-wixo)
4.  将Wikitten theme目录下clone所得的source和模板移动到root目录下，重命名主题config使其生效。
```
cp -rf themes/Wikitten/_source/* wiki/
cp themes/Wikitten/_scaffolds/embed.md scaffolds/embed.md
cp themes/Wikitten/_scaffolds/post.md scaffolds/wiki.md
cp -f themes/Wikitten/_config.yml.example themes/Wikitten/_config.yml
```
5.  修改wikitten主题的config，更改资源文件目录，logo、favicon等。

6.  修改`_config_wiki.yml`设定使wikitten主题生效
```
- theme: origin
+ theme: Wikitten

- per_page: 10

- url: https://masantu.com/
- root: /
- permalink: :year/:month/:day/:title/
+ url: https://masantu.com/wiki/
+ root: /wiki/
+ permalink: :title/
+ permalink_defaults: :year/:month/:day/:title/

+ skip_render:
+  - README.md

+ marked:
+   gfm: true

+ # 设置单独的source文件夹，用于放置wiki的源文件
- source_dir: source
+ source_dir: wiki

+ # 设置渲染到`public/wiki/`路径下
- public_dir: public
+ public_dir: public/wiki

+ default_layout: wiki
```

##  使用
### 创建别名（可选）
主要目的是简化输入，如果不嫌麻烦，可以每次输入指令。
- linux
视自己情况而定，在`.zshrc`或者`.bashrc`等文件中新增alias
```bash
alias hwk="hexo --config _config_wiki.yml"
```
- windows
```dos
doskey hwk=hexo --config _config_wiki.yml
```
参见：
1. [ windows系统如何给命令起别名？ - 知乎](https://www.zhihu.com/question/51962577)
2. [Windows alias 给cmd命令起别名 - jetwill - 博客园](https://www.cnblogs.com/chenjo/p/12550207.html)

### 新建wiki
如果跳过上步，则将下面的指令中的`hwk`替换为`hexo --config _config_wiki.yml`
```
hwk new "xxxx"
```
### 渲染页面
共用db.json（猜測）会导致主页面blog内容与wiki内容混杂，需要在渲染前后进行clean操作。
1. 首先渲染主页面，生成到/public/
```
hexo g
```
2. 删除db.json及旧的public/wiki
```
hwk clean
```
3. 渲染wiki页面，生成到/public/wiki/
```
hwk g
```
4. 手动删除db.json，**MUST！**
```
rm db.json
```
[db.json file is created and added to .gitignore using hexo.io - Stack Overflow](https://stackoverflow.com/questions/25389051/db-json-file-is-created-and-added-to-gitignore-using-hexo-io)
[hexo流程梳理之database | john's tech blog](https://johnwonder.github.io/2016/10/17/hexo-flow-second/)
5. 查看效果
```
hexo s
```

## 参考链接
[Hexo 同时使用两种主题](https://konfido.github.io/2019/03/16/hexo-wiki/)
