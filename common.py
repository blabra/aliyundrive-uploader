# -*- coding: utf-8 -*-
# +-------------------------------------------------------------------
# | 公共函数类
# +-------------------------------------------------------------------
# | 新手学习Python用
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


def chunkIt(a, n):
    n = min(n, len(a))
    k, m = divmod(len(a), n)
    return [a[i*k+min(i, m):(i+1)*k+min(i+1, m)] for i in range(n)]

def format_path(path):
    return path.replace('/', os.sep).replace('\\\\', os.sep).rstrip(os.sep) + os.sep


def print_info(message):
    log(message)
    print(f'\033[7;30;37m{message}\033[0m')


def print_warn(message):
    log_error(message)
    print(f'\033[7;30;33m{message}\033[0m')


def print_error(message):
    log_error(message)
    print(f'\033[7;30;31m{message}\033[0m')


def print_success(message):
    log(message)
    print(f'\033[7;30;32m{message}\033[0m')


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
