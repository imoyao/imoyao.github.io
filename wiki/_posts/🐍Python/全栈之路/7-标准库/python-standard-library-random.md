---
title: Python 标准库系列之 random 模块
toc: true
date: 2020-05-23 18:21:46
tags:
- 编码
- 面向对象
top: 13

---
# Python 标准库系列之 random 模块

This module implements pseudo-random number generators for various distributions.

**random.random()**

生成 0-1 的小数

```python
>>> random.random()
0.06511225392331632
>>> random.random()
0.9063480964287944
>>> random.random()
0.1255900898753961
>>> random.random()
0.6676866041289258
```

**random.randint(a, b)**

输出 a 和 b 范围内的数，包括 a 和 b

```python
>>> random.randint(1,2)
1
>>> random.randint(1,2)
1
>>> random.randint(1,2)
1
>>> random.randint(1,2)
2
>>> random.randint(1,2)
1
>>> random.randint(1,2)
1
```

**random.randrange(start, stop[, step])**

输出 start 到 stop-1 之间的数，可设置步长

```python
>>> random.randrange(1,3)
2
>>> random.randrange(1,3)
1
>>> random.randrange(1,3)
2
```

**随机验证码实例**

```python
#!/usr/bin/env python
import random
checkcode = ''
# for循环四次
for i in range(4):
    # current=0-3的数字
    current = random.randrange(0,4)
    # 如果current的值不等于i
    if current != i:
    	# 通过chr把数字转换为一个字母赋值给temp
        temp = chr(random.randint(65,90))
    else:
    	# 否则temp=0-9之间的数字
        temp = random.randint(0,9)
    # checkcode = checkcode + str(temp)
    checkcode += str(temp)
# 输出字符
print(checkcode)
```

执行

```bash
ansheng@ansheng-me:~$ python s.py
TCQ1
ansheng@ansheng-me:~$ python s.py
8L01
ansheng@ansheng-me:~$ python s.py
N2EB
ansheng@ansheng-me:~$ python s.py
XIDO
```