# -*- coding: utf-8 -*-
# +-------------------------------------------------------------------
# | 阿里云盘上传Python3脚本
# +-------------------------------------------------------------------
# | Author: 李小恩 <i@abcyun.cc>
# +-------------------------------------------------------------------
import json
import os
import sys
import time
# from concurrent.futures import ThreadPoolExecutor, as_completed
from hashlib import sha1
from common import print_warn, print_error, print_info, print_success, date, format_path


if __name__ != '__main__':
    exit()

from AliyunDrive import AliyunDrive


def get_parent_folder_id(root_path, filepath):
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
                parent_folder_id = drive.create_folder(folder, parent_folder_id)
                parent_folder_name = parent_folder_name.rstrip(os.sep) + os.sep + folder
                drive.folder_id_dict[parent_folder_name] = parent_folder_id
    else:
        parent_folder_id = drive.folder_id_dict[path_name]
    return parent_folder_id


def upload_file(path, filepath):
    realpath = os.path.join(path, filepath)
    drive.load_file(filepath, realpath)
    # 创建目录
    parent_folder_id = get_parent_folder_id(R_PATH, filepath)
    # 创建上传
    try:
        if not drive.search(parent_folder_id):
            create_post_json = drive.create(parent_folder_id)
            if 'rapid_upload' in create_post_json and create_post_json['rapid_upload']:
                print_success(f'【{drive.filename}】秒传成功！消耗{time.time() - drive.start_time}')
                return True
            upload_url = create_post_json['part_info_list'][0]['upload_url']
            file_id = create_post_json['file_id']
            upload_id = create_post_json['upload_id']
            # 上传
            drive.upload(upload_url)
            # 提交
            return drive.complete(file_id=file_id, upload_id=upload_id)
        else:
            print_success(f'发现【{drive.filename}】，已跳过。消耗{time.time() - drive.start_time}')
            return True
    except Exception as e:
        print_error(e)
        time.sleep(60)
        return L_PATH, file


StartTime = time.time()
# 配置信息
try:
    with open(os.getcwd() + '/config.json', 'rb') as f:
        config = json.loads(f.read())
        REFRESH_TOKEN = config.get('REFRESH_TOKEN')
        DRIVE_ID = config.get('DRIVE_ID')
        # 启用多线程
        # MULTITHREADING = False  # bool(config.get('MULTITHREADING'))
        # 线程池最大线程数
        # MAX_WORKERS = config.get('MAX_WORKERS')
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
                upload_file(L_PATH, file)
                count_files += 1

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
                        file_list.append(file)
                if file_list != []:
                    drive = AliyunDrive(DRIVE_ID, R_PATH, REFRESH_TOKEN)
                    drive.token_refresh()
                    print_info(f'正在上传{L_PATH}')
                    for file in file_list:
                        upload_file(L_PATH, file)
                        count_files += 1
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

# 
print(f'''=======================================================
任务开始于{date(StartTime)},结束于{date(time.time())}
共完成{count_files}个文件
耗时{round(((time.time() - StartTime) / 60), 2)}分钟
=======================================================''')

'''

多线程有bug，请勿使用

'''
# pool_executor = ThreadPoolExecutor(MAX_WORKERS)
# if MULTITHREADING:
#     with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
#         future_list = []
#         for file in file_list:
#             tmp = {
#                 "filepath": file,
#                 "upload_time": 0
#             }
#             hexdigest = sha1(file.encode('utf-8')).hexdigest()
#             if not hexdigest in task:
#                 task[hexdigest] = tmp
#                 if task[hexdigest]['upload_time'] <= 0:
#                     # 提交线程
#                     future = executor.submit(upload_file, L_PATH, file)
#                     future_list.append(future)
#             else:
#                 print_warn(os.path.basename(file) + ' 已上传，无需重复上传')

#         for res in as_completed(future_list):
#             if res.result():
#                 task[hexdigest]['upload_time'] = time.time()
#                 save_task(task)
#             else:
#                 print_error(os.path.basename(file) + ' 上传失败')
# else:
#     for file in file_list:
#         tmp = {
#             "filepath": file,
#             "upload_time": 0
#         }
#         hexdigest = sha1(file.encode('utf-8')).hexdigest()
#         if not hexdigest in task:
#             task[hexdigest] = tmp
#             if task[hexdigest]['upload_time'] <= 0:
#                 if upload_file(L_PATH, file):
#                     task[hexdigest]['upload_time'] = time.time()
#                     save_task(task)
#                 else:
#                     print_error(os.path.basename(file) + ' 上传失败')
#         else:
#             print_warn(os.path.basename(file) + ' 已上传，无需重复上传')


