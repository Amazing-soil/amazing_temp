#!/opt/hopeservice/.venv/bin/python
# -*- coding: utf-8 -*-
# @Time    : 27/11/2017 11:12
# @Author  : yao.liu
# @File    : test.py

import json
import requests
import commands
import datetime,time
import sys
import re
import os
import getopt
import signal
reload(sys)
sys.setdefaultencoding('utf8')

def check_squid_conf():
    '''检查全局被动压缩配置，ok即存在'''
    gzip_mod_check = commands.getoutput('grep -q mod_header_combination /usr/local/squid/etc/squid.conf && echo ok')
    '''检查全局0方向是否配置删除特殊头，4即配置完整'''
    del_0_header_check = commands.getoutput('egrep -c "(mod_header 0 del).*(allow all)" /usr/local/squid/etc/squid.conf')
    '''检查所需日志特殊字段是否配置，ok即配置'''
    squid_log_check = commands.getoutput('egrep "(logformat squid_custom_log)" /usr/local/squid/etc/squid.conf|grep -q -e "$AE" -e "$PB" && echo ok')
    if gzip_mod_check == 'ok':
        print u'全局配置被动压缩，压缩非压缩存两份，注意同文件会miss两次'.encode('utf8')
    else:
        print u'全局未配置被动压缩，压缩非压缩存一份，可能存在缓存问题，请确认功能需求'.encode('utf8')
    if del_0_header_check == '4':
        print u'设备已全局配置删除0方向影响缓存的特殊头'.encode('utf8')
    else:
        print u'设备未配置删除0方向影响缓存的特殊头，建议尝试配置删除0方向的Cache-Control If-None-Match If-Match If-Unmodified-Since'.encode('utf8')
    if squid_log_check == 'ok':
        return 1
    else:
        return 0

LineItem = {}
special_log = {}
num_url = {}
with open('C:\\Users\\yao.liu\\Desktop\\test.log','r') as fn:
    for i in fn.readlines():
        LineItem['Url'] = i.split()[6].split('?')[0]
        # 特殊日志字段收集，对应url
        if not special_log.has_key(LineItem['Url']):
            special_log[LineItem['Url']] = {'$AE':{'gzip': 0, 'ungzip': 0},'$PB':[]}
        for j in i.split('@in#(')[1].split('^~'):
            if 'PB' in j:
                if '-' not in j:
                    hash_squid = j.split('.')[1]
                    if hash_squid not in special_log[LineItem['Url']]['$PB']:
                        special_log[LineItem['Url']]['$PB'].append(hash_squid)
            if 'AE=' in j:
                if j.split('=')[1] == 'gzip':
                    special_log[LineItem['Url']]['$AE']['gzip'] += 1
                else:
                    special_log[LineItem['Url']]['$AE']['ungzip'] += 1
        # url数量统计
        if num_url.get(LineItem['Url']) is None:
            num_url[LineItem['Url']] = 0
        num_url[LineItem['Url']] += 1

#url数量 top 5
print u'请求url次数 TOP 5 :'.encode('utf8')
top_num_url = sorted(num_url.iteritems(), key=lambda d: d[1], reverse=True)[:5]
for item in top_num_url:
    # print special_log[item[0]]['$AE']['gzip'],special_log[item[0]]['$AE']['ungzip']
    # print len(special_log[item[0]]['$PB'])
    print u'\t{0}\t{1}\t{2:>5}\t{3}'.format('次数','压缩\非压缩','hash个数','URL').encode('utf8')
    for item in top_num_url:
        print u'\t{0:<10}\t{1}\{2:<7}\t{3:<5}\t{4}'.format(item[1],
                                                           special_log[item[0]]['$AE']['gzip'],
                                                           special_log[item[0]]['$AE']['ungzip'],
                                                           len(special_log[item[0]]['$PB']),item[0])
