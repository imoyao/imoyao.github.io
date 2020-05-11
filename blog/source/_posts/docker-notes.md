---
title: Docker 实践手册
date: 2020-05-07 14:42:38
tags:
- Docker
- 容器化
- 容器
categories:
- 工具
---
## 什么是 Docker
Docker 是针对程序开发人员和系统管理员来**开发、部署、运行**应用的一个虚拟化平台。
使用容器部署应用程序称为容器化。更多参考：[What is a Container? | App Containerization | Docker](https://www.docker.com/resources/what-container)
### 容器化的优势
灵活：即使最复杂的应用程序也可以容器化。
轻量级：容器利用并共享了主机内核，在系统资源方面比虚拟机更加有效。
可移植：您可以在本地构建，部署到云上并在任何地方运行。
解耦：容器是高度自给自足并封装的容器，使您可以在不破坏其他容器的情况下更换或升级它们。
可扩展：您可以在数据中心内增加并自动分布容器副本。
安全：容器将积极的约束和隔离应用于流程，而无需用户方面的任何配置。
### 镜像和容器
从根本上讲，一个容器不过是一个正在运行的进程，并对其应用了一些附加的封装功能，以使其与主机和其他容器隔离. 容器隔离的最重要方面之一是每个容器都与自己的专用文件系统进行交互. 该文件系统由 Docker 镜像提供。映像包括运行应用程序所需的一切——代码或二进制文件，运行时刻（runtime），依赖项以及所需的任何其他文件系统对象.
### 容器和虚拟机
容器（Linux Containers，缩写为 LXC）在 Linux 上本地运行 ，并与其他容器共享主机的内核。它运行一个隔离的进程，不占用任何其他可执行文件更多的内存，从而使其轻量化。

虚拟机（virtual machine）就是带环境安装的一种解决方案。它可以在一种操作系统里面运行另一种操作系统，比如在 Windows 系统里面运行 Linux 系统。应用程序对此毫无感知，因为虚拟机看上去跟真实系统一模一样，而对于底层系统来说，虚拟机就是一个普通文件，不需要了就删掉，对其他部分毫无影响。

虽然用户可以通过虚拟机还原软件的原始环境。但是，这个方案有几个缺点：
1. 资源占用多
虚拟机会独占一部分内存和硬盘空间。它运行的时候，其他程序就不能使用这些资源了。哪怕虚拟机里面的应用程序实际使用的内存只有 1MB，虚拟机本身依然需要几百 MB 的内存才能运行。
2. 冗余步骤多
虚拟机是完整的操作系统，一些系统级别的操作步骤，往往无法跳过，比如用户登录。
3. 启动慢
启动操作系统需要多久，启动虚拟机就需要多久。可能要等几分钟，应用程序才能真正运行。
![](/images/docker-vs-VM.png)

## Docker 架构
[Docker architecture](https://docs.docker.com/get-started/overview/#docker-architecture)
{% raw %}

<table class="reference">
 <tbody>
<tr><th width="20%">概念</th><th>说明</th></tr>
  <tr>
   <td><p>Docker 镜像(Images)</p></td>
   <td><p>Docker 镜像是用于创建 Docker 容器的模板，比如 Ubuntu 系统。 </p></td>
  </tr>
  <tr>
   <td><p>Docker 容器(Container)</p></td>
   <td><p>容器是独立运行的一个或一组应用，是镜像运行时的实体。</p></td>
  </tr>
  <tr>
   <td><p>Docker 客户端(Client)</p></td>
   <td><p>
Docker 客户端通过命令行或者其他工具使用 Docker SDK (<a href="https://docs.docker.com/develop/sdk/" target="_blank" rel="noopener noreferrer">https://docs.docker.com/develop/sdk/</a>) 与 Docker 的守护进程通信。</p></td>
  </tr>
  <tr>
   <td><p>Docker 主机(Host)</p></td>
   <td><p>一个物理或者虚拟的机器用于执行 Docker  守护进程和容器。</p></td>
  </tr>
  <tr>
   <td><p>Docker Registry</p></td>
   <td><p>Docker 仓库用来保存镜像，可以理解为代码控制中的代码仓库。</p>
<p>Docker Hub(<a href="https://hub.docker.com" target="_blank" rel="noopener noreferrer">https://hub.docker.com</a>) 提供了庞大的镜像集合供使用。</p>
  <p>一个 Docker Registry 中可以包含多个仓库（Repository）；每个仓库可以包含多个标签（Tag）；每个标签对应一个镜像。</p>

<p>通常，一个仓库会包含同一个软件不同版本的镜像，而标签就常用于对应该软件的各个版本。我们可以通过 <span class="marked">&lt;仓库名&gt;:&lt;标签&gt;</span> 的格式来指定具体是这个软件哪个版本的镜像。如果不给出标签，将以 <strong>latest</strong> 作为默认标签。</p></td>
  </tr>
  <tr>
   <td><p>Docker Machine</p></td>
   <td><p>Docker Machine是一个简化Docker安装的命令行工具，通过一个简单的命令行即可在相应的平台上安装Docker，比如VirtualBox、 Digital Ocean、Microsoft Azure。</p></td>
  </tr>
 </tbody>
</table>

{% endraw %}

## docker 环境安装
[Install Docker Engine on CentOS | Docker Documentation](https://docs.docker.com/engine/install/centos/)
### 安装校验
- 状态测试
```shell
systemctl status docker
```
```plain
● docker.service - Docker Application Container Engine
   Loaded: loaded (/usr/lib/systemd/system/docker.service; enabled; vendor preset: disabled)
   Active: active (running) since Wed 2020-05-06 18:14:52 CST; 22h ago
     Docs: http://docs.docker.com
# too long no show
Hint: Some lines were ellipsized, use -l to show in full.
```
- 版本检查
```shell
docker --version
```
```plain
Docker version 1.13.1, build 7f2769b/1.13.1
```
- 功能测试
```plain
[root@cephnode1 ~]# docker run hello-world
```
此命令会直接从 image 文件生成正在运行的容器实例，如果镜像不存在，则会自动使用`docker image pull`去仓库抓取。
```plain
WARNING: IPv4 forwarding is disabled. Networking will not work.

Hello from Docker!
This message shows that your installation appears to be working correctly.

# too long no show

Share images, automate workflows, and more with a free Docker ID:
 https://hub.docker.com/

For more examples and ideas, visit:
 https://docs.docker.com/get-started/
```

## 命令
执行`docker --help`可以看到所有支持的指令如下：

```plain
Usage:	docker COMMAND

A self-sufficient runtime for containers

Options:
      --config string      Location of client config files (default "/root/.docker")
  -D, --debug              Enable debug mode
      --help               Print usage
  -H, --host list          Daemon socket(s) to connect to (default [])
  -l, --log-level string   Set the logging level ("debug", "info", "warn", "error", "fatal") (default "info")
      --tls                Use TLS; implied by --tlsverify
      --tlscacert string   Trust certs signed only by this CA (default "/root/.docker/ca.pem")
      --tlscert string     Path to TLS certificate file (default "/root/.docker/cert.pem")
      --tlskey string      Path to TLS key file (default "/root/.docker/key.pem")
      --tlsverify          Use TLS and verify the remote
  -v, --version            Print version information and quit

Management Commands:
  container   Manage containers
  image       Manage images
  network     Manage networks
  node        Manage Swarm nodes
  plugin      Manage plugins
  secret      Manage Docker secrets
  service     Manage services
  stack       Manage Docker stacks
  swarm       Manage Swarm
  system      Manage Docker
  volume      Manage volumes

Commands:
  attach      Attach to a running container
  build       Build an image from a Dockerfile
  commit      Create a new image from a container's changes
  cp          Copy files/folders between a container and the local filesystem
  create      Create a new container
  diff        Inspect changes on a container's filesystem
  events      Get real time events from the server
  exec        Run a command in a running container
  export      Export a container's filesystem as a tar archive
  history     Show the history of an image
  images      List images
  import      Import the contents from a tarball to create a filesystem image
  info        Display system-wide information
  inspect     Return low-level information on Docker objects
  kill        Kill one or more running containers
  load        Load an image from a tar archive or STDIN
  login       Log in to a Docker registry
  logout      Log out from a Docker registry
  logs        Fetch the logs of a container
  pause       Pause all processes within one or more containers
  port        List port mappings or a specific mapping for the container
  ps          List containers
  pull        Pull an image or a repository from a registry
  push        Push an image or a repository to a registry
  rename      Rename a container
  restart     Restart one or more containers
  rm          Remove one or more containers
  rmi         Remove one or more images
  run         Run a command in a new container
  save        Save one or more images to a tar archive (streamed to STDOUT by default)
  search      Search the Docker Hub for images
  start       Start one or more stopped containers
  stats       Display a live stream of container(s) resource usage statistics
  stop        Stop one or more running containers
  tag         Create a tag TARGET_IMAGE that refers to SOURCE_IMAGE
  top         Display the running processes of a container
  unpause     Unpause all processes within one or more containers
  update      Update configuration of one or more containers
  version     Show the Docker version information
  wait        Block until one or more containers stop, then print their exit codes

Run 'docker COMMAND --help' for more information on a command.

```
更多参考：
- [Docker Command Cheat Sheet - 简书](https://www.jianshu.com/p/b3f42bc85ec3)
- [Docker Free CheatSheet – CheatSheet](https://cheatsheet.dennyzhang.com/cheatsheet-docker-A4)
- [Docker CheatSheet | Docker 配置与实践清单_慕课手记](http://www.imooc.com/article/79968)
- [awesome-cheatsheets/docker.sh at master · LeCoupa/awesome-cheatsheets](https://github.com/LeCoupa/awesome-cheatsheets/blob/master/tools/docker.sh)
- [Docker 命令大全 | 菜鸟教程](https://www.runoob.com/docker/docker-command-manual.html)

## 构建并运行自己的 image
我们可以拉取镜像来运行，但是要制作自己的image，就需要编写Dockerfile。它是一个文本文件。Docker根据改文件生成image文件。
以官网的 [例子](https://docs.docker.com/get-started/part2/) 看一下如何构建image：
首先克隆应用：
```
git clone https://github.com/dockersamples/node-bulletin-board
cd node-bulletin-board/bulletin-board-app
```
之后打开dockerfile，看里面的内容：
```
# 使用官方镜像（node:current-slim）作为父级image，冒号表示标签
FROM node:current-slim
# 设置工作目录，此处目录是你的镜像文件系统，而不是节点文件系统
WORKDIR /usr/src/app
# 将文件从节点拷贝到本地，即拷贝到/usr/src/app/package.json
COPY package.json .
RUN npm install

EXPOSE 8080
CMD [ "npm", "start" ]

COPY . .
```

## 参考资料

[Docker 入门教程 - 阮一峰的网络日志](https://www.ruanyifeng.com/blog/2018/02/docker-tutorial.html)

[什么是 Docker? - Docker 入门教程 - docker 中文社区](http://www.docker.org.cn/book/docker/what-is-docker-16.html)
[Docker 教程 | 菜鸟教程](https://www.runoob.com/docker/docker-tutorial.html)

[Docker 中文文档 Docker 概述-DockerInfo](http://www.dockerinfo.net/document)

[Docker 学习新手笔记：从入门到放弃 - Joe’s Blog](https://hijiangtao.github.io/2018/04/17/Docker-in-Action/)