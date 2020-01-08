---
title: Python 环境管理介绍
date: 2018-01-18 14:18:31
cover: /images/Python/pipenv.jpg

tags:
- Python
---
Python 环境管理是个很大的坑，坑里面有无数新人 or 老司机的尸体。venv, pyvenv, pyenv, virtualenv, virtualenvwrapper, pipenv 等工具的区别与介绍。

<!--more-->

项目开发中可能需要用到不同版本的`Python`及相关的开发环境。比如`Python2`及`Python3`，或者有的项目需要 `Django1.5` ，有的需要`2.0`，这个时候借助一些工具，往往可以达到事半功倍的效果。

![Python](https://farm5.staticflickr.com/4290/35294660055_42c02b2316_k_d.jpg)

{%note info no-icon%}
## @Update
- 2020-1-8
今天看到一篇文章 [Pipenv 有什么问题](https://frostming.com/2019/09-01/pipenv-problems)，作者是`Pipenv`的核心开发者，也对`Poetry`做了一点介绍，同时在 [这里](https://github.com/pypa/pipenv/issues/4058) 看到对`pipenv`项目进度的询问与开发者的回应，有兴趣的可以一读。
{%endnote%}

## 第三方库

### virtualenv

`virtualenv`是一个非常流行的工具，为`Python`库创建独立的`Python`环境。如果你不熟悉这个工具，我强烈建议你学习它，因为它是一个非常有用的工具，我将在这个答案的其余部分对此进行比较。

它通过在一个目录（例如：`env/`）中安装一堆文件，然后修改`PATH`环境变量来为自定义`bin`目录（例如：`env/bin/`）添加前缀。 `python`或`python3`二进制文件的精确拷贝会被放置在这个目录中，但`Python`被编程为首先在环境目录中查找相对于其路径的库。它不是`Python`标准库的一部分，但是获得`PyPA`（Python Packaging Authority）正式称赞。激活之后，你就可以使用`pip`在虚拟环境中安装软件包。

#### virtualenvwrapper

`virtualenvwrapper`是`virtualenv`的一组扩展（参见[文档](http://virtualenvwrapper.readthedocs.io/en/latest/)）。它提供例如`mkvirtualenv`、`lssitepackages`这样的命令，特别是`workon`命令，它可以在不同的`virtualenv`目录之间切换。如果你想要多个`virtualenv`目录，这个工具特别有用。

### pyenv

`pyenv`是`Python`的**版本**管理器,用于隔离`Python`版本。例如，你可能想要针对`Python 2.6`,`2.7`,`3.3`,`3.4`和`3.5`测试你的代码，因此你需要在不同`Python`版本之间进行切换。一旦激活，它就会在`PATH`环境变量前加上`~/.pyenv/shims`，其中有一些与`Python`命令（`python`，`pip`）匹配的特殊文件。这些不是`Python`提供的命令的副本;它们是根据`PYENV_VERSION`环境变量或`.python-version`文件或`~/.pyenv/version`文件决定运行哪个版本的`Python`的特殊脚本。 `pyenv`也使下载和安装多个`Python`版本的过程变得更简单，使用命令`pyenv install`即可。

#### pyenv-virtualenv

`pyenv-virtualenv`是`pyenv`的一个插件，和`pyenv`一样，允许你在同一时间方便地使用`pyenv`和`virtualenv`。但是，如果你使用`Python 3.3`或更高版本，则`pyenv-virtualenv`会尝试运行`python -m venv`（如果可用），而不是`virtualenv`。如果你不想使用便利功能，则可以搭配使用`virtualenv`和`pyenv`而不使用`pyenv-virtualenv`。

#### pyenv-virtualenvwrapper

`pyenv-virtualenvwrapper`是`pyenv`的一个插件，可以很方便地将`virtualenvwrapper`集成到`pyenv`中。

### pipenv

`pipenv`是`Python`的**包**管理器。由`Kennetth Reitz`（`requests`的作者）编写维护，是我们上面提到的这些项目里面最新的。它的目标是在命令行中将`Pipfile`、`pip`和`virtualenv`合并为一个命令。

## 标准库

### pyvenv

`pyvenv`是一个`Python 3`附带的脚本，但在**Python 3.6 中被弃用**，（参见[这里](https://docs.python.org/dev/whatsnew/3.6.html#id8)）因为它有问题（暂且不说名字还容易造成混淆）。在`Python 3.6+`中，实际上等价于命令`python3 -m venv`。

### venv

`venv`是`Python 3`附带的一个包，你可以使用`python3 -m venv`运行（虽然由于某些原因，一些发行版把它分离成一个单独的发行包，比如`Ubuntu / Debian`上的`python3-venv`）。它的作用与`virtualenv` 相似，工作方式也非常相似，但不需要复制`Python`二进制文件（`Windows`下除外）。如果你的代码不需要支持`Python 2`，可以使用它。在撰写本文时，`Python`社区似乎对`virtualenv`感到满意，`venv`相对来说比较小众。

## 参考链接

1. [Python - What is the difference between venv, pyvenv, pyenv, virtualenv, virtualenvwrapper, pipenv, etc? - Stack Overflow](https://stackoverflow.com/questions/41573587/what-is-the-difference-between-venv-pyvenv-pyenv-virtualenv-virtualenvwrappe)

2. [Pipenv & Virtual Environments — The Hitchhiker's Guide to Python](http://docs.python-guide.org/en/latest/dev/virtualenvs/)

3. [我的 Python 环境设置](https://frostming.com/2019/11-18/python-setup)