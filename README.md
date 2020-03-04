# 别院牧志

[![Netlify Status](https://api.netlify.com/api/v1/badges/88e1a8bd-d248-4658-8373-0ff1b81442c1/deploy-status)](https://app.netlify.com/sites/santu/deploys)

> 本分支用来存放站点的`sources`文件

## `LaTex` 在线公式编辑器

- [国内版](http://latex.91maths.com/)
- [国际版](http://latex.codecogs.com/eqneditor/editor.php)

## lint 工具

使用[lint-md](https://github.com/hustcc/lint-md) 检查并修复博客中的`md`文件
```bash
lint-md MD_FILE_PATH -f
```

## 修改作者信息
参考[这里](https://stackoverflow.com/questions/750172/how-to-change-the-author-and-committer-name-and-e-mail-of-multiple-commits-in-gi)     
```shell
sh ./change_user_info.sh
```

## TODO
 - [ ] homepage 着陆页，其他页面没有必要用那么大的首页，影响效率。
   [主题发现](https://www.zhihu.com/question/24422335/answer/853599441) 
   参考[hexo-theme-matery](http://ghang.top/) 
 - [ ] 友链页面参考[agency](https://startbootstrap.com/themes/agency/)改进
 - [x] 分享功能好像不好用？
 - [ ] 文章过期提示“font mater”
    优化显示参考[此处](https://docs.netlify.com/configure-builds/common-configurations/#javascript-spas)
    
  更多阅读[Hexo 主题 Butterfly 自定义之路](https://www.masantu.com/blog/2020-01-06/customize-hexo-theme-Butterfly/)
 
