#!/opt/hopeservice/.venv/bin/python
# -*- coding: utf-8 -*-
# @Time    : 07/02/2018 16:12
# @Author  : yao.liu
# @File    : tta_orign_conf.py

import os
import re
import sys

def seek_tta_orign(host):
    if os.path.exists('/usr/local/haproxy/etc/haproxy.cfg'):
        flag = 0
        with open('/usr/local/haproxy/etc/haproxy.cfg','r') as fn:
            result_dict = {}
            for line in fn.readlines():
                check_ignore = re.search(r'#p',line)
                if not check_ignore:
                    #注释内容不处理
                    if flag == 0:
                        #回源配置文件开始读取标志
                        match = re.search(host,line)
                        if match:
                            flag = 1
                    elif flag == 1:
                        #访问端口开始读取标志
                        match = re.search('bind',line)
                        if match:
                            ip_port = line.strip().split(' ')[1]
                            if not result_dict.has_key(ip_port):
                                result_dict[ip_port] = {}
                            flag = 2
                    elif flag == 2 :
                        #域名回源配置文件开始读取标志
                        match = re.search('backup',line)
                        if not match:
                            #处理上层配置信息
                            IP = line.strip().split(' ')[1]
                            if not result_dict[ip_port].has_key(IP):
                                result_dict[ip_port][IP] = {}
                            result_dict[ip_port][IP] = line.strip().split(' ')[2]
                        else:
                            #处理回源配置信息
                            result_dict[ip_port]['src'] = line.strip().split(' ')[2]
                            flag = 3
                    elif flag == 3:
                        #读取完成该访问端口类型
                        flag = 0
    else:
        return '未找到配置文件，请手动确认/usr/local/sms/conf/nginx.conf '
    #遍历完成，返回结果字典
    return result_dict

if __name__ == '__main__':
    host = sys.argv[1]
    result = seek_tta_orign(host)
    print result
