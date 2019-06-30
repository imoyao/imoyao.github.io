---
title: pip 小老弟，你怎么肥四？
date: 2018-09-21 15:52:52
tags: 
- Python
- pip
---
今天用`pip`的时候突然不能正常使用，在这里简单记录一下。
<!--more-->

## 提示`pip`版本不对

### 错误提示

```plain
You are using pip version 9.0.3, however version 18.0.1 is available.
You should consider upgrading via the 'python -m pip install --upgrade pip' command. 
```
### 处理过程

去[官网](https://pypi.org/project/pip/)下载最新版的包，直接解压安装即可；

### 参考来源

[Python2.7 自带的 pip9.0 升级到 pip18.0](https://blog.csdn.net/XavierDarkness/article/details/81234066)

## 明确已经安装`pip`，但是系统提示找不到`pip`

### 错误提示

```plain
-bash: /home/imoyao/.local/bin/pip: No such file or directory
```
### 解决方案

```shell
1.which pip 
/usr/local/bin/pip

2.pip 
-su: /usr/bin/pip: No such file or directory

3.type pip 
pip is hashed (/usr/bin/pip) 
So pip is definintely in /usr/local/bin/pip but it is been cached as in /usr/bin/pip, thanks to the Stackoverflow question, the solution is very simple:

4.hash -r 
When the cache is clear, pip is working again.
 
```
### 参考来源

[/usr/bin/pip: No such file or directory](https://blog.csdn.net/qq_32755575/article/details/80443714)

## 安装或升级`pip`时提示`SSLError`

### 错误提示

```plain
Retrying (Retry(total=4, connect=None, read=None, redirect=None, status=None)) after connection broken by 'SSLError(SSLError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed (_ssl.c:833)'),)': /simple/pip/
Retrying (Retry(total=3, connect=None, read=None, redirect=None, status=None)) after connection broken by 'SSLError(SSLError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed (_ssl.c:833)'),)': /simple/pip/
Retrying (Retry(total=2, connect=None, read=None, redirect=None, status=None)) after connection broken by 'SSLError(SSLError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed (_ssl.c:833)'),)': /simple/pip/
Retrying (Retry(total=1, connect=None, read=None, redirect=None, status=None)) after connection broken by 'SSLError(SSLError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed (_ssl.c:833)'),)': /simple/pip/
Retrying (Retry(total=0, connect=None, read=None, redirect=None, status=None)) after connection broken by 'SSLError(SSLError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed (_ssl.c:833)'),)': /simple/pip/
Could not fetch URL https://pypi.python.org/simple/pip/: There was a problem confirming the ssl certificate: HTTPSConnectionPool(host='pypi.python.org', port=443): Max retries exceeded with url: /simple/pip/ (Caused by SSLError(SSLError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed (_ssl.c:833)'),)) - skipping
#其实本人遇到的错误是
(Caused by SSLError(SSLError(1, u'[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed (_ssl.c:726)'),))
```
### 解决方案

- 临时方案

```plain
安装时添加参数：
--trusted-host pypi.python.org
此方式表示信任该域名，但是每一次安装包的时候都需要该操作，比较麻烦；
```
- 永久方案

修改`pip.conf` 配置文件，该文件在`Linux`系统中的可能位置：
```plain
/etc/pip.conf

~/.pip/pip.conf

~/.config/pip/pip.conf 
```
如果都没有的话，可以手动创建之后添加以下内容：

```plain
[global]
index-url = http://mirrors.aliyun.com/pypi/simple/      # 本机使用阿里源代理
[install]
trusted-host=mirrors.aliyun.com

# global字段还看到其他写法：
[global]
trusted-host = pypi.python.org
               pypi.org
               files.pythonhosted.org
```
### 参考来源

[pip issue installing almost any library](https://stackoverflow.com/questions/16370583/pip-issue-installing-almost-any-library)
[linux 设置 pip 镜像 Pip Warning：–trusted-host 问题解决方案](https://www.cnblogs.com/yudar/p/4657511.html)

## 安装`MySQL-python`时提示

### 错误提示
```plain
EnvironmentError: mysql_config not found
```
### 解决方案

- CentOS

```plain
yum install libffi-devel 
pip install mysql-connector-python
```

- Ubuntu

```plain
sudo apt install default-libmysqlclient-dev
```
### 参考来源
[pip install mysql-python fails with EnvironmentError: mysql_config not found](https://stackoverflow.com/questions/5178292/pip-install-mysql-python-fails-with-environmenterror-mysql-config-not-found)


