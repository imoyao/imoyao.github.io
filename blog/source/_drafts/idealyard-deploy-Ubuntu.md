---
title: idealyard-deploy-Ubuntu
date: 2020-05-14 16:39:32
tags:
categories:
hide: true
---
## 后端
1. 安装 `venv`
```bash
sudo apt-get install python3-venv
```
2. 创建虚拟环境
```bash
cd idealyard
python3 -m venv blog
source blog/bin/active
```
3. 安装 Python 依赖
```bash
pip install -r requirements.txt
```
4. 启动服务
```bash
python runserver.py

 * Serving Flask app "back" (lazy loading)
 * Environment: development
 * Debug mode: on
 * Running on http://0.0.0.0:5000/ (Press CTRL+C to quit)
 * Restarting with stat

```
### 数据库
- mariadb/MySQL
```bash
sudo apt install mariadb-server
sudo apt install mariadb-client-core-10.1
```
### redis

### 

## 前端

1. 安装依赖
```bash
cd front
npm install
```