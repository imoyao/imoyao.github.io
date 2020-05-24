---
title: Python 全栈之路系列之流程控制
toc: true
date: 2020-05-23 18:21:46
tags:
- 编码
top: 8
---

## if

if 就是一个条件判断的，当满足不同样的条件的时候执行不同的操作，用法如下：

```python
if <条件一>:
    <条件一代码块>
elif <条件二>:
    <条件二代码块>
else:
    <上面两个或者多个条件都不满足则只需这里的代码块>
```

来一个小栗子：

```python
#!/use/bin/env python
# _*_ coding:utf-8 _*_
# 只需脚本是让用户输入一个数字，并把值赋值给变量n
n = int(input("Pless Numbers: "))
# 如果n大于10
if n > 10:
    # 输出n > 10
    print("n > 10")
# 如果n等于10
elif n == 10:
    # 输出n == 10
    print("n == 10")
# 否则
else:
    # 输出n < 10
    print("n < 10")
```

## 三元运算

如果条件成立，那么就把值 1 赋值给 var，如果条件不成立，就把值 2 赋值给 var

```python
var = 值1 if 条件 else 值2
```

例子
```python
>>> var = "True" if 1==1 else "False"
>>> var
'True'
```

## for 循环

for 语句是 python 中的循环控制语句，可用来遍历某一对象，还具有一个附带的可选的 else 块，主要用于处理 for 语句中包含的 break 语句。

```python
>>> li = ['ansheng','eirc']
>>> for n in  range(len(li)):
...  print(li[n])
...
ansheng
eirc  
```

## enumrate

`enumerate`函数用于遍历序列中的元素以及它们的下标

例如定义一个列表，内容有电脑，笔记本，手机，组装机，执行脚本的时候让用户选择商品，并且给商品加上序列：

```python
>>> li = ["电脑","笔记本","手机","组装机"]
>>> for key,value in enumerate(li):
...  print(key,value)
...
0 电脑
1 笔记本
2 手机
3 组装机
```

为了给用户良好的体验，需要从 1 开始，然后用户如果输入相对应的序列那么就打印出序列对应的值：

```python
#!/usr/bin/env python
# _*_ coding:utf-8 _*_
# 定义一个列表
li = ["电脑","笔记本","手机","组装机"]
# enumerate默认从0开始自增，我们可以改为从1开始自增
for key,value in enumerate(li,1): 
    print(key,value)
# 让用户选择商品的序列
li_num = input("请选择商品:")
# print输出的时候让序列减1
print(li[int(li_num)-1])  
```
执行结果如下

```python
1 电脑
2 笔记本
3 手机
4 组装机
请选择商品:1
电脑
```

## range 和 xrange

range()函数返回在特定区间的数字序列，range()函数的用法类似切片：range(start,stop,setup)，start 的默认值为 0，即从 0 开始，stop 的参数是必须输入的，输出的最后一个数值是 stop 的前一个，step 的默认值是 1，setup 是步长
```python
>>> for n in range(5):
...  print(n)
...
0
1
2
3
4
```

反向输出

```python
>>> for n in range(5,-1,-1):
...  print(n)
...
5
4
3
2
1
0
```

### range 在 Python2.7 与 3.5 的差别

**python 2.7.11**

```python
>>> range(0,100)
[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99]
```

range 在 Python2.7 中，会把所有的序列都输出出来，没一个序列都在内存中占用一点空间

**xrange**

xrang 不会一次性把序列全部都存放在内存中，而是用到 for 循环进行迭代的时候才会一个一个的存到内存中，相当于 Python3.5 中的 range。
```python
>>> for i in xrange(1,10):
...  print(i)
...
1
2
3
4
5
6
7
8
9
```

**python 3.5.1**

```python
>>> range(1,100)
range(1, 100)
```

range 在 python3.5 中就不会一次性的占用那么多空间，他会我需要用到这个序列的时候然后再内存中开辟一块空间给这个序列，不是一次性分完，相当于 Python2.7.11 中的 xrange.

## while 循环

`while`循环不同于`for`循环，`while`循环是只要条件满足，那么就会一直运行代码块，否则就运行`else`代码块，语法如下：

```python
while <条件>:
	<代码块>
else:
	<如果条件不成立执行这里的代码块>
```

小栗子

```python
#!/use/bin/env python
# _*_ coding:utf-8 _*_

flag = True

while flag:
   print(flag)
   flag = False
else:
   print('else', flag)
```

## 练习题

### 元素分类

有如下值集合 [11,22,33,44,55,66,77,88,99,90]，将所有大于 66 的值保存至字典的第一个 key 中，将小于 66 的值保存至第二个 key 的值中。
即： {'k1': 大于 66 的所有值, 'k2': 小于 66 的所有值}

图解流程:
![python-day02-06](https://blog.ansheng.me/images/2016/12/1483016438.png)

解答：
```python
#_*_coding:utf-8_*_

num = [11,22,33,44,55,66,77,88,99,90]

dict = {
	'k1':[],
	'k2':[]
}

for n in range(len(num)):
	if num[n] <= 66:
		dict['k1'].append(num[n])
	else:
		dict['k2'].append(num[n])

print(dict.get("k1"))
print(dict.get("k2"))
```

- 输出结果

```python
[11, 22, 33, 44, 55, 66]
[77, 88, 99, 90]
```

### 查找
查找列表中元素，移动空格，并查找以 a 或 A 开头 并且以 c 结尾的所有元素。
```python
li = ["alec", " aric", "Alex", "Tony", "rain"]
tu = ("alec", " aric", "Alex", "Tony", "rain") 
dic = {'k1': "alex", 'k2': ' aric',  "k3": "Alex", "k4": "Tony"}
```

- 列表的方式

```python
#!/usr/bin/env python
# _*_ coding:utf-8 _*_

li = ["alec", " aric", "Alex", "Tony", "rain"]
for n in range(len(li)):
    # 去掉左右两边的空格然后输出内容并且把首字母换成大写
    # string = str(li[n]).strip().capitalize()
    # 把字符串中的空格替换掉，然后首字母转换成大写
    string = str(li[n]).replace(" ","").capitalize()
    # 判断如果字符串的开头是大写字母"A"并且小写字母是"c"就print输出
    if string.find("A") == 0 and string.rfind("c") == len(string) - 1:
        print(li[n],"--->",string)
```
输出的结果：
```ptyhon
alec ---> Alec
 aric ---> Aric
```

- 元组的方式

```python
#!/usr/bin/env python
# _*_ coding:utf-8 _*_

tu = ("alec", " aric", "Alex", "Tony", "rain")
for n in range(len(tu)):
    # 去掉左右两边的空格然后输出内容并且把首字母换成大写
    # string = str(li[n]).strip().capitalize()
    # 把字符串中的空格替换掉，然后首字母转换成大写
    string = str(tu[n]).replace(" ","").capitalize()
    # 判断如果字符串的开头是大写字母"A"并且小写字母是"c"就print输出
    if string.find("A") == 0 and string.rfind("c") == len(string) - 1:
        print(tu[n],"--->",string)
```
输出的结果
```python
alec ---> Alec
 aric ---> Aric
```

- 字典的方式

```python
#!/usr/bin/env python
# _*_ coding:utf-8 _*_

dic = {
    'k1': "alex",
    'k2': ' aric',
    "k3": "Alex",
    "k4": "Tony"
}

for key,val in dic.items():
    string = str(val).replace(" ","").capitalize()
    if string.find("A") == 0 and string.rfind("c") == len(string) - 1:
        print(key,val,"---",string)
```
输出的结果
```python
k2  aric --- Aric
```

### 输出商品列表

用户输入序号，显示用户选中的商品

商品
```python
li = ["手机", "电脑", '鼠标垫', '游艇']
```

```python
#!/usr/bin/env python
# _*_ coding:utf-8 _*_
li = ["手机", "电脑", '鼠标垫', '游艇']
for key,value in enumerate(li,1):
    print(key,".",value)
li_num = input("请选择商品:")
print(li[int(li_num)-1])
```
执行结果
```python
1 . 手机
2 . 电脑
3 . 鼠标垫
4 . 游艇
请选择商品:1
手机
```

### 购物车
功能要求：
要求用户输入总资产，例如：2000
显示商品列表，让用户根据序号选择商品，加入购物车
购买，如果商品总额大于总资产，提示账户余额不足，否则，购买成功。
附加：可充值、某商品移除购物车
```python
goods = [
    {"name": "电脑", "price": 1999},
    {"name": "鼠标", "price": 10},
    {"name": "游艇", "price": 20},
    {"name": "美女", "price": 998},
]
```

- 逻辑图

![python-day02-08](https://blog.ansheng.me/images/2016/12/1483016473.png)

- 代码部分

```python
#!/usr/bin/env python
# _*_ coding:utf-8 _*_

# 拥有的商品及价格
goods = [
    {"name": "电脑", "price": 1999},
    {"name": "鼠标", "price": 10},
    {"name": "游艇", "price": 20},
    {"name": "美女", "price": 998},
]

# 控制while循环开关
switch = "on"

# 购物车存放的商品及单价
gouwuche = {
    # 商品列表
    "wuping":[],
    # 单价列表
    "jiage":[]
}

# 用户输入会员卡内余额
while True:
    try:
        # 让用户输入会员卡内拥有的余额
        money = int(input("请输入你会员卡内的余额："))
    # 异常判断，如果类型不是整型则执行except内的代码
    except ValueError:
        # 提示用户输入的格式错误，让其重新输入
        print("error,余额格式输入错误，请重新输入！\n例如：5000")
        # 终端当前循环让循环重新执行
        continue
    break

# 进入购买商品的流程
while switch == "on":

    # 打印出所有的商品
    print("\n","序列","商品","单价")
    # 以序列的方式输出现拥有的商品及商品单价
    for num,val in enumerate(goods,1):
        for n in range(len(goods)):
            if num-1 == n:
                print("  ",num,goods[n]["name"],goods[n]["price"])

    # 判断用户输入的序列是否规范
    while True:
        try:
            # 输入产品序列，类型转换为整型
            x = int(input("请选择商品序列："))

        # 如果用户输入的非整型，提示用户重新输入
        except ValueError:
            print("error,请选择商品的序列")
            continue

        # 如果用户输入的序列不再产品序列当中让用户重新输入
        if x > num:
            print("error,请选择商品的序列")
            continue
        break

    # 输出购买物品的信息
    print("你已经把商品",goods[x-1]["name"],"加入购物车","物品单价是：",goods[x-1]["price"],"\n")
    # 把物品名称放入gouwuche的wuping列表中
    gouwuche["wuping"].append(goods[x-1]["name"])
    # 把物品单价放入gouwuche的jiage列表中
    gouwuche["jiage"].append(goods[x-1]["price"])

    # 用户输入选项
    while switch == "on":
        # 输出现有选项
        print("查看购物车：p 结算：w 删除商品：d 继续购买：n 充值：i 显示余额：m 退出：q")
        # 把用户输入的选项转换为字符串
        xx = str(input("请输入你的选择："))

        # 如果用户输入的是p则列出当前购物车内的商品名称
        if xx == "p":
            # 以序列的方式输出字典gouwuche内的wuping列表
            for wp_num,val in enumerate(gouwuche["wuping"], 1):
                print(wp_num, val)

        # 如果用户输入的是w则结算
        elif xx == "w":
            # 定义一个默认的变量为用户商品的总金额
            zje = 0
            # 把gouwuche中的jiage列表内的整数进行相加并复制给zje
            for n in range(len(gouwuche["jiage"])):
                zje = zje + gouwuche["jiage"][n]
            # 如果商品的总金额大于用户会员卡内的余额，则提示用户钱不够
            if zje > money:
                print("sorry, 钱不够哦~~\n")
            # 否则就退出程序，并且输出用户本次消费的情况
            else:
                switch = "off"
                print("购物愉快，您本次消费",zje,"RMB","还剩余",money-zje,"RMB")

        # 如果用户输入的是d则进入删除购物车内的商品界面
        elif xx == "d":
            # 首先输出用户购物车内的商品列表
            for wp_num, val in enumerate(gouwuche["wuping"], 1):
                print(wp_num, val)
            # 选择所删除商品的序列
            while True:
                try:
                    deltet = int(input("请选择要删除的商品序列："))
                except ValueError:
                    print("error,请输出正确的序列！")
                    continue
                if deltet > wp_num:
                    print("error,请选择商品的序列")
                    continue
                # 提示用户购物车内被删除的商品信息
                print("你已经删除产品", gouwuche["wuping"][deltet - 1], "单价为；", gouwuche["jiage"][deltet - 1])
                # 删除商品
                gouwuche["wuping"].pop(deltet - 1)
                # 删除金额
                gouwuche["jiage"].pop(deltet - 1)
                break

        # 如果用户输入的是i则进入用户会员卡充值页面
        elif xx == "i":
            # 判断用户输入的银行卡号格式是否正确
            while True:
                try:
                    user = int(input("请输入你的银行卡账号："))
                except ValueError:
                    print("error,卡号格式输入错误，请重新输入..")
                    continue
                break

            # 判断用户输入的银行卡密码格式是否正确
            while True:
                try:
                    pwd = int(input("请输入银行卡的密码："))
                except ValueError:
                    print("error,密码格式输入错误，请重新输入..")
                    continue
                break
            # 判断用户输入的账号和密码是否正确，默认的账号和密码都是123
            if user == 123 and pwd == 123:
                # 如果正确就让用户输入要充值的金额
                while True:
                    try:
                        newmoney = int(input("请输入充值的金额："))
                    except ValueError:
                        print("error,金额格式输入错误，请重新输入..")
                        continue
                    break
                # 余额加上充值的金额
                money = money + newmoney
                # 输出本次充值的信息
                print("你已成功充值",newmoney,"RMB，现在账户余额为：",money,"RMB\n")
            # 如果用户银行卡账号或密码错误，就提示用户输入错误，让后让用户重新选择
            else:
                print("银行卡账号或密码错误.\n")

        # 如果用户输入的是m则显示用户会员卡内的余额
        elif xx == "m":
            print("账户余额：",money,"\n")

        # 如果用户输入的是q则退出程序
        elif xx == "q":
            # 把变量switch的值改为off
            switch = "off"

        # 如果用户输入的是n则继续购买商品
        elif xx == "n":
            break

        # 如果用户没有输入以上的任意一个选项则让用户重新输入
        else:
            print("请输出正确的选项！")
```

- 执行结果

```python
请输入你会员卡内的余额：1000

 序列 商品 单价
   1 电脑 1999
   2 鼠标 10
   3 游艇 20
   4 美女 998
请选择商品序列：1
你已经把商品 电脑 加入购物车 物品单价是： 1999 

查看购物车：p 结算：w 删除商品：d 继续购买：n 充值：i 显示余额：m 退出：q
请输入你的选择：i
请输入你的银行卡账号：123
请输入银行卡的密码：123
请输入充值的金额：2000
你已成功充值 2000 RMB，现在账户余额为： 3000 RMB

查看购物车：p 结算：w 删除商品：d 继续购买：n 充值：i 显示余额：m 退出：q
请输入你的选择：m
账户余额： 3000 

查看购物车：p 结算：w 删除商品：d 继续购买：n 充值：i 显示余额：m 退出：q
请输入你的选择：p
1 电脑
查看购物车：p 结算：w 删除商品：d 继续购买：n 充值：i 显示余额：m 退出：q
请输入你的选择：d
1 电脑
请选择要删除的商品序列：1
你已经删除产品 电脑 单价为； 1999
查看购物车：p 结算：w 删除商品：d 继续购买：n 充值：i 显示余额：m 退出：q
请输入你的选择：p
查看购物车：p 结算：w 删除商品：d 继续购买：n 充值：i 显示余额：m 退出：q
请输入你的选择：n

 序列 商品 单价
   1 电脑 1999
   2 鼠标 10
   3 游艇 20
   4 美女 998
请选择商品序列：4
你已经把商品 美女 加入购物车 物品单价是： 998 

查看购物车：p 结算：w 删除商品：d 继续购买：n 充值：i 显示余额：m 退出：q
请输入你的选择：w
购物愉快，您本次消费 998 RMB 还剩余 2002 RMB
```

### 三级联动

用户交互，显示省市县的选择

```python
dic = {
    "河北": {
        "石家庄": ["鹿泉", "藁城", "元氏"],
        "邯郸": ["永年", "涉县", "磁县"],
    },
    "河南": {
        ...
    },
    "山西": {
        ...
    }
}
```

- 流程图解

![python-day02-09](https://blog.ansheng.me/images/2016/12/1483016506.png)

- 代码如下

```python
#!/usr/bin/env python
# _*_ coding:utf-8 _*_

# 定义一个拥有省市县的字典
dic = {
    "河北": {
        "石家庄": ["鹿泉", "藁城", "元氏"],
        "邯郸": ["永年", "涉县", "磁县"],
    },
    "河南": {
        "郑州市":["中原区","二七区","金水区"],
        "洛阳市":["涧西区","西工区","老城区"]
    },
    "山西": {
        "太原市":["迎泽区","杏花岭区","万柏林区"],
        "大同市":["大同县","天镇县","浑源县"]
    }
}

# 控制while循环的开关
switch = "on"

# 执行脚本就显示已经进入中国
print("\n你已进入中国\n")

# 开始执行while循环
while switch == "on":

    # 省得列表
    sheng = []
    # 市的列表
    shi = []
    # 镇的列表
    zhen = []

    # 让用户选择进入的生
    while switch == "on":
        # 输出省得列表
        for sheng_n, sheng_v in enumerate(dic, 1):
            print(sheng_n, sheng_v)
            sheng.append(sheng_v)
        # 用户输出选择进入的省
        try:
            # 用户输入的必须为整数
            sheng_inp = int(input("请选择你要进入的城市序列："))
        except ValueError:
            # 如果不是整数就报错然后让用户重新输入
            print("序列输入错误，请重新输入")
            continue
        # 如果用户输入的证书是0或者大于列表的序列就让用户重新输入
        if sheng_inp > sheng_n or sheng_inp == 0:
            print("序列输入错误，请重新输入")
            continue
        # 输入正确之后输出用户当前在哪里
        print("\n你已进入中国--->", sheng[sheng_inp - 1], "\n")

        # 选项
        while True:
            # 输出选项
            ify = input("b 返回上一级\nn 继续\nq 退出\n请输入你的选择：")
            # 如果用户输入的是指定的字母就退出当前循环
            if ify == "q" or ify == "b" or ify == "n":
                break
            # 如果不是指定字母就让用户重新输入
            else:
                print("输入错误，请重新输入！")
                continue
        # 如果用户输入的是b就返回上一级
        if ify == "b":
            continue
        # 如果用户输入的是q那么就把变量switch值改为off
        elif ify == "q":
            switch = "off"
            continue
        # 如果用户输入的是n就继续让用户选择市，注释就写到这儿把，下面的代码就相当于让用户重新选择省，只不过省改为市了

        while switch == "on":
            for shi_n, shi_v in enumerate(dic[sheng[sheng_inp - 1]], 1):
                print(shi_n, shi_v)
                shi.append(shi_v)
            try:
                shi_inp = int(input("请选择你要进入的城市序列："))
            except ValueError:
                print("序列输入错误，请重新输入")
                continue
            if shi_n < shi_inp or shi_inp == 0:
                print("序列输入错误，请重新输入")
                continue
            print("\n你已进入中国--->", sheng[sheng_inp - 1], "--->",shi[shi_inp - 1])

            while True:
                ify = input("b 返回上一级\nn 继续\nq 退出\n请输入你的选择：")
                if ify == "q" or ify == "b" or ify == "n":
                    break
                else:
                    print("输入错误，请重新输入！")
                    continue
            if ify == "b":
                continue
            elif ify == "q":
                switch = "off"
                continue

            while switch == "on":
                for zhen_n, zhen_v in enumerate(dic[sheng[sheng_inp - 1]][shi[shi_inp - 1]], 1):
                    print(zhen_n, zhen_v)
                    zhen.append(zhen_v)
                try:
                    zhen_inp = int(input("请选择你要进入的城市序列："))
                except ValueError:
                    print("序列输入错误，请重新输入")
                    continue
                if zhen_n < zhen_inp or zhen_inp == 0:
                    print("序列输入错误，请重新输入")
                    continue
                print("\n你已进入中国--->", sheng[sheng_inp - 1], "--->", shi[shi_inp - 1],"--->",zhen[zhen_inp - 1])
                while True:
                    ify = input("b 返回上一级\nn 继续\nq 退出\n请输入你的选择：")
                    if ify == "q" or ify == "b" or ify == "n":
                        break
                    else:
                        print("输入错误，请重新输入！")
                        continue
                if ify == "b":
                    continue
                elif ify == "q":
                    switch = "off"
                    continue
```

> 哎，代码写的 low 又没注释，笨人笨方法吧，谁让咱是新人，将就着看吧，注意这是在 Python3.5.x 系列执行的哦

- 执行结果

```python
你已进入中国

1 山西
2 河南
3 河北
请选择你要进入的城市序列：2

你已进入中国---> 河南 

b 返回上一级
n 继续
q 退出
请输入你的选择：n
1 郑州市
2 洛阳市
请选择你要进入的城市序列：1

你已进入中国---> 河南 ---> 郑州市
b 返回上一级
n 继续
q 退出
请输入你的选择：b
1 郑州市
2 洛阳市
请选择你要进入的城市序列：2

你已进入中国---> 河南 ---> 洛阳市
b 返回上一级
n 继续
q 退出
请输入你的选择：n
1 涧西区
2 西工区
3 老城区
请选择你要进入的城市序列：1

你已进入中国---> 河南 ---> 洛阳市 ---> 涧西区
b 返回上一级
n 继续
q 退出
请输入你的选择：q
```