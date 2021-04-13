# -*- coding: utf-8 -*-
# +-------------------------------------------------------------------
# | 公共函数类
# +-------------------------------------------------------------------
# | Author: 李小恩 <i@abcyun.cc>
# +-------------------------------------------------------------------
import hashlib
import os
import random
import time


def get_hash(filepath):
    with open(filepath, 'rb') as f:
        sha1 = hashlib.sha1()
        while True:
            data = f.readline()
            if not data:
                break
            sha1.update(data)
        return sha1.hexdigest()


def format_path(path):
    return path.replace('/', os.sep).replace('\\\\', os.sep).rstrip(os.sep) + os.sep


def print_info(message):
    i = random.randint(34, 37)
    log(message)
    print('\033[7;30;{i}m{message}\033[0m'.format(message=message, i=i))


def print_warn(message):
    log_error(message)
    print('\033[7;30;33m{message}\033[0m'.format(message=message))


def print_error(message):
    log_error(message)
    print('\033[7;30;31m{message}\033[0m'.format(message=message))


def print_success(message):
    log(message)
    print('\033[7;30;32m{message}\033[0m'.format(message=message))


def date(timestamp):
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp))


def log_error(message):
    file = (os.getcwd() + '/log/' + time.strftime("%Y-%m-%d", time.localtime())
             + 'error.log')
    if not os.path.exists(os.path.dirname(file)):
        os.mkdir(os.path.dirname(file))
    with open(file, 'a') as f:
        f.write(f'【{date(time.time())}】{message}\n')


def log(message):
    file = (os.getcwd() + '/log/' + time.strftime("%Y-%m-%d", time.localtime())
             + 'standard.log')
    if not os.path.exists(os.path.dirname(file)):
        os.mkdir(os.path.dirname(file))
    with open(file, 'a') as f:
        f.write(f'【{date(time.time())}】{message}\n')
