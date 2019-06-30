#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by Administrator at 2019/6/30 16:55
# TODO:
#  后期直接运行脚本获取路径，
#  各种 Exception
#  过滤 markdown 文件

"""
usage:
python get_dir_files *.md PARENT_DIRNAME
out_put: MARKDOWN file name with blank space.
lint-md OUT_PUT -f
"""
import sys
import os

dir_name = sys.argv[1]
file_list = []
if os.path.exists(dir_name) and os.path.isdir(dir_name):
    for dir_path, subpaths, files in os.walk(dir_name):
        for file in files:
            file_list.append(os.path.join(dir_path,file))
    print(' '.join(file_list))

else:
    print('Error args!')
