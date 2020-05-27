---
title: 一个示例 markdown
toc: true
date: 2020-05-26 12:27:56
tags: others
---
# [给sftp创建新用户、默认打开和限制在某个目录](https://www.cnblogs.com/xjnotxj/p/6912471.html)

# 环境：

CentOS 6.8  
使用 FileZilla 进行 sftp 连接

# 二、背景

给外包的工作人员提供我司服务器的**某一目录**的访问（包括读写）权限，方便他们部署代码文件。

之所以是某一目录的访问，是因为 SFTP 的用户登录后，默认是能看到整个系统的文件目录，这样很不安全。

题外话：如果是针对 ftp 的用户权限管理，推荐使用 vsftpd，可通过 yum 直接安装。

# 三、正文

#### 1、创建新用户

```
adduser sftpuser1
```

>

useradd 和 adduser 的区别  
useradd 只会添加一个用户，并没有创建它的主目录，除了添加一个新用户之外什么都没有。这个用户甚至不能登录，因为没有密码。所以这里选择 adduser。

>

#### 2、设置该用户密码

```
passwd sftpuser1
```

> 回车后再输入密码即可

#### 3、禁止该用户登录 SSH

因为我们只想该用户使用 SFTP，并不需要该用户能登录 SSH，威胁安全。

```
usermod -s /bin/false sftpuser1
```

将`sftpuser1`的 shell 改成 /bin/false。

#### 4、修改该用户的家目录

```
usermod -d /data/wwwroot/user1/ sftpuser1
```

这样每次用户访问服务器都会默认打开`/data/wwwroot/user1/`，但还是可以跳出这个访问其它目录，需要进行下面一步的操作。

#### 5、设置 sshd\_config：

打开`sshd_config`文件

```
vi /etc/ssh/sshd_config
```

找到 Subsystem sftp 这一行，修改成：

```
Subsystem sftp internal-sftp
UsePAM yes
Match user sftpuser1
ForceCommand internal-sftp
ChrootDirectory /data/wwwroot/user1/
```

将上面的 `sftpuser1` 和 `/data/wwwroot/user1/` 替换成你需要的。

多个用户请重复配置这三行：  
Match user sftpuser2  
ForceCommand internal-sftp  
ChrootDirectory /data/wwwroot/user2/

这样可以为不同的用户设置不同的限制目录。

#### 6、重新启动 sshd 服务：

```
/etc/init.d/sshd restart
```

现在用 SFTP 软件使用`sftpuser1`用户登录，就可以发现目录已经被限定、锁死在`/data/wwwroot/user1/`了。

* * *

# 四、可能遇到的问题

#### 1、修改`sshd_config`文件后重启 sshd，报错：Directive 'UseDNS' is not allowed within a Match block

语法错误，原因未知，只需要把两段配置的位置互调就不报错了。

修改前：

```
Subsystem sftp internal-sftp
UsePAM yes
Match user sftpuser1
ForceCommand internal-sftp
ChrootDirectory /data/wwwroot/user1/

UseDNS no
AddressFamily inet
PermitRootLogin yes
SyslogFacility AUTHPRIV
PasswordAuthentication yes
```

修改后：

```
UseDNS no
AddressFamily inet
PermitRootLogin yes
SyslogFacility AUTHPRIV
PasswordAuthentication yes

Subsystem sftp internal-sftp
UsePAM yes
Match user sftpuser1
ForceCommand internal-sftp
ChrootDirectory /data/wwwroot/user1/
```

注：当你出现这个错误的时候，sftp 肯定是连不上了。如果你习惯用 FileZilla 去修改配置文件，那么此时你得不情愿的切换到  
shell，去用 vi/vim 去修改它了。

#### 2、新用户通过 sftp 访问时，权限不全，只能读不能写

我试着用 root 账号去把该用户的家目录权限改成 777，但是会出现该用户 sftp 登陆不了的情况。（报错：Server unexpectedly closed network connection）

google 了原因如下：

给新用户的家目录的权限设定有两个要点：

>

1、由 ChrootDirectory 指定的目录开始一直往上到系统根目录为止的目录拥有者都只能是 root  
2、由 ChrootDirectory 指定的目录开始一直往上到系统根目录为止都不可以具有群组写入权限（最大权限 755）

>

如果违反了上面的两条要求，那么就会出现新用户访问不了 sftp  
的情况。

所以`/data/wwwroot/user1/`及上级的所有目录属主一定要是  
root，并且组权限和公共权限不能有写入权限，**如果一定需要有写入权限，那们可以在`/data/wwwroot/user1/`下建立 777 权限的文件夹**。

```
mkdir /data/wwwroot/user1/upload
chown -R sftpuser1:root /data/wwwroot/user1/upload
```

这样`sftpuser1`用户就可以在`/data/wwwroot/user1/upload`里随意读写文件了。
## 1. 添加账户
```
$ useradd images
$ passwd images
```
## 2.修改/etc/ssh/sshd_config
注释掉 Subsystem sftp /usr/libexec/openssh/sftp-server
在下面添加
```
Match User images
        ForceCommand internal-sftp
        ChrootDirectory /home/images
```
## 3.修改/home/images 目录权限
```
$ cd /home
$ chown root:root images
```
## 4.重启ssh
```
$ systemctl restart sshd
```
## 5.设置可写目录
```
$ cd /home/images
$ mkdir write
$ chown images:images write
```
## 6.filezilla 连接测试

*参考：*
[如何将SFTP用户限制在某个目录下？](http://www.jbxue.com/LINUXjishu/22628.html)
[centos下配置sftp且限制用户访问目录](https://segmentfault.com/a/1190000000441260)
