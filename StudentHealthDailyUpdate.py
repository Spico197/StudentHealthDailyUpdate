import re
import sys
import json
import time
import random
import hashlib
import logging
import smtplib
import traceback
from pytz import timezone
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import requests
from apscheduler.schedulers.blocking import BlockingScheduler

logger = logging.getLogger('stu_health_check')
logger.setLevel(logging.INFO)
log_path = 'stu_health_check.log'
fh = logging.FileHandler(log_path)
fh.setLevel(logging.INFO)
fmt = "[%(asctime)-15s]-%(levelname)s-%(filename)s-%(lineno)d-%(process)d: %(message)s"
datefmt = "%a %d %b %Y %H:%M:%S"
formatter = logging.Formatter(fmt, datefmt)
fh.setFormatter(formatter)
logger.addHandler(fh)
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)

# ---------------------------------------------
## 学号
student_id = "2019********"
## 密码
password = "suda********"
## 是否开启邮件提醒
email_notice = False # 若不开启邮件提醒，则下列信息无需填写
email_address = "*******@163.com"
email_token = "*******" # 授权码或密码
email_host = 'smtp.163.com' # 邮箱发信地址（SMTP服务器）
email_port = 465 # 邮箱发信端口（SMTP服务器端口）
email_receiver = "*********@qq.com" # 收信人地址
# ---------------------------------------------


def md5(password):
    hl = hashlib.md5()
    hl.update(password.encode(encoding='utf-8'))
    return hl.hexdigest()


def send_email(html_message):
    s = smtplib.SMTP_SSL(host=email_host, port=email_port)
    s.login(email_address, email_token)

    msg = MIMEMultipart()
    msg['From'] = email_address
    msg['To'] = email_receiver
    msg['Subject']="每日健康自动打卡提醒"
    msg.attach(MIMEText(html_message, 'html'))
    s.send_message(msg)
    del msg
    s.quit()


def auto_check():
    try:
        logger.info(' ------------------------- START: {} -------------------------'.format(datetime.now()))
        payload = {
            "IDButton": "Submit", 
            "IDToken1": student_id,
            "IDToken2": md5(password), 
        }
        url = "http://myauth.suda.edu.cn/default.aspx?app=sswsswzx2"
        recurrent_time = 50
        count = 0
        authorised_flag = False
        while count < recurrent_time:
            try:
                sess = requests.Session()
                res = sess.get(url)
                obj = re.search(r'.*method="post" url="(.*?)".*', res.text)
                url = obj.group(1)
                url = "http://ids1.suda.edu.cn" + url
                res = sess.post(url, data=payload)
                authorised_flag = True
                break
            except KeyboardInterrupt:
                raise KeyboardInterrupt
            except Exception as err:
                logger.info(traceback.format_exc())
                time.sleep(2+random.random())
            finally:
                count += 1
        if not authorised_flag:
            raise RuntimeError("authorise failed!")
        logger.info(' ------------------------- {} -------------------------'.format("authorised"))
        res = sess.get("http://aff.suda.edu.cn")
        url = re.findall(r'window\.location\.href="(.*?)"', res.text)[-1]
        res = sess.get(url)
        uid = re.search(r".*?/_ids/parsePicServlet\?userId=(.*?).*", res.text).group(1)

        url = "http://aff.suda.edu.cn/mobile/identityServer?targetUrl=http%253A%252F%252Feos.suda.edu.cn%252Fdefault%252Fwork%252Fsuda%252Fjkxxtb%252Fjkxxcj.jsp&appKey=com.sudytech.suda.xxhjsyglzx.jkxxcj.&appload=0"
        res = sess.get(url)
        with open("test.html", "w") as fout:
            fout.write(res.text)
        logger.info(' ------------------------- {} -------------------------'.format("ready to fill in the form"))
        
        # 填表时间
        now = datetime.now().astimezone(timezone("Asia/Shanghai")).strftime("%Y-%m-%d")
        for day in [1, 0]:
            try:
                yesterday = (datetime.now() - timedelta(days=day)).astimezone(timezone("Asia/Shanghai")).strftime("%Y-%m-%d")
                get_id_url = "http://eos.suda.edu.cn/default/work/suda/jkxxtb/com.sudytech.portalone.base.db.queryBySqlWithoutPagecond.biz.ext"
                payload = {"params":{"empcode":student_id, "tbrq":yesterday},"querySqlId":"com.sudytech.work.suda.jkxxtb.jkxxtb.queryToday"}
                headers = {
                    "Accept": "*/*",
                    "Accept-Encoding": "gzip, deflate",
                    "Accept-Language": "zh-CN,zh;q=0.9",
                    "Connection": "keep-alive",
                    "Content-Type": "text/json",
                    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.106 Safari/537.36",
                    "X-Requested-With": "XMLHttpRequest",
                }
                response = sess.post(get_id_url, data=json.dumps(payload), headers=headers)
                content = response.json()
                content = content['list'][0]
                break
            except KeyboardInterrupt:
                raise KeyboardInterrupt
            except Exception as err:
                logger.info(traceback.format_exc())
            
        if response.status_code != 200:
            raise RuntimeError("data abtaining failed!")
        
        another_content = dict()
        for key in content.keys():
            another_content[key.lower()] = content[key]
        logger.info(' ------------------------- {} -------------------------'.format("get data"))

        tjsj = datetime.now().astimezone(timezone("Asia/Shanghai")).strftime("%Y-%m-%d %H:%M")
        content = {
            "id": another_content['id'],
            "sqrid": another_content['sqrid'],
            "sqbmid": another_content['sqbmid'],
            "rysf": another_content['rysf'],
            "sqrmc": another_content['sqrmc'],
            "gh": another_content['gh'],
            "sfzh": another_content['sfzh'],
            "sqbmmc": another_content['sqbmmc'],
            "xb": another_content['xb'],
            "jgshi": another_content['jgshi'],
            "jgshen": another_content['jgshen'],
            "nl": another_content['nl'],
            "lxdh": another_content['lxdh'],
            "xjzdz": another_content['xjzdz'],
            "xq": another_content['xq'],
            "xxss": another_content['xxss'],
            "lxsj": another_content['lxsj'],
            "dlqk": another_content['dlqk'],
            "hjxz": another_content['hjxz'],
            "tbrq": now,
            "jrtw": another_content['jrtw'],
            "jkzk": another_content['jkzk'],
            "xrywz": another_content['xrywz'],
            "jtdzshi": another_content['jtdzshi'],
            "jtdzshen": another_content['jtdzshen'],
            "jtdz": another_content['jtdz'],
            "sfyxglz": another_content['sfyxglz'],
            "yxgcts": another_content['yxgcts'],
            "glfs": another_content['glfs'],
            "zzjc": another_content['zzjc'],
            "tw": another_content['tw'],
            "mrxz": another_content['mrxz'],
            "ycqkhb": another_content['ycqkhb'],
            "bz": another_content['bz'],
            "_ext": "{}",
            "tjsj": tjsj,
            "__type": "sdo:com.sudytech.work.suda.jkxxtb.jkxxtb.TSudaJkxxtb",
        }
        content = {"entity": content}
        logger.info(content)
        logger.info(' ------------------------- {} -------------------------'.format("post data"))

        info_post_url = "http://eos.suda.edu.cn/default/work/suda/jkxxtb/com.sudytech.portalone.base.db.saveOrUpdate.biz.ext"
        response = sess.post(info_post_url, data=json.dumps(content), headers=headers)
        if response.status_code != 200:
            raise RuntimeError("data update failed!")
        logger.info(response.text)
        res_json = response.json()
        if res_json.get("result", -1) != "1" or res_json['resultEntity']['gh'] != student_id:
            raise RuntimeError("Update failed, get wrong response")
        sess.close()
        if email_notice:
            send_email("每日健康打卡成功")
        logger.info("每日健康打卡成功")
    except KeyboardInterrupt:
        raise KeyboardInterrupt
    except Exception as err:
        if email_notice:
            send_email("每日健康打卡失败：{}".format(err))
        logger.info("每日健康打卡失败：{}".format(err))
    finally:
        logger.info(' ------------------------- END -------------------------')


if __name__ == "__main__":
    scheduler = BlockingScheduler(logger=logger)
    scheduler.add_job(auto_check, 'cron', hour=1, minute=30, next_run_time=datetime.now())
    scheduler.start()
