---
title: 一些暂时无用的代码片段
toc: true
date: 2020-08-14 12:27:56
tags: 
- Python
---

## 对比文件是否相同
```python
def cmp_file_is_diff(f1, f2):
    """
    该功能不一定需要，因为我们的监控操作应该可以保证数据一致性
    see also: https://stackoverflow.com/questions/254350/in-python-is-there-a-concise-way-of-comparing-whether-the-contents-of-two-text
    对比两个文件是否相同
    1. 对比文件大小
    2. 二进制读取，每次读取buffer是否相同
    :param f1: str,
    :param f2: str
    :return: bool
    """
    st1 = os.stat(f1)
    st2 = os.stat(f2)

    # 比较文件大小
    if st1.st_size != st2.st_size:
        return False

    bufsize = 8 * 1024
    with open(f1, 'rb') as fp1, open(f2, 'rb') as fp2:
        while True:
            b1 = fp1.read(bufsize)  # 读取指定大小的数据进行比较
            b2 = fp2.read(bufsize)
            if b1 != b2:
                return False
            if not b1:
                return True
```