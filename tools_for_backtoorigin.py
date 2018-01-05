#!/opt/hopeservice/.venv/bin/python
# -*- coding: utf-8 -*-
# @Time    : 07/11/2017 14:41
# @Author  : yao.liu
# @File    : tools_for_backtoorigin.py
# version  : 1.1
__author__ = 'yao.liu'
__version__ = 'v1.1'
__scriptname__ = 'tools_for_backtoorigin.py'

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

def read_ng(timestrip, ng, vtype='max'):
    '''None表示没有成功取到对应数值,非None表示预期值,参数timestrip是要取值的时间点,ng是NG的key,vtype是周围时间点聚合的类型,有sum,avg,max,min'''
    timestrip = float(timestrip)
    url = 'http://127.0.0.1:21900/Rrd/{0}/{1}/daily'.format(commands.getoutput('hostname'), ng)
    try:
        res = requests.get(url)
    except:
        return 'None1'
    if res.json().get('code', 0) != 0:
        return 'None2'
    if datetime.datetime.fromtimestamp(timestrip) > datetime.datetime.now():
        return 'None3'
    ti = len(res.json()[ng.split('-')[0]][ng.split('-')[1]]['val']) - int((datetime.datetime.now() - datetime.datetime.fromtimestamp(timestrip)).total_seconds() / 60)
    v = []
    for i in [ti - 2, ti - 1, ti, ti + 1, ti + 2]:
        if i < 0 or i > len(res.json()[ng.split('-')[0]][ng.split('-')[1]]['val']):
            continue
        v.append(float(res.json()[ng.split('-')[0]][ng.split('-')[1]]['val'][i]))
    try:
        if vtype == 'max':
            return max(v)
    except:
        return 'Null' 
        
    
def Display_ng(Time_start,Time_end,app):
    '''统计需要查看的ng数据，根据read_ng（）函数'''
    Tn_s = str(Time_start)+'0000'
    Tn_e = str(Time_end)+'0000'
    Time_s_zu = '{0}-{1}-{2} {3}:{4}:{5}'.format(Tn_s[0:4],Tn_s[4:6],Tn_s[6:8],Tn_s[8:10],Tn_s[10:12],Tn_s[12:14])
    Time_e_zu = '{0}-{1}-{2} {3}:{4}:{5}'.format(Tn_e[0:4], Tn_e[4:6], Tn_e[6:8], Tn_e[8:10], Tn_e[10:12], Tn_e[12:14])
    Time_s_now = time.mktime(time.strptime(Time_s_zu, "%Y-%m-%d %H:%M:%S"))
    Time_e_now = time.mktime(time.strptime(Time_e_zu, "%Y-%m-%d %H:%M:%S"))
    if read_ng(Time_s_now,'base-LOCAL_CONN_COUNT') == 'Null':
        print u'未查到ng数据'.encode('utf8')
    else:
    #Local_conn_count = read_ng(Time_now,'base-LOCAL_CONN_COUNT')
    #Local_load = read_ng(Time_now,'base-LOCAL_LOAD')
    #Local_disk_util = read_ng(Time_now,'base-MAX_DISK_UTIL')
    #Local_fc_response = read_ng(Time_now,'FC-RESPONSE_TIME')
        print u'\n起始时间设备连接数 :{0} 结束时间设备连接数 : {1}'.format(read_ng(Time_s_now,'base-LOCAL_CONN_COUNT'),read_ng(Time_e_now,'base-LOCAL_CONN_COUNT')).encode('utf8'),
        if read_ng(Time_s_now,'base-LOCAL_CONN_COUNT') > float(10000) or read_ng(Time_e_now,'base-LOCAL_CONN_COUNT') > float(10000):
            print u'设备连接数过高，请联系设备负责人检查'.encode('utf8'),
        print u'\n起始时间设备负载 :{0} 结束时间设备负载 : {1}'.format(read_ng(Time_s_now,'base-LOCAL_LOAD'),read_ng(Time_e_now,'base-LOCAL_LOAD')).encode('utf8'),
        if read_ng(Time_s_now,'base-LOCAL_LOAD') > float(90) or read_ng(Time_e_now,'base-LOCAL_LOAD') > float(90):
            print u'设备负载过高，请联系设备负责人检查'.encode('utf8'),
        else:
            print u'设备负载正常'.encode('utf8'),
        print u'\n起始时间设备磁盘使用率 : {0}% 结束时间设备磁盘使用率 : {1}%'.format(read_ng(Time_s_now,'base-MAX_DISK_UTIL'),read_ng(Time_e_now,'base-MAX_DISK_UTIL')).encode('utf8'),
        if read_ng(Time_s_now,'base-MAX_DISK_UTIL') > float(90) or read_ng(Time_e_now,'base-MAX_DISK_UTIL') > float(90):
            print u'磁盘使用率过高，请联系设备负责人检查'.encode('utf8'),
        else:
            print u'磁盘使用率正常'.encode('utf8'),
        if app == 'Fc' :
            print u'\n起始时间设备FC响应时间 : {0} 结束时间设备FC响应时间 : {1}'.format(read_ng(Time_s_now,'FC-RESPONSE_TIME'),read_ng(Time_e_now,'FC-RESPONSE_TIME')).encode('utf8'),

    #return [Local_conn_count,Local_load,Local_disk_util,Local_fc_response]

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

#print FormatTimerange('2017110808-2017110810')
def Cachelog_analyzer(stime,etime):
    '''处理cache log，在时间范围内，匹配信息，定制输出'''
    cache_listdir = commands.getoutput('ls /data/proclog/log/squid/cache.log*').split('\n')
    for file in cache_listdir:
        for logline in open(file,'r').readlines():
            try:
                cache_log_dict = {'Time':logline.split('|')[0].replace('/','').replace(':','').replace(' ',''), \
                                  'Details':logline.split('|')[1]}
            except:
                continue
            '''需要过滤的关键字'''
            cache_disk_info = re.compile(r'WARNING: Disk space over limit')
            '''在时间范围内匹配 输出'''
            if long(re.sub("\D", "", cache_log_dict.get('Time'))) > long(re.sub("\D", "", str(etime) + '0000')) and long(re.sub("\D", "", cache_log_dict.get('Time'))) < long(re.sub("\D", "", str(etime) + '0000')):
                if cache_disk_info.search(str(cache_log_dict.get('Details'))):
                    print u'文件系统被写满，请检查磁盘和coss aufs是否被写满，联系设备负责人处理'.encode('utf8')
                    print logline
                    return
# test = '2017/08/03 17:21:45| WARNING: Disk space over limit: 2468935304 KB > 2400256000 KB'
#Time = FormatTimerange('2017080308-2017080315')
#print Time
#Cachelog_analyzer(test,Time['starttime'],Time['endtime'])
def Squid_client_analyzer():
    '''检查squid性能方面问题'''
    flexicache_conf = open('/usr/local/squid/etc/flexicache.conf')
    flexicache_conf_list = flexicache_conf.readlines()
    '''查看squid 运行模式,存入数值 multisquid_counts'''
    Count_effective_info = re.compile(r'count_effective')
    Cc_multisquid_info = re.compile(r'cc_multisquid')
    flexicache_info = {}
    for i in flexicache_conf_list:
        if Count_effective_info.search(i):
            flexicache_info['count_effective'] = i.strip().split(' ')[1]
        if Cc_multisquid_info.search(i):
            flexicache_info['cc_multisquid'] = re.findall(r'\d',i)[0]
    if flexicache_info.get('count_effective') == 'yes':
        multisquid_counts = flexicache_info.get('cc_multisquid')
    else:
        multisquid_counts = 1
    return multisquid_counts

def Dev_inodes():
    '''计算设备inodes是否被写满'''
    inodes_info = commands.getoutput("df -i|awk '{print $5}'")
    Inodes_util = re.findall(r'\d', inodes_info)
    for i in Inodes_util:
        if int(i) >= int(99):
            print u'设备indoes已被写满，请联系设备负责人处理'.encode('utf8')
            print inodes_info
            return
    print u'\n设备indoes使用正常'.encode('utf8')
def Hpc_sta(hpcc_version,channel,starttime,endtime):
    '''统计hpcc存储日志404的top 10'''
    try:
        channel = channel.split('//')[1]
    except:
        print u'请输入完整频道名，带协议头http://'.encode('utf8')
        exit()
    if hpcc_version == 'ATS':
        '''统计ATS hpc对应时间 域名的存储404日志'''
        #hpcc_sta_log_path = '/data/proclog/log/ccts/'
        cmd = ''' ls /data/proclog/log/ccts/ccts.log_{0}.2017* '''.format(commands.getoutput('hostname'))
        hpc_sta_file_list = commands.getoutput(cmd).split('\n')
        hpc_sta_file_intime = []
        for i in hpc_sta_file_list:
            itime = ''.join(''.join(re.findall(r'\d',i.split('-')[-1].split('h')[0])))
            if int(itime) >= int(starttime) and int(itime) <= int(endtime):
                hpc_sta_file_intime.append(i)
        if int(''.join(re.findall(r'\d', hpc_sta_file_intime[-1].split('-')[-1].split('h')[0]))) < int(endtime):
            hpc_sta_file_intime.append('/data/proclog/log/ccts/ccts.log')
        for i in hpc_sta_file_intime:
            cmd =  ''' grep -a "TCP_MISS/404" {0}|awk '$8~"{1}"' >> /tmp/sta61.log  '''.format(i, channel)
            commands.getoutput(cmd)
    if hpcc_version == 'Hpcc':
        '''统计ceph hpcc对应时间 域名的存储404日志'''
        #hpcc_sta_log_path = '/data/proclog/log/storage/storage_api/storage_get_access.log'
        hpc_sta_file_list = commands.getoutput(' ls /data/proclog/log/storage/storage_api/archive/storage_get_access_2017* ').split('\n')
        hpc_sta_file_intime = []
        for i in hpc_sta_file_list:
            itime = ''.join(re.findall(r'\d',i))
            if int(itime) >= int(starttime) and int(itime) <= int(endtime):
                hpc_sta_file_intime.append(i)
        if int(''.join(re.findall(r'\d',hpc_sta_file_intime[-1]))) < int(endtime):
            hpc_sta_file_intime.append('/data/proclog/log/storage/storage_api/storage_get_access.log')
        for i in hpc_sta_file_intime:
            if i.split('.')[-1] == 'tgz':
                cmd = ''' zcat {0}|grep -a "TCP_-/404"|awk '$8~"{1}"' >> /tmp/sta61.log  '''.format(i, channel)
                commands.getoutput(cmd)
            if i.split('.')[-1] == 'log':
                cmd = ''' grep -a "TCP_-/404" {0}|awk '$8~"{1}"' >> /tmp/sta61.log  '''.format(i, channel)
                commands.getoutput(cmd)
    '''统计存储日志，对应时间段404的url次数top10'''
    cmd = ''' awk '{{num[$8]++}}END{{for(i in num)print num[i],i}}' /tmp/sta61.log| sort -nr '''
    Top10_sta_404 = commands.getoutput(cmd).split('\n')[0:9]
    if len(Top10_sta_404) > 1 :
        print u'\n存储日志该时间段，404文件排行：'.encode('utf8')
        for i in Top10_sta_404:
            print i
    else:
        print u'\n存储日志该时间段没有404文件，文件均为第一次访问，请确认是否新发布文件，导致回源：'.encode('utf8')
    commands.getoutput('rm -f /tmp/sta61.log')
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

def check_squid_conf():
    '''检查全局被动压缩配置，ok即存在'''
    gzip_mod_check = commands.getoutput('grep -q mod_header_combination /usr/local/squid/etc/squid.conf && echo ok')
    '''检查全局0方向是否配置删除特殊头，4即配置完整'''
    del_0_header_check = commands.getoutput('egrep -c "(mod_header 0 del).*(allow all)" /usr/local/squid/etc/squid.conf')
    '''检查所需日志特殊字段是否配置，ok即配置'''
    squid_log_check = commands.getoutput('egrep "(logformat squid_custom_log)" /usr/local/squid/etc/squid.conf|grep -q -e "$AE" -e "$PB" && echo ok')
    if gzip_mod_check == 'ok':
        print u'全局配置被动压缩，压缩非压缩存两份，注意同文件会miss两次'.encode('utf8')
    else:
        print u'全局未配置被动压缩，压缩非压缩存一份，可能存在缓存问题，请确认功能需求'.encode('utf8')
    if del_0_header_check == '4':
        print u'设备已全局配置删除0方向影响缓存的特殊头'.encode('utf8')
    else:
        print u'设备未配置删除0方向影响缓存的特殊头，建议尝试配置删除0方向的Cache-Control If-None-Match If-Match If-Unmodified-Since'.encode('utf8')
    if squid_log_check == 'ok':
        return 1
    else:
        return 0

def LogTogether(filenamelist):
    '''将筛选访问日志聚合'''
    #print u'\n正在打开日志包...'.encode('utf8')
    for filename in filenamelist:
        #print filename
        loggzpath = '{0}{1}'.format(logpath, filename)
        greplogpath = '/tmp/grep_61_log'
        os.system('''zcat {0} | egrep '{1}' >> {2}'''.format(loggzpath, url, greplogpath))
    return greplogpath

def sla_standard():
    return {'slowspeed': {'hit': 300, 'unhit': 100},
            'slowrt': {'hit': 200, 'unhit': 500}}

if __name__ == '__main__':
    signal.signal(signal.SIGINT, quit)
    signal.signal(signal.SIGTERM, quit)
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
    if timerange is None and opts_dir.get('log') is None:
        print u'-t 和 --url= 参数为必填项,-t格式xxx(起始时间)-xxx（结束时间）,--url=http://chinacache.com  如筛选2017年5月10日19点的日志:-t 2017051019-2017051020,使用-h可以查看帮助'.encode('utf8')
        exit()
    Time_use = FormatTimerange(opts_dir['timerange'])
    url = opts_dir['url']
    app = witchapp()
    logpath = {"Fc": "/data/proclog/log/squid/access/", "Hpcc": "/data/proclog/log/hpc/access/",
               "ATS": "/data/proclog/log/hpc/access/"}.get(app)
    '''检查ng数据'''
    Display_ng(Time_use['starttime'],Time_use['endtime'],app)
    '''FC检查cache报错是否文件系统写满'''
    if app == 'Fc':
        Cachelog_analyzer(Time_use['starttime'], Time_use['endtime'])
    '''检查设备inodes是否被写满'''
    Dev_inodes()
    '''hpcc检查存储日志404文件是否异常'''
    if app == 'Hpcc' or app == 'ATS' :
        Hpc_sta(app, url, Time_use['starttime'], Time_use['endtime'])
    '''检查squid关键配置'''
    log_flag = check_squid_conf()
    greplogpath = LogTogether(GetFileName(Time_use['starttime'],Time_use['endtime'] ))
    opts_dir = {}

    if not os.path.exists(greplogpath):
        print u'选中的时间段内没有找到对应日志包,请确认时间段是否有误'.encode('utf8')
        tc.end(0)
        exit()

    with open(greplogpath, 'r') as f1:
        # 得到日志各字段
        Itemlog = {}
        LineItem = {}
        slowtype_sum = {'slowrt': {}, 'slowspeed': {}}
        flow_url = {}
        flow_type = {}
        num_url = {}
        special_log = {}
        request_flow = {'GET': int(0), 'POST': int(0), 'HEAD': int(0)}
        sum_ua = {}
        size0Url = []
        # 逐行数据记录
        sumnum_mate = 0
        for sumnum, line in enumerate(f1):
            try:
                LineItem['Date'] = line.split()[0]
                LineItem['ResponesTime'] = float(line.split()[1])
                LineItem['ClientIp'] = line.split()[2]
                LineItem['CacheCode'] = line.split()[3]
                LineItem['Cache'] = line.split()[3].split('/')[0]
                LineItem['Code'] = line.split()[3].split('/')[1]
                LineItem['Size'] = round(float(line.split()[4]) / 1024, 3)
            except:
               break
            # 标识慢时慢速归属
            if LineItem['Size'] > 200 and LineItem['Code'].startswith('2'):
                LineItem['slowtype'] = 'slowspeed'
            elif LineItem['Size'] <= 200 and LineItem['Code'].startswith('2'):
                LineItem['slowtype'] = 'slowrt'
            else:
                LineItem['slowtype'] = ''
            LineItem['Method'] = line.split()[5]
            LineItem['Url'] = line.split()[6].split('?')[0]
            LineItem['type'] = line.split()[6].split('?')[0].split('.')[-1].split('/')[-1]
            LineItem['Range'] = ''
            if 'CL=bytes=' in line:
                match = re.search('CL=bytes=[0-9]*-[0-9]* ', line)
                if match:
                    LineItem['Range'] = match.group().split('=')[-1]
            LineItem['UrlRange'] = '{0}\t{1}'.format(LineItem['Url'], LineItem['Range'])
            # 响应时间为0时,将下载速度定为文件大小速度
            if LineItem['ResponesTime'] == 0:
                LineItem['Speed'] = LineItem['Size']
            # 当Size为0时,将下载速度定为0
            elif LineItem['Size'] == 0:
                LineItem['Speed'] = 0
                size0Url.append(LineItem['Url'])
            # 都正常时,speed=size / respones time
            else:
                LineItem['Speed'] = round(LineItem['Size'] / LineItem['ResponesTime'], 4)
            if opts_dir.get('speedlt') is not None:
                if LineItem['Speed'] > opts_dir['speedlt']:
                    continue
            if opts_dir.get('speedgt') is not None:
                if LineItem['Speed'] < opts_dir['speedgt']:
                    continue
            LineItem['Upper'] = line.split()[8].split(':')[0].split('/')[-1]
            LineItem['UA'] = line.split('\"')[3]
            LineItem['hitstate'] = {'-': 'hit', '': 'hit'}.get(LineItem['Upper'], 'unhit')
            # 若存在特殊日志字段，对应url收集
            if log_flag == 1:
                if LineItem['hitstate'] == 'unhit':
                    if not special_log.has_key(LineItem['Url']):
                        special_log[LineItem['Url']] = {'$AE': {'gzip': 0, 'ungzip': 0}, '$PB': []}
                    for j in line.split('@in#(')[1].split('^~'):
                        if 'PB' in j:
                            if '-' not in j:
                                hash_squid = j.split('.')[1]
                                if hash_squid not in special_log[LineItem['Url']]['$PB']:
                                    special_log[LineItem['Url']]['$PB'].append(hash_squid)
                        if 'AE=' in j:
                            if j.split('=')[1] == 'gzip':
                                special_log[LineItem['Url']]['$AE']['gzip'] += 1
                            else:
                                special_log[LineItem['Url']]['$AE']['ungzip'] += 1
            # 匹配日志数+1
            if LineItem['hitstate'] == 'unhit':
                sumnum_mate += 1
            # 数据统计
            # 慢时慢速基数
            if LineItem['slowtype'] != '':
                if slowtype_sum[LineItem['slowtype']].get(LineItem['Cache']) is None:
                    slowtype_sum[LineItem['slowtype']][LineItem['Cache']] = 0L
                if slowtype_sum[LineItem['slowtype']].get(LineItem['CacheCode']) is None:
                    slowtype_sum[LineItem['slowtype']][LineItem['CacheCode']] = 0L
                slowtype_sum[LineItem['slowtype']][LineItem['Cache']] += 1
                slowtype_sum[LineItem['slowtype']][LineItem['CacheCode']] += 1
            # UA数量计数
            if LineItem['hitstate'] == 'unhit':
                if sum_ua.get(LineItem['UA']) is None:
                    sum_ua[LineItem['UA']] = 0L
                sum_ua[LineItem['UA']] += 1
            # 总流量计数
            if LineItem['hitstate'] == 'unhit':
                if flow_url.get('sum_flow') is None:
                    flow_url['sum_flow'] = 0.0
                flow_url['sum_flow'] += LineItem['Size']
            #url数量统计
            if LineItem['hitstate'] == 'unhit':
                if num_url.get(LineItem['Url']) is None:
                    num_url[LineItem['Url']] = 0
                num_url[LineItem['Url']] += 1
            # url流量统计
            if LineItem['hitstate'] == 'unhit':
                if flow_url.get(LineItem['UrlRange']) is None:
                    flow_url[LineItem['UrlRange']] = 0.0
                flow_url[LineItem['UrlRange']] += LineItem['Size']
            # 文件后缀流量统计
            if LineItem['hitstate'] == 'unhit':
                if flow_type.get(LineItem['type']) is None:
                    flow_type[LineItem['type']] = 0.0
                flow_type[LineItem['type']] += LineItem['Size']
            # 请求方式get post head 流量统计
            if LineItem['hitstate'] == 'unhit':
                if LineItem['Method'] == 'GET':
                    request_flow['GET'] += LineItem['Size']
                if LineItem['Method'] == 'POST':
                    request_flow['POST'] += LineItem['Size']
                if LineItem['Method'] == 'HEAD':
                    request_flow['HEAD'] += LineItem['Size']
        if sumnum_mate == 0:
            print '没有筛选到符合条件的回源日志条目'
            os.remove(greplogpath)
            tc.end(0)
            exit()
        # 请求方式流量占比
        print u'\n请求方式流量占比'.encode('utf8')
        for k, v in request_flow.items():
            print '\t{0} \t{1}%\t{2}KB'.format(k, round(float(v) / float(flow_url['sum_flow']), 2) * 100, v)
        # 网民UA占比 top 20
        print u'\n网民UA占比 top 10'.encode('utf8')
        top_sum_ua = sorted(sum_ua.iteritems(), key=lambda d: d[1], reverse=True)
        for k, v in top_sum_ua[0:10]:
            print '\t{0}\t{1}%\t{2}'.format(v, round(float(v) / float(sumnum_mate), 4) * 100, k)
        # 后缀类型流量最高 TOP 10
        print u'\n占用流量最高的url后缀 TOP 10 :（可查看缓存策略是否合理，针对性调整）'.encode('utf8')
        top_flow_type = sorted(flow_type.iteritems(), key=lambda d: d[1], reverse=True)[:11]
        for item in top_flow_type:
            print u'\t{0}\t{1}MB'.format(item[0],round(item[1] / 1024.0, 2))
        # 占用流量最高的url TOP 10
        print u'\n占用流量最高的url TOP 10 :'.encode('utf8')
        top_flow_url = sorted(flow_url.iteritems(), key=lambda d: d[1], reverse=True)[:11]
        for item in top_flow_url:
            print u'\t{0}MB\t{1}'.format(round(item[1] / 1024.0, 2), item[0])
        #url数量 top 5
        print u'请求url次数 TOP 5 :'.encode('utf8')
        top_num_url = sorted(num_url.iteritems(), key=lambda d: d[1], reverse=True)[:5]
        print u'\t{0}\t{1}\t{2:>5}\t{3}'.format('次数', '压缩\非压缩', 'hash个数', 'URL').encode('utf8')
        for item in top_num_url:
            print u'\t{0:<7}\t{1}\{2:<7}\t{3:<10}\t{4}'.format(item[1],
                                                               special_log[item[0]]['$AE']['gzip'],
                                                               special_log[item[0]]['$AE']['ungzip'],
                                                               len(special_log[item[0]]['$PB']), item[0])
        os.remove(greplogpath)
        tc.end(0)
