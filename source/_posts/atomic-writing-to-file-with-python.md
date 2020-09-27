---
title: 如何使用 Python 对文件进行原子性（atomic）读写操作？
date: 2020-09-23 19:54:54
tags:
- Python
- 文件
- 原子
- 并行
- 上下文管理器
categories:
---

## 前言
我们知道：Python 中一切类文件操作的最佳实践都是使用`with`语句。（如果对于这个说法有疑惑，请参考阅读：[language features - What is the python "with" statement designed for? - Stack Overflow](https://stackoverflow.com/questions/3012488/what-is-the-python-with-statement-designed-for)）在编写[仲裁服务](/blog/2020-07-22/dual-active-with-drbd/)时，我们需要将仲裁服务器的信息记录进配置文件`referee.conf`。同时，不可避免地需要对该文件进行更新。由于系统需要对文件在某个线程中进行读，与此同时另一个线程可能正在对其进行修改。此时，使配置文件操作保持原子性便至关重要。

## 说明
比如我们要将`enable`由`True`改为`False`代表禁用该功能。同时另一个线程读取仲裁服务器的`ip`以不停探测仲裁服务运行状态。则必须保证文件修改操作具有原子性。即使使用 with 打开，还是会有一个窗口导致文件被打开但是新内容没有被刷写，此时意外掉电或重新进入窗口，则可能会导致：数据修改失效、文件被清空等，即无法避免竞态操作。

## 解决方案
一种可行的方案是让文件真正落盘，然后对文件重命名。参考代码：
```python
import os
import tempfile

import os
import tempfile
from contextlib import contextmanager

@contextmanager
def tempfile_cmgr(suffix='', dir=None):
    """ Context for temporary file.

    Will find a free temporary filename upon entering
    and will try to delete the file on leaving, even in case of an exception.

    Parameters
    ----------
    suffix : string
        optional file suffix
    dir : string
        optional directory to save temporary file in
    """

    tf = tempfile.NamedTemporaryFile(delete=False, suffix=suffix, dir=dir)
    tf.file.close()
    try:
        yield tf.name
    finally:
        try:
            os.remove(tf.name)
        except OSError as e:
            if e.errno == 2:
                pass
            else:
                raise

@contextmanager
def open_atomic(filepath, *args, **kwargs):
    """ Open temporary file object that atomically moves to destination upon
    exiting.

    Allows reading and writing to and from the same filename.

    The file will not be moved to destination in case of an exception.

    Parameters
    ----------
    filepath : string
        the file path to be opened
    fsync : bool
        whether to force write the file to disk
    *args : mixed
        Any valid arguments for :code:`open`
    **kwargs : mixed
        Any valid keyword arguments for :code:`open`
    """
    fsync = kwargs.get('fsync', False)

    with tempfile_cmgr(dir=os.path.dirname(os.path.abspath(filepath))) as tmppath:
        with open(tmppath, *args, **kwargs) as file:
            try:
                yield file
            finally:
                # make sure that all data is on disk
                # see http://stackoverflow.com/questions/7433057/is-rename-without-fsync-safe
                if fsync:
                    file.flush()
                    os.fsync(file.fileno())
        os.rename(tmppath, filepath)

```
该方案需要注意的是：
 1. `rename`操作的原子性只针对`POSIX`系统；
 2. 操作的文件系统需要保持一致，即代码中在同一个目录的目的；
 3. 在电源故障，系统崩溃等情况下，性能/响应能力比数据完整性更重要，则可以跳过`os.fsync`步骤；

关于`os.fsync`的说明参见官方文档，[此处](https://docs.python.org/zh-cn/3/library/os.html#os.fsync)：
{% note info %}
强制将文件描述符 `fd` 指向的文件写入磁盘。在 Unix，这将调用原生 `fsync()` 函数；在 Windows，则是 MS `_commit()` 函数。
如果要写入的是缓冲区内的 Python 文件对象 f，请先执行 `f.flush()`，然后执行 `os.fsync(f.fileno())`，以确保与 f 关联的所有**内部缓冲区都写入磁盘**。 
{% endnote %} 
- 不要造轮子 

直接装包：[untitaker/python-atomicwrites: Powerful Python library for atomic file writes.](https://github.com/untitaker/python-atomicwrites)，然后代码这么写：
```python

from atomicwrites import atomic_write

with atomic_write('foo.txt', overwrite=True) as f:
    f.write('Hello world.')
    # "foo.txt" doesn't exist yet.
```

## 推荐阅读
- [Reliable file updates with Python – gocept blog](https://blog.gocept.com/2013/07/15/reliable-file-updates-with-python/)
- 上文中文版：[使用 Python 进行稳定可靠的文件操作 - OSCHINA](https://www.oschina.net/translate/reliable-file-updates-with-python)
- [atomic writing to file with Python - Stack Overflow](https://stackoverflow.com/questions/2333872/atomic-writing-to-file-with-python)
- [通过临时文件实现安全的/原子性的更新文件 - Huang Huang 的博客](https://mozillazg.com/2018/05/a-way-to-atomic-write-or-safe-update-a-file.html)
