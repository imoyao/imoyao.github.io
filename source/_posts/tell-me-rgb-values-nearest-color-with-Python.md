---
title: 中国传统色 | 如何判断一个颜色属于什么色系？
date: 2020-04-15 23:19:44
tags:
- 色系
- 颜色
- Python
- 装饰器
categories:
- Projects
- GUSCSS
cover: /images/colorful-pexel.jpg
subtitle: 谁能在彩虹里画下紫色结束、橙色开始的分界线呢？我们能清晰地看到颜色的不同，但是究竟在什么地方一种颜色逐渐地混入了另一种颜色呢？理智和疯狂的界限，亦是如此。<br> ——赫尔曼·梅维尔，《比利·巴德》
---

## 背景

在做 [项目](https://github.com/imoyao/GUSCSS/) 的时候，需要判断一个颜色值所在色系（如：红橙黄绿青蓝紫黑白灰），用眼睛观察太慢，算不上好办法，那么怎么判断呢？通过阅读 [该讨论](https://www.v2ex.com/amp/t/153186) 知道了一种方案：将 RGB 色值转化为 HSV，之后通过 Hue 去判断彩色的种类，用明度去判断黑白灰。具体实现如下。

## 基础知识

### RGB

RGB 是从颜色发光的原理来设计定的，通俗点说它的颜色混合方式就好像有红、绿、蓝三盏灯，当它们的光相互叠合的时候，色彩相混，而亮度却等于两者亮度之总和，越混合亮度越高，即加法混合。

红、绿、蓝三个颜色通道每种色各分为 256 阶亮度，在 0 时“灯”最弱——是关掉的，而在 255 时“灯”最亮。当三色灰度数值相同时，产生不同灰度值的灰色调，即三色灰度都为 0 时，是最暗的黑色调；三色灰度都为 255 时，是最亮的白色调。

在电脑中，RGB 的所谓“多少”就是指亮度，并使用整数来表示。通常情况下，RGB 各有 256 级亮度，用数字表示为从 0、1、2...直到 255。注意虽然数字最高是 255，但 0 也是数值之一，因此共 256 级。
![RGB](/images/RGB.png)

### HSV

HSV 是一种比较直观的颜色模型，所以在许多图像编辑工具中应用比较广泛，这个模型中颜色的参数分别是：色调（H, Hue），饱和度（S,Saturation），明度（V, Value）。
{% gallery %}
![HSV1](/images/HSV1.png)
![HSV2](/images/HSV2.png)
{% endgallery %}

#### 色调（Hue）

用角度度量，取值范围为 0°～360°，从红色开始按逆时针方向计算，红色为 0°，绿色为 120°,蓝色为 240°。它们的补色是：黄色为 60°，青色为 180°,品红为 300°；

#### 饱和度（Saturation）

饱和度 S 表示颜色接近光谱色的程度。一种颜色，可以看成是某种光谱色与白色混合的结果。其中光谱色所占的比例愈大，颜色接近光谱色的程度就愈高，颜色的饱和度也就愈高。饱和度高，颜色则深而艳。光谱色的白光成分为 0，饱和度达到最高。通常取值范围为 0%～100%，值越大，颜色越饱和。

#### 明度（Value）

明度表示颜色明亮的程度，对于光源色，明度值与发光体的光亮度有关；对于物体色，此值和物体的透射比或反射比有关。通常取值范围为 0%（黑）到 100%（白）。

#### 取值范围说明

我们需要注意的在不同应用场景中，HSV 取值范围是不尽相同的。

1.PS 软件时，H 取值范围是 0-360，S 取值范围是（0%-100%），V 取值范围是（0%-100%）。

2.利用 openCV 中 cvSplit 函数的在选择图像 IPL_DEPTH_32F 类型时，H 取值范围是 0-360，S 取值范围是 0-1（0%-100%），V 取值范围是 0-1（0%-100%）。

3.利用 openCV 中 cvSplit 函数的在选择图像 IPL_DEPTH_8UC 类型时，H 取值范围是 0-180，S 取值范围是 0-255，V 取值范围是 0-255。

那么，开始写代码吧！

## RGB 转 HSV

### 公式
- 常量
![constant](/images/constant_HSV.svg)
```mathml
$$
\begin{array}{l}
R^{\prime}=R / 255\\

G^{\prime}=G / 255\\

B^{\prime}=B / 255\\
\operatorname{Cmax}=\max \left(R^{\prime}, G^{\prime}, B^{\prime}\right)\\

C \min =\min \left(R^{\prime}, G^{\prime}, B^{\prime}\right)\\
\Delta=\mathrm{Cmax}-\mathrm{Cmin}
\end{array}
$$
```
- H 计算
![H](/images/HSV_Hue.svg)
```plain
$$
H=\left\{\begin{array}{cc}0^{\circ} & \Delta=0 \\ 60^{\circ} \times\left(\frac{G^{\prime}-B^{\prime}}{A} \bmod 6\right) & , C_{\max }=R^{\prime} \\ 60^{\circ} \times\left(\frac{B^{\prime}-R^{\prime}}{\Delta}+2\right) & , C_{\max }=G^{\prime} \\ 60^{\circ} \times\left(\frac{R^{\prime}-G^{\prime}}{\Delta}+4\right) & , C_{\max }=B^{\prime}\end{array}\right.
$$
```
- S 计算
![S](/images/HSV_S.svg)
```plain
$$
S=\left\{\begin{array}{cl}
0 & C \max =0 \\
\frac{\Delta}{C \max } & C \max \neq 0
\end{array}\right.
$$
```
- V 计算
![V](/images/HSV_V.svg)
```plain
$V=C \max$
```

### 代码（RGB 转 HSV）
```python
def hue_calculate_org(round1, round2, delta, add_num):
    return ((round1 - round2) / delta + add_num) * 60


def rgb_to_hsv_org(rgb_seq):
    r, g, b = rgb_seq
    r_round = float(r) / 255
    g_round = float(g) / 255
    b_round = float(b) / 255
    max_c = max(r_round, g_round, b_round)
    min_c = min(r_round, g_round, b_round)
    delta = max_c - min_c
    h = None
    if delta == 0:
        h = 0
    elif max_c == r_round:
        h = ((g_round - b_round) / delta % 6) * 60
    elif max_c == g_round:
        h = hue_calculate_org(b_round, r_round, delta, 2)
    elif max_c == b_round:
        h = hue_calculate_org(r_round, g_round, delta, 4)
    if max_c == 0:
        s = 0
    else:
        s = delta / max_c
    return h, s, max_c
```
另一种计算方式来自此处：👉 [Python Math: Convert RGB color to HSV color - w3resource](https://www.w3resource.com/python-exercises/math/python-math-exercise-77.php)
```python
def hue_calculate(round1, round2, delta, add_num):
    return (((round1 - round2) / delta) * 60 + add_num) % 360


def rgb_to_hsv(rgb_seq):
    r, g, b = rgb_seq
    r_round = float(r) / 255
    g_round = float(g) / 255
    b_round = float(b) / 255
    max_c = max(r_round, g_round, b_round)
    min_c = min(r_round, g_round, b_round)
    delta = max_c - min_c

    h = None
    if delta == 0:
        h = 0
    elif max_c == r_round:
        h = hue_calculate(g_round, b_round, delta, 360)
    elif max_c == g_round:
        h = hue_calculate(b_round, r_round, delta, 120)
    elif max_c == b_round:
        h = hue_calculate(r_round, g_round, delta, 240)
    if max_c == 0:
        s = 0
    else:
        s = (delta / max_c) * 100
    v = max_c * 100
    return h, s, v
```

## 颜色划分

### 分析

{%raw%}
<table class="dtable">
		<tbody><tr>
			<th>Color</th>
			<th>Color name</th>
			<th>(H,S,V)</th>
			<th>Hex</th>
			<th>(R,G,B)</th>
		</tr>
		<tr>
			<td style="background-color:#000000">&nbsp;</td>
			<td>Black</td>
			<td>(0°,0%,0%)</td>
			<td>#000000</td>
			<td>(0,0,0)</td>
		</tr>
        <tr>
			<td style="background-color:#808080">&nbsp;</td>
			<td>Gray</td>
			<td>(0°,0%,50%)</td>
			<td>#808080</td>
			<td>(128,128,128)</td>
		</tr>
		<tr>
			<td style="background-color:#FFFFFF">&nbsp;</td>
			<td>White</td>
			<td>(0°,0%,100%)</td>
			<td>#FFFFFF</td>
			<td>(255,255,255)</td>
		</tr>
		<tr>
			<td style="background-color:#FF0000">&nbsp;</td>
			<td>Red</td>
			<td>(0°,100%,100%)</td>
			<td>#FF0000</td>
			<td>(255,0,0)</td>
		</tr>
        <tr>
			<td style="background-color:#FFFF00">&nbsp;</td>
			<td>Yellow</td>
			<td>(60°,100%,100%)</td>
			<td>#FFFF00</td>
			<td>(255,255,0)</td>
		</tr>
		<tr>
			<td style="background-color:#00FF00">&nbsp;</td>
			<td>Lime</td>
			<td>(120°,100%,100%)</td>
			<td>#00FF00</td>
			<td>(0,255,0)</td>
		</tr>
		<tr>
			<td style="background-color:#00FFFF">&nbsp;</td>
			<td>Cyan</td>
			<td>(180°,100%,100%)</td>
			<td>#00FFFF</td>
			<td>(0,255,255)</td>
		</tr>
		<tr>
			<td style="background-color:#0000FF">&nbsp;</td>
			<td>Blue</td>
			<td>(240°,100%,100%)</td>
			<td>#0000FF</td>
			<td>(0,0,255)</td>
		</tr>
		<tr>
			<td style="background-color:#FF00FF">&nbsp;</td>
			<td>Magenta</td>
			<td>(300°,100%,100%)</td>
			<td>#FF00FF</td>
			<td>(255,0,255)</td>
		</tr>
	</tbody>
</table>
{%endraw%}

数据来源：[HSV to RGB conversion | color conversion](https://www.rapidtables.com/convert/color/hsv-to-rgb.html)
看~~色图~~，哦不，色环图。😳
![色环图](/images/color_circle.jpg)

先不管黑灰白三种色，找其他颜色与色环的对应关系，我们很容易发现 H 与色环的对应关系。
1. 变换色相 H，保持 S，V 不变，颜色发生变化；
{% gallery %}
![H30](/images/change_H_30.png)
![H60](/images/change_H_60.png)
![H180](/images/change_H_180.png)
![H210](/images/change_H_210.png)
![H270](/images/change_H_270.png)
![H330](/images/change_H_330.png)
![H360](/images/change_S_4.png)
{% endgallery %}
修改 H 会引起颜色变化；
2. 变换亮度 V，保持 H，S 不变，我们发现颜色在黑灰白之间变化；
{% gallery %}
![V100](/images/change_V_100.png)
![V50](/images/change_V_50.png)
![V0](/images/change_V_0.png)
{% endgallery %}
3. 变换饱和度 S，保持 H，V 不变，颜色不会变化，变的只是颜色的深浅程度；
{% gallery %}
![HSV1](/images/change_S_1.png)
![HSV1](/images/change_S_2.png)
![HSV1](/images/change_S_3.png)
![HSV1](/images/change_S_4.png)
{% endgallery %}
因为人眼对明亮的颜色更加敏感，所以我们适当调高亮度，之后逐渐修改 S，观察颜色变化。
有内味儿了，颜色变得越来越浓郁了！

### 代码

#### 颜色归类（按色系）

```python

def find_color_series(rgb_seq):  # TODO:此处是否有更好实现？
    """
    将rgb转为hsv之后根据h和v寻找色系
    :param rgb_seq:
    :return:
    """
    h, s, v = rgb_to_hsv(rgb_seq)
    cs = None
    if 30 < h <= 90:
        cs = 'yellow'
    elif 90 < h <= 150:
        cs = 'green'
    elif 150 < h <= 210:
        cs = 'cyan'
    elif 210 < h <= 270:
        cs = 'blue'
    elif 270 < h <= 330:
        cs = 'purple'
    elif h > 330 or h <= 30:
        cs = 'red'

    if s < 10:  # 色相太淡时，显示什么颜色主要由亮度来决定
        cs = update_by_value(v)
    assert cs in COLOR_SERIES_MAP
    return cs
    
def update_by_value(v):
    """
    根据 V 值去更新色系数据
    :param v: 
    :return: 
    """
    if v <= 100 / 3 * 1:
        cs = 'black'
    elif v <= 100 / 3 * 2:
        cs = 'gray'
    else:
        cs = 'white'
    return cs
```
#### 代码验证

```python

if __name__ == '__main__':

    color_list = [[22, 24, 35], [36, 134, 185], [234, 137, 88], [32, 161, 98], [100, 106, 88]]

    for item in color_list:
        print(find_color_series(item))

```
返回结果：
```plain
blue
cyan
red
cyan
yellow
```

至此，我们完成了数据颜色粗略的归类。
到这里就结束了吗？显然没有。实际上，这种数据返回结果是很粗糙的，我们需要对 Hue 进行反复修正才能得出一个较为满意的结果。正如物理实验一样：理论和实践可能存在较大偏差甚至可能得出完全相反的结论，此处我们不再展开。😂我们进一步分析数据，发现：

> 甚三**紅**、**黄**朽葉、千歳**緑**、錆**青**磁、江戸**紫**、**白**練……

你细品~是的，部分颜色名称里面已经包含了颜色的色系关键字。我们假定名称的命名是靠谱的。那么，我们可以利用正则把色系关键字提取出来，然后只对没有指明的颜色进行计算。

可是上面的代码已经写完了，我不想再大动干戈修改此函数，怎么办？此处，我们使用装饰器。

#### 颜色归类（按名称）

```python
import re
from functools import wraps, partial


def attach_wrapper(obj, func=None):
    if func is None:
        return partial(attach_wrapper, obj)
    setattr(obj, func.__name__, func)
    return func


def find_color_series_by_name(name=''):
    """
    装饰器：通过颜色的中文名称利用正则匹配获取颜色名称
    我们假定命名是符合人类主观意识的，即：名称比我们的代码更可靠
    因为按照hsv去匹配的时候会有误差，所以我们先通过名称去直接匹配色系，如果名称中没有关键字，我们再使用自己写的规则
    :param name:str,
    :return:
    """

    def deco(func):
        color_name_char = name

        @wraps(func)
        def wrapper(*args, **kwargs):
            color_series = ''
            if color_name_char:
                re_ret = re.match(REG_COLOR_SERES, color_name_char)
                if re_ret:
                    color_signal = re_ret.group(1)
                    color_series = COLOR_SERIES_MAP_REVERSE.get(color_signal)

            if color_series == '':
                color_series = func(*args, **kwargs)
            return color_series

        @attach_wrapper(wrapper)
        def set_color_name(new_name):
            nonlocal color_name_char
            color_name_char = new_name

        return wrapper
    return deco
```
关于此处装饰器的写法，参见《Python Cookbook 中文版》V3 P342 第 9.5 章节：*定义一个属性可由用户修改的装饰器*。

最后，我们给之前写的函数戴上这顶叫做装饰器的“帽子”。
![装饰器](/images/your_hat.jpg)

##### 装饰器使用

```python
@find_color_series_by_name(name='')
def find_color_series(rgb_seq):
    pass    # 省略重复代码
    
if __name__ == '__main__':
    
    test_color_map = {'东方红': [254, 223, 225], '红东方': [215, 196, 187], '方红东': [86, 46, 55], '黄丹': [240, 94, 28],
                      '万红丛中一点绿': [63, 43, 54]}
    for k, v in test_color_map.items():
        find_color_series.set_color_name(k)
        find_color = find_color_series(v)
        print(find_color)

```
返回结果
```plain
red
red
red
yellow
green
```
## 总结展望
经过上面的步骤我们完成了颜色的分类，但是这种分类是粗粒度的，结果也可能是不够准确的。如果需要更精准的计算，可能需要建模及算法甚至训练模型去实现，这里不再展开（~~主要是我不会~~）。

如果颜色本身命名错误，如上例中的“万红丛中一点绿”，我们直接走装饰器判断逻辑，就会使计算过滤的逻辑失效。所以我们可以数据分别走两套逻辑，对于两者返回一致的，我们认为这个数据是可信的；对于不一致的部分，我们则需要使用人工智能的“人工”部分对数据进行二次编辑，之后将结果更新上去。

## 西风吟
1. 我们知道 Python 是一门自带电池的语言，关于颜色 rgb 转 hsv，其实 [官方模块](https://docs.python.org/zh-cn/3.7/library/colorsys.html) `colorsys` 中已经有自己的实现，我们需要的只是对数据做相应比例的放大。当然我们也可以在后续逻辑中直接用官方返回的数据划分区域。
```plain
>>> import colorsys
>>> colorsys.rgb_to_hsv(0.2, 0.4, 0.4)
(0.5, 0.5, 0.4)
>>> colorsys.hsv_to_rgb(0.5, 0.5, 0.4)
(0.2, 0.4, 0.4)
```
2. 关于颜色的判断，我们知道色的三原色为 RGB（红绿蓝），而实际颜色是按照不同比例混合的，所以颜色是没有办法真的做明显界线区分的。
> 谁能在彩虹里画下紫色结束、橙色开始的分界线呢？我们能清晰地看到颜色的不同，但是究竟在什么地方一种颜色逐渐地混入了另一种颜色呢？理智和疯狂的界限，亦是如此。
3. 日常黑男性环节：
![男生眼中的颜色 vs 女生眼中的颜色](/images/colors-for-male-and-female.jpg)

## 链接

### 源码下载
🍭 [my_practices/codes/tell_color_by_rgb at master · imoyao/my_practices](https://github.com/imoyao/my_practices/tree/master/codes/tell_color_by_rgb)

### 参考链接
- [从 RGB 到 HSV 的转换详细介绍_人工智能_hanshanbuleng 的博客-CSDN 博客](https://blog.csdn.net/hanshanbuleng/article/details/80383813)
- [知道一个颜色的 RGB 如何归类到特定颜色（如赤橙黄绿青蓝紫黑白灰）？ - V2EX](https://www.v2ex.com/amp/t/153186)
- [How can I tell basic color a hex code is closest to? - Graphic Design Stack Exchange](https://graphicdesign.stackexchange.com/questions/92984/how-can-i-tell-basic-color-a-hex-code-is-closest-to)
- [algorithm - "Rounding" colour values to the nearest of a small set of colours - Stack Overflow](https://stackoverflow.com/questions/4057475/rounding-colour-values-to-the-nearest-of-a-small-set-of-colours/4356523#4356523)

### 推荐阅读
- [青色是什么样子的？| 果壳 科技有意思](https://www.guokr.com/article/437666/)

### 其他
- [颜色列表 - 维基中文镜像，自由的百科全书](http://www.bosimedia.com/wiki/%E9%A2%9C%E8%89%B2%E5%88%97%E8%A1%A8)
- [latex 在线公式编辑器汉化版](http://www.jq22.com/yanshi16883)
- [HSV to RGB conversion | color conversion](https://www.rapidtables.com/convert/color/hsv-to-rgb.html)
