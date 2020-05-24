---
title: Python 标准库系列之 Paramiko 模块
toc: true
date: 2020-05-23 18:21:46
tags:
- 编码
- 面向对象
top: 2

---
# Python 标准库系列之 Paramiko 模块

`Paramiko`是一个 Python 实施`SSHv2`的协议，提供客户端和服务器的功能。虽然它利用一个 Python C 扩展低级别加密的 paramiko 本身就是围绕 SSH 联网概念的纯 Python 接口。

Paramiko 官网：http://www.paramiko.org/

## 安装 Paramiko

```bash
pip3 install paramiko
```

安装之后进入 python 解释器导入模块，如果导入成功则安装成功，否则安装失败.

```python
C:\Users\Administrator>python
Python 3.5.2 (v3.5.2:4def2a2901a5, Jun 25 2016, 22:18:55) [MSC v.1900 64 bit (AMD64)] on win32
Type "help", "copyright", "credits" or "license" for more information.
>>> import paramiko
```

##  使用用户名与密码的方式连接

```python
# 导入paramiko模块
>>> import paramiko
# 创建SSHClient对象
>>> ssh = paramiko.SSHClient()
# 如果是一个新主机连接，会出现yes/no，AutoAddPolicy自动填写yes的
>>> ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
# 连接服务器
>>> ssh.connect(hostname='192.168.56.100', port=22, username='root', password='123456')
# 执行命令
>>> stdin, stdout, stderr = ssh.exec_command('df -h')
# 获取正确的输出
>>> result = stdout.read()
# 关闭连接
>>> ssh.close()
# 获取到的值
>>> result
b'Filesystem      Size  Used Avail Use% Mounted on\n/dev/sda3        48G  3.3G   45G   7% /\ndevtmpfs        984M     0  984M   0% /dev\ntmpfs           993M     0  993M   0% /dev/shm\ntmpfs           993M  8.9M  984M   1% /run\ntmpfs           993M     0  993M   0% /sys/fs/cgroup\n/dev/sda1       197M  137M   60M  70% /boot\ntmpfs           199M     0  199M   0% /run/user/0\n'
```

## 使用密钥的方式连接

在使用密钥的方面连接之前我们需要先做`ssh-key`认证，步骤如下：

```bash
[root@linux-node1 ~]# ssh-keygen -t rsa -f ~/.ssh/id_rsa -P ''
[root@linux-node1 ~]# cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys
[root@linux-node1 ~]# chmod 600 ~/.ssh/authorized_keys
```
然后下载`/root/.ssh/id_rsa`下载下来，复制到`E:\python-intensive-training\`目录系，下面是在`windows`下使用`paramiko`连接脚本如下
```python
#!/use/bin/env python
# _*_ coding: utf-8 _*_

import paramiko

# 指定密钥的文件
private_key = paramiko.RSAKey.from_private_key_file('E:\python-intensive-training\id_rsa')

# 创建SSH对象
ssh = paramiko.SSHClient()

# 允许连接不在know_hosts文件中的主机，要不然一台新机器去连接它的时候会让你输入yes/no
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

# 连接服务器
ssh.connect(hostname='192.168.56.100', port=22, username='root', pkey=private_key)

# 执行命令
stdin, stdout, stderr = ssh.exec_command('df -h')
"""
stdin：标准输入
stdout：标准输出
stderr：错误输出
"""

# 获取命令执行的正确结果
result = stdout.read()

# 关闭连接
ssh.close()

# 输出执行结果
print(str(result, encoding='utf-8'))
```

## 文件上传与下载

```python
#!/usr/bin/python

import paramiko

t = paramiko.Transport(('192.168.56.100', 22))

t.connect(username="root", password="123456")

sftp = paramiko.SFTPClient.from_transport(t)

# 远程目录
remotepath = '/tmp/id_rsa'

# 本地文件
localpath = 'id_rsa'

# 上传文件
sftp.put(localpath, remotepath)

# 下载文件
# sftp.get(remotepath, localpath)

# 关闭连接
t.close()
```
