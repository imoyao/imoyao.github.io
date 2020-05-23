---
title: Python 全栈之路系列之 scrapy 爬虫
toc: true
date: 2020-05-23 18:21:46
tags:
- 编码
- scrapy
- 爬虫
---

> An open source and collaborative framework for extracting the data you need from websites.

官网：https://scrapy.org
GITHUB 地址：https://github.com/scrapy/scrapy

Scrapy 运行流程大概如下：

1. 引擎从调度器中取出一个链接(URL)用于接下来的抓取
2. 引擎把 URL 封装成一个请求(Request)传给下载器
3. 下载器把资源下载下来，并封装成应答包(Response)
4. 爬虫解析 Response
5. 解析出实体（Item）,则交给实体管道进行进一步的处理
6. 解析出的是链接（URL）,则把 URL 交给调度器等待抓取

## 安装

因为我是 Ubuntu 系统，所以可以直接通过 pip 安装 scrapy

```bash
pip install scrapy
```

## 使用

创建项目

```bash
scrapy startproject xiaohuar
```

目录结构

```bash
⇒  tree xiaohuawang 
xiaohuawang
# 项目的配置信息，主要为Scrapy命令行工具提供一个基础的配置信息。（真正爬虫相关的配置信息在settings.py文件中）
├── scrapy.cfg
└── xiaohuawang
    ├── __init__.py
    # 设置数据存储模板，用于结构化数据
    ├── items.py
    # 数据处理行为，如：一般结构化的数据持久化
    ├── pipelines.py
    ├── __pycache__
    # 配置文件，如：递归的层数、并发数，延迟下载等
    ├── settings.py
    # 爬虫目录，如：创建文件，编写爬虫规则
    └── spiders
        ├── __init__.py
        └── __pycache__

4 directories, 6 files
```

编写爬虫

创建文件："xiaohuar/xiaohuar/spiders/myspider.py"

```python
#!/usr/bin/env python
# -*- coding:utf-8 -*-
import scrapy

class XiaoHuarSpider(scrapy.spiders.Spider):
    name = "xiaohuar"  # APP的名字，必须定义
    start_urls = [
        "http://www.xiaohuar.com/hua/",  # 起始URL
    ]

    def parse(self, response):  # 抓取start_urls页面，自动执行parse回调函数
        current_url = response.url  # 当前请求的URL
        body = response.body  # 请求的内容
        unicode_body = response.body_as_unicode()  # 编码
        print(body)
```

运行

进入 xiaohuar 目录，运行命令

```bash
scrapy runspider myspider.py --nolog  # 不输出debug日志
```

一个抓取图片的小实例

```python
#!/usr/bin/env python
# -*- coding:utf-8 -*-
import scrapy
import os
import urllib
from scrapy.selector import HtmlXPathSelector


class XiaoHuarSpider(scrapy.spiders.Spider):
    name = "xiaohuar"  # APP的名字，必须定义
    start_urls = [
        "http://www.xiaohuar.com/hua/",  # 起始URL
    ]

    def parse(self, response):  # 抓取start_urls页面，自动执行parse回调函数
        hxs = HtmlXPathSelector(response)  # 匹配查找
        items = hxs.select('//div[@class="item_list infinite_scroll"]/div')
        for i in range(len(items)):
            srcs = hxs.select(
                '//div[@class="item_list infinite_scroll"]/div[%d]//div[@class="img"]/a/img/@src' % i).extract()
            names = hxs.select(
                '//div[@class="item_list infinite_scroll"]/div[%d]//div[@class="img"]/span/text()' % i).extract()
            schools = hxs.select(
                '//div[@class="item_list infinite_scroll"]/div[%d]//div[@class="img"]/div[@class="btns"]/a/text()' % i).extract()
            if srcs and names and schools:
                # print(names, srcs, schools)
                # ['覃罗莹'] ['/d/file/20161018/5385b7113046ac9ae560da41a44b12af.jpg'] ['广西农业职业技术学院']
                try:
                    ab_src = "http://www.xiaohuar.com" + srcs[0]  # 文件路径
                    file_name = names[0] + "." + srcs[0].split(".")[-1]  # 保存的文件名
                    file_path = os.path.join("./pic", file_name)  # 保存的路径
                    # print(ab_src, file_name, file_path)
                    # http://www.xiaohuar.com/d/file/20161018/5385b7113046ac9ae560da41a44b12af.jpg 覃罗莹jpg ./pic/覃罗莹jpg
                    urllib.request.urlretrieve(ab_src, file_path)  # 下载文件
                except Exception as e:
                    print("错误》》", e)
```

## 选择器

基本的选择器

|选择器|描述|
|:--|:--|
|`//`|子子孙孙|
|`/`|孩子|
|`//div[@class="c1"][@id='i1']`|属性选择器|
|`//div//img/@src`|div 下所有的 img 属性 src|
|`//div//a[1]`|索引取值|
|`//div//a[1]//text()`|索引取值的内容|

通过 extract 获取真实的数据：

```python
//div[@class="c1"][@id='i1'].extract()
```

支持正则

|选择器|描述|
|:--|:--|
|`//.select("div//a[1]").re("昵称:(\w+)")`|正则|

官方文档：http://scrapy-chs.readthedocs.io/zh_CN/latest/topics/selectors.html

两种查找方式

```python
# 即将被废弃的
from scrapy.selector import HtmlXPathSelector
hxs = HtmlXPathSelector(response)
items_HtmlXPathSelector = hxs.select('//div[@class="item_list infinite_scroll"]/div')
print(len(items_HtmlXPathSelector))

from scrapy.selector import Selector
items_Selector = Selector(response=response).xpath('//div[@class="item_list infinite_scroll"]/div')
print(len(items_Selector))
```

正则表达式实例

```html
<body>
    <li class="item-"><a href="link.html">first item</a></li>
    <li class="item-0"><a href="link1.html">first item</a></li>
    <li class="item-1"><a href="link2.html">second item</a></li>
</body>
```
```python
ret = Selector(response=response).xpath('//li[re:test(@class, "item-\d*")]//@href').extract()
# re -- 通过正则进行匹配
# test -- 匹配
```

## 扩展

重复的 URL 不访问

先把长的 URL 进行 MD5 加密，加密成 32 或者 64 位，可以保存在一个集合或者缓存、数据库中，每次抓取之前都先判断有没有这个 URL。

递归查找

![scrapy-level](https://blog.ansheng.me/images/2016/12/1483065549.png)

设置查找深度：修改`settings.py`配置文件，加入以下参数指定深度`DEPTH_LIMIT = 1`

内容格式化

就是相当于分类，比如说下面的文件：

|文件|功能|
|:--|:--|
|`myspider.py`|查找 URL 的规则|
|`items.py`|数据|
|`pipelines.py`|数据持久化|

如图所示：

![scrapy-format](https://blog.ansheng.me/images/2016/12/1483065578.png)