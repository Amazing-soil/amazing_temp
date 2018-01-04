#!/opt/hopeservice/.venv/bin/python
# -*- coding: utf-8 -*-
# @Time    : 16/11/2017 13:43
# @Author  : yao.liu
# @File    : test.py

import commands
import requests
import json
import sys,os

reload(sys)
sys.setdefaultencoding('utf8')

def log_manage():
    cmd = ''' wget -qO /tmp/sn_channel.sh http://223.202.204.189/amazing/sn_channel.sh|sh /tmp/sn_channel.sh'''
    os.system(cmd)
    #cmd = ''' awk '$2 != "wild." && $4 != "no_detect" && NF == '6'' /var/log/chinacache/detectorigin.log > /tmp/61_tmp.log '''
    cmd = ''' awk '$1 != "wild." && NF == '10' && $1 ~/^[0-9a-zA-Z]/{print "GET",$1,$4,"200","OK",$8}' /tmp/anyhost_need > /tmp/61_tmp.log '''
    os.system(cmd)

def look_for_ip_location(ip):
    '''输入ip返回所属运营商列表'''
    url = 'http://223.202.202.183:12345/iplocation/'
    data = ''' {{ 'source':["online"], 'list':["{0}"] }} '''.format(ip)
    res = requests.post(url,json.dumps(eval(data)))
    operator = res.json()[ip]['online'][0]['name'].split('-')[0]
    return operator

def orign_iscc(ip):
    '''是蓝汛ip返回False,否则返回True'''
    url = 'http://223.202.204.189:81/AACode/isccdevice/'
    data = {'ip':'{0}'.format(ip)}
    res = requests.post(url,data=data)
    return res.json().has_key('msg')

'''结果字典，列表第一个元素为总数，第二个元素为ip_down数,第三个元素为ip_bad数 '''
result_dict = { 'chn':[0,0,0],
                'cnc':[0,0,0],
                'cmn':[0,0,0],
                'other':[0,0,0],
                'sum':[0,0,0]}
ip_list = []
ip_operator = {}
log_manage()
orign_cc = {}
no_cmn_channel = []
with open('/tmp/61_tmp.log','r') as fn:
    for i in fn.readlines():
        ip = i.split()[2]
        '''判断过滤掉源站ip'''
        #if not orign_cc.has_key(ip):
        #    orign_cc[ip] = orign_iscc(ip)
        #if not orign_cc.get(ip):
        result_dict['sum'][0] += 1
        '''ip-运营商字典形成'''
        if not ip_operator.has_key(ip):
            ip_operator[ip] = look_for_ip_location(ip)
        operator = ip_operator[ip]
        '''运营商计数'''
        if result_dict.has_key(operator):
            result_dict[operator][0] += 1
        else:
            result_dict['other'][0] += 1
        '''ip_down 运营商计数'''
        if i.split()[5] == 'ip_down':
            result_dict['sum'][1] += 1
            if result_dict.has_key(operator):
                result_dict[operator][1] += 1
            else:
                result_dict['other'][1] += 1
        '''ip_bad 运营商计数'''
        if i.split()[5] == 'ip_bad':
            result_dict['sum'][2] += 1
            if result_dict.has_key(operator):
                result_dict[operator][2] += 1
            else:
                result_dict['other'][2] += 1
        if operator != 'cmn':
            if i.split()[1] not in no_cmn_channel:
                no_cmn_channel.append(i.split()[1])

with open('/tmp/no_cmn_or_channel.log','w') as fn:
    for i in no_cmn_channel:
        fn.write(i+'\n')
print '存在回上游非移动ip域名列表 >>>>>>>>>>  /tmp/no_cmn_or_channel.log'.encode('utf8')

print '{0:>15}{1:>15}{2:>15}{3:>20}{4:>25}{5:>25}{6:>25}'.format(u'运营商'.encode('utf8'),
                                                           u'源站总数'.encode('utf8'),
                                                           u'down/总数'.encode('utf8'),
                                                           u'bad/总数'.encode('utf8'),
                                                           u'down_bad总数'.encode('utf8'),
                                                           u'down/down_bad总数'.encode('utf8'),
                                                           u'bad/down_bad总数'.encode('utf8'),
                                                            )
for i in result_dict.iterkeys():
    ip_sum = float(result_dict[i][0])
    ip_down = float(result_dict[i][1])
    ip_bad = float(result_dict[i][2])
    ip_bad_down_sum = float(ip_down + ip_bad)
    if ip_sum != 0 and ip_bad_down_sum != 0:
        print '{0:>11}{1:>11}{2:>11}%{3:>15}%{4:>23}{5:>20}%{6:>20}%'.format(i,
                                                               ip_sum,
                                                               round( ip_down / ip_sum,2) * 100,
                                                               round( ip_bad / ip_sum, 2) * 100,
                                                               ip_bad_down_sum,
                                                               round( ip_down / ip_bad_down_sum, 2) * 100,
                                                               round( ip_bad / ip_bad_down_sum, 2) * 100,
                                                              )
