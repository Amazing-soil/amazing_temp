#!/opt/hopeservice/.venv/bin/python
# -*- coding: utf-8 -*-
# @Time    : 06/12/2017 19:11
# @Author  : yao.liu
# @File    : tta_check.py

import requests
import json
import sys,os

def seek_nameid(ip):
    """根据设备ip查找关联的nameid，去重返回结果(多个即返回多个nameid)，返回.前字段"""
    requests.packages.urllib3.disable_warnings()
    url = 'https://223.202.202.117/ip/{0}/nameLocationIps '.format(ip)
    res = requests.get(url,verify=False)
    nameid_list = [ i['nameidName'].split('.')[0] for i in res.json() ]
    nameid_list = list(set(nameid_list))
    return nameid_list

def handle_ip_netcard():
    '''输出设备网卡ip和绑定网卡名关系，到/tmp/tta_ip_netcard.log'''
    cmd = ''' /sbin/ip a|grep secondary|awk '{print $2,$8}'|awk -F "[/ ]" '{print $1,$3}' > /tmp/tta_ip_netcard.log '''
    os.system(cmd)

if __name__ == '__main__':
    handle_ip_netcard()
    '''设备ip解析关系字典'''
    ip_nameid = {}
    error = 1
    '''和cms数据对比，不一致返回错误信息'''
    with open('/tmp/tta_ip_netcard.log','r') as fn:
        for i in fn.readlines():
            ip = i.split(' ')[0]
            nameid = 'tta'+'0'*(3-len(str(i.split(' ')[1].split(':')[1].strip())))+str(i.split(' ')[1].split(':')[1].strip())
            cms_nameid = seek_nameid(ip)
            if len(cms_nameid) > 1:
                print u'{0}网卡和cms中对应关系有误，一个ip对应多个nameid，请修改！'.format(ip).encode('utf8')
                error = 0
            if len(cms_nameid) == 0:
                print u'{0}网卡在cms中无对应nameid绑定关系，请确认！'.format(ip).encode('utf8')
                error = 0
            if len(cms_nameid) == 1:
                if nameid not in cms_nameid:
                    print u'{0}网卡和cms中对应关系有误,请修改！'.format(ip).encode('utf8')
                    error = 0
        if error:
            print u'此设备检查无误！'.encode('utf8')

