#!/opt/hopeservice/.venv/bin/python
# -*- coding: utf-8 -*-
# @Time    : 10/01/2018 11:12
# @Author  : yao.liu
# @File    : tools_urlmd5_check.py
__author__ = 'yao.liu'
__version__ = 'v1.1'
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
-t\t(必填)筛选时间区间,格式xxx(起始时间)-xxx（结束时间）,如筛选2017年5月10日19点的日志：-t 2017051019-2017051020
--url=\t(必填)筛选要过滤的频道或url，支持泛匹
--cip=168.235.205.197\t(必填)筛选要过滤的客户端ip
--ip1=163.53.89.116:80\t(必填)需要对比的ip及访问端口
--ip2=163.53.89.116:80\t(必填)需要对比的ip及访问端口
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
        print color.red(u'时间区间格式输入有误,正确示例 : 2017050901-2017050903'.encode('utf8'))
        exit()
    try:
        starttime = timerange.split('-')[0]
        endtime = timerange.split('-')[1]
    except:
        print color.red(u'时间区间格式输入有误,正确示例 : 2017050901-2017050903'.encode('utf8'))
        exit()
    try:
        starttime = str(int(starttime)) + '0' * (10 - len(starttime))
        endtime = str(int(endtime)) + '0' * (10 - len(endtime))
    except:
        print color.red(u'时间区间格式输入有误 : 开始时间和结束时间必须都是小于等于10位的时间戳数字 ,正确示例 : 2017050901-2017050903'.encode('utf8'))
        exit()
    if starttime > endtime:
        print color.red(u'开始时间不能大于结束时间'.encode('utf8'))
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
            if ':' in value:
                print u'输入有误，请输入 -h 查看使用方法'.encode('utf-8')
                exit()
            opts_dir['cip'] = value
        elif op == '--ip1':
            if not ':' in value:
                print u'输入有误，请输入 -h 查看使用方法'.encode('utf-8')
                exit()
            opts_dir['ip1'] = value
        elif op == '--ip2':
            if not ':' in value:
                print u'输入有误，请输入 -h 查看使用方法'.encode('utf-8')
                exit()
            opts_dir['ip2'] = value
    if not opts_dir.has_key('ip1') and not opts_dir.has_key('ip1') and  not opts_dir.has_key('cip'):
        print color.red(u'输入参数不全，请添加完整cip，ip1，ip2 ,可输入-h 查看详细帮助信息'.encode('utf8'))
        exit()
    return opts_dir

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

def url_md5(url,ip_port):
    '''返回url的压缩和非压缩MD5值 字典'''
    url_compare_result_dict = {'gzip':'','ungzip':''}
    requests.packages.urllib3.disable_warnings()
    '''设置代理，抓取的url和端口'''
    proxies = {'http':'{0}'.format(ip_port)}
    '''区分http和https抓取方式'''
    if url.split(':')[0] == 'http' :
        try:
            res_gzip = requests.get(url, proxies=proxies, headers={'Accept-Encoding': 'gzip'},timeout=3)
            res = requests.get(url,proxies=proxies,timeout=3)
        except:
            print color.yellow(u'抓取失败，请检查对比ip和访问端口是否正确：{0} ip {1}'.format(url,ip_port).encode('utf8'))
            return 0
    else:
        '''https，取uri，host拼接url'''
        uri = url.split('/',3)[3]
        host = url.split('/',3)[2]
        urls = 'https://{0}/{1}'.format(ip_port,uri)
        try:
            res_gzip = requests.get(urls, verify=False, headers={'Accept-Encoding': 'gzip','Host':host},timeout=3)
            res = requests.get(urls, verify=False,headers={'Host':host},timeout=3)
        except:
            print color.yellow(u'抓取失败，请检查对比ip和访问端口是否正确：{0} host {1}'.format(urls, host).encode('utf8'))
            return 0
    try:
        '''抓取状态码非200，显示提示，异常状态码会影响MD5校验的准确性'''
        res.raise_for_status()
    except:
        print color.yellow(u'抓取非200状态码,MD5一致 提醒：{0} code {1} ip {2}'.format(url,res.status_code,ip_port).encode('utf8'))
    '''非压缩MD5'''
    md5check = hashlib.md5()
    md5check.update(res.content)
    url_compare_result_dict['ungzip'] = md5check.hexdigest()
    '''压缩MD5'''
    md5check = hashlib.md5()
    md5check.update(res_gzip.content)
    url_compare_result_dict['gzip'] = md5check.hexdigest()
    return url_compare_result_dict

if __name__ == '__main__':
    #输出颜色
    color = Colored()
    # 收集脚本参数
    opts_dir = opts_get()
    tc = toolscount(username=opts_dir.get('username'), argv=str(opts_dir))
    # 必要参数补充默认值
    timerange = opts_dir.get('timerange')
    if timerange is None and opts_dir.get('log') is None:
        print u'-t 和 --url= 参数为必填项,-t格式xxx(起始时间)-xxx（结束时间）,--url=http://chinacache.com  如筛选2017年5月10日19点的日志:-t 2017051019-2017051020,使用-h可以查看帮助'.encode('utf8')
        tc.end(0)
        exit()
    url = opts_dir['url']
    app = witchapp()
    logpath = {"Fc": "/data/proclog/log/squid/access/", "Hpcc": "/data/proclog/log/hpc/access/",
               "ATS": "/data/proclog/log/hpc/access/"}.get(app)
    #整合过滤日志的时间
    Time_use = FormatTimerange(opts_dir['timerange'])
    #找到对应时间日志包
    greplogpath = LogTogether(GetFileName(Time_use['starttime'], Time_use['endtime']))
    if not os.path.exists(greplogpath):
        print color.red(u'选中的时间段内没有找到对应日志包,请确认时间段是否有误'.encode('utf8'))
        tc.end(0)
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
                LineItem['Method'] = line.split()[5]
                LineItem['Url'] = line.split()[6]
            except:
                break
            #过滤出匹配客户端ip的数据
            if LineItem['ClientIp'] == opts_dir['cip'] and LineItem['Method'] == 'GET':
                sumnum_mate += 1
                #重复url只记录一次
                if not Compare_url.has_key(LineItem['Url']):
                    Compare_url[LineItem['Url']] = {opts_dir['ip1']:{'gzip':'','ungzip':''},opts_dir['ip2']:{'gzip':'','ungzip':''}}
        if sumnum_mate == 0:
            print color.red(u'没有筛选到符合条件的日志'.encode('utf-8'))
            os.remove(greplogpath)
            tc.end(0)
            exit()
        os.remove(greplogpath)
    print u'开始比对url压缩非压缩MD5值'.encode('utf8')
    #循环对比每个url，键为url，值为对比ip的压缩非压缩字典
    for key,vaule in Compare_url.iteritems():
        url = key
        for ip in vaule.keys():
            #计算对比ip的压缩非压缩MD5，填充字典值
            url_compare_result_dict = url_md5(url, ip)
            #若不是异常退出，则赋值MD5
            if not url_compare_result_dict == 0:
                vaule[ip]['gzip'] = url_compare_result_dict['gzip']
                vaule[ip]['ungzip'] = url_compare_result_dict['ungzip']
    #根据数据结果，对比并展示
    for key,vaule in Compare_url.iteritems():
        keys_list = vaule.keys()
        if not vaule[keys_list[0]]['gzip'] == vaule[keys_list[1]]['gzip']:
            print color.red(u'压缩请求不一致:{0}\n{1}:{2}\n{3}:{4}'.format(key,keys_list[0],vaule[keys_list[0]]['gzip'],keys_list[1],vaule[keys_list[1]]['gzip'])).encode('utf-8')
        if not vaule[keys_list[0]]['ungzip'] == vaule[keys_list[1]]['ungzip']:
            print color.red(u'非压缩请求不一致:{0}\n{1}:{2}\n{3}:{4}'.format(key, keys_list[0], vaule[keys_list[0]]['ungzip'], keys_list[1], vaule[keys_list[1]]['ungzip']))
        else:
            print color.green(u'压缩非压缩验证一致:\t{0}'.format(key).encode('utf-8'))

    tc.end(0)
    exit()