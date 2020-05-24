---
title: Git 常用操作
toc: true
date: 2020-05-23 18:21:46
tags:
- Git

---

## git 设置远程仓库和强制推送

```bash
git remote add origin git@github.com:XXXXX/demo.git  
git push -u origin master -f
```

慎用，此命令会删掉远程仓库的数据强行将本地仓库 push 至远程仓库

参考：[git 设置远程仓库和强制推送 - 三重罗生门 - 博客园](https://www.cnblogs.com/start2019/p/11465525.html)