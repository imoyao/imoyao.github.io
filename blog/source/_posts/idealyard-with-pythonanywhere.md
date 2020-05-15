---
title: idealyard|使用 pythonanywhere 部署博客应用
date: 2020-05-13 09:57:52
tags:
categories:
hide: true
---
## 环境设置
### 注册账户
去 [官网](https://www.pythonanywhere.com/) 注册账户
![dashboard](/images/pa-dashboard.png)

### 创建新的 web 应用
1. 自定义域名
因为我们是白嫖党，所以不自定义域名，直接下一步
2. 选择 Python 的 web 框架
因为书上说：
> Python Anywhere 默认提供 0.11 和 0.12 版本的 Flask，因为我们需要使用最新版，同时为了更灵活地定义其他设置，这里选择了手动配置

经过我的亲自尝试，目前支持 Flask1.1.1，如果我们不想自己配置，则可以使用该默认配置，而且里面也提供了 [虚拟环境功能](https://help.pythonanywhere.com/pages/Virtualenvs) ，可以自行配置 Flask 版本。

因为我是第一次部署，所以还是按照书上的顺序先尝试一下，直接选择使用手动配置，然后下一步。
3. 选择 Python 版本
此处我们选择 Python3.7。然后下一步；
4. 确认配置
> 手动配置可以编辑/var/www/下面的配置，还可为你的应用指定虚拟环境
点击下一步。
5. 验证
之后我们访问`https://www.pythonanywhere.com/user/imoyao/webapps/`即可访问 hello world 应用，其中`imoyao`位置填写你自己的用户名。
![hello-world](/images/pa-hello-world.png)

## 部署
1. 进入 console
访问[bash](https://www.pythonanywhere.com/user/imoyao/consoles/bash/new)，将链接`https://www.pythonanywhere.com/user/imoyao/consoles/bash/new`中的用户名改为自己的
2. 克隆代码
```bash
git clone https://github.com/imoyao/idealyard.git
```
由于这个在国外，所以我们不需要换源什么的就可以很快完成安装。
3. 创建数据库
访问[此处](https://www.pythonanywhere.com/user/imoyao/databases/)配置数据库密码，我们选择 MySQL 作为后端数据库，因为 Postgres 要钱。🤦‍♂️密码最好不要和你的用户名的登录密码相同。吐过不想使用默认的数据库，我们还可以使用自定义数据库名称。
![Database](/images/pa-db.png)
4. 安装 pipenv
```bash
pip3 install pipenv
```
5. 安装 Python 依赖
```plain
cd idealyard
pipenv shell
(idealyard) 03:18 ~/idealyard (master)$ pwd
/home/imoyao/idealyard
```
由于我们使用的是阿里云镜像源安装的包，这个上面好像没法连接（？），所以我们直接`cd back`使用`pip`安装依赖
```bash
pip install -r requeriements.txt
```
使用`pip list`验证安装
6. 设置环境变量路径
```plain
(idealyard) 03:31 ~/idealyard (master)$ which python
/home/imoyao/.virtualenvs/idealyard--xXyk2CF/bin/python # 此处取/home/imoyao/.virtualenvs/idealyard--xXyk2CF
```
配置到 web 选项的`Virtualenv`处
7. 编辑`wsgi.py`配置
```python
# This file contains the WSGI configuration required to serve up your
# web application at http://imoyao.pythonanywhere.com/
# It works by setting the variable 'application' to a WSGI handler of some
# description.
#

# +++++++++++ GENERAL DEBUGGING TIPS +++++++++++
# getting imports and sys.path right can be fiddly!
# We've tried to collect some general tips here:
# https://help.pythonanywhere.com/pages/DebuggingImportError

# +++++++++++ FLASK +++++++++++
# Flask works like any other WSGI-compatible framework, we just need
# to import the application.  Often Flask apps are called "app" so we
# may need to rename it during the import:
#
#
import sys

# The "/home/imoyao" below specifies your home
# directory -- the rest should be the directory you uploaded your Flask
# code to underneath the home directory.  So if you just ran
# "git clone git@github.com/myusername/myproject.git"
# ...or uploaded files to the directory "myproject", then you should
# specify "/home/imoyao/myproject"
path = '/home/imoyao/idealyard' # 根据你的实际目录填写
if path not in sys.path:
    sys.path.append(path)

from wsgi import app as application  # noqa
#
# NB -- many Flask guides suggest you use a file called run.py; that's
# not necessary on PythonAnywhere.  And you should make sure your code
# does *not* invoke the flask development server with app.run(), as it
# will prevent your wsgi file from working.
```
### 配置环境变量
```plain
vi .env
MYSQL_USER=xxx      # 数据库用户名
MYSQL_PASSWORD=xxx  # 数据库密码
MYSQ_DB=xxx         # 数据库名称
```

## 部署前端
1. 切换目录并安装
```bash
cd frontend
npm install
```
## 更新
如果 Git 代码更新了，我们可以使用下面的命令更新代码仓库
```plain
pwd
/home/imoyao/idealyard
git pull
```