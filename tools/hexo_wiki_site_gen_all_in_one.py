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
## 运行
python3 tools\hexo_wiki_site_gen_all_in_one.py
"""
import os
import subprocess

from libcoms import delegator

# hexo_path = r'C:\Users\Administrator\AppData\Roaming\npm\hexo.cmd'
# lint_md_path = r'C:\Users\Administrator\AppData\Roaming\npm\lint-md.cmd'
DB_FP = r'db.json'
WIKI_CONF = r'_config_wiki.yml'


class ExcuteError(Exception):
    pass


def custom_run(_cmd):
    """

    https://stackoverflow.com/questions/2715847/read-streaming-input-from-subprocess-communicate/17698359#17698359

    https://stackoverflow.com/questions/2715847/read-streaming-input-from-subprocess-communicate

    :param _cmd:
    :return:
    """
    if isinstance(_cmd, list):
        shell = False
    else:
        shell = True

    with subprocess.Popen(_cmd, shell=shell, stdout=subprocess.PIPE, bufsize=1, universal_newlines=True,
                          encoding='utf-8') as p:
        # for line in p.stdout:
        # https://docs.python.org/zh-cn/3/library/subprocess.html#subprocess.Popen.communicate
        for line in p.communicate()[0]:
            # UnicodeDecodeError: 'gbk' codec can't decode byte 0xa7 in position 59: illegal multibyte sequence
            print(line, end='')
        _ret_code = p.wait()
    return _ret_code


def tool_fp(tool_name):
    win_cmd = 'where {tn}'.format(tn=tool_name)
    _ret = delegator.run(win_cmd)
    return _ret.out.split()[1]


def lint():
    """
    用于lint-md文章
    :return:
    """
    lint_md_path = tool_fp('lint-md')
    lint_site_posts = r'{lint} source\_posts\ -f'.format(lint=lint_md_path)
    _ret = custom_run(lint_site_posts)
    if _ret == 0:
        print('Lint posts success!')
    else:
        raise ExcuteError('The command {} run error.'.format(lint_site_posts))

    lint_site_posts = r'{lint} wiki\_posts\ -f'.format(lint=lint_md_path)
    return_code = custom_run(lint_site_posts)
    if return_code == 0:
        print('Lint wiki success!')
    else:
        raise ExcuteError('The command {} run error.'.format(lint_site_posts))

    assert return_code == 0
    return return_code


def gen():
    """
    用于渲染生成内容
    :return:
    """
    hexo_path = tool_fp('hexo')
    wiki_clean_cmd = '{hexo} --config {wk} clean'.format(hexo=hexo_path, wk=WIKI_CONF)
    ret = custom_run(wiki_clean_cmd)
    if ret == 0:
        print('Clean wiki success!')
    else:
        raise ExcuteError('The command {} run error.'.format(wiki_clean_cmd))
    # return_code = ret.return_code
    # print('-----run--0----', return_code)
    wiki_generate_cmd = '{hexo} --config {wk} generate'.format(hexo=hexo_path, wk=WIKI_CONF)
    ret = custom_run(wiki_generate_cmd)
    if ret == 0:
        print('Generate wiki success!')
    else:
        raise ExcuteError('The command {} run error.'.format(wiki_generate_cmd))
    # return_code = ret.return_code
    # print('-----run--1----', return_code)
    if os.path.exists(DB_FP):
        os.remove(DB_FP)
    site_generate_cmd = '{hexo} generate'.format(hexo=hexo_path, )
    return_code = custom_run(site_generate_cmd)
    if ret == 0:
        print('Generate posts success!')
    else:
        raise ExcuteError('The command {} run error.'.format(site_generate_cmd))
    assert return_code == 0
    return return_code


def main(lint_md=True):
    """
    添加lint为可配置，否则会出问题 >>> plain
    :param lint_md:
    :return:
    """
    if lint_md:
        _ret = lint()
        if _ret == 0:
            print('lint-md execute success!')
    _ret = gen()
    if _ret == 0:
        print('Site generate success,please run `hexo s` to Start the server.')


if __name__ == '__main__':
    main()
