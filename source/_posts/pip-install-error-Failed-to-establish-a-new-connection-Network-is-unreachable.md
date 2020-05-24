---
title: 使用 pip 装包时提示'[Errno 101] Network is unreachable'
date: 2020-01-12 10:32:26
tags:
- Python
- pip
- pipenv
---
## 缘起
今天写代码安装依赖的时候，执行`pipenv install {SOMETHING}`时报错：
```plain
(PyTinyPng) [root@172 PyTinyPng]# pipenv install tinify
Installing tinify…
✔ Installation Succeeded 
Pipfile.lock not found, creating…
Locking [dev-packages] dependencies…
Locking [packages] dependencies…
✘ Locking Failed! 
#……
[pipenv.exceptions.ResolutionFailure]:       No versions found
[pipenv.exceptions.ResolutionFailure]: Warning: Your dependencies could not be resolved. You likely have a mismatch in your sub-dependencies.
  First try clearing your dependency cache with $ pipenv lock --clear, then try the original command again.
 Alternatively, you can use $ pipenv install --skip-lock to bypass this mechanism, then run $ pipenv graph to inspect the situation.
  Hint: try $ pipenv lock --pre if it is a pre-release dependency.
ERROR: ERROR: Could not find a version that matches tinify
No versions found
Was https://pypi.org/simple reachable?

```
## 解决方案

给 pip 换清华源
```shell
cd ~
mkdir .pip/pip.conf
vi .pip/pip.conf
#写入新地址
[global]
index-url = https://pypi.tuna.tsinghua.edu.cn/simple
```
外部执行测试安装，可以正常安装，进入 pipenv 之后还是报错，修改 Pipfile
```plain
(PyTinyPng) [root@172 PyTinyPng]# find / -name Pipfile
/root/iyblog/Pipfile
/root/Flog/Pipfile
/root/PyTinyPng/Pipfile
```
修改对应项目的 Pipfile，换成清华源或者阿里源，之后执行`pipenv install {SOMETHING}`即可。

## 总结

网络原因导致 pypi 源不可达，修改 pip.conf 可以使 pip 正常使用，但是 pipenv 有自己的配置文件，不会跟着修改，即使把虚拟环境删了（`pipenv --rm`），Pipenv 也不会删除（我测试的时候是这样）。所以需要重新生成该文件或者直接修改文件。