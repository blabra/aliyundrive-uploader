## 阿里云盘上传脚本

* Author：李小恩
* Github：https://github.com/Hidove/aliyundrive-uploader

> 如有侵权，请联系我删除
> 
> 禁止用于非法用途，违者后果自负


## 自用小修改
>
> 添加了防止重复上传的小功能
>
> 自动移动已完成文件（路径：本地被上传目录/文件所在目录下的finish目录），防止出错后反复上传浪费时间
>
> 多线程功能已被暂时禁用
>
> 发生网络错误后等待60秒自动重试
## 环境要求
* python3

## 使用方法
### 安装
```shell
git clone https://github.com/blabra/aliyundrive-uploader.git
cd aliyundrive-uploader
pip install -r requirements.txt
```

如果执行`pip install`时提示`-bash: pip: command not found`
就是`pip`命令没有安装，执行下方命令安装即可，然后再执行即可

```shell
wget https://bootstrap.pypa.io/get-pip.py
python3 get-pip.py
```

* 重命名`example.config.json`为`config.json`
* 填写好`config.json`的内容

![](https://z3.ax1x.com/2021/03/27/6zB8JA.png)

```json
{
  "REFRESH_TOKEN": "refresh_token",
  "DRIVE_ID": "drive_id",
  "ROOT_PATH": "网盘目录",
  "FILE_PATH": "D:\\Pictures\\",
  "MULTITHREADING": false,
  "MAX_WORKERS": 5
}
```
| 参数             | 注释                              | 值              |   |
|----------------|---------------------------------|----------------|---|
| REFRESH_TOKEN  | 阿里云盘刷新的token                 |                |   |
| DRIVE_ID       | 阿里云盘驱动ID，目前不知道做何使用的，可能后续官方有新想法吧 |                |   |
| ROOT_PATH      | 云端目标目录                        |    我的照片      |   |
| FILE_PATH      | 本地文件夹目录，填写绝对路径                    | D:\\Pictures\\ |   |
| MULTITHREADING | 多线程已被禁用| true/false     |   |
| MAX_WORKERS    | 线程池最大线程数，请根据自己机器填写              | 5              |   |

> PS:如使用多线程上传，多任务并发，可能会造成网盘创建多个相同目录的问题，事后请自行检查删除
> PS:原版多线程会导致同个文件被多个线程同时上传造成文件重复，重复个数为线程数，因而禁用
### 运行

> 多文件上传
```shell
python3 main.py
```
```shell
python3 main.py 本地待上传目录 云端目标目录(根目录请输入'/root')
```
> 单文件上传

```shell
python3 main.py /www/lixiaoen.jpg
```
## 更新
```shell
cd ~/aliyundrive-uploader
git fetch --all 
git reset --hard origin/master 
git pull
```
## 文件解读

* `config.json` 
  * 脚本配置文件
* `task.json`
  * 脚本上传任务记录文件
* `/log`
  * 脚本执行记录

## 支持
> 觉得写得不错可以给我打赏哦

![](https://z3.ax1x.com/2021/03/26/6Xh5ex.md.png)