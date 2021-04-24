# -*- coding: utf-8 -*-
# +-------------------------------------------------------------------
# | 阿里云盘API
# +-------------------------------------------------------------------
# | Author: 李小恩 <i@abcyun.cc>
# +-------------------------------------------------------------------
import json
import os
import time

import requests
from tqdm import tqdm

requests.packages.urllib3.disable_warnings()
from UploadChunksIterator import UploadChunksIterator
from common import print_warn, print_info, print_error, print_success


class AliyunDrive:

    def __init__(self, drive_id, root_path, refresh_token, folder_id_dict=None):
        if folder_id_dict is None:
            folder_id_dict = {}
        self.folder_id_dict = folder_id_dict
        self.drive_id = drive_id
        self.root_path = root_path
        self.refresh_token = refresh_token
    

    def search(self, filepath, parent_folder_id, ThreadId):
        post_payload = {
            'drive_id': self.drive_id,
            'limit': 100,
            'order_by': 'updated_at DESC',
            'query': "name match " + f'\"{filepath}\"'
        }
        try:
            search_post = requests.post(
                url='https://api.aliyundrive.com/v2/file/search',
                headers=self.headers,
                data=json.dumps(post_payload),
                verify=False,
                timeout=10
            )
            search_post_json = search_post.json()
            lst = search_post_json['items']
            if not lst:
                return False
            num = 0
            list_num = len(lst) - 1
            while not num > list_num:
                if filepath == lst[num].get('name') and parent_folder_id == lst[num].get('parent_file_id'):
                    return True
                num += 1
            return False
        except Exception as e:
            print_warn(f'Thread-{ThreadId} --【{filepath}】发生错误')
            print_error(e)
            print_warn(f'Thread-{ThreadId} --Step: Search 发生错误，程序将在暂停60秒后继续执行')
            time.sleep(60)
            return self.search(filepath, parent_folder_id, ThreadId)


    def token_refresh(self):
        data = {"refresh_token": self.refresh_token,
                "grant_type": "refresh_token"
                }
        try:
            post = requests.post(
                url='https://websv.aliyundrive.com/token/refresh',
                data=json.dumps(data),
                headers={
                'content-type': 'application/json;charset=UTF-8'
                },
                verify=False,
                timeout=10
            )
            try:
                post_json = post.json()
                # 刷新配置中的token
                with open(os.getcwd() + '/config.json', 'rb') as f:
                    config = json.loads(f.read())
                config['REFRESH_TOKEN'] = post_json['refresh_token']
                with open(os.getcwd() + '/config.json', 'w') as f:
                    f.write(json.dumps(config))
                    f.flush()
            except Exception as e:
                print_warn('refresh_token已经失效')
                raise e
            access_token = post_json['access_token']
            self.headers = {
                'authorization': access_token
            }
            self.refresh_token = post_json['refresh_token']
            return True
        except Exception as e1:
            print_error(e1)
            time.sleep(60)
            return self.token_refresh()


    def create(self, hash, filename, filesize, parent_file_id, ThreadId):
        create_data = {
            "auto_rename": True,
            "content_hash": hash,
            "content_hash_name": 'sha1',
            "drive_id": self.drive_id,
            "hidden": False,
            "name": filename,
            "parent_file_id": parent_file_id,
            "type": "file",
            "size": filesize
        }
        try:
            create_post = requests.post(
                'https://api.aliyundrive.com/v2/file/create',
                data=json.dumps(create_data),
                headers=self.headers,
                verify=False,
                timeout=10
            )
            create_post_json = create_post.json()
            if create_post_json.get('code') == 'AccessTokenInvalid':
                if self.token_refresh():
                    return self.create(hash, filename, filesize, parent_file_id, ThreadId)
                print(create_post_json.get('code'))
                print_error('无法刷新AccessToken，准备退出。Step: Create')
                exit()
            return create_post_json
        except Exception as e:
            print_warn(f'Thread-{ThreadId} --【{filename}】发生错误')
            print_error(e)
            print_warn(f'Thread-{ThreadId} --Step: Create 发生错误，程序将在暂停60秒后继续执行')
            time.sleep(60)
            return self.create(hash, filename, filesize, parent_file_id, ThreadId)


    def upload(self, upload_url, realpath, ThreadId):
        with open(realpath, "rb") as f:
            total_size = os.fstat(f.fileno()).st_size
            f = tqdm.wrapattr(f, "read", desc=f'Thread-{ThreadId}-正在上传', miniters=1, total=total_size, ascii=True)
            with f as f_iter:
                res = requests.put(
                    url=upload_url,
                    data=UploadChunksIterator(f_iter, total_size=total_size),
                    verify=False
                )
                res.raise_for_status()


    def complete(self, file_id, upload_id, filename, start_time, ThreadId):
        complete_data = {
            "drive_id": self.drive_id,
            "file_id": file_id,
            "upload_id": upload_id
        }
        try:
            complete_post = requests.post(
                url='https://api.aliyundrive.com/v2/file/complete',
                data=json.dumps(complete_data),
                headers=self.headers,
                verify=False,
                timeout=10
            )
            complete_post_json = complete_post.json()
            if complete_post_json.get('code') == 'AccessTokenInvalid':
                if self.token_refresh():
                    return self.complete(file_id, upload_id, filename, start_time, ThreadId)
                print_error('无法刷新AccessToken，准备退出。Step: Complete')
                print(complete_post_json.get('code'))
                exit()
            s = time.time() - start_time
            if 'file_id' in complete_post_json:
                print_success(f'Thread-{ThreadId} --【{filename}】上传成功！消耗{s}秒')
                return True
            else:
                print_warn(f'Thread-{ThreadId} --【{filename}】上传失败！消耗{s}秒')
                return False
        except Exception as e:
            print_warn(f'Thread-{ThreadId} --【{filename}】发生错误')
            print_error(e)
            print_warn(f'Thread-{ThreadId} --Step: Complete 发生错误，程序将在暂停60秒后继续执行')
            time.sleep(60)
            return self.complete(file_id, upload_id, filename, start_time, ThreadId)


    def create_folder(self, folder_name, parent_folder_id, filepath, ThreadId):
        create_data = {
            "drive_id": self.drive_id,
            "parent_file_id": parent_folder_id,
            "name": folder_name,
            "check_name_mode": "refuse",
            "type": "folder"
        }
        try:
            create_post = requests.post(
                'https://api.aliyundrive.com/v2/file/create',
                data=json.dumps(create_data),
                headers=self.headers,
                verify=False,
                timeout=10
            )
            create_post_json = create_post.json()
            if create_post_json.get('code') == 'AccessTokenInvalid':
                if self.token_refresh():
                    return self.create_folder(folder_name, parent_folder_id, filepath, ThreadId)
                print_error('无法刷新AccessToken，准备退出。Step: Create Folder')
                print(create_post_json.get('code'))
                exit()
            return create_post_json.get('file_id')
        except Exception as e:
            print_warn(f'Thread-{ThreadId} --【{filepath}】发生错误')
            print_error(e)
            print_warn(f'Thread-{ThreadId} --Step: Create_Folder 发生错误，程序将在暂停60秒后继续执行')
            time.sleep(60)
            return self.create_folder(folder_name, parent_folder_id, filepath, ThreadId)
