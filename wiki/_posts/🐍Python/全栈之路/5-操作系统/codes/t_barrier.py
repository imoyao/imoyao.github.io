#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by imoyao at 2020/6/28 17:37
import threading
import time
import random

"""
https://www.cnblogs.com/ZXYloveFR/p/11300172.html

Barrier从字面理解是屏障的意思，主要是用作集合线程，然后再一起往下执行。再具体一点，在Barrier之前，若干个thread各自执行，然后到了Barrier的时候停下，等待规定数目的所有的其他线程到达这个Barrier，之后再一起通过这个Barrier各自干自己的事情。

这个概念特别像小时候集体活动的过程，大家从各自的家里到学校集合，待人数都到齐之后，之后再一起坐车出去，到达指定地点后一起行动或者各自行动。

而在计算机的世界里，Barrier可以解决的问题很多，比如，一个程序有若干个线程并发的从网站上下载一个大型xml文件，这个过程可以相互独立，因为一个文件的各个部分并不相关。而在处理这个文件的时候，可能需要一个完整的文件，所以，需要有一条虚拟的线让这些并发的部分集合一下从而可以拼接成为一个完整的文件，可能是为了后续处理也可能是为了计算hash值来验证文件的完整性。而后，再交由下一步处理。

本示例中模拟发车，按照上座率进行发车，只有等够3个人，才会发一次车，否则会一直等
"""


def worker(barrier):
    # global NUM_THREADS
    print(threading.current_thread().name,
          'waiting for barrier with {} others'.format(
              barrier.n_waiting))
    pause_time = random.randint(1, 5) / 10
    time.sleep(pause_time)

    worker_id = barrier.wait()
    print(threading.current_thread().name, 'after barrier',
          worker_id)

    # except threading.BrokenBarrierError:
    #     print('------!!!--------', NUM_THREADS)
    #     barrier.abort()
    #     print(threading.current_thread().name, 'aborting')
    # else:
    #     print('Sleep {},There just {} leaves!'.format(pause_time, NUM_THREADS))
    #     print(threading.current_thread().name, 'after barrier',
    #           worker_id)


NUM_THREADS_PARTIES = 3
NUM_THREADS = 10


def main():
    b = threading.Barrier(NUM_THREADS_PARTIES)
    for i in range(NUM_THREADS):
        t = threading.Thread(target=worker, args=(b,))
        t.start()
        time.sleep(.6)


main()
