---
title: 中国传统色 | 朱砂痣还是白月光，哪个才是我们的心头好？
date: 2020-04-13 21:15:00
tags:
- Python
cover: /images/place.jpg
top_img: /images/zhusha-or-yuebai.png
subtitle: 梅子金黄杏子肥，麦花雪白菜花稀。<br>——范成大 ·《四时田园杂兴·其二》
reward: true
categories:
- Projects
- GUSCSS
---

## 引言
张爱玲在《红玫瑰与白玫瑰》中这样写道：
> 也许每一个男子全都有过这样的两个女人，至少两个。娶了红玫瑰，久而久之，红的变了墙上的一抹蚊子血，白的还是"床前明月光”；娶了白玫瑰，白的便是衣服上沾的一粒饭黏子，红的却是心口上一颗朱砂痣。

那么白月光和朱砂痣到底有什么不同呢？嘿嘿，其实这是一篇讲自己开源项目的文章，被标题骗进来的非战斗人员可以选择自行离场啦。😳

## 背景

用于展示中国传统色的网站很多，为什么我还要叠床架屋地去自己造轮子呢？为了练手，顺便打发自己闲得挠墙的无聊时光。众所周知，人类的本质是复读机。🤬

## 技术栈

### 后端
1. [x] 使用 Python 收集、整理、去重数据；
2. [ ] 爬虫，使用 request 模块等；

### 前端
 使用 Vue 编写页面，展示数据；

## 具体解决方案介绍

### 数据获取
1. 对于网站给出源码的（目前已完成）
    直接去源码中拿数据，之后对格式拼装、组合；
2. 没有源码的（后期开发计划）
    1. 上爬虫，给👴爬！
    2. 利用 OCR 技术识别文字和 PIL 获取颜色对应的 RGB 值数据；
        - [Kite - AI Autocomplete for Python](https://kite.com/python/answers/how-get-the-rgb-values-of-an-image-using-pil-in-python)

### 数据处理

#### 颜色名称

使用 pypinyin 获取名称拼音，使用 zhtools 保存颜色简体和繁体两种名称；

#### 文字显示
- [判断颜色为深颜色还是浅颜色来动态调整 app 文字和图标颜色_移动开发_YD-10-NG 的博客-CSDN 博客](https://blog.csdn.net/sinat_38184748/article/details/93002587)
颜色描述使用默认描述，当默认描述为空时，调用[今日诗词 API](https://www.jinrishici.com/)，如果调用失败，则显示默认诗句。

#### 色系判断
将颜色的 RGB 色值转化为 HSV，之后通过 hue 去判断彩色的色值，用明度去判断黑白灰。
参见 [如何判断一个颜色属于什么色系？](/blog/2020-04-15/tell-me-rgb-values-nearest-color-with-Python/)

## 更新字典
[python - Merge two list of dicts with same key - Code Review Stack Exchange](https://codereview.stackexchange.com/questions/209202/merge-two-list-of-dicts-with-same-key)
将数据按照色系分组
[Python | Merging two list of dictionaries - GeeksforGeeks](https://www.geeksforgeeks.org/python-merging-two-list-of-dictionaries/)

## 添加“亿点点”细节
使用 Vue 将页面展示出来，此处参考了开源项目 [ssshooter/nippon-color](https://github.com/ssshooter/nippon-color)。写后端的你硬让我写前端，我看你是在为难我胖虎。
![如何画马](/images/draw_horse.jpeg)


## 效果展示

![朱砂](/images/zhusha.png)
<figcaption>朱砂 on 电脑</figcaption>

![青葱](/images/iPad-with-case-on-wood-table.png)
<figcaption>青葱 on 平板</figcaption>

![月白](/images/yuebai.png)
<figcaption>月白 on 手机</figcaption>

## 部署
Github 支持部署 docs 目录为项目文档，我们直接修改`vue.config.js`设置`outputDir: 'docs'`，把其导出到 docs 目录，
参见[Simpler GitHub Pages publishing - The GitHub Blog](https://github.blog/2016-08-17-simpler-github-pages-publishing/)

## 展望
还有很多点可以完善：
1. 多音字词组的正确发音。如[卡其绿](https://colors.masantu.com/#/?colorId=100115112)
2. 更加权威的数据来源。

## Help Wanted

### 我是开发者
你可以 fork 此仓库之后修改[amend 文件](https://github.com/imoyao/GUSCSS/blob/dev/_data/amend.json) 中的 data 字段，修改是以 id 为参考基准，只需要提交修改新值，不修改值直接不写（我们会使用 Python 字典的 update 方法 patch 更新数据），之后提交 pr 即可。当然，也欢迎提交代码逻辑及实现中不合理的地方及 bug 修复。更多参考 [此处](https://github.com/imoyao/GUSCSS/projects/1)
参考数据样式：
```json
{
  "id": "1847572",
  "name": "朱砂",
  "tra_name": "硃砂",
  "color_series": "red",
  "pinyin": "zhū shā",
  "font_color": "dark",
  "is_bright": true,
  "rgb": [
    184,
    75,
    72
  ],
  "hex": "#FF461F",
  "cmyk": [
    0,
    59,
    61,
    28
  ],
  "desc": "",
  "figure": ""
}
```

### 我是普通用户
如果你不会写代码，但是发现页面中有严重错误。如果你有 Github 账号，可以去 [issue 页面](https://github.com/imoyao/GUSCSS/issues) 提交反馈；如果你没有账号或者不会使用 Github，可以通过留言方式或者直接发邮件 [给我](mailto:immoyao@gmail.com) 进行反馈，邮箱地址：immoyao@gmail.com。

### 我除了钱啥都没
请使用微信（WeChat）扫描下方二维码与我一起做**公益**吧！  
![腾讯公益](https://www.masantu.com/img/PublicWelfare-for-Children.jpg)
当然，还可以去我的博客找赞赏码给我打钱。（慢慢找去吧）😊

## 数据来源
- [Traditional Chinese Colors | 中国传统颜色](http://boxingp.github.io/traditional-chinese-colors/)
    源码：[BoxingP/traditional-chinese-colors](https://github.com/BoxingP/traditional-chinese-colors)
- [colors-source.yml](https://colors.flinhong.com/)| [中国の伝統色 320 色](https://htmlcss.jp/color/china.html)
    源码：[flinhong/colors: 青山绿水，白草红叶黄花。颜色都该有它好听的名字！](https://github.com/flinhong/colors/)
- [nipponcolor](https://ssshooter.github.io/nippon-color/#/) 
    源码 [ssshooter/nippon-color: nippon-color PWA build with vue-cli 3](https://github.com/ssshooter/nippon-color)
- [中国传统颜色手册 | Chinese Color Cheatsheet](https://colors.ichuantong.cn/)
    源码：[zerosoul/chinese-colors: 🇨🇳🎨Chinese traditional color cheatsheet online](https://github.com/zerosoul/chinese-colors)
- [乾隆色谱——从历史档案复原清代色彩](https://www.douban.com/doulist/34917690/)

## 链接
- [GUSCSS | 给你点颜色瞧瞧](https://colors.masantu.com/#/)
- [源码 · imoyao/GUSCSS](https://github.com/imoyao/GUSCSS)

{% blockquote 张爱玲,《红玫瑰与白玫瑰》%}
娇蕊放下茶杯，立起身，从碗橱里取出一罐子花生酱来，笑道：“我是个粗人，喜欢吃粗东西。”振保笑道：“哎呀！这东西最富于滋养料，最使人发胖的！”娇蕊开了盖子道：“我顶喜欢犯法。你不赞成犯法么？”振保把手按住玻璃罐，道：“不。”娇蕊踌躇半日，笑道：“这样罢，你给我面包上塌一点。你不会给我太多的。”振保见她做出那楚楚可怜的样子，不禁笑了起来，果真为她的面包上敷了花生酱。娇蕊从茶杯口上凝视着他，抿着嘴一笑道：“你知道我为什么支使你？要是我自己，也许一下子意志坚强起来，塌得极薄极薄。可是你，我知道你不好意思给我塌得太少的！”两人同声大笑。
{% endblockquote %}