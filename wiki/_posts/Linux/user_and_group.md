---
title: 用户、组管理
toc: true
date: 2020-05-30 12:27:56
tags: Linux
---
在 Linux 操作系统下，如何添加一个新用户到一个特定的组中？如何同时将用户添加到多个组中？又如何将一个已存在的用户移动到某个组或者给他增加一个组？对于不常用 Linux 的人来讲，记忆 Linux 那繁多的命令行操作真是件不容易的事。
useradd 是 Linux 添加新用户的命令，这个命令提供了一次性创建新用户账户及设置用户 HOME 目录结构的简便方法。

1、useradd命令加参数-D参看系统的默认值：
```bash
# useradd -D
```
```plain
GROUP=100
HOME=/home
INACTIVE=-1
EXPIRE=
SHELL=/bin/bash
SKEL=/etc/skel
CREATE_MAIL_SPOOL=yes
```
解释：
1）新用户添加到 GID 为 100 的公共组
2）新用户的 HOME 目录将会位于/homoe/username
3）新用户账户密码在过期后不会被禁用
4）新用户账户未被设置为某个日期后就过期
5）新用户账户将 bash shell 作为默认 shell
6）系统会将/etc/skel 目录下的内容复制到用户的 HOME 目录下
7）系统为该用户账户在 mail 目录下创建一个用于接收邮件的文件
倒数第 2 个值很有意思。useradd 命令允许管理员创建一个默认的 HOME 目录配置，然后把它作为创建新用户 HOME 目录的模板。这样，就能自动在每个新用户的 HOME 目录里放置默认的系统文件。在 Ubuntu Linux 系统上，/etc/skel 目录下有下列文件：

```bash
$ ls -la /etc/skel
```
```plain
total 32
drwxr-xr-x 2 root root 4096 Jun 24 09:43 .
drwxr-xr-x 132 root root 12288 Jun 19 09:53 ..
-rw-r--r-- 1 root root 220 Apr 3 2012 .bash_logout
-rw-r--r-- 1 root root 3486 Apr 3 2012 .bashrc
-rw-r--r-- 1 root root 179 Apr 3 2012 example.desktop
-rw-r--r-- 1 root root 675 Apr 3 2012 .profile
$
```
在创建用户时，可以使用下面的命令行参数改变默认值或默认行为：

============================================================================
参 数 描 述
----------------------------------------------------------------------------
-c comment 给新用户添加备注
-d home_dir 为主目录指定一个名字（如果不想用登录名作为主目录名的话）
-e expire_date 用 YYYYY-MM-DD 格式指定一个账户过期的日期
-f inactive_days 指定这个帐户密码过期后多少天这个账户被禁用；0 表示密码一过期就立即禁
用，-1 表示禁用这个功能
-g initial_group 指定用户登录组的 GID 或组名
-G group ... 指定用户除登录组之外所属的一个或多个附加组
-k 必须和-m 一起使用，将/etc/skel 目录的内容复制到用户的 HOME 目录
-m 创建用户的 HOME 目录
-M 不创建用户的 HOME 目录（当默认设置里指定创建时，才用到）
-N 不要创建一个同用户登录名同名的新组
-r 创建系统账户
-p passwd 为用户账户指定默认密码
-s shell 指定默认登录 shell
-u uid 为账户指定一个唯一的 UID
============================================================================

同样，你可以用-D 参数后面跟一个要修改的值的参数，来修改系统默认的新用户值。这些参数如下表：

============================================================================
参数描述
----------------------------------------------------------------------------
-b default_home 更改默认的创建用户 HOME 目录的位置
-e expiration_date 更改默认的新账户的过期日期
-f inactive_days 更改默认的新用户从密码过期到账户被禁用的天数
-g group 更改默认的组名称或 GID
-s shell 更改默认的登录 shell
============================================================================

如 #useradd -D -s /bin/tsch ，修改默认的 shell 为/bin/tsch。

另外，删除用户，使用 userdel 命令。默认情况下，userdel 命令只会删除/etc/passwd 文件中的信息，而不会删除系统中属于该账户的任何文件。
如果加上-r，userdel 会删除用户的 HOME 目录以及 mail 目录。然后，系统上仍可能存有归已删除用户所有的其他文件。这在有些环境中会造成问题。
PS：在有大量用户的环境中使用-r 参数时要特别小心。你永远不知道用户是否在他的 HOME 目录下存放了其他用户或其他程序要使用的重要文件。记住在删除用户的 HOME 之前一定要检查清楚！

在 Linux 中，增加用户或改变用户的组属性可以使用 `useradd` 或者 `usermod` 命令。useradd 增加一个新用户或者更新默认新用户信息。`usermod` 则是更改用户帐户属性，例如将其添加到一个已有的组中。

在 Linux 用户系统中存在两类组。第一类是主要用户组，第二类是附加用户组。所有的用户帐户及相关信息都存储在 `/etc/passwd` 文件中，`/etc/shadow` 和 `/etc/group` 文件存储了用户信息。

## useradd 示例 – 增加一个新用户到附加用户组¶
新增加一个用户并将其列入一个已有的用户组中需要用到 `useradd` 命令。如果还没有这个用户组，可以先创建该用户组。

命令参数如下：
```bash
useradd -G {group-name} username
```
例如，我们要创建一个新用户 cnzhx 并将其添加到用户组 developers 中。首先需要以 root 用户身份登录到系统中。先确认一下是否存在 developers 这个用户l组，在命令行输入：
```bash
grep developers /etc/group
```
输出类似于：
```plain
developers:x:1124:
```
如果看不到任何输出，那么就需要先创建这个用户组了，使用 `groupadd` 命令：
```bash
groupadd developers
```
然后创建用户 cnzhx 并将其加入到 developers 用户组：
```bash
useradd -G developers cnzhx
```
为用户 cnzhx 设置密码：
```bash
passwd cnzhx
```
为确保已经将该用户正确的添加到 developers 用户组中，可以查看该用户的属性，使用 id 命令：
```bash
id cnzhx
```
输出类似于：
```bash
uid=1122(cnzhx) gid=1125(cnzhx) groups=1125(cnzhx),1124(developers)
```
前面命令中用到的大写的 `G （-G）` 参数就是为了将用户添加到一个附加用户组中，而同时还会为此用户创建一个属于他自己的新组 cnzhx。如果要将该用户同时增加到多个附加用户组中，可以使用英文半角的逗号来分隔多个附加组名（不要加空格）。例如，同时将 cnzhx 增加到 admins, ftp, www 和 developers 用户组中，可以输入以下命令：
```bash
useradd -G admins,ftp,www,developers cnzhx
```

## useradd 示例 – 增加一个新用户到主要用户组¶
要增加用户 cnzhx 到组 developers，可以使用下面的指令：
```bash
useradd -g developers cnzhx
```
验证
```bash
id cnzhx
```
输出类似于：
```plain
uid=1123(cnzhx) gid=1124(developers) groups=1124(developers)
```
请注意如前面的示例的区别，这里使用了小写字母 `g （-g）`作为参数，此时用户的主要用户组不再是 cnzhx 而直接就是 developers。

小写字母 `g （-g）`将新增加的用户初始化为指定为登录组（主要用户组）。此组名必须已经存在。组号（gid）即是此已有组的组号。

## usermod 示例 – 将一个已有用户增加到一个已有用户组中¶
将一个已有用户 cnzhx 增加到一个已有用户组 apache 中，使此用户组成为该用户的附加用户组，可以使用带 `-a` 参数的 `usermod`  指令。`-a` 代表 append， 也就是将用户添加到新用户组中而不必离开原有的其他用户组。不过需要与 `-G` 选项配合使用：
```bash
usermod -a -G apache cnzhx
```
如果要同时将 cnzhx 的主要用户组改为 apache，则直接使用 `-g` 选项：
```bash
usermod -g apache cnzhx
```
如果要将一个用户从某个组中删除，则
```bash
gpasswd -d user group
```
但是这个时候需要保证 group 不是 user 的主组。

## 附：管理用户（user）和用户组（group）的相关工具或命令¶

### 管理用户（user）的工具或命令
```plain
useradd    注：添加用户
adduser    注：添加用户
passwd     注：为用户设置密码
usermod    注：修改用户命令，可以通过usermod 来修改登录名、用户的家目录等等；
pwcov      注：同步用户从/etc/passwd 到/etc/shadow
pwck       注：pwck是校验用户配置文件/etc/passwd 和/etc/shadow 文件内容是否合法或完整；
pwunconv   注：是pwcov 的立逆向操作，是从/etc/shadow和 /etc/passwd 创建/etc/passwd ，然后会删除 /etc/shadow 文件；
finger     注：查看用户信息工具
id         注：查看用户的UID、GID及所归属的用户组
chfn       注：更改用户信息工具
su         注：用户切换工具
sudo       注：sudo 是通过另一个用户来执行命令（execute a command as another user），su 是用来切换用户，然后通过切换到的用户来完成相应的任务，但sudo 能后面直接执行命令，比如sudo 不需要root 密码就可以执行root 赋与的执行只有root才能执行相应的命令；但得通过visudo 来编辑/etc/sudoers来实现；
visudo     注：visodo 是编辑 /etc/sudoers 的命令；也可以不用这个命令，直接用vi 来编辑 /etc/sudoers 的效果是一样的；
sudoedit   注：和sudo 功能差不多；
```

### 管理用户组（group）的工具或命令
```bash
groupadd    注：添加用户组；
groupdel    注：删除用户组；
groupmod    注：修改用户组信息
groups      注：显示用户所属的用户组
grpck
grpconv     注：通过/etc/group和/etc/gshadow 的文件内容来同步或创建/etc/gshadow ，如果/etc/gshadow 不存在则创建；
grpunconv   注：通过/etc/group 和/etc/gshadow 文件内容来同步或创建/etc/group ，然后删除gshadow文件；
```
将一个用户添加到某个组，即可让此用户拥有该组的权限。比如在配置 VPS 上的 LAMP 服务器的时候，运行网站的 apache 用户修改的文件，如果服务器管理用户 cnzhx（可以通过 ssh 登录到服务器）需要修改此文件的话，就可以将 cnzhx 加入到 apache 组中达到目的。

### `-b`和`-d`的区别
-b 指定用户主目录的位置。在普通 Linux 机器上，这将是`/home`;可以通过编辑`/ etc/default/useradd`更改默认值。 useradd 将新用户名添加到此路径以获取主目录。 这意味着如果我们执行：
```bash
useradd -b /somewhere ian
```
新用户的目录将是`/somewhere/ian`。

`-d`显式设置主目录，而不考虑缺省值。所以
```bash
useradd -d /somewhere-else/foo ian
```
那么用户的主目录将设置为`/somewhere-else/foo`。

**注意**：该目录将在密码文件中设置，但实际上不会创建，除非也指定了`-m`（或在默认文件中启用了`CREATE_HOME`设置）。

[linux - difference between useradd -b and useradd -d - Unix & Linux Stack Exchange](https://unix.stackexchange.com/questions/83930/difference-between-useradd-b-and-useradd-d)

## 参考链接
[Linux 中将用户添加到组的指令 | 水景一页](http://cnzhx.net/blog/linux-add-user-to-group/)
[Linux 命令之 useradd - 苦逼运维 - 博客园](https://www.cnblogs.com/diantong/p/9430258.html)