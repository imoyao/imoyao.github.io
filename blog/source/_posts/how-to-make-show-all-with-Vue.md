---
title: 如何在 Vue 中实现显示全部的功能？
date: 2019-07-05 22:30:13
tags:
- Vue
- element-ui
- 前端

---
## 功能分析

我们可以简单分析一下功能实现：

1. 显示内容是从后台一次性获取到的，不存在点击“阅读更多”再去请求一次后台获取剩余数据的可能；
2. 通过第一步其实可以得出，网站是通过控制显示元素的高度来实现这一功能，而非控制内容的获取；
3. 可以看到“阅读更多”按钮上有一层渐变遮罩层，网站通过这一遮罩挡住剩余内容。

## 完整代码

```vue
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta http-equiv="X-UA-Compatible" content="ie=edge">
  <title>Document</title>
</head>
<body>
  <div id="app">
    <div v-for="(item, key) in testItems" v-show="key<limitShowNum">
      {{item}}
    </div>
    <el-button @click="showMore" type="text" style="color:#79bbff;">{{showAllTip}}</el-button>
  </div>
<link rel="stylesheet" href="https://unpkg.com/element-ui/lib/theme-chalk/index.css">
<!-- 引入组件库 -->
<script src="https://unpkg.com/element-ui/lib/index.js"></script>
  <script src="https://unpkg.com/vue"></script>
  <script>
    var app = new Vue({
      el: '#app',
      data(){
        return{
          testItems: ['海客谈瀛洲，烟涛微茫信难求；', '越人语天姥，云霞明灭或可睹。', '天姥连天向天横，势拔五岳掩赤城。', '天台四万八千丈，对此欲倒东南倾。', '我欲因之梦吴越，一夜飞度镜湖月。', '湖月照我影，送我至剡溪。', '谢公宿处今尚在，渌水荡漾清猿啼。', '脚著谢公屐，身登青云梯。', '半壁见海日，空中闻天鸡。', '千岩万转路不定，迷花倚石忽已暝。', '熊咆龙吟殷岩泉，栗深林兮惊层巅。', '云青青兮欲雨，水澹澹兮生烟。', '列缺霹雳，丘峦崩摧。', '洞天石扉，訇然中开。', '青冥浩荡不见底，日月照耀金银台。', '霓为衣兮风为马，云之君兮纷纷而来下。', '虎鼓瑟兮鸾回车，仙之人兮列如麻。', '忽魂悸以魄动，恍惊起而长嗟。', '惟觉时之枕席，失向来之烟霞。', '世间行乐亦如此，古来万事东流水。', '别君去兮何时还？且放白鹿青崖间。须行即骑访名山。', '安能摧眉折腰事权贵，使我不得开心颜！'],
          isShow: true,
		  showAllTip: '我全都要 😜',
		  limitShowNum: 5,
	      defaultShowNum:5
        }
      },
      methods: {
        // 功能实现
        showMore(){
			let showDataLen = this.testItems.length
			this.isShow = !this.isShow;
			this.limitShowNum = this.isShow? this.defaultShowNum: showDataLen;
			this.showAllTip = this.isShow?'我全都要 😜':'收起'
		}
      }
    })
  </script>
</body>
</html>
```
## 功能演示
此处显示与直接代码运行效果不一样，主要是因为样式以及添加i标签图标等导致；样式不会写的话可以参考`element-ui`官方文档的实现。

![显示全部与折叠](/images/show_all_example.gif)

## 参考链接

[利用vue实现“显示更多”功能](https://blog.csdn.net/XuM222222/article/details/80189355)