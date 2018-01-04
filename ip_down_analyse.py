#!/opt/hopeservice/.venv/bin/python 
# -*- coding: UTF-8 -*-
# @Time    : 13/11/2017 20:00
# @Author  : yao.liu
# @File    : anyhost_ip_detect.py
# version  : 1.1

import commands
import json
import os
import sys
import requests
from datetime import datetime

reload(sys)
sys.setdefaultencoding('utf8')

def find_ipdown_channel():
    '''解析anyhost日志,更新history_info字典'''
    '''判断是否存在/tmp/history_info_log解析字典，并初始化告警记录以外的字典数据，#字典元素内容：域名：{告警记录，是否需要告警，ipdown总次数，频道回源ip总个数}'''
    if os.path.isfile('/tmp/history_info_log'):
        history_info_file = open('/tmp/history_info_log','r')
        history_info = eval(history_info_file.read())
        for i in history_info.iterkeys():
            history_info[i]['channel_count'] = 0
            history_info[i]['ipdown_count'] = 0
    else:
        history_info = {}
    '''处理anyhost日志，分离出所需数据并临时存放在/tmp/anyhost_temp'''
    cmd = ''' awk '$1 != "wild." && $8 != "no_detect" && NF == '10'{sub(/;/,"",$1);print $1,$8}' /var/named/anyhost  > /tmp/anyhost_temp '''

    os.system(cmd)
    '''解析anyhost，更新history_info 标准字典'''
    with open('/tmp/anyhost_temp','r') as fn:
        for i in fn.readlines():
            channel = i.split()[0]
            status = i.split()[1]
            history_info.setdefault(channel,{'channel_count':int(0),'ipdown_count':int(0),'warning':0,'flag':0})
            history_info[channel]['channel_count'] += 1
            if status == 'ip_down':
                history_info[channel]['ipdown_count'] += 1
    for i in history_info.iterkeys():
        if history_info[i]['channel_count'] == history_info[i]['ipdown_count']:
            history_info[i]['warning'] = 1
        else:
            history_info[i]['warning'] = 0
            history_info[i]['flag'] = 0
    return history_info

def warning_channel_seek(history_info):
    '''根据告警规则更新history_info，并返回应该告警频道的列表，同时存放history_info 到/tmp/history_info_log'''
    warning_channel = [ i for i in history_info.iterkeys() if history_info[i]['warning'] == 1 and history_info[i]['flag'] == 0 ]
    for i in warning_channel:
        history_info[i]['flag'] = 1
    history_info_log = open('/tmp/history_info_log', 'w')
    json.dump(history_info, history_info_log)
    return warning_channel

def sendmail(content):
    '''发送告警邮件'''
    data = {'tos': 'yang_gao@chinacache.com,shi.qiu@chinacache.com,yao.liu@chinacache.com,haomiao.zhang@chinacache.com',
            'subject': '[devops] anyhost_ipdown -{}'.format(commands.getoutput('hostname')),
            'content': '{}'.format(content)}
    res = requests.post('http://223.202.201.32:8700/email', data=data)


if __name__ == '__main__':
    time_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open('/tmp/attention_channel', 'r') as fn:
        attention_channel = [ i.strip('\n') + '.' for i in fn.readlines() ]
    channels = [ i for i in warning_channel_seek(find_ipdown_channel()) if i in attention_channel ]
    if len(channels) != 0:
        conent1 = '</td></tr><tr><td>'.join(channels)
        content = '''<meta http-equiv="Content-Type" content="text/html; charset=utf-8"><b>您好,以下域名在【{0}】回源探测全部ip_down:</b><table border="1"> \
        <tbody><tr> <td><div style="text-align:center;margin:0;" align="center"><b>告警域名</b></td> </tr><td>{1}'''.format(time_now,conent1)
        sendmail(content)

