#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by imoyao at 2020/7/2 14:30
# https://my.oschina.net/hanhanztj/blog/515065
__author__ = 'ZHANGTIANJIONG629'
import BaseHTTPServer
import threading
import time

lock_timeout_seconds = 8
lock = threading.Lock()
lock_client_ip = ""
lock_time = 0


class LockService(BaseHTTPServer.BaseHTTPRequestHandler):
    def do_get(self):
        '''define url route'''
        pass

    def lock(self, client_ip):
        global lock_client_ip
        global lock_time
        # if lock is free
        if lock.acquire():
            lock_client_ip = client_ip
            lock_time = time.time()
            self.send_response(200, 'ok')
            self.close_connection
            return
            # if current client hold lock,updte lock time
        elif lock_client_ip == client_ip:
            lock_time = time.time()
            self.send_response(200, 'ok,update')
            self.close_connection
            return
        else:
            # lock timeout,grab lock
            if time.time() - lock_time > lock_timeout_seconds:
                lock_client_ip = client_ip;
                lock_time = time.time()
                self.send_response(200, 'ok,grab lock')
                self.close_connection
                return
            else:
                self.send_response(403, 'lock is hold by other')
                self.close_connection

    def update_lock(self, client_ip):
        global lock_client_ip
        global lock_time
        if lock_client_ip == client_ip:
            lock_time = time.time()
            self.send_response(200, 'ok,update')
            self.close_connection
            return
        else:
            self.send_response(403, 'lock is hold by other')
            self.close_connection
            return

    def unlock(self, client_ip):
        global lock_client_ip
        global lock_time
        if lock.acquire():
            lock.release()
            self.send_response(200, 'ok,unlock')
            self.close_connection
            return
        elif lock_client_ip == client_ip:
            lock.release()
            lock_time = 0
            lock_client_ip = ''
            self.send_response(200, 'ok,unlock')
            self.close_connection
            return
        else:
            self.send_response(403, 'lock is hold by other')
            self.close_connection
            return


if __name__ == '__main__':
    http_server = BaseHTTPServer.HTTPServer(('127.0.0.1', '88888'), LockService)
    http_server.serve_forever()
