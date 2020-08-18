---
title: 如何使用 flask-celery 实现异步任务？
date: 2019-06-18 14:14:46
tags:
- Celery
- Flask
- HOWTO
- TODO

categories:
- 工作日常
---
# 先决条件
- `redis`版本
```bash
redis-cli --version
redis-cli 5.0.4
```
- `celery`版本
```bash
celery --version
4.3.0 (rhubarb)
```
- `Flask`和 `Python` 版本
```bash
flask --version
Flask 1.0.2
Python 3.6.5 (default, Apr  1 2018, 05:46:30) 
[GCC 7.3.0]
```
- `Linux` 版本
```bash
lsb_release -a
No LSB modules are available.
Distributor ID:	Ubuntu
Description:	Ubuntu 18.04 LTS
Release:	18.04
Codename:	bionic
# ---
uname -a
Linux local 4.15.0-22-generic #24-Ubuntu SMP Wed May 16 12:15:17 UTC 2018 x86_64 x86_64 x86_64 GNU/Linux

```

## `Celery`是什么

### 概念

`Celery` 是一个“自带电池”的专注于实时处理和任务调度的分布式任务队列，同时提供操作和维护分布式系统所需的**工具**。

### 整体架构

![celery架构图](/images/structure-of-celery.png)
<center><span>celery架构图</span></center>

`Celery`支持定时任务（Celery Beat）和异步执行(Async Task)两种模式。同步模式为任务调用方等待任务执行完成，这种方式等同于 RPC(Remote Procedure Call)， 异步方式为任务在后台执行，调用方调用后就去做其他工作，之后再根据需要来查看任务结果。`Celery`自己没有实现消息队列，而是直接已存在的消息队列作为`Broker`角色。

### 组件

使用 `Celery` 运行后台任务并不像在线程中这样做那么简单，但是好处多多。`Celery` 具有分布式架构，使应用更加易于扩展。一个 `Celery` 安装有三个核心组件：

- `Celery` 客户端: 用于发布后台作业。当与 `Flask` 一起工作的时候，客户端与 `Flask` 应用一起运行。
- Celery workers: 任务消费者，是运行后台作业的进程。`Celery` 支持本地和远程的 `workers`，因此你就可以在 `Flask` 服务器上启动一个单独的 `worker`，随后随着你的应用需求的增加而新增更多的 `workers`。
- 消息代理（`Broker`）: 客户端通过消息队列和 `workers` 进行通信，`Celery` 支持多种方式来实现这些队列。常见的为 `RabbitMQ` 和 `Redis`。
- 任务结果存储：用来存储`workers`执行的任务结果。
详见[Celery 是……](http://docs.jinkan.org/docs/celery/getting-started/introduction.html#id19)

## `Celery`的安装配置

### 安装 `Celery`

```bash
pip install celery
```
安装时会自动解决依赖： 
```bash
Installing collected packages: vine, amqp, kombu, billiard, celery
```
验证
```bash
celery --version
4.3.0 (rhubarb)
```
### 与 `redis` 结合使用

redis 安装可以参考之前写的这篇文章[Linux 下如何安装 Redis？](https://imoyao.github.io/blog/2019-04-11/how-to-install-Redis-on-Linux/)

**注意**： 此处需要同时安装`redis`客户端和`redis`的`Python`支持。
### 验证结果
```plain
imoyao@local:~$ redis-cli
127.0.0.1:6379> keys *
1) "_kombu.binding.celery"
2) "celery-task-meta-a9db6911-e15a-4b9e-b321-958f5298652a"
3) "celery-task-meta-e22b0603-8117-4f0d-ac6b-ad621738e256"
4) "unacked_mutex"
5) "_kombu.binding.celery.pidbox"
6) "celery-task-meta-aac524bd-cb47-4493-b0dd-9712a98a3f14"
7) "_kombu.binding.celeryev"
8) "celery-task-meta-ccd8d274-7f14-4abc-8244-e80f01932097"
9) "celery-task-meta-3b2b3efa-4ad7-4c7e-b92d-27636eaeaa6b"
127.0.0.1:6379> get celery-task-meta-a9db6911-e15a-4b9e-b321-958f5298652a
"{\"status\": \"SUCCESS\", \"result\": 30, \"traceback\": null, \"children\": [], \"task_id\": \"a9db6911-e15a-4b9e-b321-958f5298652a\", \"date_done\": \"2019-06-13T18:43:43.491009\"}"
```
## 如何在项目中使用`Celery`

以与`Flask`结合为例(使用`redis`作为`backend`)

- 创建`celery`实例

```python
# app\__init__.py
from celery import Celery

def init_celery(app):
    """
    参见：http://docs.jinkan.org/docs/flask/patterns/celery.html
    初始化celery
    :return:
    """
    celery = Celery(app.import_name, broker=app.config['CELERY_BROKER_URL'])
    celery.conf.update(app.config)
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    celery.Task = ContextTask
    return celery
```

- 创建后台任务

```python
import os
from celery.utils.log import get_task_logger

from app import create_app, init_celery

lg = get_task_logger(__name__)      # 记录日志
celery = init_celery(create_app(os.getenv('FLASK_CONFIG', 'default')))

# @celery.task(name='pmrearend.task.log_it')        # 此处是解决导入失败的一种方案，但是感觉不够优雅，需要深入了解
@celery.task
def log_it(num1, num2):
    msg = num1 + num2
    print(msg)
    lg.debug("in log_test()")
    return msg


if __name__ == '__main__':
    # task = log_it.delay(5,8)
    task = log_it.apply_async(args=[10, 20], countdown=10)
```
- 新建目录及文件
    ```bash
    sudo mkdir -p /var/log/celery/
    sudo touch /var/log/celery/celery.log 
    ```
- 启动 celery worker 服务

    ```bash
    celery -A task worker -l debug -f /var/log/celery/celery.log
    ```
---

### 遇到的问题记录

1. sqlalchemy.exc.InvalidRequestError

    ```bash
    sqlalchemy.exc.InvalidRequestError: Table 'user' is already defined for this MetaData instance.  
    Specify 'extend_existing=True' to redefine options and columns on an existing Table object.
    
    ```
    解决：在对应 model 中添加`'extend_existing': True`
    ```python
    __table_args__ = {'extend_existing': True}
    ```
2. celery: command not found
    ```bash
    sudo: celery: command not found
    ```
    解决：按照绝对路径调用`celery`
    ```bash
    which celery
    /home/imoyao/envs/py3flk/bin/celery
    ```
    替换此处`celery`的位置即可运行（TODO：不够优雅，暂时测试性解决方案）
    
    ```bash
    sudo /home/imoyao/envs/py3flk/bin/celery -A pmrearend.task worker -l debug -f /var/log/celery/celery.log
    ```
3. 没有导入`task`模块
    ```bash
    [2019-06-14 02:32:40,115: ERROR/MainProcess] Received unregistered task of type 'pmrearend.log_it'.
    The message has been ignored and discarded.
    
    Did you remember to import the module containing this task?
    Or maybe you're using relative imports?
    
    ```
    解决：每个任务必须有不同的名称。如果没有显示提供名称，任务装饰器将会自动产生一个，产生的名称会基于这些信息： 1）任务定义所在的模块， 2）任务函数的名称

    显示设置任务名称的例子：在装饰器`@app.task`中加入参数`name`，就可以被`celery`读取到。  
    
    ```python
    @celery.task(name='pmrearend.task.log_it')
    def log_it(num1, num2):
        msg = num1 + num2
        print(msg)
        lg.debug("in log_test()")
        return msg
    ```   
    正常运行结果
    
    ```plain
    [2019-06-14 02:43:43,139: DEBUG/MainProcess] TaskPool: Apply <function _fast_trace_task at 0x7f72a03fef28> (args:('pmrearend.task.log_it', 'a9db6911-e15a-4b9e-b321-958f5298652a', {'lang': 'py', 'task': 'pmrearend.task.log_it', 'id': 'a9db6911-e15a-4b9e-b321-958f5298652a', 'shadow': None, 'eta': '2019-06-13T18:43:43.139123+00:00', 'expires': None, 'group': None, 'retries': 0, 'timelimit': [None, None], 'root_id': 'a9db6911-e15a-4b9e-b321-958f5298652a', 'parent_id': None, 'argsrepr': '[10, 20]', 'kwargsrepr': '{}', 'origin': 'gen4669@local', 'reply_to': 'a2563c50-9249-3718-85a8-9ad44174831c', 'correlation_id': 'a9db6911-e15a-4b9e-b321-958f5298652a', 'delivery_info': {'exchange': '', 'routing_key': 'celery', 'priority': 0, 'redelivered': None}}, b'[[10, 20], {}, {"callbacks": null, "errbacks": null, "chain": null, "chord": null}]', 'application/json', 'utf-8') kwargs:{})
    [2019-06-14 02:43:43,281: DEBUG/MainProcess] basic.qos: prefetch_count->4
    [2019-06-14 02:43:43,284: WARNING/ForkPoolWorker-1] 30
    [2019-06-14 02:43:43,286: DEBUG/MainProcess] Task accepted: pmrearend.task.log_it[a9db6911-e15a-4b9e-b321-958f5298652a] pid:4089
    [2019-06-14 02:43:43,287: DEBUG/ForkPoolWorker-1] pmrearend.task.log_it[a9db6911-e15a-4b9e-b321-958f5298652a]: in log_test()
    [2019-06-14 02:43:43,504: INFO/ForkPoolWorker-1] Task pmrearend.task.log_it[a9db6911-e15a-4b9e-b321-958f5298652a] succeeded in 0.22014467700500973s: 30
    [2019-06-14 02:43:44,751: INFO/MainProcess] Received task: pmrearend.task.log_it[aac524bd-cb47-4493-b0dd-9712a98a3f14]  ETA:[2019-06-13 18:43:54.619709+00:00] 
    [2019-06-14 02:43:44,752: DEBUG/MainProcess] basic.qos: prefetch_count->5
    [2019-06-14 02:43:54,621: DEBUG/MainProcess] TaskPool: Apply <function _fast_trace_task at 0x7f72a03fef28> (args:('pmrearend.task.log_it', 'aac524bd-cb47-4493-b0dd-9712a98a3f14', {'lang': 'py', 'task': 'pmrearend.task.log_it', 'id': 'aac524bd-cb47-4493-b0dd-9712a98a3f14', 'shadow': None, 'eta': '2019-06-13T18:43:54.619709+00:00', 'expires': None, 'group': None, 'retries': 0, 'timelimit': [None, None], 'root_id': 'aac524bd-cb47-4493-b0dd-9712a98a3f14', 'parent_id': None, 'argsrepr': '[10, 20]', 'kwargsrepr': '{}', 'origin': 'gen4706@local', 'reply_to': 'ee66dc1c-aebd-3111-9ef4-f07a71943fc0', 'correlation_id': 'aac524bd-cb47-4493-b0dd-9712a98a3f14', 'delivery_info': {'exchange': '', 'routing_key': 'celery', 'priority': 0, 'redelivered': None}}, b'[[10, 20], {}, {"callbacks": null, "errbacks": null, "chain": null, "chord": null}]', 'application/json', 'utf-8') kwargs:{})
    [2019-06-14 02:43:54,631: DEBUG/MainProcess] basic.qos: prefetch_count->4
    [2019-06-14 02:43:54,637: WARNING/ForkPoolWorker-1] 30
    [2019-06-14 02:43:54,639: DEBUG/ForkPoolWorker-1] pmrearend.task.log_it[aac524bd-cb47-4493-b0dd-9712a98a3f14]: in log_test()
    [2019-06-14 02:43:54,645: DEBUG/MainProcess] Task accepted: pmrearend.task.log_it[aac524bd-cb47-4493-b0dd-9712a98a3f14] pid:4089
    [2019-06-14 02:43:54,650: INFO/ForkPoolWorker-1] Task pmrearend.task.log_it[aac524bd-cb47-4493-b0dd-9712a98a3f14] succeeded in 0.012691148993326351s: 30
    ```
## 问题记录

```bash
celery.platforms.LockFailed: [Errno 13] Permission denied: '/home/xxx/celerybeat.pid'
```    
pid 文件没有权限；这种情况有两种解决办法：

- 修改 pid 文件存储路径，放到当前执行用户有权限的位置

    ```bash
    celery beat -A celeryapp --loglevel=INFO --pidfile="/tmp/celerybeat.pid"        # 修改路径
    ```

- 对 pid 文件所在目录加权限，然后执行：  
 ```bash
chown -R YOUR_USER_NAME:YOUR_USER_NAME  CURRENT_PATH
celery -A celery_worker:celery beat --loglevel=INFO
```plain
[参见这里](https://github.com/celery/celery/issues/3828)

## 注意问题
**不要**将 task 写进类中，因为可能导致执行出错等各种问题，如果真的要这么做，可以参考这里：  
参见 [using class methods as celery tasks](https://stackoverflow.com/questions/9250317/using-class-methods-as-celery-tasks)

## TODO
因为个人时间关系，这个暂时没有学完。关于`Celery`的使用需要进一步实践学习。

## 参考阅读
[Celery 4.3.0 documentation »](http://docs.celeryproject.org/en/latest/)
[在 Flask 中使用 Celery 的最佳实践](https://www.jianshu.com/p/807efde55d81)
[Celery 中文文档](https://blog.csdn.net/libing_thinking/article/details/78547816)
[Celery-4.1 用户指南: Calling Tasks](https://blog.csdn.net/libing_thinking/article/details/78563222)

## 相关代码库
[1](https://github.com/nebularazer/flask-celery-example)    
[2](https://github.com/chiqj/flask-with-celery-example) 
