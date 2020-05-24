---
title: 我的博客 idealyard 待办事项记录
date: 2019-08-29 19:28:06
tags:
- 博客
- Flask
- 开源
- TODO
categories:
- Projects
- IdealYard
cover: /images/photo-1475767770551-49f1b43f71cd.jpg
---

## BUGs 记录

### 前端

- [x] 新建文章报错；
- [x] 首页无限滚动时提示`Duplicate keys detected: 'xxxx'. This may cause an update error.`
- [x] 用户注册页面；
    - [x] 用户注册成功，但是跳转首页之后显示问题；
- [x] 用户写文章时，作者不是当前登录用户；
- [x] 点击页内锚点，跳转到文章分类页面，应该在本页面内跳转；
- [x] cookie 中密码没有加密；
 解决办法[参考这里](https://www.cnblogs.com/xiaolucky/p/11165179.html)
- [x] token 超时时弹出很多 message,应该使用更友好的方式！或者精准提示，一次只提示一条即可；
    解决办法：[如何让 Element UI 的 Message 消息提示每次只弹出一个](https://segmentfault.com/a/1190000020173021)
- [x] 标签云  
 1.  ~~参考[这里](https://github.com/MikeCoder/hexo-tag-cloud)~~
 2. [这里](https://juejin.im/post/5c99a0f7e51d454e9b3c3343)
 3. ~~[这里](https://github.com/nobalmohan/vue-tag-cloud)~~  
最终参考[VueWordCloud](https://github.com/SeregPie/VueWordCloud) 实现；
- [x] 记住密码；
- [x] 标签、分类页面，item 数量为 0 时，点击事件 disable；
- [x] 找回密码；
 - [x] 前端异常处理；

- [x] 盘古之白
> 有研究显示，打字的时候不喜欢在中文和英文之间加空格的人，感情路都走得很辛苦，有七成的比例会在 34 岁的时候跟自己不爱的人结婚，而其餘三成的人最后只能把遗產留给自己的猫。毕竟爱情跟书写都需要适时地留白。
[中文文案排版指北](https://github.com/sparanoid/chinese-copywriting-guidelines)
 1. [python 版本](https://github.com/hustcc/hint)
 2. [python 版本](https://github.com/hjiang/scripts/blob/master/add-space-between-latin-and-cjk)
 3. [JS 版本](https://github.com/hustcc/lint-md/tree/master/packages/lint-md)
- [x] 首页摘要信息获取错误
- [x] 概览页（index）显示
- [x] 更新文章，对原有标签删除时，不成功，但新加正常
- [x] 首页点击查看全部进入空白页
- [x] 编辑文章时已经存在的标签会二次添加（查询中间表可以看到写了两次！）  
    ~~1. 新建标签失败~~  
    ~~2. 标题无法修改（目前有该入口，正常来说应该是可以更新的<除非代码没有这块逻辑，如果没有，则不添加，文章新建之后就不要改变链接了>）~~
- [x] 文章详情页 header 下划线显示异常
    
### 后端

- [x] 数据库迁移报错
    ```plain
    werkzeug.utils.ImportStringError: import_string() failed for 'mains.bp'. Possible reasons are:
    
    - missing __init__.py in a package;
    - package or module path not included in sys.path;
    - duplicated package or module name taking precedence in sys.path;
    - missing module, class, function or variable;
    
    Debugged import:
    
    - 'mains' not found.
    
    Original exception:
    
    ModuleNotFoundError: No module named 'mains'
    ```
- [x] 未注册用户登录（假用户）无提示，后台报错:
    ```plain
    TypeError: unauthorized() takes 0 positional arguments but 1 was given
    ```
- [x] 首页热门标签应该显示最热，而不是全部
- [x] 首页点标签名称，进去之后的名称 title 不对

## TODO

### 已完成

- [x] 文章阅读计数
- [x] 添加获取用户信息 API
- [x] 博客自己修改  
  - [x] view 页面需要 summary,因为在编辑时，摘要不能消失；  
  - [x] 编辑时需要对新的和旧的标签对比，正常不走 add 逻辑；  
  - [x] 编辑时应该是 post 请求，将用户提交的全量更新，没有的置空；
- [x] 博客作者自己删除
- [x] slug 选项在更新文章时应该是不可见的（url 确定之后不可修改！）
- [x] 链接由 id 变成数字和 slug 的组合
- [x] 找回密码
    - [x] 生成随机密码，给用户发送明文，并把数据库中数据加密更新保存；
    - [x] 用户输入一次之后过期；（Redis？~~Celery 清除？~~）
    - [x] 通过则设置密码，否则重新发送并重新设置密码；
    
### 待完成
- [x] ~~访问已删除文章时，不会跳转到首页！~~
 - [ ] 目前可以跳转，但是由于 abort() 函数，导致会有报错闪现。
- [ ] 用户邮箱验证，如果没有验证，则在首页提示用户去验证，完成验证之后才可以写文章；否则登录也无法进行有效操作。
   - [x] 消息提示已完成；
   - [ ] 需要完成激活邮箱；
- [ ] 使用 swagger 生成 Flask RESTful    
    参考[使用 swagger 生成 Flask RESTful API - 古寺比的寺 - SegmentFault 思否](https://segmentfault.com/a/1190000010144742)
- [ ] `vendor`文件过大，导致首页刷新时间过长；
 参考[这里](https://forum.vuejs.org/t/vue-cli-vendor-js/37246)  
 参考[这里](https://segmentfault.com/q/1010000008832754)  
 参考[这里](https://www.jianshu.com/p/e78c2210c410)
- [ ] 使用`盘古之白`之后不能输入`emoji`表情；
 ```shell
  pymysql.err.InternalError: (1366, "Incorrect string value: '\\xF0\\x9F\\x98\\x98</...' for column 'content_html' at row 1")
 ```
- [ ] 链接的 slug 中直接把 emoji 也给显示出来了，此处需要对 emoji 进行过滤或者转换为字符说明。
 1. [removing emojis from a string in Python - Stack Overflow](https://stackoverflow.com/questions/33404752/removing-emojis-from-a-string-in-python)
 2. [Python - replace unicode emojis with ASCII characters - Stack Overflow](https://stackoverflow.com/questions/43797500/python-replace-unicode-emojis-with-ascii-characters/43813727#43813727)
- [ ] 需要增加用户详情页（about?），可编辑用户信息；
- [ ] 使`aside`侧边栏固定，不会随鼠标滚动消失；
- [ ] 参考博客后端管理系统；
 - [基于 vue 全家桶 + element-ui 构建的一个后台管理集成解决方案](https://github.com/uncleLian/vue-blog)
 - [vue-admin](https://github.com/taylorchen709/vue-admin)
 - [vue-element-admin](https://github.com/PanJiaChen/vue-element-admin)
- [ ] 自适应时 footer 只有半个；
- [ ] 时间线无法正常显示；
- [ ] 使用`celery`备份博客
 1. 每创建一篇文章；自动生成`xxxx.md`用于静态博客；
 2. 每个月备份数据库；将数据库通过邮件发送到本人邮箱；
- [x] 发送邮件改为`Celery`异步

---

优先级中等
- [ ] 管理员账户
- [ ] 标签管理员手动添加
- [ ] 分类管理员手动添加
- [ ] i18n（en&zh）
- [ ] 前端文件太大[继续优化博客 Vue+Webpack 生成的 Javascript 文件体积 - 小明明 s à domicile](https://www.dongwm.com/post/optimize-javascript/)

---
优先级低

- [ ] 移动端自适应