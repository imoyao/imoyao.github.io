---
title: Python 换源操作
toc: true
date: 2020-05-23 18:21:46
tags:
- PyPI
- pip
- Python

---

## 常用的国内 PyPI 镜像列表
```plain
豆瓣 https://pypi.doubanio.com/simple/
网易 https://mirrors.163.com/pypi/simple/
阿里云 https://mirrors.aliyun.com/pypi/simple/
清华大学 https://pypi.tuna.tsinghua.edu.cn/simple/
```
顺便提一下，使用镜像源需要注意一个问题：包的版本可能不会及时更新，遇到这种情况可以通过临时换回官方源解决。

官方 PyPI 源的 URL 为 `https://pypi.org/simple` （旧的 URL 为 `https://pypi.python.org/simple` ），下面我们将以豆瓣提供的镜像源为例（URL 为 `https://pypi.doubanio.com/simple/`），介绍不同工具更改 PyPI 镜像源的方法：

## pip
临时设置可以通过 -i 选项：

```bash
pip install -i https://pypi.doubanio.com/simple/ flask
```

全局设置有不同的层级和文件位置，以用户全局（per-user）为例，在 Linux & macOS 中，配置需要写到 `~/.pip/pip.conf` 文件中；Windows 中，配置文件位置为 `%HOMEPATH%\pip\pip.ini`，`%HOMEPATH%` 即你的用户文件夹，一般为“\Users\<你的用户名>”，具体值可以使用 `echo %HOMEPATH%`命令查看。

通常你需要手动创建对应的目录和文件，然后写入下面的内容：

```plain
[global]
index-url = https://pypi.doubanio.com/simple
[install]
trusted-host = pypi.doubanio.com
```
附注：按照 pip 文档，上面的配置文件位置是旧（legacy）的配置方式，但是因为比较方便设置，这里沿用了。新的建议是 Linux & macOS 放到 `$HOME/.config/pip/pip.conf`，Windows 则放到 `%APPDATA%\pip\pip.ini`。具体可以访问 pip 文档配置部分查看。

## Pipenv
类似 pip 的 -i （–index-url）选项，你可以使用 `–pypi-mirror` 临时设置镜像源地址：

```bash
$ pipenv install --pypi-mirror https://pypi.doubanio.com/simple flask
```

如果想对项目全局（per-project）设置，可以修改 Pipfile 中 [[source]] 小节：
```bash
[[source]]

url = "https://pypi.doubanio.com/simple"
verify_ssl = true
name = "douban"
```
另外一种方式是使用环境变量 `PIPENV_PYPI_MIRROR` 设置（Windows 系统使用 set 命令）：
```bash
$ export PIPENV_PYPI_MIRROR=https://pypi.doubanio.com/simple
```
你可以通过把这个环境变量的设置语句写入到终端的配置文件里实现“永久”设置，Linux & macOS 可参考这里，Windows 可参考这里。

## Poetry / Flit
因为 Poetry，Flit 这些工具遵循 PEP 518 创建了一个 pyproject.toml 文件来替代 setup.py、Pipfile 等配置文件，所以我们可以在这个文件里更改 PyPI 源。

使用 Poetry 时，在 pyproject.toml 末尾添加下面的内容来设置自定义镜像源：
```plain
[[tool.poetry.source]]
name = "douban"
url = "https://pypi.doubanio.com/simple/"
```
目前暂时没有其他方式，未来或许会为 poetry add 命令添加一个相关的设置选项。

同样的，Flit 大概要添加下面这些内容（未测试）：
```plain
[[tool.flit.source]]
name = "douban"
url = "https://pypi.doubanio.com/simple/"
```

## 原文链接
[从国内的 PyPI 镜像（源）安装 Python 包 | 李辉的个人网站](https://greyli.com/set-custom-pypi-mirror-url-for-pip-pipenv-poetry-and-flit/)