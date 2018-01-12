#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 20/12/2017 16:12
# @Author  : yao.liu
# @File    : 61run2.py

import requests
import hashlib

def url_md5(url,ip_port):
    url_compare_result_dict = {'gzip':'','ungzip':''}
    requests.packages.urllib3.disable_warnings()
    proxies = {'http':'{0}'.format(ip_port)}
    if url.split(':')[0] == 'http' :
        res_gzip = requests.get(url, proxies=proxies, headers={'Accept-Encoding': 'gzip'})
        res = requests.get(url,proxies=proxies)
    else:
        uri = url.split('/',3)[3]
        host = url.split('/',3)[2]
        url = 'https://{0}/{1}'.format(ip_port,uri)
        res_gzip = requests.get(url, verify=False, headers={'Accept-Encoding': 'gzip','Host':host})
        res = requests.get(url, verify=False,headers={'Host':host})
    try:
        res.raise_for_status()
    except:
        print u'抓取非200状态码提醒：{0} code {1}'.format(url,res.status_code).encode('utf8')
    '''非压缩MD5'''
    md5check = hashlib.md5()
    md5check.update(res.content)
    url_compare_result_dict['ungzip'] = md5check.hexdigest()
    '''压缩MD5'''
    md5check = hashlib.md5()
    md5check.update(res_gzip.content)
    url_compare_result_dict['gzip'] = md5check.hexdigest()
    return url_compare_result_dict

Compare_url = {'https://c1-q.mafengwo.net/s10/M00/ED/F6/wKgBZ1mKv5iAdqYCAAG3C6S4TaQ813.png': {'180.153.126.76': {'gzip': '', 'ungzip': ''}, '14.215.89.135': {'gzip': '', 'ungzip': ''}}}
for key, vaule in Compare_url.iteritems():
    url = key
    print vaule
    for ip in vaule.keys():
        url_compare_result_dict = url_md5(url, ip)
        vaule[ip]['gzip'] = url_compare_result_dict['gzip']
        vaule[ip]['ungzip'] = url_compare_result_dict['ungzip']
print  Compare_url
