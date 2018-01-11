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
    proxies = {'http':'http://{0}'.format(ip_port),'https':'https://{0}'.format(ip_port)}
    '''非压缩MD5'''
    res = requests.get(url,verify=False,proxies=proxies)
    print res.status_code
    md5check = hashlib.md5()
    md5check.update(res.content)
    url_compare_result_dict['ungzip'] = md5check.hexdigest()
    '''压缩MD5'''
    res_gzip = requests.get(url, verify=False, proxies=proxies, headers={'Accept-Encoding': 'gzip'})
    print res_gzip.status_code
    md5check = hashlib.md5()
    md5check.update(res_gzip.content)
    url_compare_result_dict['gzip'] = md5check.hexdigest()

    return url_compare_result_dict

Compare_url = {'http://ms2.aginomoto.com/user/Service/getMessagesNew?model=W32S&group=0&userType=tv&sn=LD1636D1003547Q09C&uid=a43a5bc9e598d88bd2fcfa60494a6576&token=9bbbab0cca54b18f953016f148afb281&deviceid=8e33f9b7-3f82-51cf-b503-b77591f740f2&romVersion=APOLLOR-02.02.02.1729413': {'106.75.3.253:80': {'gzip': '', 'ungzip': ''}, '101.69.149.253:80': {'gzip': '', 'ungzip': ''}}, 'http://ms2.aginomoto.com/user/Service/getMessagesNew?model=WTV43K1J&group=0&userType=tv&sn=KC1621AB002515B0C9&uid=f98ce64d6eba2a11dfb353b3d5644e86&token=6f6a69b5a1eed1cf9c7adf30a85c474d&deviceid=a211f379-c23b-536a-95b8-6712780928f3&romVersion=HELIOSR-02.02.02.1729413': {'106.75.3.253:80': {'gzip': '', 'ungzip': ''}, '101.69.149.253:80': {'gzip': '', 'ungzip': ''}}, 'http://ms2.aginomoto.com/user/Service/getMessagesNew?model=WTV43K1&group=0&userType=tv&sn=KB1636AB010275B003&uid=80496168&token=1486562665-36c105-80496168-b91a52e389c71dace31081c1c2fd5db8&deviceid=f5fb726d-d465-5994-9a2f-0b147a4b34f9&romVersion=HELIOSR-02.02.02.1729413': {'106.75.3.253:80': {'gzip': '', 'ungzip': ''}, '101.69.149.253:80': {'gzip': '', 'ungzip': ''}}, 'http://ms2.aginomoto.com/user/Service/getMessagesNew?model=W43F&group=0&userType=tv&sn=KP1641A8007677X03C&uid=&token=&deviceid=d5bdd5f4-c92c-55df-8e80-a8c6facb71b2&romVersion=APOLLOR-02.02.02.1729413': {'106.75.3.253:80': {'gzip': '', 'ungzip': ''}, '101.69.149.253:80': {'gzip': '', 'ungzip': ''}}}
for key, vaule in Compare_url.iteritems():
    url = key
    print vaule
    for ip in vaule.keys():
        url_compare_result_dict = url_md5(url, ip)
        vaule[ip]['gzip'] = url_compare_result_dict['gzip']
        vaule[ip]['ungzip'] = url_compare_result_dict['ungzip']
print  Compare_url
