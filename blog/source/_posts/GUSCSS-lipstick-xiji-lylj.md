---
title: 不问色号 | 口红色号获取之烈艳蓝金系列
date: 2020-05-10 10:52:09
subtitle: 红色是一种宣言，是存在的证明，是女性气质充满张力的演绎
top_img: /images/Dior-lylj.png
cover: /images/p2559419222.jpg
tags:
- Python
- 爬虫
categories:
- Projects
- GUSCSS
---
## 引言
在项目 `给你点颜色瞧瞧|GUSCSS` 的 [不问色号](https://colors.masantu.com/#/lipsticks) 模块中，需要收集口红的颜色，本文以西集网烈焰蓝金系列唇膏为例，演示如何通过简单的爬虫获取图片，之后使用 OCR 技术对图片文字进行识别，同时获取图片特征颜色部分作为口红的 RGB 色值。

## 使用 urllib.request 获取网页
```plain
import urllib.request
from backend import settings


def get_html(url):
    response = urllib.request.urlopen(url)  # 发出请求并且接收返回文本对象
    html = response.read()  # 调用read()进行读取
    return html


if __name__ == '__main__':
    url = settings.DIOR_LYLJ_URL
    print(get_html(url))

```
### 返回结果
```plain
  File "/usr/local/lib/python3.7/urllib/request.py", line 649, in http_error_default
    raise HTTPError(req.full_url, code, msg, hdrs, fp)
urllib.error.HTTPError: HTTP Error 403: Forbidden

Process finished with exit code 1
```
![公共厕所咩·电影《疯狂的石头》](/images/Snipaste_2020-05-07_22-56-56.png)
<figcaption> 公共厕所咩·电影《疯狂的石头》</figcaption>

这么写，一般网站是不会让你看的。因为正常的用户访问会带浏览器的请求头，而我们用程序访问时没有请求头，网站知道我们是“垃圾请求”，只会白白消耗流量，所以拒绝为我们这样的请求服务。

## 遇到 403 怎么办
为了获取到数据，我们要将程序伪装成“正经人”，告诉网站：我来给你们送钱了，让我进去康康吧？
![headers 作用·电影《赌侠》](/images/urllib-headers.gif)
<figcaption> 穿上燕尾服再去参加 party·电影《赌侠》</figcaption>

于是，我们戴上`headers`的装扮，门口保安一看：这位没问题，进来吧。程序就顺利地进去了。

```python
from urllib.request import urlopen,Request

DIOR_LYLJ_URL = 'https://www.xiji.com/product-127266.html'
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4121.0 Safari/537.36 Edg/84.0.495.2'}


def get_html(url):
        """
        爬取一次之后，保存网页到本地
        """
        content = Request(url, headers=HEADERS)
        response = urlopen(content, timeout=10)
        html = response.read()  # 调用read()进行读取
        with open('../../_data/xiji/products.html', 'wb+') as f:
            f.write(html)
        return html


if __name__ == '__main__':
    print(get_html(DIOR_LYLJ_URL))

```

读取到的内容与我们鼠标右键读取网页源码所获取到的数据实质是一样的。

## 利用 lxml 使用 xPath 解析网页
获取到网站源码之后，我们使用 xpath 规则对目标元素进行提取。
![xPath 提取页面目标元素](/images/Snipaste_2020-05-10_11-40-57.png)
依次获取到页面中该系列链接、编号、名称，之后对图片进行提取并保存到本地。
```python
from lxml import etree
from urllib.request import urlopen, Request

class LYLJ:
    DIOR_LYLJ_URL = 'https://www.xiji.com/product-127266.html'

    @staticmethod
    def get_item_element_tree(item_url):
        """
        给出网页地址，获得网页信息
        :param item_url:
        :return:
        """
        content = Request(item_url, headers=HEADERS)
        response = urlopen(content, timeout=10)
        html = response.read()  # 调用read()进行读取
        result = etree.HTML(html)
        return result

    def load_content(self):
        result = self.get_item_element_tree(DIOR_LYLJ_URL)
        links = result.xpath('//*[@id="product_spec"]/ul/li/span[2]/ul/li/a/@href')
        item_ids = result.xpath('//*[@id="product_spec"]/ul/li/span[2]/ul/li/a/@rel')
        names = result.xpath('//*[@id="product_spec"]/ul/li/span[2]/ul/li/a/span')

        dir_name = self.mk_dir()

        img_src_list = []  # 对当前页单独处理
        img_src = self.get_image_src(result)
        current_id = self.current_item_id()
        self.save_image(img_src, dir_name, current_id)
        img_src_list.append(img_src)

        current_names = [name.text for name in names]
        links.pop(0)  # 移除第一个script
        print('Start get details……')
        for img_id, link in zip(item_ids, links):
            real_link = self.join_link(link)
            result = self.get_item_element_tree(real_link)
            img_src = self.get_image_src(result)
            self.save_image(img_src, dir_name, img_id)
            img_src_list.append(img_src)

        item_ids.insert(0, current_id)
        return item_ids, current_names, img_src_list
```
{% note danger %}
**注意**：
如果遇到报错`lxml.etree.XMLSyntaxError: Opening and ending tag mismatch: link line 14 and head, line 15, column 182`是因为网页中 html 语法不规范，如本例中的`<link rel="stylesheet" href="https://img0.xiji.com/themes/ecstore/images/styles_ex.css?d2019110801">`应该是自闭标签。
{%endnote%}

我们可以添加解析器：
```python
parser = etree.HTMLParser(encoding='utf-8')
html = etree.parse('../../_data/xiji/products.html', parser=parser)
```

爬取到的图片数据如下：
{% gallery %}
![网页](/images/Snipaste_2020-05-10_11-50-52.png)
![本地](/images/Snipaste_2020-05-10_11-48-38.png)
{% endgallery %}

## 数据处理
获取数据完成，下一步，我们需要对图片进行分析，借助`Pillow`识别口红色号的 RGB 色值，使用 [百度 OCR 接口](/blog/2020-05-01/python-OCR/) 识别图片下方的推荐词作为单个色号的描述。具体实现参考源码
最后返回的的处理结果如下：
```plain
[{'id': '127266', 'name': '#520',
      'src': 'https://img0.xiji.com/images/19/01/5b96671ae769403827ec84b8200805abb36a40a0.jpg?1577773530#w',
      'rgb': (247, 0, 83), 'subtile': '爱情水红恋爱中的粉红', 'desc': '这是一支非常有寓意的口红,520我爱你,表白专属色。这是散发着恋爱中粉红泡泡的颜色,暧昧、热恋,都洋溢在唇间。'},
     {'id': '127267', 'name': '#080',
      'src': 'https://img3.xiji.com/images/19/01/cf3cc958da0bc2b3715b69038ad417ef29523110.jpg?1577773529#w',
      'rgb': (220, 2, 3), 'subtile': '微笑正红春晚同款色', 'desc': '这款也是正红偏橘的色调,红多橘少,像是血橙的颜色,清新诱人,更适合日常使用。滋润质地,对唇部非常友好。'},
     {'id': '127268', 'name': '#740',
      'src': 'https://img3.xiji.com/images/19/01/12248f21bf2a429cce01b41fcfd79b232f391e70.jpg?1577773531#w',
      'rgb': (181, 46, 24), 'subtile': '脏橘色南瓜色百搭', 'desc': '网红人气爆款,实力显白,送人送礼佳品,这支口红真的是人见人爱,厚涂也可以hold住!'},
     {'id': '127269', 'name': '#888',
      'src': 'https://img1.xiji.com/images/19/01/003d9dd19d6612a42b107f427cea2a534c851c42.jpg?1577773531#w',
      'rgb': (220, 29, 36), 'subtile': '火焰开运色', 'desc': '888发发发,让人想到热烈的火焰,红红火火。如果觉得正红太艳丽大可选择这款,正红偏橘,非常显白有活力。'},
     {'id': '127270', 'name': '#999金属',
      'src': 'https://img4.xiji.com/images/19/01/fea134055f2050c0a3c9ad992529aa377b0a722f.jpg?1577773532#w',
      'rgb': (168, 15, 9), 'subtile': '人鱼姬正红', 'desc': '已经有999的小仙女一定不能错过这款金属光正红,偏光的微闪人鱼姬色在阳光下不灵不灵的,非常富有层次感。'},
     {'id': '127271', 'name': '#999滋润',
      'src': 'https://img0.xiji.com/images/19/01/6efcdf3646ab405e003d3feefa2d463ac20b9d3a.jpg?1577773534#w',
      'rgb': (201, 2, 5), 'subtile': '经典正红色', 'desc': '颜色最纯正的一款正红色,不挑肤色,喜庆特别显气质。嘴唇状态不好的小仙女一定要选这款,能让唇妆看起来更美腻~'},
     {'id': '127272', 'name': '#999哑光',
      'src': 'https://img1.xiji.com/images/19/01/ae4fa46845a4db70dc8fe02ed4faa214de12ad1c.jpg?1577773533#w',
      'rgb': (190, 18, 14), 'subtile': '经典正红色', 'desc': '李佳琦墙裂推荐的一个色号,每个女人都必须拥有,涂上气场两米八!哑光质地,不偏橘也不偏玫,厚涂薄涂都美到爆炸!'}]
```