#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from elasticsearch import Elasticsearch
import requests
import json
import os


def search_ng_devname():
    '''返回公司ng设备列表，只能获取设备名'''
    url = 'http://cmm.imp.chinacache.com:50031/api/hope/ng_list'
    #url = 'http://101.251.97.90:50031/api/hope/ng_list'
    res = requests.get(url)
    result = res.json()['data']
    devname = []
    for devname_info in result:
        if devname_info['status'] == 'OPEN':
            devname.append(devname_info['device_name'])
    return devname

def search_ng_ip(Devname):
    '''根据返回ng设备名列表，从cms查询ip返回'''
    requests.packages.urllib3.disable_warnings()
    url = 'https://rcmsapi.chinacache.com/device/%s' % Devname
    Devname_list = ','.join(Devname)
    #url = 'https://223.202.203.16/multidevice/%s' % Devname_list
    res = requests.get(url,verify=False)
    devAdmin_info_list = res.json()
    devAdminIP_list = []
    for IP in devAdmin_info_list:
        devAdminIP_list.append(IP['devAdminIP'])
    return devAdminIP_list

if __name__=='__main__':
    ng_ip_file = open('/var/www/html/amazing/All_devs/ngip_list',"a+")
    old_ng_ip_list = [i.rstrip('\n') for i in ng_ip_file.readlines()]
    devAdmin_name = search_ng_devname()
    ng_ip_list = search_ng_ip(devAdmin_name)
    for ip_info in ng_ip_list:
        if ip_info not in old_ng_ip_list:
            ng_ip_file.write(ip_info+'\n')
    ng_ip_file.close()
    '''查找大网所有设备ip'''
    es = Elasticsearch(['http://223.202.204.189:9200/'])
    with open('/var/www/html/amazing/All_devs/Alldevs','w') as fn:
        product = 'BRE_DL.*|BRE_WEB.*|BRE_GAD.*|BRE_MSO.*'
        res = es.search(index='ccdevice', doc_type='server', body={"size": 99999, "query": {"bool": {"must": [{"regexp": {"mrtg": "{}".format(product)}}, {"match_phrase": {"rcms_status": "OPEN"}}]}}})['hits']['hits']
        for i in res:
            fn.write(i['_source']['ip']+'\n')

    cmd = '''cat /var/www/html/amazing/All_devs/Alldevs /var/www/html/amazing/All_devs/ngip_list|sort -u > /var/www/html/amazing/All_devs/result '''
    os.system(cmd)