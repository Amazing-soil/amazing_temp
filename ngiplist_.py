#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2/11/2017 22:01
# @Author  : yao.liu
# @File    : ngiplist.py

import requests
import json

'''return ng_list devname list'''
def search_ng_devname():
    #url = 'http://cmm.imp.chinacache.com:50031/api/hope/ng_list'
    url = 'http://101.251.97.90:50031/api/hope/ng_list'
    res = requests.get(url)
    result = res.json()['data']
    devname = []
    for devname_info in result:
        if devname_info['status'] == 'OPEN':
            devname.append(devname_info['device_name'])
    return devname
'''return ip according to devname'''
def search_ng_ip(Devname):
    requests.packages.urllib3.disable_warnings()
    # url = 'https://rcmsapi.chinacache.com/device/%s' % Devname
    Devname_list = ','.join(Devname)
    url = 'https://223.202.203.16/multidevice/%s' % Devname_list
    res = requests.get(url,verify=False)
    devAdmin_info_list = res.json()
    devAdminIP_list = []
    for IP in devAdmin_info_list:
        devAdminIP_list.append(IP['devAdminIP'])
    return devAdminIP_list

if __name__=='__main__':
    ng_ip_file = open('/tmp/ngip_list',"a+")
    old_ng_ip_list = [i.rstrip('\n') for i in ng_ip_file.readlines()]
    devAdmin_name = search_ng_devname()
    ng_ip_list = search_ng_ip(devAdmin_name)
    for ip_info in ng_ip_list:
        if ip_info not in old_ng_ip_list:
            ng_ip_file.write(ip_info+'\n')
    ng_ip_file.close()
    history_log = open('/root/route_switch_history.log',"a+")
    history_log.write('ng_ip_list already update\n')
