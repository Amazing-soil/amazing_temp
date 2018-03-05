#!/opt/hopeservice/.venv/bin/python
# -*- coding: utf-8 -*-
# @Time    : 01/02/2018 11:12
# @Author  : yao.liu
# @File    : tools_tta_orign.py
__author__ = 'yao.liu'
__version__ = 'v1.0'
__scriptname__ = 'tools_tta_orign.py'

import requests
import sys
import os
import getopt
import re
import json


reload(sys)
sys.setdefaultencoding('utf8')
helptext = u'''
bre 设备对应频道查找回源配置
支持参数：
-h \t输出帮助信息
--host=\t(必填)查询指定频道的回源流
--ip=\t(必填)目标tta虚拟IP
程序支持:bre自动化运维组<bre-ops-dev@chinacache.com>
'''

def find_master_dev(ip):
    '''根据虚拟ip查询宿主机设备名称'''
    url = 'http://223.202.204.189:81/AACode/isccdevice/'
    data = {'ip':'{0}'.format(ip)}
    res = requests.post(url,data=data)
    if res.json().has_key('msg'):
        return False
    else:
        return res.json().get("dn")

def tta_conf_seek(dev,host):
    #调用django接口，联动设备查配置
    print '正在联动查找上层回源配置，调用salt受网络影响，请耐心等待'
    headers = {'content-type': 'application/x-www-form-urlencoded'}
    url = 'http://223.202.204.189:81/Amazing61/tta_orign_ip/'
    data = { "vhost":host,"dev":dev }
    res = requests.post(url,data=data,headers=headers)
    if res.status_code == 200:
        return res.json()[dev]
    else:
        return None


class Colored(object):
    RED = '\033[31m'  # 红色
    GREEN = '\033[32m'  # 绿色
    YELLOW = '\033[33m'  # 黄色
    RESET = '\033[0m'

    def color_str(self, color, s):
        return '{}{}{}'.format(getattr(self, color), s, self.RESET)

    def red(self, s):
        return self.color_str('RED', s)

    def green(self, s):
        return self.color_str('GREEN', s)

    def yellow(self, s):
        return self.color_str('YELLOW', s)

def dispaly_tta(result_dict):
    #传入参数为字典，格式如：{'218.60.45.49:80': {'IP2': '43.255.229.231:4041', 'src': 'data-cn.tradingview.com:80', 'IP1': '43.255.229.215:4041'}}
    print color.green('{0:<15}{1:<20}{2:<30}'.format(u'访问类型'.encode('utf8'),
                                                            u'目标ip port'.encode('utf8'),
                                                            u'回源域名'.encode('utf8'),
                                                            ))
    ip = result_dict.keys()[0]
    print '{0:<10}{1:<20}{2:<30}{3:<10}'.format(result_dict[ip]['methods'],
                                                ip,
                                                result_dict[ip]['vhost'],
                                                result_dict[ip]['weight'].replace(';\n',''),
                                                )

if __name__ == '__main__':
    #收集脚本参数 域名
    try:
        opts, args = getopt.getopt(sys.argv[1:], "h", ["host="])
    except Exception, e:
        print e
        exit()
    for op, value in opts:
        if op == '-h' or op == '--help':
            print '{0}'.format(helptext.encode('utf8'))
            exit()
        elif op == '--host':
            host = value
        elif op == '--ip':
            ip = value
    color = Colored()
    #查找宿主设备名称
    dev = find_master_dev(ip)
    if not dev:
        print color.red('未在cms中查询到虚拟ip的设备名称，请手动检查')
        exit()
    #调用接口查询tta配置
    conf_result = tta_conf_seek(dev,host)
    if conf_result:
        dispaly_tta(conf_result)


