---
title: 如何把当前改动追加到某次指定 commit 上（非上次）
date: 2019-03-05 09:56:37
tags:
- git
- 版本控制

categories:
- 工作日常
---
注意：本例中使用`Gerrit`进行演示。

0. 暂存目前修改的代码
    ```bash
    git stash
    git stash list # 可以验证暂存是否成功
    ```
1. 查找到需要指定的`commit`的编号；
    ```bash
    git log
    ```
    ![rebase](/images/snipaste_20190305_123504.jpg) 
2. 找到`git rebase`编号，即要修改的`commit`之前那个`commit`；
    ```bash
    git rebase --interactive a6f372877d26xxx0690aedf6dc6b6e7c
    ```
    ![rebase](/images/InsertPic_C032-11-05-09-52-53.jpg)   
3. 找到要更改的`commit`, 将行首的`pick`更改为`edit`, 保存退出；   
    ![pick2edit](/images/InsertPic_36EE-11-05-09-52-53.jpg)    
4. 本地修改需要修改的代码

5. 恢复暂存的修改
    ```bash
    git stash pop 
    ```
    **注意**：如果此时有冲突，需要自己手动解决冲突
6. 解决冲突后，添加修改文件
    ```bash
    git add xxx    # 文件名称
    git commit --amend
    ```
7. 回退到当前状态；
    ```bash
    git rebase --continue
    ```
    ![pick2edit](/images/Catch-11-05-09-52-53.jpg)  
    **注意**：如果`rebase`版本较多，可能需要多次重复上述步骤，且每`rebase`一步，可能都要解决与其他组员`commit`的冲突；
8. rebase 到 master 之后，push 当前版本到远程
    ```bash
    git push origin 0d163929c240xxx745b520d07b854c207 ① :refs/changes/8xxx4 ②
    ```
    ①：此处为你自己需要`amend`的`commit`版本号；
    ②：此处为远端你的`change`的编号，如果远端版本已经`closed`，则无法进行`amend`，只能 `git reset`；

### 总结

`git`非常智能化，每一次操作应该根据提示进行问题分析、逐步操作则可顺利达到预期效果。