#!/opt/hopeservice/.venv/bin/python
# -*- coding: UTF-8 -*-
# @Time    : 27/02/2018 10:00
# @Author  : yao.liu
# @File    : cname_detect.py
# version  : 1.0

import commands
import sys
import requests
import re
from datetime import datetime

reload(sys)
sys.setdefaultencoding('utf8')

def cname_check(domain):
    '''dig测试域名'''
    cmd = ' dig @8.8.8.8 {0} '.format(domain)
    res = commands.getoutput(cmd)
    match = re.compile('ccgslb|chinacache',res)
    if match:
        return True
    else:
        return None

def sendmail(content):
    '''发送告警邮件'''
    #填写收件人
    data = {'tos': 'yao.liu@chinacache.com',
            'subject': '[devops] cname_detect -域名已切回蓝汛加速',
            'content': '{}'.format(content)}
    res = requests.post('http://223.202.201.32:8700/email', data=data)

if __name__ == '__main__':
    time_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    domain_file = sys.argv[1]
    with open(domain_file,'r') as fn:
        for i in fn.readlines():
            if cname_check(i):
                content = '''<meta http-equiv="Content-Type" content="text/html; charset=utf-8"><b>您好【{0}】:</b><table border="1"> \
                <tbody><tr> <td><div style="text-align:center;margin:0;" align="center"><b>域名切回至蓝汛服务</b></td> </tr><td>{1}'''.format(time_now,i)
                sendmail(content)

