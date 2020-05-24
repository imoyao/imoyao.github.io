---
title: Python 标准库系列之 requests 模块
toc: true
date: 2020-05-23 18:21:46
tags:
- 编码
- 面向对象
top: 8

---

# Python 标准库系列之 requests 模块

> Requests is the only Non-GMO HTTP library for Python, safe for human consumption.

官方文档：http://docs.python-requests.org/en/master/

## 安装`Requests`模块

`Requests`模块官方提供了两种方式安装：

pip 方式安装

```bash
pip install requests
```

源码方式安装

```bash
git clone git://github.com/kennethreitz/requests.git
cd requests
python setup.py install
```

验证是否安装成功

进入`python`解释的，导入模块试试，如果导入成功则安装成功，否则就需要检查那里执行错误了呢。

```python
C:\Users\anshengme> python
Python 3.5.1 (v3.5.1:37a07cee5969, Dec  6 2016, 01:54:25) [MSC v.1900 64 bit (AMD64)] on win32
Type "help", "copyright", "credits" or "license" for more information.
>>> import requests
```

## 环境准备

安装`gunicorn`和`httpbin`

```bash
sudo pip3 install gunicorn httpbin
```

启动一个`gunicorn`Server

```bash
⇒  sudo gunicorn httpbin:app
[2016-10-27 11:45:08 +0800] [12175] [INFO] Starting gunicorn 19.6.0
[2016-10-27 11:45:08 +0800] [12175] [INFO] Listening at: https://blog.ansheng.me:8000 (12175)
[2016-10-27 11:45:08 +0800] [12175] [INFO] Using worker: sync
[2016-10-27 11:45:08 +0800] [12178] [INFO] Booting worker with pid: 12178
```

打开浏览器输入将会得到以下页面，相当于在本地启动一个 http server 便于学习 requests 模块

![requests-01](/images/2016/12/1483018481.png)

## 简单的一个 requests 小程序

下面的一个小程序会通过`requests`请求`'https://blog.ansheng.me:8000/ip'`这个 URI 链接，获取到对应的数据。

```python
#!/use/bin/env python3
# _*_ coding:utf-8 _*_
import requests

URL_IP = 'https://blog.ansheng.me:8000/ip'

def use_params_requests():
    # 参数
    params = {'params1': 'Hello', 'params2': 'World'}
    # 发送请求
    response = requests.get(URL_IP, params=params)
    print("响应的状态码：", response.status_code, response.reason)
    print("返回的头部：", response.headers)
    print("把返回的数据转换为json:", response.json())
    print("响应的文本：", response.text)

if __name__ == '__main__':
    use_params_requests()
```

## 发送请求

通过 GITHUB 提供的 API 获取用户信息

```python
#!/use/bin/env python3
# _*_ coding:utf-8 _*_
import requests
import json

URL = 'https://api.github.com'


def build_uri(endpoint):
    return '/'.join([URL, endpoint])


def better_print(json_str):
    return json.dumps(json.loads(json_str), indent=4)


def request_method():
    # 获取用户的所有信息
    response = requests.get(build_uri('users/anshengme'))
    print(better_print((response.text)))

    print("\n")

    # 获取用户的邮箱
    response = requests.get(build_uri('user/emails'), auth=("anshengme.com@gmail.com", "xxxxxx"))
    print(better_print((response.text)))


if __name__ == '__main__':
    request_method()
```

带参数的请求

```Python
# 使用params传参
def params_request():
    response = requests.get(build_uri('users'), params={'since': 11})
    print(better_print(response.text))
    print(response.request.headers)
    print(response.url)

# 使用json传参方式
def json_request():
    response = requests.get(build_uri('user'), auth=("username", "email"), json={"name": "asdas"})
    print(better_print(response.text))
```

异常处理

```python
def timeout_request():
    try:
        response = requests.get(build_uri('user/emails'), timeout=10)
        response.raise_for_status()
    except Exception as e:
        print(e)
    else:
        print(response.text)
        print(response.status_code)
```

自定义 request

```python
from requests import Request, Session

def hard_request():
    s = Session()
    # 创建请求
    headers = {'User-Agent': 'fake1.3.4'}
    req = Request('GET', build_uri('user/emails'), auth=('anshengme.com@gmail.com', 'xxxxxx'), headers=headers)
    prepped = req.prepare()
    print("请求头》》", prepped.headers)
    # 发送请求
    resp = s.send(prepped)
    print(resp.status_code)
    print(resp.request.headers)
    print(resp.text)
```

## 实例

下载图片/文件

```python
#!/use/bin/env python3
# _*_ coding:utf-8 _*_
import requests
from contextlib import closing


# 流传输的模式
def download_img():
    url = "http://www.sinaimg.cn/IT/cr/2016/0331/725124517.jpg"
    # headers = {
    #     'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36'}
    # response = requests.get(url, headers=headers, stream=True)
    response = requests.get(url, stream=True)
    print(response.status_code, response.reason)

    with open('github.jpg', 'wb') as fd:
        for chunk in response.iter_content(128):
            fd.write(chunk)

def download_img_improved():
    url = "http://www.sinaimg.cn/IT/cr/2016/0331/725124517.jpg"
    with closing(requests.get(url, stream=True)) as response:
        # 打开并写入文件
        with open('github1.jpg', 'wb') as fd:
            for chunk in response.iter_content(128):
                fd.write(chunk)

download_img()
download_img_improved()
```

处理响应的事件钩子

```python
#!/use/bin/env python3
# _*_ coding:utf-8 _*_
import requests

def get_key_info(response, *args, **kwargs):
    print(response.headers["Content-Type"])

def main():
    requests.get("https://www.baidu.com", hooks=dict(response=get_key_info))

if __name__ == "__main__":
    main()
```