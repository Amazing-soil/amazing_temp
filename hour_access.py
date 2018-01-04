#!/opt/hopeservice/.venv/bin/python
# -*- coding: utf-8 -*-
# @Time    : 15/11/2017 18:40
# @Author  : yao.liu
# @File    : test.py

from datetime import datetime
import os

time_log = datetime.now().strftime('%Y%m%d%H')
cmd = '''zcat /data/proclog/log/squid/access/*{0}* |awk '{{ print $7}}'|awk -F "/" '{{print $3}}'|sort -u >/tmp/attention_channel'''.format(time_log)
os.system(cmd)

if datetime.now().strftime('%H') == '00':
    os.system(" /bin/rm -f /tmp/history_info_log ")
