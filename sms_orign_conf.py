#!/opt/hopeservice/.venv/bin/python
# -*- coding: utf-8 -*-
# @Time    : 01/31/2018 16:12
# @Author  : yao.liu
# @File    : sms_orign_conf.py

import os
import re
import sys

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
                            ip = i_pretty.split('/')[2]
                            result_dict[ip] = {'vhost': '', 'methods': '', 'weight': 0}
                            result_dict[ip]['vhost'] = i_pretty.split('vhost=')[1].split(' ')[0]
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

if __name__ == '__main__':
    host = sys.argv[1]
    result = seek_sms_orign(host)
    print result

