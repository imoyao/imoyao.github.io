---
title: Python 多线程模块 threading 初探
tags:
- Python
---
写`Python`这么久了，一直对`socket`和`threading`等模块懵懵懂懂，项目中看到这里的相关代码基本也是绕着走。但是：
> 我经常有那种感觉，如果这个事情来了，你却没有勇敢地去解决掉，它一定会再来。生活真是这样，它会一次次地让你去做这个功课直到你学会为止。
<div align = right> <font size = 2> ——廖一梅·《像我这样笨拙地生活》 </font> </div>​​​​

所以，只得硬着头皮尽量学习一下，前期最起码的要求是能看懂别人写的代码，后面继续学习。

## 单线程处理
设想这样一个场景，当我们还是刚上班的小菜鸟的时候，一般会这样度过一天：先做手头的工作，然后悄咪咪地放歌听。一般都是先做完工作才敢去听歌。用代码写一下：
```python

#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time


def play_music(mu_names):
    for index, music in enumerate(mu_names):
        print('For {0},I am playing music:{1} at {2}.'.format(
            index, music, time.time()))
        time.sleep(1)


def do_job(job_names):
    for index, job in enumerate(job_names):
        print('For {0},I am doing job:{1} at {2}.'.format(
            index, job, time.time()))
        time.sleep(3)


def noob_time(job_names, music_names):
    print('time for working...', time.time())
    do_job(job_names)
    play_music(music_names)
    print('time for Go-live...', time.time())


if __name__ == '__main__':

    music_name_lists = ['山丘', '同桌的你', '历历万乡']
    work_lists = ['Program', 'Edit_Document', 'Debug']
    noob_time(work_lists, music_name_lists)

```
我们用 `Sublime` 运行一下：
```plain
# 运行结果
('time for working...', 1512702893.041)
For 0,I am doing job:Program at 1512702893.04.
For 1,I am doing job:Edit_Document at 1512702896.04.
For 2,I am doing job:Debug at 1512702899.04.
For 0,I am playing music:山丘 at 1512702902.04.
For 1,I am playing music:同桌的你 at 1512702903.04.
For 2,I am playing music:历历万乡 at 1512702904.04.
('time for Go-live...', 1512702905.043)
[Finished in 12.2s]
```
耗时 12 秒。
随着我们慢慢学习进步，对项目代码越来越熟悉，技术更加精进，对自己的能力很有信心的时候：工作上面就那些东西，同时做也没啥问题。于是我们开启工作娱乐两不误的工作模式：

```python

#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
import threading


def play_music(mu_names):   # 同上
    pass


def do_job(job_names):      # 同上
    pass


def intermediate_time(music_names, job_names):
    thread_lists = []
    music_th = threading.Thread(target=play_music, args=(music_names,))
    thread_lists.append(music_th)
    job_th = threading.Thread(target=do_job, args=(job_names,))
    thread_lists.append(job_th)
    print('time for entertaining...', time.time())
    for task in thread_lists:
        task.start()
    time.sleep(2)
    print('time for Go-live...', time.time())


if __name__ == '__main__':

    music_lists = ['山丘', '同桌的你', '历历万乡']
    job_lists = ['Program', 'Edit_Document', 'Debug']
    intermediate_time(music_lists, job_lists)

```
运行结果：
```plain
('time for entertaining...', 1512718414.723)
For 0,I am playing music:山丘 at 1512718414.73.
For 0,I am doing job:Program at 1512718414.73.
For 1,I am playing music:同桌的你 at 1512718415.73.
('time for Go-live...', 1512718416.727)
Do things together(intermediate_time) cost:2.0039999485     # 程序结束
For 2,I am playing music:历历万乡 at 1512718416.73.
For 1,I am doing job:Edit_Document at 1512718417.73.
For 2,I am doing job:Debug at 1512718420.73.
[Finished in 10.2s]
```
上面我们导入`Python`多线程模块`threading`,调用`threading.Thread()`方法创建两个线程：`music_th`和`job_th`将线程加入队列（此处暂使用列表假代）
注意在`2s`的时候程序本应该结束，但是因为没有守护线程，所以任务被挂起。相当于项目中没有项目经理，所以虽然`deadline`到了，但是项目并没有完成交付。
Python 中的`threading` 模块，它支持守护线程，可以通过 `setDaemon()` 函数来设定线程的 daemon 属性。当 daemon 属性设置为 `True` 的时候表明主线程的退出可以不用等待子线程完成。默认情况下，daemon 标志为 `False` ，所有的非守护线程结束后主线程才会结束。
```python
def intermediate_time(music_names, job_names):
    thread_lists = []
    mus_th = threading.Thread(target=play_music, args=(music_names,))
    thread_lists.append(mus_th)
    job = threading.Thread(target=do_job, args=(job_names,))
    thread_lists.append(job)
    print('time for entertaining...', time.time())
    for task in thread_lists:
        task.setDaemon(True)        # 设置为守护进程
        task.start()
    time.sleep(2)
    print('time for Go-live...', time.time())
```
运行结果：
```plain
('time for entertaining...', 1512718992.165)
For 0,I am playing music:山丘 at 1512718992.17.
For 0,I am doing job:Program at 1512718992.17.
For 1,I am playing music:同桌的你 at 1512718993.17.
('time for Go-live...', 1512718994.167)
Do things together(intermediate_time) cost:2.00200009346        # 线程耗时
Exception in thread Thread-1 (most likely raised during interpreter shutdown):
[Finished in 3.2s]
```
有了项目经理之后，项目限定 2 个月完成。于是在计时完成后，直接结束。注意：此时我们的项目并没有正常完成。
> Exception in thread Thread-1 (most likely raised during interpreter shutdown)

很明显，这不是我们想要的结果。

于是，老板高薪聘请大牛：调用 `threading` 中的 `join()`方法。该方法能够阻塞当前上下文环境的线程，直到调用此方法的线程终止或到达指定的 timeout（ 可选参数）。利用该方法可以方便地控制主线程和子线程以及子线程之间的执行。
```python

def intermediate_time(music_names, job_names):
    thread_lists = []
    mus_th = threading.Thread(target=play_music, args=(music_names,))
    thread_lists.append(mus_th)
    job = threading.Thread(target=do_job, args=(job_names,))
    thread_lists.append(job)
    print('time for entertaining...', time.time())
    for task in thread_lists:
        task.setDaemon(True)        # 设置为守护进程
        task.start()
    task.join()
    task.join()
    print('time for Go-live...', time.time())

```
运行结果：
```plain
('time for entertaining...', 1512719421.376)
For 0,I am playing music:山丘 at 1512719421.38.
For 0,I am doing job:Program at 1512719421.38.
For 1,I am playing music:同桌的你 at 1512719422.38.
For 2,I am playing music:历历万乡 at 1512719423.38.
For 1,I am doing job:Edit_Document at 1512719424.38.
For 2,I am doing job:Debug at 1512719427.38.
('time for Go-live...', 1512719430.382)
Do things together(intermediate_time) cost:9.007999897
[Finished in 10.2s]
```
与单线程对比，程序运行时间减少 2s ，这样我们就有更多的时间约喜欢的女孩子一起吃着火锅唱着歌啦。

## 参考来源

[python 多线程就这么简单 - 虫师 - 博客园](https://www.cnblogs.com/fnng/p/3670789.html)

深入理解：

[python 专题八.多线程编程之 thread 和 threading](http://blog.csdn.net/eastmount/article/details/50155353)