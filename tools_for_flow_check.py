#!/opt/hopeservice/.venv/bin/python
# -*- coding: utf-8 -*-
# @Time    : 27/11/2017 11:12
# @Author  : yao.liu
# @File    : tools_for_flow_check.py
__author__ = 'yao.liu'
__version__ = 'v1.1'
__scriptname__ = 'tools_for_flow_check.py'

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
    #print '开始时间:{0}\t结束时间:{1}'.format(int(starttime), int(endtime))
    return {'starttime': int(starttime), 'endtime': int(endtime)}

def Product_time(Time_start, Time_end, type):
    '''处理时间戳，返回portal接口需要的时间，和前一天同比时间,1为前一天'''
    Tn_s = str(Time_start) + '0000'
    Tn_e = str(Time_end) + '0000'
    # 2 portal api time ('2017-12-20 08:00:00', '2017-12-20 09:00:00')
    Time_s_zu = '{0}-{1}-{2} {3}:{4}:{5}'.format(Tn_s[0:4], Tn_s[4:6], Tn_s[6:8], Tn_s[8:10], Tn_s[10:12], Tn_s[12:14])
    Time_e_zu = '{0}-{1}-{2} {3}:{4}:{5}'.format(Tn_e[0:4], Tn_e[4:6], Tn_e[6:8], Tn_e[8:10], Tn_e[10:12], Tn_e[12:14])
    if type == 1:
        # 1 前一天同比时间 ('2017-12-20 08:00:00', '2017-12-20 09:00:00')
        Time_s_now = time.mktime(time.strptime(Time_s_zu, "%Y-%m-%d %H:%M:%S"))
        Time_s_befor = (datetime.datetime.fromtimestamp(Time_s_now) - datetime.timedelta(days=1)).strftime("%Y%m%d%H")
        Time_e_now = time.mktime(time.strptime(Time_e_zu, "%Y-%m-%d %H:%M:%S"))
        Time_e_befor = (datetime.datetime.fromtimestamp(Time_e_now) - datetime.timedelta(days=1)).strftime("%Y%m%d%H")
        return Time_s_befor + '-' + Time_e_befor
    elif type == 2:
        return Time_s_zu, Time_e_zu
    elif type == 3:
        # 3 es api time ('2017-12-22T10:00:09+0800','2017-12-22T11:20:09+0800')
        Time_s_es = '{0}-{1}-{2}T{3}:{4}:{5}+0800'.format(Tn_s[0:4], Tn_s[4:6], Tn_s[6:8], Tn_s[8:10], Tn_s[10:12], Tn_s[12:14])
        Time_e_es = '{0}-{1}-{2}T{3}:{4}:{5}+0800'.format(Tn_e[0:4], Tn_e[4:6], Tn_e[6:8], Tn_e[8:10], Tn_e[10:12], Tn_e[12:14])
        return Time_s_es, Time_e_es


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

def orign_iscc(ip):
    '''是蓝汛ip返回False,否则返回True'''
    url = 'http://223.202.204.189:81/AACode/isccdevice/'
    data = {'ip':'{0}'.format(ip)}
    res = requests.post(url,data=data)
    return res.json().has_key('msg')

class Colored(object):
    RED = '\033[31m'       # 红色  
    GREEN = '\033[32m'     # 绿色  
    YELLOW = '\033[33m'    # 黄色  
    RESET = '\033[0m' 
    def color_str(self, color, s):  
        return '{}{}{}'.format(getattr(self, color), s, self.RESET)
    def red(self, s):  
        return self.color_str('RED', s)
    def green(self, s):  
        return self.color_str('GREEN', s)
    def yellow(self, s):  
        return self.color_str('YELLOW', s)  

def check_preload_info(channel,stime,etime):
    '''根据频道查找客户ID'''
    headers = {'content-type': 'application/x-www-form-urlencoded'}
    url_rcms = 'http://223.202.204.189:81/Amazing61/seek_channel_info/'
    data = {"channel":channel,"name":'customerName' }
    try:
        res = requests.post(url_rcms,data=data,headers=headers)
        ID = res.text
    except:
        return None
    url_portal = 'http://223.202.204.189:81/Amazing61/seek_preload_sys/'
    data = {"ID":ID,"stime":stime,"etime":etime}
    try:
        res = requests.post(url_portal,data=data,headers=headers)
        return res.text
    except:
        return None

def check_preload_shell_info(channel,stime,etime):
    headers = {'content-type': 'application/x-www-form-urlencoded'}
    url_shell = 'http://223.202.204.189:81/Amazing61/seek_preload_shell/'
    data = {"channel": channel, "stime": stime, "etime": etime}
    try:
        res = requests.post(url_shell,data=data,headers=headers)
        return res.text
    except:
        return None

def run_info(Time_use):
    #Time_use = FormatTimerange(opts_dir['timerange'])
    greplogpath = LogTogether(GetFileName(Time_use['starttime'], Time_use['endtime']))
    if not os.path.exists(greplogpath):
        print u'选中的时间段内没有找到对应日志包,请确认时间段是否有误'.encode('utf8')
        exit()
    with open(greplogpath, 'r') as f1:
        # 得到日志各字段
        LineItem = {}
        flow_url = {}
        num_url = {}
        num_client = {}
        cache_status = {}
        code_status = {}
        # 逐行数据记录
        sumnum_mate = 0
        for sumnum, line in enumerate(f1):
            try:
                LineItem['Date'] = line.split()[0]
                LineItem['ClientIp'] = line.split()[2]
                LineItem['CacheCode'] = line.split()[3]
                LineItem['Cache'] = line.split()[3].split('/')[0]
                LineItem['Code'] = line.split()[3].split('/')[1]
                LineItem['Size'] = round(float(line.split()[4]) / 1024, 3)
                LineItem['Url'] = line.split()[6].split('?')[0]
                LineItem['Upper'] = line.split()[8].split(':')[0].split('/')[-1]
                LineItem['hitstate'] = {'-': 'hit', '': 'hit'}.get(LineItem['Upper'], 'unhit')
            except:
               break
            # 匹配日志数url总数 +1
            sumnum_mate += 1
            # 数据统计
            # 总流量计数
            if flow_url.get('sum_flow') is None:
                flow_url['sum_flow'] = 0.0
            flow_url['sum_flow'] += LineItem['Size']
            # url流量统计
            if flow_url.get(LineItem['Url']) is None:
                flow_url[LineItem['Url']] = 0.0
            flow_url[LineItem['Url']] += LineItem['Size']
            #url数量统计
            if num_url.get(LineItem['Url']) is None:
                num_url[LineItem['Url']] = 0
            num_url[LineItem['Url']] += 1
            #来访ip数量统计 [数量，占比，是否蓝汛ip]
            if num_client.get(LineItem['ClientIp']) is None:
                num_client[LineItem['ClientIp']] = [0,0,'']
            num_client[LineItem['ClientIp']][0] += 1
            #hit unhit 流量
            if cache_status.get(LineItem['hitstate']) is None:
                cache_status[LineItem['hitstate']] = 0
            cache_status[LineItem['hitstate']] += LineItem['Size']
            #状态码 [数量，占比]
            if code_status.get(LineItem['CacheCode']) is None:
                code_status[LineItem['CacheCode']] = [0, 0]
            code_status[LineItem['CacheCode']][0] += 1

        if sumnum_mate == 0:
            print '没有筛选到符合条件的回源日志条目'
            os.remove(greplogpath)
            exit()
        color = Colored()
        #统计时间范围
        print color.red(u'开始时间:{0}\t结束时间:{1}'.format(Time_use['starttime'], Time_use['endtime']).encode('utf8'))
        #unhit流量占比
        if cache_status.has_key('unhit'):
            print color.yellow(u'Unhit流量占比{0}%'.format(round(float(cache_status['unhit']) / float(flow_url['sum_flow']),4) * 100).encode('utf8'))
        else:
            print color.yellow(u'此时间段无unhit请求').encode('utf8')
        # 网民IP占比 top 10
        print color.yellow(u'网民IP总数量{0} top 10'.format(sumnum_mate).encode('utf8'))
        top_sum_ip = sorted(num_client.iteritems(), key=lambda d: d[1][0], reverse=True)
        # 判断是否蓝汛ip
        for i in top_sum_ip[0:10]:
            if i[1][2] == '':
                if orign_iscc(i[0]):
                    i[1][2] = 'not-cc'
                else:
                    i[1][2] = 'cc'
            print '\t{0}\t{1}\t{2}%\t{3}'.format(i[1][0], i[0], round(float(i[1][0]) / float(sumnum_mate),4) * 100,i[1][2])
        # 占用流量最高的url top 10
        print color.yellow(u'占用流量最高的url TOP 10 :'.encode('utf8'))
        top_flow_url = sorted(flow_url.iteritems(), key=lambda d: d[1], reverse=True)[1:11]
        for item in top_flow_url:
            print u'\t{0}MB\t{1}'.format(round(item[1] / 1024.0, 2), item[0])
        #url数量 top 10
        print color.yellow(u'请求url次数 TOP 10 :'.encode('utf8'))
        top_num_url = sorted(num_url.iteritems(), key=lambda d: d[1], reverse=True)[:10]
        for item in top_num_url:
            print u'\t{0}\t{1}'.format(item[1], item[0])
        # 状态码数量及占比
        print color.yellow(u'状态码总数量{0} top 10'.format(sumnum_mate).encode('utf8'))
        top_sum_ip = sorted(code_status.iteritems(), key=lambda d: d[1][0], reverse=True)
        for i in top_sum_ip[0:10]:
            print '\t{0}\t{1:>20}\t{2}%'.format(i[1][0], i[0], round(float(i[1][0]) / float(sumnum_mate),4) * 100)
        os.remove(greplogpath)

if __name__ == '__main__':
    # signal.signal(signal.SIGINT, quit)
    # signal.signal(signal.SIGTERM, quit)
    opts_dir = {}
    # 收集脚本参数
    try:
        opts, args = getopt.getopt(sys.argv[1:], "ht:", ["url="])
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
    tc = toolscount(username=opts_dir.get('username'), argv=str(opts_dir))
    # 必要参数补充默认值
    timerange = opts_dir.get('timerange')
    if timerange is None :
        print u'-t 和 --url= 参数为必填项,-t格式xxx(起始时间)-xxx（结束时间）,--url=http://chinacache.com  如筛选2017年5月10日19点的日志:-t 2017051019-2017051020,使用-h可以查看帮助'.encode('utf8')
        exit()
    url = opts_dir['url']
    app = witchapp()
    logpath = {"Fc": "/data/proclog/log/squid/access/", "Hpcc": "/data/proclog/log/hpc/access/",
               "ATS": "/data/proclog/log/hpc/access/"}.get(app)
    color = Colored()
    print color.green(u'Running.................................................')
    Time_use = FormatTimerange(opts_dir['timerange'])
    #检查时间范围内是否有预加载行为
    preload_time = Product_time(Time_use['starttime'], Time_use['endtime'],type=2)
    preload_es_time = Product_time(Time_use['starttime'], Time_use['endtime'],type=3)
    preload_num = check_preload_info(url, preload_time[0], preload_time[1])
    preload_shell_info = check_preload_shell_info(url.strip('/'),preload_es_time[0],preload_es_time[1])
    print color.green(u'该时间段portal提交总预加载条数为：{0}'.format(preload_num).encode('utf8'))
    print color.green(u'{0}'.format(preload_shell_info).encode('utf8'))
    run_info(Time_use = FormatTimerange(opts_dir['timerange']))
    #跑前一天数据
    run_info(Time_use = FormatTimerange(Product_time(Time_use['starttime'], Time_use['endtime'],type=1)))
    tc.end(0)






