---
title: 术语
toc: true
date: 2020-05-23 12:27:56
tags: wiki
---

## 孤儿进程

一个父进程退出，而它的一个或多个子进程还在运行，那么那些子进程将成为孤儿进程。孤儿进程将被init进程(进程号为1)所收养，并由init进程对它们完成状态收集工作。

## 僵尸进程
一个进程使用fork创建子进程，如果子进程退出，而父进程并没有调用wait或waitpid获取子进程的状态信息，那么子进程的进程描述符仍然保存在系统中。这种进程称之为僵死进程。 僵尸进程占用进程描述符，无法释放，会导致系统无法正常的创建进程。
```bash
cat /proc/sys/kernel/pid_max
32768
```
## 守护进程

守护进程一般是后台运行的进程，例如sshd, mysqld, dockerd等等，他们的特点就是他们的ppid是1， 也就是说，守护进程也是孤儿进程的一种。

```plain
root      9696     1  0 Oct06 ?        00:05:16 /usr/sbin/sshd -D
```

[Linux系统进程分享 · 语雀](https://www.yuque.com/wangdd/blog/pbcbub#J7ItX)