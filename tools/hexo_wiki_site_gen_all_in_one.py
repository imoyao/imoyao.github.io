#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by Administrator at 2020/5/23 16:03
"""
## 前置条件
调用前请确保安装 hexo 和 lint-md；
Win10 Python 3.7+ 测试通过
~~如果程序默认路径与配置中不同，请修改为正确路径后再执行！~~
运行生成前请保证没有 hexo 进程正在运行（会导致db.json删除失败）
## 作用
1. 对文章内容进行lint
2. 生成site和wiki
"""
import os

from libcoms import delegator

# hexo_path = r'C:\Users\Administrator\AppData\Roaming\npm\hexo.cmd'
# lint_md_path = r'C:\Users\Administrator\AppData\Roaming\npm\lint-md.cmd'
DB_FP = r'db.json'
WIKI_CONF = r'_config_wiki.yml'


def tool_fp(tool_name):
    win_cmd = 'where {tn}'.format(tn=tool_name)
    ret = delegator.run(win_cmd)
    return ret.out.split()[1]


def lint():
    """
    用于lint-md文章
    :return:
    """
    lint_md_path = tool_fp('lint-md')
    lint_site_posts = r'{lint} source\_posts\ -f'.format(lint=lint_md_path)
    ret = delegator.run(lint_site_posts, block=False)
    ret.block()
    # return_code = ret.return_code
    # print('lint site ret_code:', return_code)
    lint_site_posts = r'{lint} wiki\_posts\ -f'.format(lint=lint_md_path)
    ret = delegator.run(lint_site_posts, block=False)
    ret.block()
    return_code = ret.return_code
    # print('lint site ret_code:', return_code)
    assert return_code == 0
    return return_code


def gen():
    """
    用于渲染生成内容
    :return:
    """
    hexo_path = tool_fp('hexo')
    wiki_clean_cmd = '{hexo} --config {wk} clean'.format(hexo=hexo_path, wk=WIKI_CONF)
    ret = delegator.run(wiki_clean_cmd, block=False)
    ret.block()
    # return_code = ret.return_code
    # print('-----run--0----', return_code)
    wiki_generate_cmd = '{hexo} --config {wk} generate'.format(hexo=hexo_path, wk=WIKI_CONF)
    ret = delegator.run(wiki_generate_cmd, block=False)
    ret.block()
    # return_code = ret.return_code
    # print('-----run--1----', return_code)
    if os.path.exists(DB_FP):
        os.remove(DB_FP)
    site_generate_cmd = '{hexo} generate'.format(hexo=hexo_path, )
    ret = delegator.run(site_generate_cmd, block=False)
    ret.block()
    return_code = ret.return_code
    assert return_code == 0
    return return_code


def main(lint_md=False):
    """
    添加lint为可配置，否则会出问题 >>> plain
    :param lint_md:
    :return:
    """
    if lint_md:
        ret = lint()
        if ret == 0:
            print('lint-md execute success!')
    ret = gen()
    if ret == 0:
        print('site generate success,please run `hexo s` to Start the server.')


if __name__ == '__main__':
    main()
