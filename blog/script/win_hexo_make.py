#!/usr/bin/env python
# -*- coding: gbk -*-
# Created by imoyao at 2019/4/11 19:11

"""
�������������б�д hexo ����
"""
import argparse
import os
import sys

import utils


# https://yiyibooks.cn/xx/python_352/library/argparse.html
# https://blog.csdn.net/qq_36653505/article/details/83788460
'''
--- Hexo�Դ����� ---
-n/--new �½�һƪ���ġ�  -n 'add-a-post-for-blog'
-g/--generate ���ɾ�̬�ļ��� -g
-s/--server ������������Ĭ������£�������ַΪ�� http://localhost:4000/
-d/--deploy ������վ��Ĭ�������Ϊ github page.
-----
-x/ --xcopy �ļ��ƶ�
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
        print(" ���±�������Ӧ��ʹ�� '-'���л��ߣ��ָ")
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
    xcopy_file()  # ����֮���ִ��


def xcopy_file(bak_file_fp='', new_create_fp=''):
    """
    ��Ϊaboutҳ����ʽ��������ÿ��hexo_generate����Ҫ�� about\index.html.bak.html �滻�����ɵ� index.html
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
        parser = argparse.ArgumentParser(description='�������������������ֱ�ӱ�дHexo��������')
    # group = parser.add_mutually_exclusive_group()

    # group.add_argument('title', metavar='Title',
    #                     help='�½����ĵı��⡣')
    parser.add_argument('-n', '--new', dest='create_post', action='store_const',
                        const=new_post, default=new_post,
                        help='�½�һƪ���ġ�')
    parser.add_argument('-g', '--generate', dest='generate_post', action='store_const',
                        const=hexo_generate, default=hexo_generate,
                        help='���ɾ�̬�ļ���')

    parser.add_argument('-s', '--server', dest='server_post', action='store_const',
                        const=hexo_post, default=hexo_post,
                        help='������������')
    parser.add_argument('-d', '--deploy', dest='deploy_post', action='store_const',
                        const=hexo_post, default=hexo_post,
                        help='������վ��')

    parser.add_argument('-x', '--xcopy', '-cp', dest='cp_file', action='store_const',
                        const=xcopy_file, default=xcopy_file,
                        help='�ƶ��ļ���')

    args = parser.parse_args()
    print(args)
    '''
    parser = argparse.ArgumentParser(description='�������������������ֱ�ӱ�дHexo���ͣ�')
    # parser.add_argument('-n', '--new', dest='create_post', action='store_const',
    #                     const=new_post, default=new_post,
    #                     help='�½�һƪ���ġ�')
    subparsers = parser.add_subparsers()
    parser_n = subparsers.add_parser('n', help='�½�һƪ���ġ�')
    parser_n.add_argument('title', help='�½�һƪ���ġ�')
    parser_n.set_defaults(func=new_post)

    parser_g = subparsers.add_parser('g', help='���ɾ�̬�ļ���')
    parser_g.set_defaults(func=hexo_generate)
    # args = parser.parse_args()
    # print(args)
    # args.func()

    parser_s = subparsers.add_parser('s', help='������������')
    # parser_n.add_argument('flag', help='������������')
    parser_s.set_defaults(func=hexo_post)
    # args = parser.parse_args()

    parser_s = subparsers.add_parser('d', help='������վ��')
    parser_s.set_defaults(func=hexo_post)

    parser_x = subparsers.add_parser('x', help='�ƶ��ļ���')     # TODO:f/tӦ���ǿ�ѡ����
    parser_x.add_argument('f', default='', help='Դ�ļ�����')
    parser_x.add_argument('t', default='', help='���ļ�����')
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
        parser.print_help()     # TODO:���� help()����
        pass


if __name__ == '__main__':
    main()
