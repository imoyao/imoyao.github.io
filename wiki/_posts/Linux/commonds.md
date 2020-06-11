---
title: 日常指令
toc: true
date: 2020-05-23 12:27:56
tags: wiki
---
## dos2unix
在进行日常开发的时候，很多人可能用的是 Windows 系统，而在代码运行的开发环境一般是 Linux 环境，直接上传可能文件格式不同，所以需要进行转换。

### 单个文件转换
1. 查看文件格式
使用 vim 打开`set ff`可以看到 dos 或 unix 的字样；
2. 设置文件类型
`set ff=unix`
把它强制设为 unix 格式, 然后存盘退出

### 整个目录转换
下面列出怎么对整个目录中的文件做`dos2unix`操作  
`$ find . -type f -exec dos2unix {} \;`

其中具体命令的解释如下：
```plain
find .
= find files in the current directory		查找当前目录
-type f
= of type f		文件类型为f的（文件file）
-exec dos2unix {} \;
= and execute dos2unix on each file found	执行文件转换
```