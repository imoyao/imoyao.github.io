#!/usr/bin/env python
# -*- coding: gbk -*-
# Created by imoyao at 2019/4/11 19:11

"""
用于在命令行中编写 hexo 博客
"""
import argparse
import os
import sys

import utils


# https://yiyibooks.cn/xx/python_352/library/argparse.html
# https://blog.csdn.net/qq_36653505/article/details/83788460
'''
--- Hexo自带命令 ---
-n/--new 新建一篇博文。  -n 'add-a-post-for-blog'
-g/--generate 生成静态文件。 -g
-s/--server 启动服务器。默认情况下，访问网址为： http://localhost:4000/
-d/--deploy 部署到网站。默认情况下为 github page.
-----
-x/ --xcopy 文件移动
'''


def new_post(post_title):
    """
    :param post_title:
    :return:
    """
    post_title = post_title.title
    print('---- title-----', post_title)

    # see: http://www.dsyybj.com/article/about-url-is-underline-or-bar-problem-section.html
    if '_' in post_title:
        print(" 文章标题链接应该使用 '-'（中划线）分割。")
    else:
        make_new_post_cmd = 'hexo n {0}'.format(post_title)
        ret_code, proc = utils.cust_popen(make_new_post_cmd)
        if ret_code:
            print(proc.stderr.read())
        else:
            print(proc.stdout.read())


def hexo_post(hexo_flag):
    """
    :param hexo_flag:
    :return:
    """
    print('------', hexo_flag)
    hexo_cmd = ''
    # http://www.dsyybj.com/article/about-url-is-underline-or-bar-problem-section.html
    if hexo_flag == 's':
        hexo_cmd = 'hexo s'
    elif hexo_flag == 'd':
        hexo_cmd = 'hexo d'
    if hexo_cmd:
        ret_code, proc = utils.cust_popen(hexo_cmd)
        if ret_code:
            print(proc.stderr.read())
        else:
            print(proc.stdout.read())


def hexo_generate():
    hexo_cmd = 'hexo g'
    ret_code, proc = utils.cust_popen(hexo_cmd)
    if ret_code:
        print(proc.stderr.read())
    else:
        print(proc.stdout.read())
    xcopy_file()  # 生成之后就执行


def xcopy_file(bak_file_fp='', new_create_fp=''):
    """
    因为about页面样式错误，所以每次hexo_generate都需要用 about\index.html.bak.html 替换新生成的 index.html
    :param bak_file_fp:
    :param new_create_fp:
    :return:
    """
    if not bak_file_fp:
        bak_file_fp = r'blog\public\about\index.html.bak.html'
    if not new_create_fp:
        new_create_fp = r'blog\public\about\index.html'
    if os.path.exists(bak_file_fp) and os.path.isfile(bak_file_fp) and all((bak_file_fp, new_create_fp)):
        xcpoy_cmd = 'echo Y|xcopy {from_fp} {to_fp}'.format(from_fp=bak_file_fp, to_fp=new_create_fp)
        ret_code, _ = utils.cust_popen(xcpoy_cmd)
        return ret_code


def main():
    """
    pass
    :return:
    """
    '''
        parser = argparse.ArgumentParser(description='现在你可以在命令行中直接编写Hexo博客啦！')
    # group = parser.add_mutually_exclusive_group()

    # group.add_argument('title', metavar='Title',
    #                     help='新建博文的标题。')
    parser.add_argument('-n', '--new', dest='create_post', action='store_const',
                        const=new_post, default=new_post,
                        help='新建一篇博文。')
    parser.add_argument('-g', '--generate', dest='generate_post', action='store_const',
                        const=hexo_generate, default=hexo_generate,
                        help='生成静态文件。')

    parser.add_argument('-s', '--server', dest='server_post', action='store_const',
                        const=hexo_post, default=hexo_post,
                        help='启动服务器。')
    parser.add_argument('-d', '--deploy', dest='deploy_post', action='store_const',
                        const=hexo_post, default=hexo_post,
                        help='部署到网站。')

    parser.add_argument('-x', '--xcopy', '-cp', dest='cp_file', action='store_const',
                        const=xcopy_file, default=xcopy_file,
                        help='移动文件。')

    args = parser.parse_args()
    print(args)
    '''
    parser = argparse.ArgumentParser(description='现在你可以在命令行中直接编写Hexo博客！')
    # parser.add_argument('-n', '--new', dest='create_post', action='store_const',
    #                     const=new_post, default=new_post,
    #                     help='新建一篇博文。')
    subparsers = parser.add_subparsers()
    parser_n = subparsers.add_parser('n', help='新建一篇博文。')
    parser_n.add_argument('title', help='新建一篇博文。')
    parser_n.set_defaults(func=new_post)

    parser_g = subparsers.add_parser('g', help='生成静态文件。')
    parser_g.set_defaults(func=hexo_generate)
    # args = parser.parse_args()
    # print(args)
    # args.func()

    parser_s = subparsers.add_parser('s', help='启动服务器。')
    # parser_n.add_argument('flag', help='启动服务器。')
    parser_s.set_defaults(func=hexo_post)
    # args = parser.parse_args()

    parser_s = subparsers.add_parser('d', help='部署到网站。')
    parser_s.set_defaults(func=hexo_post)

    parser_x = subparsers.add_parser('x', help='移动文件。')     # TODO:f/t应该是可选参数
    parser_x.add_argument('f', default='', help='源文件名。')
    parser_x.add_argument('t', default='', help='新文件名。')
    parser_s.set_defaults(func=xcopy_file)

    args = parser.parse_args()
    print(args)
    opt = sys.argv[1]
    if opt in ['n', 'g', 's', 'd', 'x']:
        if opt == 'd':
            args.func('d')
        elif opt == 's':
            args.func('s')
        elif opt == 'g':
            args.func()
        else:
            args.func(args)
    else:
        parser.print_help()     # TODO:调用 help()方法
        pass


if __name__ == '__main__':
    main()
