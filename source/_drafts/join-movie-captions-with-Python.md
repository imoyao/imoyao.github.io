---
title: '''利用 Python 实现电影字幕拼接'''
date: 2018-03-06 14:07:39
tags:
- Python
---
## 准备

### 安装 OpenCV

#### 首先更新相关的 package

sudo apt-get update

sudo apt-get install build-essential cmake git libgtk2.0-dev pkg-config libavcodec-dev libavformat-dev libswscale-dev

编译 OpenCV 需要用到下面的一些 package： GCCCMakeGTK+2.x or higherpkg-configffmpeg or libav development packages: libavcodec-dev, libavformat-dev, libswscale-dev

sudo apt-get install python2.7-dev #2.7 可以改为 3.2 或者 3.5
3. 下载 OpenCV 的源码

OpenCV 官网上有 Linux 版本的源码包可以下载，不过最好是从 git 上下载，这样可以保证下载得到的是最新的代码：

wget -O opencv.zip https://github.com/Itseez/opencv/archive/3.2.0.zip
unzip opencv.zip
4. 编译安装

进入到 OpenCV 的文件夹中，创建一个 build 目录，进行编译：

cd opencv-3.2.0
mkdir build
cd build
cmake -D CMAKE_BUILD_TYPE=RELEASE -D CMAKE_INSTALL_PREFIX=/usr/local ..

# 下载 ippicv_linux_20151201.tgz 过程较慢时，可以使用第三方软件下载或者

wget https://raw.githubusercontent.com/Itseez/opencv_3rdparty/81a676001ca8075ada498583e4166079e5744668/ippicv/ippicv_linux_20151201.tgz

sudo make

sudo make install

# 验证
python
import cv2
如果提示：
ImportError: No module named cv2

sudo pip install opencv-python
