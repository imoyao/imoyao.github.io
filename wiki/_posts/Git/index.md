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

## git 放弃暂存区的修改
1. 放弃暂存区的修改
```bash
git reset HEAD
```
2. 对比
```bash
git diff --cached  

```
3. 删除工作区内容
```bash
git clean -d -f
```
4. 从远程仓库拉取
```bash
git pull
```
[Git 撤销工作区的所有修改并删除暂存区文件_git_Acettest's Blogs-CSDN 博客](https://blog.csdn.net/u010178308/article/details/86167195)

## 查看某个指定文件的修改历史

```bash
git log --follow -p {file_path}
```

## 新建分支(以mydev为例)并推送
```bash
git checkout -b mydev
git push origin mydev:mydev
```