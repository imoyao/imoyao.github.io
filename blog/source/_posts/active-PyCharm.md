---
title: PyCharm 专业版（2018.3.2）激活，最新实验有效
date: 2019-12-25 22:23:02
tags: 
- PyCharm
- Python

cover: /images/Python/PyCharm.jpg
---

## 说明

本记录来源网络，仅用于个人记录，若收到官方律师函后果自负。希望不差钱的同学支持正版，[去官网购买](https://www.jetbrains.com/pycharm/buy/)
这个网站提供激活码，可用性及时效性没有验证[ PyCharm 激活码](http://www.ifdll.com/pycharm/)

PyCharm 和操作系统版本信息如下：
```plain
PyCharm 2018.3.2 (Professional Edition)
Build #PY-183.4886.43, built on December 18, 2018
Licensed to Rover12421 / Rover12421
Subscription is active until January 1, 2100
JRE: 1.8.0_152-release-1343-b26 amd64
JVM: OpenJDK 64-Bit Server VM by JetBrains s.r.o
Windows 10 10.0
```

## 破解补丁

下载[破解补丁](https://pan.baidu.com/s/1mcQM8CLUnweY02ahKEr4PQ)并放置到 PyCharm 程序安装目录\bin 目录下；

## 修改配置文件

在`\bin` 目录下找到 `pycharm.exe.vmoptions` 和 `pycharm64.exe.vmoptions` 两个文件，使用文本编辑器（如：Notepad、Sublime Text 等）打开在两个文件最后追加：
```plain
-javaagent:{{ Where pycharm.exe }} JetbrainsCrack-release-enc.jar
```
其中`Where pycharm.exe`是一个变量，即你的 PyCharm 安装目录，如：
```bash
-javaagent:D:\Program Files\JetBrains\PyCharm 2018.3.2\bin\JetbrainsCrack-release-enc.jar
```
**update** 如果是`Linux`或者`Mac`系统，上方的`pycharm.exe.vmoptions`文件可能并不存在，这个时候请活学活用，查找`vmoptions`关键字即可；另外，如果是`32`位操作系统，可能并没有`64`位的应用程序，这种情形本人并没有进行过相应尝试。

## 输入激活码

点击桌面图标，在弹出的激活对话框中输入以下内容：
```shell
ThisCrackLicenseId-{
“licenseId”:”11011″,
“licenseeName”:”别院牧志”,
“assigneeName”:”masantu.com”,
“assigneeEmail”:”immoyao@gmail.com”,
“licenseRestriction”:””,
“checkConcurrentUse”:false,
“products”:[
{“code”:”II”,”paidUpTo”:”2099-12-31″},
{“code”:”DM”,”paidUpTo”:”2099-12-31″},
{“code”:”AC”,”paidUpTo”:”2099-12-31″},
{“code”:”RS0″,”paidUpTo”:”2099-12-31″},
{“code”:”WS”,”paidUpTo”:”2099-12-31″},
{“code”:”DPN”,”paidUpTo”:”2099-12-31″},
{“code”:”RC”,”paidUpTo”:”2099-12-31″},
{“code”:”PS”,”paidUpTo”:”2099-12-31″},
{“code”:”DC”,”paidUpTo”:”2099-12-31″},
{“code”:”RM”,”paidUpTo”:”2099-12-31″},
{“code”:”CL”,”paidUpTo”:”2099-12-31″},
{“code”:”PC”,”paidUpTo”:”2099-12-31″}
],
“hash”:”2911276/0″,
“gracePeriodDays”:7,
“autoProlongated”:false}
```
查看激活信息
![激活成功](/images/Snipaste_2019-12-25_22-35-48.png)

## 太长不读

如果觉得手动操作太累，可以尝试直接用`Python`代码的方式实现。源码见此[Active_PyCharm](https://github.com/imoyao/my_practices/tree/master/codes/active_pycharm)