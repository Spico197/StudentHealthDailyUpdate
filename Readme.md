# 苏州大学学生健康情况每日自动打卡脚本

- 脚本自动获取上次打卡的信息，并作为本次打卡信息进行填报
- 脚本为定时脚本，可自定义修改打卡时间。若挂在服务器后台，则可实现每日自动打卡
- 脚本提供了登陆认证的功能，不需要手动获取Cookies，但是需要用户提供学号和密码（第33、35行）
- 脚本提供了邮件提醒的功能，需要用户将第37行的`email_notice`改为`True`，并填写邮件客户端的相关信息

## 安装

- 要求
    - Python3
    - requests库：用于模拟http请求
    - apscheduler库：用于crontab任务脚本

```bash
$ pip install apscheduler requests
```

## 使用

1. 修改脚本31-43行的配置信息
2. 启动脚本

```bash
$ python StudentHealthDailyUpdate.py
```

## 免责声明

- 本脚本不保证始终可用，请及时手动检查
- 本脚本仅作为学习交流使用，请勿用于商业用途
- 由于使用本脚本所产生的一切后果由用户自行承担
- 疫情凶猛，若有身体不适或地点转移，请及时通过相关渠道向校方上报

## 更新说明

- v2：解决同一天多次打卡时打卡失败的问题