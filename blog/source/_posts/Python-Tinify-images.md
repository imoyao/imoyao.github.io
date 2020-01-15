---
title: 使用 Python 压缩图片(借助 TinyPng 的接口)
date: 2020-01-12 11:03:14
tags:
- Python
- 压缩图片
- TODO
---
## 缘起

## 思路

1. 如果没有给出参数，则递归压缩当前目录下的文件，并保存到`tiny`目录；
2. 如果给出参数并且是文件，则压缩单个文件
    1. 如果没有额外参数，则压缩该文件并保存到 tiny 目录；
    2. 如果给出的额外参数是 -d xxx，则保存到用户指定的目录（目录可以是相对，也可以是绝对路径）；
    3. 如果给出的参数是 -f  xxx，如果为空，则压缩成同名+'_tinified'；如果不为空且有后缀，则验证后缀相同再压缩，否则 raise；如果没有后缀，则判断是否同名，不同名则压缩之后命名新名称文件，否则覆盖提示；
3. 如果给出参数[源目录 目的目录]，则将文件保存到指定目录；

## 参数
 - `--key`
 从官网申请的 key，提供三种方式：
     1. 代码中直接填充；
     2. 执行前，命令行导入环境变量；
         ```shell
         export TINY_KEY='{{YOU GET FROM tinypng.com }}'
         ```
     3. 写进配置文件`tiny.key`；
         ```bash
         echo '{{YOU GET FROM tinypng.com }}' > tiny.key
         ```

## TODO

源码中的 click 使用 Google 开源库 [Python Fire](https://github.com/google/python-fire)

## 更多

- [图片无损压缩工具都有哪些？ - 知乎](https://www.zhihu.com/question/19779256)
---
{% blockquote 萧伯纳 %}
明白事理的人使自己适应世界；不明事理的人想使世界适应自己。所以，所有进步都要靠不明事理的人。
{% endblockquote %}