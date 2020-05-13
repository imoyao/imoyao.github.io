---
title: 如何用 Python 识别图片文字（基于百度 OCR API）
date: 2020-05-01 23:57:06
tags:
- Python
- OCR
categories:
- Projects
- GUSCSS
cover: /images/gO1532084224753.jpg
subtitle: 最初选用 OCR 第三方模块，后来发现识别率太低或者硬件要求较高，最后直接使用 API 实现。
---
做项目的时候需要用到文字识别功能，以下是对一些方案的实践，最后选择了[百度文字识别 API](https://ai.baidu.com/ai-doc/OCR/Ek3h7yeiq)，其他的要么是云服务器内存太小，要么是 CPU 太低，没法用。还是直接找最简单快捷的办法。

## 百度文字识别 api

### 安装
```shell
pip install baidu-aip
```
### 代码

```python
from aip import AipOcr
from backend import secrets


class BaiduOCR:
    def __init__(self):
        self.client = AipOcr(secrets.APP_ID, secrets.API_KEY, secrets.SECRET_KEY)
        self.options = {"language_type": "CHN_ENG", "detect_direction": "true", "detect_language": "true",
                        "probability": "true"}

    @staticmethod
    def get_file_content(file_path):
        """
        读取图片
        """
        with open(file_path, 'rb') as fp:
            return fp.read()

    def basic_parse(self, fp):
        image = self.get_file_content(fp)
        ret = self.client.basicGeneral(image)
        return ret

    def main(self, fp):
        ret_data = self.basic_parse(fp)
        return ret_data
        
if __name__ == '__main__':
    fp = '../../_data/lipsticks/mp_test.png' # 测试识别文件路径
    bd_ocr = BaiduOCR()
    ret_data = bd_ocr.main(fp)
    print(ret_data)
```
运行结果
```json5
{'log_id': 2510103433725039650, 'words_result_num': 2, 'words_result': [{'words': '·微信搜一搜'}, {'words': 'Q三傻的编程生活'}]}
```
{% note warning %}
**注意**：估计是原图带有二维码，所以导致识别超时，返回`requests.exceptions.ConnectionError: ('Connection aborted.', timeout('The write operation timed out'))`；而我们手动给二维码打码之后，才可以正常识别。
{% endnote %}

测试图片
![不可识别](/images/mp.png)
![可识别](/images/mp_test.png)

### 再来一遍

调用远程 url 图片：

```python
def basic_parse_url(self, url):
    ret = self.client.basicGeneralUrl(url, self.options)
    return ret
    
if __name__ == '__main__':

    bd_ocr = BaiduOCR()
    url = 'http://img4.xiji.com/images/19/01/6efcdf3646ab405e003d3feefa2d463ac20b9d3a.jpg'
    url_ret_data = bd_ocr.basic_parse_url(url)
    print(url_ret_data)
```
返回结果
```json5
{'log_id': 8559002589980060578, 'direction': 0, 'words_result_num': 4, 'words_result': [{'words': '迪奥999排滋润', 'probability': {'variance': 0.016349, 'average': 0.931602, 'min': 0.602039}}, {'words': '迪奥#99滋润(经典正红色)', 'probability': {'variance': 7.6e-05, 'average': 0.99548, 'min': 0.969314}}, {'words': '颜色最纯正的一款正红色,不挑肤色,喜庆特别显气质。嘴唇状态不好的小仙女', 'probability': {'variance': 0.00176, 'average': 0.988948, 'min': 0.788893}}, {'words': '要选这款,能让唇妆看起来更美', 'probability': {'variance': 5.8e-05, 'average': 0.996976, 'min': 0.97018}}], 'language': -1}
```
![999滋润](https://img4.xiji.com/images/19/01/6efcdf3646ab405e003d3feefa2d463ac20b9d3a.jpg)

### 更多阅读

[文字识别 - 简介 | 百度 AI 开放平台](https://ai.baidu.com/ai-doc/OCR/Ek3h7yeiq)

---

以下方案由于服务器性能不够，没法正常运行。

## pytesseract

### 装包
```plain
pipenv install pytesseract
pipenv install tesseract
yum install tesseract
```
### 下载语言扩展
[tessdoc | Tesseract documentation](https://tesseract-ocr.github.io/tessdoc/Data-Files)

### 编写代码

```python
from PIL import Image
import pytesseract
from backend import settings

def get_content_from_image(image_fp):
    image = Image.open(image_fp)
    content = pytesseract.image_to_string(image, lang='chi_sim')
    return content


if __name__ == '__main__':
    fp = settings.TEST_IMAGE_FP
    ret = get_content_from_image(fp)
    print(ret)

```
### 查看运行结果
![](/images/ocr-1.png)

尼玛，坑爹呢！

## chineseocr_lite

### 下载
```plain
git clone -b master https://github.com/ouyanghuiyu/chineseocr_lite.git

```
### 编译安装
```plain
cd psenet/pse

rm -rf pse.so 
make 
make: python3-config: Command not found
make: python3-config: Command not found
g++ -o pse.so -I include  -std=c++11 -O3   pse.cpp --shared -fPIC
make: g++: Command not found
make: *** [pse.so] Error 127
```
安装 g++
```plain
yum -y install gcc+ gcc-c++
yum install python3-devel -y
```
### 回到主目录
```plain
cd ../..
pwd
/home/imoyao/chineseocr_lite
```
### 安装依赖
如果国内下载依赖太慢可以配置镜像，参考此处：
- [换阿里源](/blog/2018-09-21/get-some-trouble-with-pip/#解决方案)
- [换清华源](/blog/2020-01-12/pip-install-error-Failed-to-establish-a-new-connection-Network-is-unreachable/#%E8%A7%A3%E5%86%B3%E6%96%B9%E6%A1%88)
```plain
pip install -r requirements.txt
pip install torch
pip install torchvision
```
### 运行服务
```plain
(chineseocr_lite) bash-4.2# python app.py 
make: Entering directory `/home/imoyao/chineseocr_lite/psenet/pse'
make: `pse.so' is up to date.
make: Leaving directory `/home/imoyao/chineseocr_lite/psenet/pse'
device: cpu
load model
device: cpu
load model
device: cpu
load model
device: cpu
load model
Traceback (most recent call last):
  File "/root/.local/share/virtualenvs/chineseocr_lite-GxZWTh-N/lib/python3.7/site-packages/web/utils.py", line 526, in take
    yield next(seq)
StopIteration

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "app.py", line 125, in <module>
    app = web.application(urls, globals())
  File "/root/.local/share/virtualenvs/chineseocr_lite-GxZWTh-N/lib/python3.7/site-packages/web/application.py", line 62, in __init__
    self.init_mapping(mapping)
  File "/root/.local/share/virtualenvs/chineseocr_lite-GxZWTh-N/lib/python3.7/site-packages/web/application.py", line 130, in init_mapping
    self.mapping = list(utils.group(mapping, 2))
  File "/root/.local/share/virtualenvs/chineseocr_lite-GxZWTh-N/lib/python3.7/site-packages/web/utils.py", line 531, in group
    x = list(take(seq, size))
RuntimeError: generator raised StopIteration
(chineseocr_lite) bash-4.2# cp /root/.local/share/virtualenvs/chineseocr_lite-GxZWTh-N/lib/python3.7/site-packages/web/utils.py /root/.local/share/virtualenvs/chineseocr_lite-GxZWTh-N/lib/python3.7/site-packages/web/utils.py.bak
```
修改如下：
```plain
 def take(seq, n):
    for i in range(n):
        try:
            yield next(seq)
        except StopIteration:
            return
```
启动服务
```plain
python app.py
```
访问应用：
```plain
http://{{YOUR_DEV_IP}}:8080/ocr # 注意后面的ocr路由而不是首页！
```
### 报错
```plain
  File "/root/.local/share/virtualenvs/chineseocr_lite-GxZWTh-N/lib/python3.7/site-packages/web/httpserver.py", line 255, in __iter__
    path = self.translate_path(self.path)
  File "/usr/local/lib/python3.7/http/server.py", line 820, in translate_path
    path = self.directory
AttributeError: 'StaticApp' object has no attribute 'directory'

```
添加代码
```plain
class StaticApp(SimpleHTTPRequestHandler):
    """WSGI application for serving static files."""
    def __init__(self, environ, start_response):
        self.headers = []
        self.environ = environ
        self.start_response = start_response
        self.directory = os.getcwd()    # 此行

```
参见[此处](https://stackoverflow.com/questions/52439325/webpy-serving-static-files-staticapp-object-has-no-attribute-directory)和[此处](https://github.com/webpy/webpy/pull/468/files)

### 安装 leptonica
```报错
tesseract_ocr.cpp:633:34: fatal error: leptonica/allheaders.h: No such file or directory
     #include "leptonica/allheaders.h"
```
### 安装
```plain
wget http://www.leptonica.org/source/leptonica-1.79.0.tar.gz
tar -xzvf leptonica-1.79.0.tar.gz
cd leptonica-1.79.0
./configure --prefix=/usr/local/leptonica
make && make install

```
### 验证安装
```plain
tesseract -v
tesseract 3.04.00
 leptonica-1.72
  libgif 4.1.6(?) : libjpeg 6b (libjpeg-turbo 1.2.90) : libpng 1.5.13 : libtiff 4.0.3 : zlib 1.2.7 : libwebp 0.3.0
```
