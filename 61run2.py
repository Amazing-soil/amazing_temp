#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 20/12/2017 16:12
# @Author  : yao.liu
# @File    : 61run2.py

a = range(1,9)
j = 0
k = 0
c = len(a)
def amazing(a,j,k,c):
    if j < c:
        for i in a:
            print a
            print i,
            a.remove(i)
            j += 1
        return amazing(a,j,k,c)
    else:
        if k < c:
            k += 1
            b = a[0]
            a.remove(b)
            a.append(b)
            return amazing(a,j,k,c)
        else:
            print 'end'

amazing(a,j,k,c)

