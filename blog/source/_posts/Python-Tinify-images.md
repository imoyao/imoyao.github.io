---
title: 使用 Python 压缩图片(借助 TinyPng 的接口)
date: 2020-01-12 11:03:14
tags:
- Python
- 压缩图片
- TODO
---
## 缘起
    pass
    
## 思路

### key
在执行前直接配置：程序自动获取（环境变量、文件、代码中）；如果获取失败则提示配置，设置key成功，保存到文件中，下一次执行时，直接在文件中直接读取；

### 压缩处理

1. 如果没有给出参数，则递归压缩当前目录下的文件，并保存到`tiny`目录；
2. 如果给出参数并且是文件，则压缩单个文件
    1. 如果没有额外参数，则压缩该文件并保存到 tiny 目录；
    2. 如果给出的额外参数是 -d xxx，则保存到用户指定的目录（目录可以是相对，也可以是绝对路径）；
    3. 如果给出的参数是 -f  xxx，如果为空，则压缩成同名+'_tinified'；如果不为空且有后缀，则验证后缀相同再压缩，否则 raise；如果没有后缀，则判断是否同名，不同名则压缩之后命名新名称文件，否则覆盖提示；
3. 如果给出参数[源目录 目的目录]，则将文件保存到指定目录；

## 参数
- 不带参数
    递归压缩当前目录下的所有图片，并保存到tiny目录
    ```bash
    python shrink_img.py
    ```
- `--key/-k`
 从官网申请的 `key`，提供三种方式导入使用：
     1. 代码中直接填充；
     2. 执行前，命令行导入环境变量；
         ```shell
         export TINY_KEY='{{YOU GET FROM tinypng.com }}'
         ```
     3. 写进配置文件`tiny.key`；
         ```bash
         echo '{{YOU GET FROM tinypng.com }}' > tiny.key
         ```
     4. 执行时，搭配`--key`指定；如果没有给出，则要求用户输入；
     
- `--file/-f`
    指定图片名称，必须包含文件全名（即包含后缀名）。如果不带额外参数，则表示保存到当前目录下；否则，为用户指定目录下文件。
    搭配以下指令使用。
    - `--fcover/-c`
        以覆盖形式压缩，即直接将压缩后文件保存为被压缩文件的位置（且同名）；
        
    - `--save/-s`
        可选参数，缺省时为**当前执行目录**下的`tiny`目录；给定参数时，为指定保存的目录；
- `--dir/-d`  
    指定压缩的目录。缺省时为**当前执行目录**下的`tiny`目录，可选指定目录名称；
    
    可选搭配以下参数使用:
    - `--recurse|--not-recurse/-r|-nr`
        递归式压缩指定目录。如果使用`--recurse/-r`则递归压缩指定目录下所有层级下的图片文件；如果使用`--not-recurse/-nr`表示只压缩该层级目录；
    - `--save/-s`
        可选参数，可以选择搭配`--recurse`使用。缺省时为**当前执行目录**下的`tiny`目录（即和默认不指定目录名称效果相同）；给定参数时，为指定保存的目录；
         
- resize
    只支持单文件resize,根据官网API，目前支持`--scale/--fit/--cover/--thumb`参数，指定该参数中的其一时，表示 resize 的文件名称，后面跟*file name和width和/或height*；
    1. 其中指定为`--scale`时，**必须**--width或者--height；
        ```bash
        --scale FILENAME --width INT
        --scale FILENAME --height INT
        ```
    2. 其余参数时，第一个参数为文件名，剩余两个参数**依次**为*width和height*，不需要显式指定`--width`和`--height`；
        ```bash
        --[fit,cover,thumb] FILENAME INT INT
        ```  
 
## 报错记录
- TypeError: It would appear that nargs is set to conflict with the composite type arity.

参考 [here](https://stackoverflow.com/questions/40794429/typeerror-it-would-appear-that-nargs-is-set-to-conflict-with-the-composite-type)和 [github issue](https://github.com/pallets/click/issues/472)  
> Click does not have a way currently to define default values for nargs > 1 when different types are used. A workaround is to set default=(None, None) for instance.
也就是说你必须给 tuple 一个默认值为 None 的等长元祖；
```python
import click
@click.option('--baz', '-b',
              default=[None] * 6,
              type=click.Tuple([str, str, str, str, str, str]),help='bar')
def foo(baz):
    pass
```

## TODO

源码中的 click 使用 Google 开源库 [Python Fire](https://github.com/google/python-fire)
## 参考文档
- [欢迎查阅 Click 中文文档 — click](https://click-docs-zh-cn.readthedocs.io/zh/latest/)

## 更多

- [图片无损压缩工具都有哪些？ - 知乎](https://www.zhihu.com/question/19779256)
---
{% blockquote 萧伯纳 %}
明白事理的人使自己适应世界；不明事理的人想使世界适应自己。所以，所有进步都要靠不明事理的人。
{% endblockquote %}