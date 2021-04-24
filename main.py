# -*- coding: utf-8 -*-
# +-------------------------------------------------------------------
# | 阿里云盘上传Python3脚本
# +-------------------------------------------------------------------
# | Author: 李小恩 <i@abcyun.cc>
# +-------------------------------------------------------------------
import json
import os
import sys
import time, queue, threading
# from concurrent.futures import ThreadPoolExecutor, as_completed
from hashlib import sha1
from common import print_warn, print_error, print_info, print_success, date, format_path, get_hash


if __name__ != '__main__':
    exit()

from AliyunDrive import AliyunDrive


local = threading.local()
workQueue = queue.Queue()
locker = threading.Lock()

class myThread(threading.Thread):
    def __init__(self, ThreadId, FilePath, workQueue):
        threading.Thread.__init__(self)
        self.ThreadId = ThreadId
        self.FilePath = FilePath
        self.work_queue = workQueue
    
    
    def run(self):
        print(f'Thread - {self.ThreadId} Running')
        Multi_Threading(self.FilePath, self.work_queue, self.ThreadId)
        print(f'Thread - {self.ThreadId} Stopped')

def Multi_Threading(FilePath, workQueue, ThreadId):
    while not exitFlag:
        locker.acquire()
        if not workQueue.empty():
            file = workQueue.get()
            locker.release()
            upload_file(L_PATH, file, ThreadId)
        else:
            locker.release()
    time.sleep(0.5)


def load_file(filepath, realpath):
        local.start_time = time.time()
        local.filepath = filepath
        local.filename = os.path.basename(realpath)
        local.hash = get_hash(realpath)
        local.filesize = os.path.getsize(realpath)


def get_parent_folder_id(root_path, filepath, ThreadId):
    filepath_split = (root_path + filepath.lstrip(os.sep)).split(os.sep)
    del filepath_split[len(filepath_split) - 1]
    path_name = os.sep.join(filepath_split)
    if not path_name in drive.folder_id_dict:
        parent_folder_id = 'root'
        parent_folder_name = os.sep
        if len(filepath_split) > 0:
            for folder in filepath_split:
                if folder == '':
                    continue
                parent_folder_id = drive.create_folder(folder, parent_folder_id, filepath, ThreadId)
                parent_folder_name = parent_folder_name.rstrip(os.sep) + os.sep + folder
                drive.folder_id_dict[parent_folder_name] = parent_folder_id
    else:
        parent_folder_id = drive.folder_id_dict[path_name]
    return parent_folder_id


def upload_file(path, filepath, ThreadId):
    local.filepath = filepath
    local.set_time = time.perf_counter()
    local.realpath = os.path.join(path, local.filepath)
    # 创建目录
    locker.acquire()
    local.parent_folder_id = get_parent_folder_id(R_PATH, local.filepath, ThreadId)
    locker.release()
    # 创建上传
    try:
        if not drive.search(local.filepath, local.parent_folder_id, ThreadId):
            print(f'Thread-{ThreadId} 正在加载【{filepath}】')
            load_file(local.filepath, local.realpath)
            local.create_post_json = drive.create(local.hash, local.filename, local.filesize, local.parent_folder_id, ThreadId)
            if 'rapid_upload' in local.create_post_json and local.create_post_json['rapid_upload']:
                print_success(f'Thread-{ThreadId}【{local.filepath}】秒传成功！消耗{time.perf_counter() - local.set_time}')
                return True
            local.upload_url = local.create_post_json['part_info_list'][0]['upload_url']
            local.file_id = local.create_post_json['file_id']
            local.upload_id = local.create_post_json['upload_id']
            # 上传
            drive.upload(local.upload_url, local.realpath, ThreadId)
            # 提交
            return drive.complete(local.file_id, local.upload_id, local.filename, local.start_time,ThreadId)
        else:
            print_success(f'Thread-{ThreadId} 发现【{local.filepath}】，已跳过。消耗{time.perf_counter() - local.set_time}')
            return True
    except Exception as e:
        print_error(local.realpath)
        print_error(e)
        time.sleep(60)
        return upload_file(L_PATH, file, ThreadId)


StartTime = time.time()
# 配置信息
try:
    with open(os.getcwd() + '/config.json', 'rb') as f:
        config = json.loads(f.read())
        REFRESH_TOKEN = config.get('REFRESH_TOKEN')
        DRIVE_ID = config.get('DRIVE_ID')
        # 启用多线程
        MULTITHREADING = bool(config.get('MULTITHREADING'))
        # 线程池最大线程数
        MAX_WORKERS = config.get('MAX_WORKERS')
except Exception as e:
    print_error('请配置好config.json后重试')
    raise e


if len(sys.argv) == 3:
    # 目录上传
    if os.path.isdir(sys.argv[1]):
        count_files = 0
        # 上传一级目录下的文件
        L_PATH = format_path(sys.argv[1])
        R_PATH = format_path(sys.argv[2])
        drive = AliyunDrive(DRIVE_ID, R_PATH, REFRESH_TOKEN)
        drive.token_refresh()
        for file in os.listdir(L_PATH):
            if os.path.isfile(os.path.join(L_PATH, file)):
                workQueue.put(file)
                count_files += 1
        if MULTITHREADING:
            threads = []
            exitFlag = False
            for i in range(MAX_WORKERS):
                a_thread = myThread(i, L_PATH, workQueue)
                a_thread.start()
                threads.append(a_thread)
            while not workQueue.empty():
                pass
            exitFlag = True
            for th in threads:
                th.join()
        else:
            while not workQueue.empty():
                file = workQueue.get()
                upload_file(L_PATH, file, 0)
        print('Next Folder')

        for root, dirs, files in os.walk(sys.argv[1], topdown=True):
            # 上传嵌套目录下的文件
            for dir in dirs:
                # 重定位本地待上传目录
                lpath = os.path.join(root, dir)
                L_PATH = format_path(lpath)
                # 保持远程目录与本地目录结构相同
                full_rpath = sys.argv[2] + os.sep + lpath.replace(sys.argv[1], '').lstrip(os.sep)
                R_PATH = format_path(full_rpath)
                file_list = []
                for file in os.listdir(lpath):
                    fullpath = os.path.join(L_PATH, file)
                    if os.path.isfile(fullpath):
                        workQueue.put(file)
                        count_files += 1
                if not workQueue.empty():
                    print_info(f'正在上传{L_PATH}')
                    if MULTITHREADING:
                        exitFlag = False
                        threads = []
                        for i in range(MAX_WORKERS):
                            a_thread = myThread(i, L_PATH, workQueue)
                            a_thread.start()
                            threads.append(a_thread)
                        while not workQueue.empty():
                            pass
                        exitFlag = True
                        for th in threads:
                            th.join()
                    else:
                        while not workQueue.empty():
                            file = workQueue.get()
                            upload_file(L_PATH, file, 0)
                print('Next Folder')
    else:
        # 单文件上传
        L_PATH = os.path.dirname(sys.argv[1])
        R_PATH = format_path(sys.argv[2])
        drive = AliyunDrive(DRIVE_ID, R_PATH, REFRESH_TOKEN)
        drive.token_refresh()
        upload_file(L_PATH, os.path.basename(sys.argv[1]))
        count_files = 1
else:
    print('请正确输入参数后再运行')
    exit()


print(f'''=======================================================
任务开始于{date(StartTime)},结束于{date(time.time())}
共完成{count_files}个文件
耗时{round(((time.time() - StartTime) / 60), 2)}分钟
=======================================================''')