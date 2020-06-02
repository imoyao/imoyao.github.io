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

## 删除已经跟踪的文件或者目录

这种情况就是说：之前不小心把一些本不应该提交的文件或目录提交上去了，现在发现了，需要对上游仓库进行删除，同时本地不再跟踪文件变化。
1. 首先修改`.gitignore`，排除要删除的文件。
2. 按照如下执行，分别删除本地和git跟踪
```bash
rm -rf {file name}    # 删除本地文件
git rm -r --cached {file name}  #从index中删除（不再跟踪）
```
3. 提交修改
```bash
git add -A/. # 添加到暂存区
git push origin {branch name}   # 推送到远程仓库
```
看一下`git rm`的用法
> $ git rm -r --cached
> usage: git rm [<options>] [--] <file>...
>
>    -n, --dry-run         dry run
    -q, --quiet           do not list removed files
    --cached              only remove from the index
    -f, --force           override the up-to-date check
    -r                    allow recursive removal
    --ignore-unmatch      exit with a zero status even if nothing matched

{%note primary%}
如果同名的文件过多，如：`.class` 文件被提交了，那么如果这样一个个显然效率太低，可以按照下面方法操作:
```bash
find . -iname {filename} -exec rm -rf {}\
```
重复上面的步骤，将文件名替换为下一个要删除的文件名
{%endnote%}

参见：[删除git已经跟踪的文件或者目录 - 简书](https://www.jianshu.com/p/706560653753)