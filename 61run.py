#!/opt/hopeservice/.venv/bin/python
# -*- coding: utf-8 -*-
# @Time    : 01/02/2018 11:12
# @Author  : yao.liu
# @File    : tools_sms_orign.py
__author__ = 'yao.liu'
__version__ = 'v1.0'
__scriptname__ = 'tools_sms_orign.py'

import requests
import commands
import sys
import os
import getopt
import json
import seek_sms_orign

reload(sys)
sys.setdefaultencoding('utf8')
helptext = u'''
bre 设备对应频道对应时间，过滤来源ip的访问url，抓取对比压缩非压缩MD5
支持参数：
-h \t输出帮助信息
--host=\t(必填)查询指定频道的回源流
程序支持:bre自动化运维组<bre-ops-dev@chinacache.com>
'''

class toolscount():
    '''调用统计记录接口'''
    def __init__(self, username=None, device=None, toolname=None, version=None, argv=None):
        if username is None:
            self.username = commands.getoutput('whoami').strip()
        else:
            self.username = username
        if device is None:
            self.device = commands.getoutput('hostname').strip()
        else:
            self.device = device
        if toolname is None:
            self.toolname = __scriptname__
        else:
            self.toolname = toolname
        if version is None:
            self.version = __version__
        else:
            self.version = version
        if argv is None:
            self.argv = sys.argv[1:]
        else:
            self.argv = argv
        self.remark = ''
        self.start()

    def modify_username(self, username):
        self.username = username


    def start(self):
        '''触发start动作'''
        url = 'http://223.202.204.189:81/toolscount/start/'
        data = {'device': self.device, 'username': self.username, 'toolname': self.toolname, 'version': self.version, 'argv': self.argv}
        try:
            res = requests.post(url=url, data=data, timeout=3)
            if res.status_code == 200:
                self.id = res.json()['msg']
                print '< count task id {} >'.format(self.id)
        except:
            pass

    def end(self, exitcode=0):
        '''触发end动作'''
        url = 'http://223.202.204.189:81/toolscount/end/'
        try:
            data = {'id': self.id, 'remark': self.remark, 'exitcode': exitcode}
            res = requests.post(url=url, data=data, timeout=3)
        except:
            pass

def orign_iscc(ip):
    '''是蓝汛ip返回False,否则返回True'''
    url = 'http://223.202.204.189:81/AACode/isccdevice/'
    data = {'ip':'{0}'.format(ip)}
    res = requests.post(url,data=data)
    return res.json().has_key('msg')

def sms_conf_seek(dev,host):
    #调用django接口，联动设备查配置
    url = 'http://223.202.204.189:81/Amazing61/sms_orign_ip/'
    data = ''' {{ 'vhost':"{0}",'dev':"{1}"}} '''.format(host,dev)
    print data
    res = requests.post(url,data=data)
    return res.status_code

if __name__ == '__main__':
    #收集脚本参数 域名
    try:
        opts, args = getopt.getopt(sys.argv[1:], "h:", ["host="])
    except Exception, e:
        print e
        exit()
    for op, value in opts:
        if op == '-h' or op == '--help':
            print '{0}'.format(helptext.encode('utf8'))
            exit()
        elif op == '--host':
            host = value
    #测试接口，当前返回500
    print sms_conf_seek('CHN-TT-3-3g8', host)

    #查询本机配置
    hostname = commands.getoutput('hostname|head -1')
    first_lay = seek_sms_orign(hostname)
    print '本机配置：'
    for i in first_lay
        print i
    ip1 = first_lay.keys()[0]
    if not orign_iscc(ip1):
        print '上游配置：'
        #根据ip返回设备名
        dev_name =
        #查找第二层配置
        second_lay = sms_conf_seek(dev_name, first_lay[ip1]['vhost'])
        for i in second_lay
        print i
    else:
        print '查询结束，上游费非蓝汛ip'