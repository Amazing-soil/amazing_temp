#!/opt/hopeservice/.venv/bin/python
# -*- coding: utf-8 -*-
# @Time    : 01/02/2018 11:12
# @Author  : yao.liu
# @File    : tools_sms_orign.py
__author__ = 'yao.liu'
__version__ = 'v1.2'
__scriptname__ = 'tools_sms_orign.py'

import requests
import sys
import os
import getopt
import re
import json


reload(sys)
sys.setdefaultencoding('utf8')
helptext = u'''
bre 设备对应频道查找回源配置，并联动查找下一层回源配置
支持参数：
-h \t输出帮助信息
--host=\t(必填)查询指定频道的回源流
程序支持:bre自动化运维组<bre-ops-dev@chinacache.com>
'''

def ccip_switch_dev(ip):
    '''是蓝汛ip返回设备名,否则返回False'''
    url = 'http://223.202.204.189:81/AACode/isccdevice/'
    data = {'ip':'{0}'.format(ip)}
    res = requests.post(url,data=data)
    if res.json().has_key('msg'):
        return False
    else:
        return res.json().get("dn")

def sms_conf_seek(dev,host):
    #调用django接口，联动设备查配置
    print '正在联动查找上层回源配置，调用salt受网络影响，请耐心等待'
    headers = {'content-type': 'application/x-www-form-urlencoded'}
    url = 'http://223.202.204.189:81/Amazing61/sms_orign_ip/'
    data = { "vhost":host,"dev":dev }
    res = requests.post(url,data=data,headers=headers)
    if res.status_code == 200:
        try:
            return res.json()[dev]
        except:
            print '无法读取设备配置{0}，请手动确认设备是否可用'.format(data.get('dev'))
            return False
    else:
        return False

def seek_sms_orign(host):
    if os.path.exists('/usr/local/sms/conf/nginx.conf'):
        flag = 0
        with open('/usr/local/sms/conf/nginx.conf','r') as fn:
            result_dict = {}
            for line in fn.readlines():
                check_ignore = re.search(r'#p',line)
                if not check_ignore:
                    #注释内容不处理
                    if flag == 0:
                        #回源配置文件开始读取标志
                        match = re.search('listen 1935',line)
                        if match:
                            flag = 1
                    elif flag == 1:
                        #域名配置文件开始读取标志
                        match = re.search(host,line)
                        if match:
                            flag = 2
                    elif flag == 2 :
                        #流配置文件开始读取标志
                        match = re.search('rtmp://',line)
                        match_end = re.search('}',line)
                        if match:
                            #处理记录数据
                            i_pretty = line.lstrip()
                            ip = i_pretty.split('/')[2].split(' ')[0]
                            result_dict[ip] = {'vhost': '', 'methods': '', 'weight': 0}
                            if re.search('vhost=',i_pretty):
                                result_dict[ip]['vhost'] = i_pretty.split('vhost=')[1].split(' ')[0]
                            else:
                                result_dict[ip]['vhost'] = ip
                            result_dict[ip]['methods'] = i_pretty.split(' ')[0]
                            if re.search('weight=',i_pretty):
                                for w_i in i_pretty.split(' '):
                                    if 'weight' in w_i:
                                        result_dict[ip]['weight'] = w_i.split('=')[1]
                            else:
                                result_dict[ip]['weight'] = '0'
                        elif match_end:
                            flag = 3
                    elif flag == 3:
                        # 读取完成，返回数据，退出函数
                        return result_dict
    else:
        return '未找到配置文件，请手动确认/usr/local/sms/conf/nginx.conf '

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

def dispaly_sms(result_dict):
    #传入参数为字典，格式如：{'180.97.183.224': {'vhost': 'downvideo.cguoguo.com', 'methods': 'pull', 'weight': '2'}}
    print color.green('{0:<15}{1:<20}{2:<30}{3:<10}'.format(u'方式'.encode('utf8'),
                                                            u'目标ip'.encode('utf8'),
                                                            u'回源域名'.encode('utf8'),
                                                            u'权重系数'.encode('utf8'),
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
    color = Colored()
    #查询本机配置
    first_lay = seek_sms_orign(host)
    if not first_lay:
        print color.red('没有该频道配置，请检查')
        exit()
    print color.yellow(u'本机配置：'.encode('utf8'))
    for k,v in first_lay.items():
        i_dict = {k:v}
        #展示函数参数字典需求
        dispaly_sms(i_dict)
    ip1 = first_lay.keys()[0]
    #判断回源方式是否为pull，push不联动查询
    if first_lay[ip1]['methods'] == 'pull':
        #判断回源ip是否我方，我方则联动查询
        if ccip_switch_dev(ip1):
            print color.yellow(u'上游配置：'.encode('utf8'))
            #根据ip返回设备名
            dev_name = ccip_switch_dev(ip1)
            #查找第二层配置
            second_lay = sms_conf_seek(dev_name, first_lay[ip1]['vhost'])
            if second_lay:
                second_lay = eval(second_lay)
                try:
                    for k,v in second_lay.items():
                        i_dict = {k:v}
                        #展示函数参数字典需求
                        dispaly_sms(i_dict)
                except:
                    print '联动上层查找配置时，发现上层没有同步最新的自动化工具路径，请手动确认'
            else:
                print '上游联动失败，可能是网络问题，可能是上游设备未部署salt，请手动确认，并通知自动化运维组'
        else:
            print '查询结束，上游非蓝汛ip'
    else:
        print '查询结束，push推流，不联动查询'