#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
#   Author  :   XueWeiHan
#   E-mail  :   595666367@qq.com
#   Date    :   2019-12-28
#   Desc    :   刷新本机 DNS 加速访问 GitHub 速度、解决图裂的问题
import requests


# content = requests.get('https://github.com/521xueweihan/HelloGitHub')
# content

# import dns.resolver
#
# myResolver = dns.resolver.Resolver()
# myResolver.nameservers = ['180.76.76.76', '223.6.6.6']
# myAnswers = myResolver.query("github.githubassets.com", "A")
# for rdata in myAnswers:
#     print(rdata)
#
import socket

def getip():
    sock = socket.create_connection(('ns1.dnspod.net', 6666), 20)
    ip = sock.recv(16)
    sock.close()
    return ip
getip()