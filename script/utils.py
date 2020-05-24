#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    import Queue
except ImportError:
    import queue as Queue
import base64
import json
import platform
import re
import socket
import subprocess
import sys
import time
import traceback
from threading import Thread


# ----------------------------------
# async read
# ----------------------------------
class AsynchronousFileReader(Thread):
    def __init__(self, fd, queue):
        Thread.__init__(self)
        self._fd = fd
        self._queue = queue

    def run(self):
        for line in iter(self._fd.readline, ''):
            self._queue.put(line)

    def eof(self):
        return not self.is_alive() and self._queue.empty()


# ----------------------------------
def asyncread(command=None, readline=True, sudo=True, close_fds=True):
    outlist = []
    errlist = []
    retcode = 0
    if command:
        if sudo:
            if type(command) == list:
                tmpcmd = ['sudo']
                tmpcmd.extend(command)
                command = tmpcmd
            else:
                command = 'sudo %s' % command
        try:
            asyncprocess = None
            if close_fds and platform.system().lower() == 'linux':
                if type(command) == list:
                    asyncprocess = subprocess.Popen(command, shell=False, stdin=sys.stdin, stdout=subprocess.PIPE,
                                                    stderr=subprocess.PIPE, close_fds=True)
                else:
                    asyncprocess = subprocess.Popen(command, shell=True, stdin=sys.stdin, stdout=subprocess.PIPE,
                                                    stderr=subprocess.PIPE, close_fds=True)
            else:
                asyncprocess = subprocess.Popen(command, shell=True, stdin=sys.stdin, stdout=subprocess.PIPE,
                                                stderr=subprocess.PIPE)
            stdout_queue = Queue.Queue()
            stderr_queue = Queue.Queue()
            stdout_reader = AsynchronousFileReader(asyncprocess.stdout, stdout_queue)
            stderr_reader = AsynchronousFileReader(asyncprocess.stderr, stderr_queue)
            stdout_reader.start()
            stderr_reader.start()
            while not stdout_reader.eof() or not stderr_reader.eof():
                while not stdout_queue.empty():
                    outlist.append(stdout_queue.get())
                while not stderr_queue.empty():
                    errlist.append(stderr_queue.get())
                time.sleep(.1)
            retcode = asyncprocess.wait()
            stdout_reader.join()
            stderr_reader.join()
            asyncprocess.stdout.close()
            asyncprocess.stderr.close()
        except Exception as e:
            print(traceback.print_exc())
    if readline:
        outresult = outlist
        errresult = errlist
    else:
        outresult = outlist.join()
        errresult = errlist.join()
    return retcode, outresult, errresult


# ----------------------------------------
# user defined execute command
# ----------------------------------------
def cust_popen(cmd, no_wait=False, close_fds=True, sudo=True):
    if sudo:
        if type(cmd) == list:
            tmpcmd = ['sudo']
            tmpcmd.extend(cmd)
            cmd = tmpcmd
        else:
            cmd = 'sudo %s' % cmd
    try:
        proc = None
        retcode = None
        if close_fds and platform.system().lower() == 'linux':
            if type(cmd) == list:
                proc = subprocess.Popen(cmd, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                        close_fds=True)
            else:
                proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, close_fds=True)
        else:
            proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if not no_wait:
            retcode = proc.wait()
        return retcode, proc
    except Exception as e:
        print(traceback.print_exc())


# ----------------------------------------
# check if exists
# ----------------------------------------
# def path_exists(filepath):
#     pathexists = False
#     retcode,proc = cust_popen([commandlib.STAT, '-c%%a', filepath])
#     if retcode == 0:
#         pathexists = True
#     return pathexists
# ------------------------
# check command if exists
# ------------------------
def check_command(command):
    has_command = True
    retcode, proc = cust_popen('which %s' % command)
    result = proc.stdout.read().strip()
    if result.find('no %s in' % command) >= 0:
        has_command = False
    return has_command


# ------------------------
# sort string contain number
# ------------------------
re_digits = re.compile(r'(\d+)')


def embedded_numbers(s):
    pieces = re_digits.split(s)
    pieces[1::2] = map(int, pieces[1::2])
    return pieces


def sort_strings(alist):
    return sorted(alist, key=embedded_numbers)


# ----------------------------------------
# socket
# ----------------------------------------
def socketclient(app_type='user', ip='0.0.0.0', port=9997, clientip='127.0.0.1', **kwargs):
    rtndata = []
    params = {}
    # session = web.config.get('_session')
    # params = {'ip': 'ip' in web.ctx and web.ctx.ip or '127.0.0.1',
    #           'suid': session and app_type in session and 'id' in session[app_type] and session[app_type].id or '',
    #           'usrname': session and app_type in session and 'name' in session[app_type] and session[
    #               app_type].name or '',
    #           'usrpass': session and app_type in session and 'passwd' in session[app_type] and session[
    #               app_type].passwd or '',
    #           'lang': session and app_type in session and 'lang' in session[app_type] and session[
    #               app_type].lang or 'zh_CN'}
    if 'params' in kwargs:
        params.update(kwargs['params'])
    cmdstr = json.dumps({"target": kwargs['target'], "op": kwargs['op'], "params": params})
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((ip, port))
        try:
            sock.send(cmdstr)
        except:
            pass
        while True:
            buf = sock.recv(1024)
            if len(buf):
                rtndata.append(buf)
            else:
                break
        sock.close()
    except Exception as e:
        print >> sys.stderr, traceback.print_exc()
        try:
            sock.close()
        except:
            pass
    try:
        retresult = json.loads(''.join(rtndata))
    except:
        retresult = {'state': '1', 'result': {'message': '9999'}}
        print >> sys.stderr, traceback.print_exc()
    return retresult


# ----------------------------------------
# check if ip address
# ----------------------------------------
def check_ip(ip):
    retval = False
    m = re.match("^(\d+)\.(\d+)\.(\d+)\.(\d+)$", ip)
    if m:
        if 1 <= int(m.group(1)) <= 255 and 0 <= int(m.group(2)) <= 255 and 0 <= int(m.group(3)) <= 255 and 0 <= int(
                m.group(4)) <= 255:
            retval = True
    return retval


def make_file_java_byte_array_compatible(f, flag='file'):
    """ 
    Reads in a file and converts it to a format accepted as Java byte array 
    :param file object
    :return string
    """
    if flag == 'file':
        encoded_data = base64.b64encode(f.read())
    else:
        encoded_data = base64.b64encode(f)
    strg = ''
    for i in range(int(len(encoded_data) / 40) + 1):
        strg += encoded_data[i * 40:(i + 1) * 40]

    return strg
