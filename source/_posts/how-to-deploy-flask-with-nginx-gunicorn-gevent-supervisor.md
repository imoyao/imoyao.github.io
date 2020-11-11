---
title: 如何使用 Gunicorn+Gevent+Supervisor+Nginx 部署 Flask 应用
date: 2019-08-07 15:21:59
tags:
- Nginx
- Flask
- 部署
- Web 开发
---
## 组件介绍

1. Nginx: 高性能`Web`服务器，负责反向代理；

2. gunicorn: （Green Unicorn，绿色独角兽）高性能 uWSGI 服务器；

3. gevent: 将`Python`同步代码转换为异步的协议库；

4. supervisor: 监控服务流程的工具；

## 版本信息
```bash
-bash-4.2# gunicorn --version
gunicorn (version 19.9.0)

```

## 安装 gunicorn 和 gevent

```bash
pip install gunicorn
pip install gevent
```
## 配置 gunicorn
```python
# gun.py
import os
import gevent.monkey

gevent.monkey.patch_all()

import multiprocessing

if not os.path.exists('log'):
    os.mkdir('log')
debug = True
loglevel = 'debug'
# 绑定的ip及端口号
bind = '0.0.0.0:5000'
pidfile = 'log/gunicorn.pid'
logfile = 'log/debug.log'

# 启动的进程数
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = 'gunicorn.workers.ggevent.GeventWorker'

x_forwarded_for_header = 'X-FORWARDED-FOR'

```
### 启动服务

```bash
-bash-4.2# gunicorn -k gevent -c gun.py runserver:app
[2019-08-07 16:00:20 +0800] [32111] [DEBUG] Current configuration:
  config: gun.py
  bind: ['0.0.0.0:5000']
  backlog: 2048
  workers: 3
  worker_class: gevent
  threads: 1
# ………… 省略中间部分
  ciphers: TLSv1
  raw_paste_global_conf: []
[2019-08-07 16:00:20 +0800] [32111] [INFO] Starting gunicorn 19.9.0
[2019-08-07 16:00:20 +0800] [32111] [DEBUG] Arbiter booted
[2019-08-07 16:00:20 +0800] [32111] [INFO] Listening at: http://0.0.0.0:5000 (32111)
[2019-08-07 16:00:20 +0800] [32111] [INFO] Using worker: gevent
[2019-08-07 16:00:20 +0800] [32115] [INFO] Booting worker with pid: 32115
[2019-08-07 16:00:20 +0800] [32116] [INFO] Booting worker with pid: 32116
[2019-08-07 16:00:20 +0800] [32117] [INFO] Booting worker with pid: 32117
[2019-08-07 16:00:20 +0800] [32111] [DEBUG] 3 workers

```
此时正常访问`http://10.10.15.111:5000/`应该可以看到首页信息提示表示连接服务正常。  
**注意**：此处 ip 和端口均由自己设置，所以访问时应该做相应调整。  
如果无法正常访问，则需要验证防火墙是否正常：  
- CentOS 7 以下版本  
```bash
# 查询
-bash-4.2# iptables -nL|grep 5000
# 开放指定端口
-bash-4.2# iptables -I INPUT -p tcp --dport 5000 -j ACCEPT
# 再次查询
-bash-4.2# iptables -nL|grep 5000
ACCEPT     tcp  --  0.0.0.0/0            0.0.0.0/0            tcp dpt:5000
```
- CentOS 7  
使用`firewall-cmd`管理防火墙端口
```bash
firewall-cmd --query-port=5000/tcp      # no
firewall-cmd --add-port=5000/tcp --permanent
firewall-cmd --reload
firewall-cmd --query-port=5000/tcp  # yes
systemctl status firewall
systemctl status firewalld
systemctl restart firewalld
```
## 安装 nginx 和 supervisor

```bash
yum -y install nginx supervisor
```
### 配置 nginx


默认安装的 Nginx 配置文件`/etc/nginx/nginx.conf`内有如下配置

```bash
include /etc/nginx/conf.d/*.conf;
```

即从外部目录`/etc/nginx/conf.d/`文件夹下还引入了其他配置文件。
这样，我们不修改默认配置，只在`/etc/nginx/conf.d/`目录下增加一个`***.conf`，来在外面增加新配置。

在`/etc/nginx/conf.d/`增加`app.conf`，内容如下：

```bash
server {
    listen  80;     # 如果80端口被占用，可以使用其他端口，记得在防火墙中打开相应端口
    server_name localhost;
    charset utf-8; 
    access_log /var/pmmt/access.log;
    error_log /var/pmmt/error.log;

    client_max_body_size 100M;

    location / {
            proxy_pass  http://0.0.0.0:5000;
            proxy_http_version 1.1;
            proxy_connect_timeout 300;
            proxy_send_timeout 300;
            proxy_read_timeout 300;
            send_timeout 300;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_set_header Host $http_host;
            proxy_set_header X-Scheme $scheme;
            proxy_set_header X-Forwarded-For $remote_addr;
            proxy_set_header X-Forwarded-Port $server_port;
            proxy_set_header X-Request-Start $msec;
    }
}
```
### 启动服务
```bash
systemctl start nginx
```
- 报错`nginx: [emerg] getpwnam("nginx") failed in /etc/nginx/nginx.conf:5`
查看配置该行内容为`user nginx;`，添加用户`useradd nginx`；

### 报错

- ERR_CONTENT_LENGTH_MISMATCH  
    查看 nginx 错误日志
    
    ```bash
    $ tailf /var/log/nginx/error.log
    2019/08/09 03:04:21 [crit] 24616#0: *204 open() "/var/lib/nginx/tmp/proxy/2/03/0000000032" failed (13: Permission denied) while reading upstream, client: 10.10.15.199, server: localhost, request: "GET /static/js/app.1b53c809113e333c2727.js.map HTTP/1.1", upstream: "http://0.0.0.0:5000/static/js/app.1b53c809113e333c2727.js.map", host: "10.10.15.111:82"
    ```

    参考这里：[ERR_CONTENT_LENGTH_MISMATCH 解决方法](https://blog.csdn.net/mr_ooo/article/details/81068369)      
- 进入首页出现`403 Forbidden`
    1. nginx 启动用户和配置中的工作用户不一致（注意：如果你的`nginx`服务是`root`用户运行，则配置中`user`项配置为`root`）；
    2. 配置文件中缺少 index index.html index.htm index.php 行；
    3. nginx 用户没有相应工作目录的操作权限（`chown -R nginx:nginx WORK_DIR_PATH`）；
    4. 防火墙设置。         
    参考这里：[解决 Nginx 出现 403 forbidden (13: Permission denied)报错的四种方法](https://blog.csdn.net/onlysunnyboy/article/details/75270533)


## 配置 Supervisor

首先检查是否存在配置文件，一般配置文件的路径是`/etc/supervisord.conf`，如果配置文件不存在，我们可以通过命令来生成：
```bash
echo_supervisord_conf > /etc/supervisord.conf
```
配置文件的内容很多，项目配置可以参照[官网文档](http://www.supervisord.org/introduction.html)

打开配置文件的最后一行
```bash
;[include]
;files = /etc/supervisord/*.conf    # 注意：本人安装版本为ini格式，所以我们自写的配置也应该调整为相应的.ini格式[include] \n files = supervisord.d/*.ini 
```
默认一般是注释掉的，我们可以取消注释，这行配置的作用也很浅显，就是导入设置的路径下的所有`conf`文件，这使得我们如果有多个项目可以不用都写在同一个配置文件里，可以一个项目一个配置文件，更适合管理。这里的路径也是可以按照实际需求随意更改。
手动启动 Supervisord
```bash
supervisord -c /etc/supervisord.conf
```
在设置的路径下新建一个配置文件，命令请根据上一步设置的扩展名。
```bash
[program:project_name]
command=/usr/bin/gunicorn -c gun.py runserver:app       # 具体路径根据自己安装或者虚拟环境中的位置进行配置
directory=/project_path/        # 项目路径
startsecs=0
stopwaitsecs=0
autostart=true
autorestart=true
```
`project_name`按照你的实际需求修改，作为你这个服务的唯一标识，用于启动停止服务时使用。
`command`修改为测试`gunicorn`时使用的命令，建议使用绝对路径。
`directory`指定了工作路径，通常设置为项目根目录，我们填写的 gun.py 和 app 都是基于这个路径的。

管理`Supervisor`的项目是使用`supervisorctl`命令，我们可以启动项目试试看

```bash
supervisorctl start PROJECT_NAME
```
如果没有报错，应该可以和上一步测试`gunicorn`一样可以正常访问项目了。
验证
```bash
-bash-4.2# supervisorctl
app                              RUNNING   pid 24639, uptime 0:20:55
```
### 报错记录

- Error: Another program is already listening on a port that one of our HTTP servers is configured to use.  Shut this program down first before starting supervisord. For help, use /usr/bin/supervisord -h  
```bash
# 可以查看supervisor.sock并删除 
-bash-4.2# find / -name supervisor.sock 
/run/supervisor/supervisor.sock
-bash-4.2# unlink /run/supervisor/supervisor.sock
```
再次重新启动
```bash
-bash-4.2# supervisord -c /etc/supervisord.conf
```

## 参考来源
1. [Huawei Cloud Centos7 Flask+Gunicorn+Gevent+Supervisor+Nginx Multi-site Production Environment Deployment](https://programmer.help/blogs/5c13afa73d10a.html)
2. [Flask + Nginx + Gunicorn + Gevent 部署](https://www.jianshu.com/p/192e62a5cdd2)
3. [gunicorn+gevent+nginx 部署 flask 应用](https://www.jianshu.com/p/65fae00615b9)
4. [CentOS 上 Flask + uWSGI + Nginx 部署](https://blog.csdn.net/spark_csdn/article/details/80790929)
4. [Nginx、Gunicorn 在服务器中分别起什么作用](https://www.zhihu.com/question/38528616)
