---
title: 如何将代码打补丁（patch）？
date: 2020-11-04 17:57:53
tags:
- git
- 开源
categories:
---
## 前言
在基于开源项目做二次开发的时候，我们可能会在某一个版本号上开始，然后做开发。当开发进行一段时间之后，远程上面的代码可能已经和我们的代码大相径庭了，这个时候想要合并就会变得相对比较困难，所以在此记录一下流程。
## 工作流
### 查找 patch 开始的 id
一般来说，我们二次开发时会先拉取分支作为本地仓库，即第一次 git init 的内容是和开源某一个分支或者 tag 代码完全一致。
![init 提交](/images/Snipaste_2020-11-04_18-08-50.png)
所以我们需要把 init 之后的第一次代码作为补丁的开始端（该仓库第二次提交），找到该提交的 commi id。

### 生成 patch 文件
```plain
git format-patch 703ae2b80580e1xxx3f718d428572b50
```
### 应用 patch
1. 一般来说，我们使用`git am`就可以将补丁应用上去
```shell
imoyao@DESKTOP-NIQS11K MINGW64 /d/Gerrit/dashboard (master)
$ git am ../patches/0029-fix-bug-16115-fix-bug-16117.patch
Applying: fix bug 16115:关机之后无法点击开机;fix bug 16117:批量点灯也需要传节点名称;
```
没有 error 则表示补丁打成功了。但是，有的提交里面难免会有冲突，这个时候`am`打补丁会报错：
```shell
imoyao@DESKTOP-NIQS11K MINGW64 /d/Gerrit/dashboard (master)
$ git am ../patches/0031-fix-bug-16115-1.-socket-host.patch
error: patch failed: controllers/host.py:13
error: controllers/host.py: patch does not apply
error: patch failed: controllers/ipmitool.py:484
error: controllers/ipmitool.py: patch does not apply
Applying: fix bug:16115:xxx
Use 'git am --show-current-patch' to see the failed patch
When you have resolved this problem, run "git am --continue".
If you prefer to skip this patch, run "git am --skip" instead.
To restore the original branch and stop patching, run "git am --abort".
```
如果直接`am`报错（上一步不可跳过），此时操作流程如下：
2. 尝试以 apply 的方式直接 [reject](https://git-scm.com/docs/git-apply#Documentation/git-apply.txt---reject) 到源码上。
{% note info %}
**reject**
为了满足原子性，`git apply`命令默认在某些 hunks 无法应用时会直接返回失败且不会创建工作树，该配置使补丁可以部分应用同时将那些被拒绝的内容直接保留在`*.rej` 文件中。
{% endnote %}
> For atomicity, git apply by default fails the whole patch and does not touch the working tree when some of the hunks do not apply. This option makes it apply the parts of the patch that are applicable, and leave the rejected hunks in corresponding *.rej files.

 ```shell
git apply patches/0002-1.-2.-disk-host.get-api-3.-4.-utils-5.-conf.patch --reject
 ```
3. 手动解决冲突，找到 rej 文件，然后把冲突内容手动添加上去，之后手动删除 rej 文件。
```shell
git status | grep rej
rm xxx.rej
```
4. 之后提交代码，使用`git am`应用补丁：
{% note info %}
**--resolved**
补丁失败后(例如，试图应用冲突的补丁)，用户已经手动应用它并且索引文件存储应用的结果。使用从电子邮件消息和当前索引文件中提取的 author 和 commit 日志对内容进行提交，然后继续。
{% endnote %}
> After a patch failure (e.g. attempting to apply conflicting patch), the user has applied it by hand and the index file stores the result of the application. Make a commit using the authorship and commit log extracted from the e-mail message and the current index file, and continue.

 ```shell
 git add .
 git am --resolved
 ```
5. 查看日志，之前提交的内容应该已经作为补丁应用到新代码上面了。
```shell
git log
```

## 参考链接
[Git - git-am Documentation](https://git-scm.com/docs/git-am)
[Git - git-apply Documentation](https://git-scm.com/docs/git-apply)
[git 打补丁方法总结_JT 的专栏-CSDN 博客](https://blog.csdn.net/sinat_20059415/article/details/80598347)