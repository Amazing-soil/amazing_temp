#!/opt/hopeservice/.venv/bin/python
# -*- coding: utf-8 -*-
# @Time    : 01/31/2018 16:12
# @Author  : yao.liu
# @File    : sms_orign_conf.py


import requests
import json

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

def dispaly_sms(result_dict):
    color = Colored()
    print type(result_dict)
    if not isinstance(result_dict,dict):
        result_dict = eval(result_dict)
    print type(result_dict)
    print color.green('{0:<15}{1:<20}{2:<20}{3:<10}'.format(u'方式'.encode('utf8'),
                                                            u'目标ip'.encode('utf8'),
                                                            u'回源域名'.encode('utf8'),
                                                            u'权重系数'.encode('utf8'),
                                                            ))
    ip = result_dict.keys()[0]
    print '{0:<10}{1:<20}{2:<20}{3:<10}'.format(result_dict[ip]['methods'],
                                                ip,
                                                result_dict[ip]['vhost'],
                                                result_dict[ip]['weight'],
                                                            )

second = str({'116.211.123.6': {'vhost': 'live.kksmg.com', 'methods': 'pull', 'weight': '1'}})
dispaly_sms(eval(second))