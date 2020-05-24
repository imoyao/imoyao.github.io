---
title: Python 标准库系列之 hashlib 模块
toc: true
date: 2020-05-23 18:21:46
tags:
- 编码
- 面向对象
top: 14

---
# Python 标准库系列之 hashlib 模块

This module implements a common interface to many different secure hash and message digest algorithms. Included are the FIPS secure hash algorithms SHA1, SHA224, SHA256, SHA384, and SHA512 (defined in FIPS 180-2) as well as RSA’s MD5 algorithm (defined in Internet RFC 1321). The terms “secure hash” and “message digest” are interchangeable. Older algorithms were called message digests. The modern term is secure hash.

官方文档：https://docs.python.org/3.5/library/hashlib.html

用于加密相关的操作，代替了 md5 模块和 sha 模块，主要提供 SHA1, SHA224, SHA256, SHA384, SHA512 ，MD5 算法

md5 加密

```python
>>> import hashlib
# hashlib后面是把数据加密成什么类型
>>> hash = hashlib.md5()
# 在python3内，加密的字符串转换成字节指定字符编码
>>> hash.update(bytes('ansheng', encoding='utf-8'))
# 获取加密后的md5值
>>> hash.hexdigest()
'b689c8cb15a344802f1cc65480a85dd2'
```

sha1

```python
>>> import hashlib
>>> hash = hashlib.sha1()
>>> hash.update(bytes('ansheng', encoding='utf-8'))
>>> hash.hexdigest()
'd1dec3927fbe94ace7f7ebe6c53a844e0265455a'
```

sha256

```python
>>> import hashlib
>>> hash = hashlib.sha256()
>>> hash.update(bytes('ansheng', encoding='utf-8'))
>>> hash.hexdigest()
'af4a59d7386b9ff8b45212fe61ad081235f8dad3df5fa99904f6f2e8bad90cb8'
```

sha384

```python
>>> import hashlib
>>> hash = hashlib.sha384()
>>> hash.update(bytes('ansheng', encoding='utf-8'))
>>> hash.hexdigest()
'01cab50e3cc7801fec2988573ad62a645daf636a6d2a47d41c7a456113bee6e657a3ff367029f617e38a03d732c8113d'
```

sha512

```python
>>> import hashlib
>>> hash = hashlib.sha512()
>>> hash.update(bytes('ansheng', encoding='utf-8'))
>>> hash.hexdigest()
'79cc48a191152112bd8285979784fc4bba9b0f2d5ac26f96de1ec87a6fbf4935dcb3ba9bc027c3791875b96dd725e01863602f59d4a561bbd2823495cd4553fc'
```

为防止别人对我们的 md5 值进行撞库，我们可以给 md5 加个盐

```python
>>> import hashlib
# hashlib.md5括号内填写盐的内容
>>> hash = hashlib.md5(bytes('me', encoding='utf-8'))
>>> hash.hexdigest()
'ab86a1e1ef70dff97959067b723c5c24'
```

另外一个加盐的模块

```python
>>> import hmac
>>> h = hmac.new(bytes('me', encoding='utf-8'))
>>> h.update(bytes('me', encoding='utf-8'))
>>> h.hexdigest()
'1ad251aa7475610a2376d074cd79d22d'
```