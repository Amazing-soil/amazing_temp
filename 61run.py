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
helptext = u'''
bre 设备对应频道对应时间，回源原因分析
支持参数：
-h \t输出帮助信息
-t\t(必填)筛选时间区间,格式xxx(起始时间)-xxx（结束时间）,如筛选2017年5月10日19点的日志：-t 2017051019-2017051020
--url\t(必填)筛选要过滤的频道或url，支持泛匹
程序支持:bre自动化运维组<bre-ops-dev@chinacache.com>
'''

def FormatTimerange(timerange):
    '''处理时间戳'''
    if '-' not in timerange:
        print u'时间区间格式输入有误,正确示例 : 2017050901-2017050903'.encode('utf8')
        exit()
    try:
        starttime = timerange.split('-')[0]
        endtime = timerange.split('-')[1]
    except:
        print u'时间区间格式输入有误,正确示例 : 2017050901-2017050903'.encode('utf8')
        exit()
    try:
        starttime = str(int(starttime)) + '0' * (10 - len(starttime))
        endtime = str(int(endtime)) + '0' * (10 - len(endtime))
    except:
        print u'时间区间格式输入有误 : 开始时间和结束时间必须都是小于等于10位的时间戳数字 ,正确示例 : 2017050901-2017050903'.encode('utf8')
        exit()
    if starttime > endtime:
        print u'开始时间不能大于结束时间'.encode('utf8')
        exit()
    print '开始时间:{0}\t结束时间:{1}'.format(int(starttime), int(endtime))
    return {'starttime': int(starttime), 'endtime': int(endtime)}

def GetFileName(starttime, endtime):
    '''根据条件过滤文件名'''
    filenamelist = []
    listdir = os.listdir(logpath)
    listdir.sort()
    for filename in listdir:
        try:
            filetime = int(filename.split('.')[4][0:10])
            filetype = filename.split('.')[-1]
        except:
            continue
        if filetime >= int(starttime) and filetime <= int(endtime) and filetype == 'gz':
            filenamelist.append(filename)
    return filenamelist

def witchapp():
    '''判断设备是FC，ats，hpcc'''
    res = commands.getoutput('ccamr list | grep \' HPCC\'')
    if 'HPCC' in res:
        hpc_res = commands.getoutput(' rpm -q HPC ' )
        if 'ATS' in hpc_res:
            return 'ATS'
        else:
            return 'Hpcc'
    else:
        return 'Fc'

def LogTogether(filenamelist):
    '''将筛选访问日志聚合'''
    #print u'\n正在打开日志包...'.encode('utf8')
    for filename in filenamelist:
        #print filename
        loggzpath = '{0}{1}'.format(logpath, filename)
        greplogpath = '/tmp/grep_61_log'
        os.system('''zcat {0} | egrep '{1}' >> {2}'''.format(loggzpath, url, greplogpath))
    return greplogpath

def opts_get():
    '''收集脚本,返回opts_dir字典'''
    opts_dir = {}
    try:
        opts, args = getopt.getopt(sys.argv[1:], "ht:", ["url=","cip=","ip1=","ip2="])
    except Exception, e:
        print e
        exit()
    for op, value in opts:
        if op == '-h' or op == '--help':
            print '{0}'.format(helptext.encode('utf8'))
            exit()
        elif op == '-t':
            opts_dir['timerange'] = value
        elif op == '--url':
            opts_dir['url'] = value
        elif op == '--cip':
            opts_dir['cip'] = value
        elif op == '--ip1':
            opts_dir['ip1'] = value
        elif op == '--ip2':
            opts_dir['ip2'] = value
    return opts_dir


if __name__ == '__main__':
    # 收集脚本参数
    opts_dir = opts_get()
    #tc = toolscount(username=opts_dir.get('username'), argv=str(opts_dir))
    # 必要参数补充默认值
    timerange = opts_dir.get('timerange')
    if timerange is None and opts_dir.get('log') is None:
        print u'-t 和 --url= 参数为必填项,-t格式xxx(起始时间)-xxx（结束时间）,--url=http://chinacache.com  如筛选2017年5月10日19点的日志:-t 2017051019-2017051020,使用-h可以查看帮助'.encode('utf8')
        exit()
    url = opts_dir['url']
    app = witchapp()
    logpath = {"Fc": "/data/proclog/log/squid/access/", "Hpcc": "/data/proclog/log/hpc/access/",
               "ATS": "/data/proclog/log/hpc/access/"}.get(app)
    Time_use = FormatTimerange(opts_dir['timerange'])
    greplogpath = LogTogether(GetFileName(Time_use['starttime'], Time_use['endtime']))
    if not os.path.exists(greplogpath):
        print u'选中的时间段内没有找到对应日志包,请确认时间段是否有误'.encode('utf8')
        exit()
    with open(greplogpath, 'r') as f1:
        # 得到日志各字段
        LineItem = {}
        Compare_url = {}
        # 逐行数据记录
        sumnum_mate = 0
        for sumnum, line in enumerate(f1):
            try:
                LineItem['ClientIp'] = line.split()[2]
                LineItem['Url'] = line.split()[6]
            except:
                break
        if LineItem['ClientIp'] == opts_dir['cip']:
            sumnum_mate += 1
            if not Compare_url.has_key(LineItem['Url']):
                Compare_url[LineItem['Url']] = {opts_dir['ip1']:{'gzip':'','unzip':''},opts_dir['ip2']:{'gzip':'','unzip':''}}
        if sumnum_mate == 0:
            print '没有筛选到符合条件的日志'
            os.remove(greplogpath)
            exit()
    print Compare_url