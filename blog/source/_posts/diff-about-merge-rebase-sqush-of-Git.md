---
title: Git merge/rebase/squash 的区别
date: 2020-01-08 22:13:53
tags:
- Git
cover: /images/logos/Git.svg
---

### git merge
如果 A 同学选择用 git merge 的方式进行合并 dev 到 master 分支，那么 git 会这么做：

1. 找出 dev 分支和 master 分支的最近共同祖先 commit 点；
2. 将 dev 最新一次 commit 和 master 最新一次 commit 合并后生成一个新的 commit，有冲突的话需要解决冲突；
3. 将以上两个分支 dev 和 master 上的所有提交点按照提交时间的先后顺序进行依次放到 master 分支上；

### git rebase 后再 git merge
1. rebase 之前需要经 master 分支拉到最新；
 ```plain
 git checkout master
 git pull
 ```
2. 切换分支到需要 rebase 的分支，假定是 dev 分支；
 ```bash
 git checkout dev
 ```
3. 变基，执行 `git rebase -i master`，有冲突就解决冲突，解决后直接 `git add` ，再 逐步`git rebase --continue` ；
注意，这里的变基其实就是找到两个分支共同的祖先，然后在当前分支上合并从共同祖先到现在的所有 commit，所以我们在第二步的时候会选择怎么处理这些 commit，然后我们就得到了一个从公共 commit 到现在的单个 commit，将 commit 合并到 master 也只会在 master 上留下一个 commit 记录，而在 dev 分支上的开发者的操作已经被合并改写了；

4. 切换到 master 分支，执行 `git merge dev`；

### squash merge

在使用 git 的过程中，可能你遇到过想要合并多个 commit 为一个，然后很多人会告诉你用 `git commit --amend`，然后你发现里面有你的多个 commit 历史，你可以通过 pick 选择，squash 合并等等。同样的，merge 的时候也可以这么干，你只需要这么简单的两步：
1. 切换到目标分支：`git checkout master`
2. 以 squash 的形式 merge：`git merge --squash devel`
你会发现，在 master 分支上居然有未提交的修改，然后你就需要在 master 上主动提交了修改，注意，这里是 master 上的你 commit 的，也就是改变了 commit 的 author。

### 总结
git merge 操作合并分支会让两个分支的每一次提交都按照提交时间（并不是 push 时间）排序，并且会将两个分支的最新一次 commit 点进行合并成一个新的 commit，最终的分支树呈现非整条线性直线的形式；

git rebase 操作实际上是将当前执行 rebase 分支的所有基于原分支提交点之后的 commit 打散成一个一个的 patch，并重新生成一个新的 commit hash 值，再次基于原分支目前最新的 commit 点上进行提交，并不根据两个分支上实际的每次提交的时间点排序，rebase 完成后，切到基分支进行合并另一个分支时也不会生成一个新的 commit 点，可以保持整个分支树的完美线性；

squash 也可以保持 master 分支干净，但是 master 中 author 都是管理者（maintainer），而不是原 owner，也就是有点“窃取劳动果实”的味道。

值得一提的是：当我们开发一个功能时，可能会在本地有无数次 commit，而你实际上在你的 master 分支上只想显示每一个功能测试完成后的一次完整提交记录就好了，其他的提交记录并不想将来全部保留在你的 master 分支上，那么 rebase 将会是一个好的选择，他可以在 rebase 时将本地多次的 commit 合并成一个 commit，还可以修改 commit 的描述等。

主分支上不能 rebase。否则，主分支的历史将被篡改，不能看到原始的历史记录。

## 参考阅读

- [你真的懂 git rebase 吗？ - 简书](https://www.jianshu.com/p/6960811ac89c)
- [merge squash 和 merge rebase 区别](https://liqiang.io/post/difference-between-merge-squash-and-rebase/)
