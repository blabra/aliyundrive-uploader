## 阿里云盘上传脚本

* Author：李小恩
* Github：https://github.com/Hidove/aliyundrive-uploader

> 如有侵权，请联系我删除
> 
> 禁止用于非法用途，违者后果自负


## 自用小修改
>
> 添加了防止重复上传的小功能(此功能对形如【1.png】这类的简单名字的文件效果并不好)
>
> 保持本地目录结构上传
>
> 实验性多线程（开启多线程程序将保持占满一个核心，单核机慎用)
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
  "MULTITHREADING": false,
  "MAX_WORKERS": 5
}
```
| 参数             | 注释                              | 值              |   |
|----------------|---------------------------------|----------------|---|
| REFRESH_TOKEN  | 阿里云盘刷新的token                 |                |   |
| DRIVE_ID       | 阿里云盘驱动ID，目前不知道做何使用的，可能后续官方有新想法吧 |                |   |
| MULTITHREADING | 实验性多线程| true/false     |   |
| MAX_WORKERS    | 线程池最大线程数，请根据自己机器填写              | 5              |   |

> PS: 多线程对CPU单核性能要求较高，请谨慎拉高线程
>
### 运行

> 多文件上传
```shell
python3 main.py
```
```shell
python3 main.py 本地待上传目录 云端目标目录

python3 main.py /localdir/localdir2 /root（远程根目录）

python3 main.py /localdir/localdir2 RemoteDir/Remotedir2（位于根目录下的目录）
```
> 单文件上传

```shell
python3 main.py /www/lixiaoen.jpg 远程目标目录
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
