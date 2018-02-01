#!/opt/hopeservice/.venv/bin/python
# -*- coding: utf-8 -*-
# @Time    : 10/01/2018 11:12
# @Author  : yao.liu
# @File    : tools_urlmd5_check.py
__author__ = 'yao.liu'
__version__ = 'v1.0'
__scriptname__ = 'tools_urlmd5_check.py'

import requests
import hashlib
import commands
import sys
import os
import getopt

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
            opts_dir['vhost'] = value