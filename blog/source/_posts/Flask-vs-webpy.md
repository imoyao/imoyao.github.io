---
title: Python 之 Web 开发框架对比——Flask vs Web.py
date: 2019-06-05 18:03:49
tags:
- Flask
- Web.py
- Web 开发

categories:
- 工作日常
toc: true
---
`Python` 常用的`web`开发框架有很多如`Django`、`Flask`、`Tornado`、`Web.py`等，我们之前项目中使用的是 `Web.py`，但是新项目中选择哪个？或许是个值得思考的问题。本文主要对`Web.py`和`Flask`进行一个简单的对比。

<!--more-->

## 为什么要从`Web.py`迁移到`Flask`

大势所趋。根据最新的[Python 开发者调研-2018](https://www.jetbrains.com/research/python-developers-survey-2018/)结果显示，`Flask`和`Django`已经成为最流行的`web`开发框架。对企业的良性发展和开发者个人成长而言，使用热门技术都是值得鼓励且必要的。而且，众所周知，官方计划在`2020`年停止`Python2`支持，而相比`Flask`而言，`Web.py`的版本更新计划有点跟不上节奏的感觉。

![Web-frameworks-python-developers-survey-2018](/images/Web-frameworks-python-developers-survey-2018.jpg)
<figcaption>Web-frameworks-python-developers-survey-2018</figcaption>

## TL;DR，`Flask` 对比 `Web.py` 的不同点

`Flask`拥有活跃的社区文化和丰富而强大的第三方扩展，而`Web.py`在原作者（Aaron Swartz）自杀之后自身维护已举步维艰，第三方扩展的发展更是不言而喻。

- **维护积极性**  - 最新版本分别为`Flask-1.0.2`和 `webpy-0.39`。

{% gallery %}
![flask-contributors](/images/flask-contributors.jpg)
![webpy-contributors](/images/webpy-contributors.jpg)
{% endgallery %}

- **官方文档** - `Flask`具有良好的官方文档，并且有国内使用者翻译的中文文档；`Web.py`只有勉强够用、捉襟见肘的入门级官方文档，剩下的需要开发人员自行摸索。
- **社区活跃度** - `Flask`拥有活跃的社区文化和数量庞大的拥趸者，`Web.py`国内只有不活跃的专门的豆瓣小组或者在一些热门`Python`社区偶有提及。
- 第三方扩展  
    - 表单 - `Flask` 使用扩展`Flask-WTF`和`WTForms`可以实现很好的表单验证和 `csrf` 安全保护；（参阅[Flask-WTF 与 WTForms 的用法详解](https://www.jianshu.com/p/7e16877757f8)）；而`Web.py`自带[Form 库](http://webpy.org/form)，可以实现表单及简单校验。
    - 数据库 -  `Flask` 使用扩展`Flask-SQLAlchemy`实现对数据库的`ORM`操作，可以很好地管理和实现数据库的迁移(借助`Flask-Migrate`)工作；`Web.py`我们使用自己封装的`database.py`。
    - 身份验证和权限 - `Flask`提供安全`cookie`作为您自己实现的工具，第三方扩展如`Flask-Login`(用户会话管理)，`Flask-HTTPAuth`<sup>①</sup>（简化了使用`Flask`路由的`HTTP`身份验证的使用），`Flask-Security`（提供一站式管理）， `Flask-Social`（用于添加“社交”或`OAuth`登录和连接管理）等，这些扩展良莠不齐，使用时需要对其有个初步了解并进行遴选；`Web.py`还是要自己造轮子。
    - `RESTful` - 使用`Flask-RESTful` 可以创建`REST`的`API`。
    - 强大的页面渲染 -`Flask`使用`jinja2`作为模板引擎；`Web.py`使用`Templetor`类 `python` 写起来信手拈来，无痛衔接，也可以使用`Mako`模板引擎，两者平分秋色。性能对比见这里👉 [几个模板系统的性能对比](http://www.pythontip.com/blog/post/2239/)
- 伸缩性 - `Flask`既可以像`Web.py`那样做微框架开发一个很小的`web`应用，也可以借助上方的各种扩展做到`Django`级别的应用。
    
## Flask 框架

> Flask is a microframework for Python based on Werkzeug, Jinja 2 and good intentions. 
Flask 是一个基于 `Jinja2` 模板引擎和 `Werkzeug WSGI` 套件的一个微型的`Web`开发框架。体现了`logo`中的口号`web development, one drop at a time.`(`web`开发，一次一滴。)

### 什么是 “微”

> “微” (“Micro”) 并不是意味着把整个 `Web` 应用放入到一个 `Python` 文件，尽管确实可以这么做。当然“微” (“Micro”) 也不是意味 `Flask` 的功能上是不足的。微框架中的 “微” (“Micro”) 是指 `Flask` 旨在保持代码简洁且易于扩展。`Flask` 不会替你做出太多决策——比如使用何种数据库。而那些 `Flask` 所选择的——比如使用何种模板引擎——则很容易替换。除此之外的一切都可由你掌握。如此，`Flask` 可以与您珠联璧合。  
默认情况下，`Flask` 并不包含数据库抽象层，表单验证或者任何其他现有的库( `Django` )能够处理的。相反，`Flask` 支持扩展，这些扩展能够添加功能到你的应用，像是 `Flask` 本身实现的一样。众多的扩展提供了数据库集成，表单验证，上传处理，多种开放的认证技术等功能。`Flask` 可能是“微”型的，但它可以游刃有余地应付需求繁杂的生产环境的使用。

① 在 `Web` 应用中，我们经常需要保护我们的 `api`，以避免非法访问。比如，只允许登录成功的用户发表评论等。`Flask-HTTPAuth` 扩展可以很好地对 `HTTP` 的请求进行认证，不依赖于 `Cookie` 和 `Session`。而是基于密码和基于令牌 (`token`)。
## `Web.py` 框架
> Web.py is a web framework for Python that is as simple as it is powerful. 
Web.py 是一个简单且功能强大的用于 Python 语言的 web 框架。

### `Web.py`设计哲学

`Web.py`的口号是`Think about the ideal way to write a web app. Write the code to make it happen.`（思考编写`web`应用程序的理想方式，然后去编写代码实现它。）  
在用`Python`编写`web`应用程序的时候，我想象自己想要`API`的方式。它始于导入`web`，然后有一个定义`URL`的地方，处理`GET`和`POST`的简单函数和一些处理输入变量的东西。一旦代码对我来说看起来是正确的， 我就会想尽办法使它在不更改应用程序代码的情况下执行——结果就是 `Web.py`。
有人抱怨说我“搞了另一套模板语言”（yet another template language），我写了更多文字关于我的设计理念：[参阅](http://groups.google.com/group/webpy/msg/f266701d97e7ceb1)

你不必使用它——`Web.py`的每个部分都与其他部分完全分离。但你是对的， 它是“另一种模板语言”，而我不会为此道歉。  
`Web.py` 的目标是构建制作 `web` 应用程序的理想方法。如果为了实现这个目标需要有微小差异化的来重塑陈旧的东西， 我会捍卫自己对它们进行改造的权利。`理想的方式`和`几乎理想的方式`之间的区别， 正如马克·吐温所言：是闪电和萤火虫之间的区别。（The difference between the right word and the almost right word is the difference between lightning and the lightning Bug.）  
但这些不仅仅是细微的差异。`Web.py` 允许您构建 `http` 响应， 而不暴露 `Python` 对象。`Web.py` 使数据库更易使用，而不试图使数据库看起来像一个对象。 `Web.py` 模板系统试图把 `Python` 纳入 `HTML`而不是想出另一种方法来编写 `HTML`。没多少人真正尝试过这么做的可能性。  
你可以不同意这些方法更好并给出原因，但仅仅批评它们与众不同是浪费时间。是的， 它们天生骄傲。我的话讲完了。  
文字来源：[The Web.py Philosophy](http://webpy.org/philosophy)

## Show me the code

### Web.py

```python
import web

urls = (
    '/', 'Index'
)

class Index:
    def GET(self):
        return "Hello, world!"
    
    # def POST(self):
    #     pass    # TODO

if __name__ == "__main__":
    web.config.debug = False
    app = web.application(urls, globals())
    app.run()
```
1. 导入`web`模块；
2. 组装`url`结构；
    - 第一部分为匹配`URL`的正则表达式，第二部分是接受请求的类名称
3. 定义类
    - 定义处理`GET`请求的方法；
    - 定义（可选的）处理`POST`请求的方法；
4. `debug`模式
    当应用在内建的服务器中运行时，它会以`debug`模式启动程序。在`debug`模式下，任何代码、模板的修改，都会让服务器重新加载它们，然后还会输出有用的错误消息。  
    只有在生产环境中`debug`模式是关闭的，如果你想禁用`debug`模式，你可以在创建程序/模板前添加置为`False`。
5. 创建应用，这个`application`会在这个文件的全局命名空间中查找`urls`中定义的对应类。
6. 启动应用。

### Flask

```python
# app.py
from flask import Flask,request
app = Flask(__name__)

@app.route('/',methods=['GET', 'POST'])
def hello_world():
    return 'Hello World!'

if __name__ == '__main__':
    '''
    打开调试模式的另一种设置方式
    app.debug = True
    app.run()
    '''
    app.run(host='0.0.0.0',debug=True)
```
运行之后，浏览`http://IP_ADDR:5000/`即可访问。
```bash
$ python app.py
 * Running on http://0.0.0.0:5000/
```
代码解释
1. 导入`Flask`类；
2. 实例化，即生成我们的 `WSGI` 应用，第一个参数是应用模块的名称。 如果你使用的是单一的模块（就如本例），第一个参数应该使用 `__name__`。我们还可以传递给它模块或包的名称。这样 `Flask` 才会知道去哪里寻找模板、静态文件等等。
3. 使用装饰器 `route()` 告诉 `Flask` 哪个 `URL` 才能触发我们的函数。
    - 默认情况下，路由只会响应 `GET` 请求， 但是能够通过给 `route()` 装饰器提供 `methods` 参数改变。
4. 定义函数，该函数名也是用来给特定函数生成 `URLs`，并且返回我们想要显示在用户浏览器上的信息。
5. 最后我们用函数 `run()` 启动本地服务器来运行我们的应用。
    - `host='0.0.0.0'`你可以让你的服务器对外可见。
    - `debug=True`开启调式模式，仅适用于开发阶段，在代码修改的时候服务器能够自动加载，发生错误之后可以更好追踪调试； **生产模式时，一定要关闭该选项。**

**注意**   
可能有人想要使用`Flask`实现`Web.py`类似的`RESTful`的代码设计风格，借助`Flask-RESTful`可以实现像`Web.py`一样的`RESTful`设计。示例如下：  
```python
from flask import Flask
from flask_restful import Resource, Api

app = Flask(__name__)
api = Api(app)

class HelloWorld(Resource):

    def get(self):
        return {'hello': 'world'}

api.add_resource(HelloWorld, '/')

if __name__ == '__main__':
    app.run(debug=True)
```
## 关于 Flask 的蓝本/蓝图（Blueprint）
在`Flask`中可以用`Blueprint` (蓝图) 实现应用的**模块化**，应用层次清晰，蓝图可以极大地**简化大型应用**并为扩展提供集中的注册入口。
蓝图通常作用于相同的`URL`前缀，如`/user/:id`、`/user/profile`这样的地址，都以`/user`开头，它们是一组用户相关的操作，那么就可以放在一个模块中。
在大型项目中，一般都是协同开发各共同进行的，使用蓝图可以避免互相干扰，开发人员一看路由就能很快的找到对应的视图，可以更容易地**开发和维护**项目。

一个典型的使用蓝图组织应用的项目结构：  
```bash
app/
    __init__.py
    admin/
        __init__.py
        views.py
        static/
        templates/
    home/
        __init__.py
        views.py
        static/
        templates/
    control_panel/
        __init__.py
        views.py
        static/
        templates/
    models.py
    runserver.py
```
参阅：[如何理解 Flask 中的蓝本？](https://www.zhihu.com/question/31748237)

## 总结
需求驱动，没有最好的框架，只有适合你的框架。  
两者都是轻量级`web`开发框架（相较于`Django`而言），都具有良好的扩展性并遵循`Pythonic`设计，非常适合初学者学习与使用。    
`Web.py`坚持小而美的设计理念。简单直接，学习成本更低，对于新手理解 web 处理流程很有帮助，更适合敏捷开发和定制化，当然也就意味着可能需要自己造更多的轮子。
而`Flask`拥有庞杂的第三方扩展可以参考使用，具备良好的扩展性，遇到问题更好向社区寻求答案。当然，随着开发的深入，可能伴随一系列扩展的了解和学习，会消耗较多时间。但是相比`Django`这种`完美主义者用来赶期限的选择`，你不必一开始就学所有的东西（session、ORM、CSRF、Form、Template、Middleware 等），可以自主搭配，渐进开发。
所以，对于全新项目，为了后续的可持续迭代和维护，相比`Web.py`更建议选择`Flask`。

## 参考阅读

### 框架对比  
- [Flask vs Django](https://kite.com/blog/python/flask-vs-django-python)
- [Web.py,web2py,django 三者间到底是什么关系？有什么不同呢？- 豆瓣](https://www.douban.com/group/topic/29598761/)
- [Flask 框架怎么样，比起 Web.py 有哪些不同？- 知乎](https://www.zhihu.com/question/20708601)
- [Web.py-and-flask- StackOverflow](https://stackoverflow.com/questions/5695689/web-py-and-flask)
- [Which is better: Flask vs Web.py? Why?-Quora](https://www.quora.com/Which-is-better-Flask-vs-web-py-Why)
- [Can anyone explain the differences between web2py, Django, Flask, etc, and when I should use one or the other and what the benefits and drawbacks of each?-Reddit](https://www.reddit.com/r/Python/comments/28qr7c/can_anyone_explain_the_differences_between_web2py/)
    
### `Flask`学习资源
- [Welcome | Flask (A Python Microframework)](http://flask.pocoo.org/)
- [Flask 中文文档](http://docs.jinkan.org/docs/flask/index.html)
- [Flask Web 开发入门](https://www.ctolib.com/docs/sfile/head-first-flask/)
- [欢迎进入 Flask 大型项目教程](http://www.pythondoc.com/flask-mega-tutorial/index.html)
- [Flask Web 开发：基于 Python 的 Web 应用开发实战 -（狗书）](https://book.douban.com/subject/26274202/)
- [Flask Web 开发实战 -（狼书）](https://book.douban.com/subject/30310340/)

### `Flask`扩展
- [Awesome Flask(Flask 资源和插件的精选列表)](https://github.com/humiaozuzu/awesome-flask)
- [Flask 文档和主流第三方扩展文档](http://www.pythondoc.com/)

### 其他
- [亚伦·斯沃茨 (Aaron Swartz) 是怎么样一个人？](https://www.zhihu.com/question/20711220)
