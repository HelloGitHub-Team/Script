#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
#   Author  :   XueWeiHan
#   E-mail  :   595666367@qq.com
#   Date    :   2020-09-29 14:18
#   Desc    :
import os
import time
import re
import requests
flag_url = "gif"
data_file = "vx.txt"
save_pic_dir = "/Users/xueweihan/Desktop/pic/"


def parse_img():
    # 正则表达式
    pattern = re.compile(r'https://mmbiz[^\s]*"')
    with open(data_file, "r") as fb:
        year = 2020
        # 提取图片
        urls = pattern.findall(fb.read())
        for url in urls:
            if flag_url in url:
                year = year - 1
                continue
            file_name = "{}.png".format(year)

            if os.path.exists(save_pic_dir+file_name):
                file_name = "{}_{}.png".format(year, int(time.time()))
            download(file_name, url)
            time.sleep(0.3)
        print("download {} picture.".format(len(urls)))


def download(file_name, url):
    rs = requests.get(url)
    if rs.status_code == 200:
        with open(save_pic_dir + file_name, 'wb+') as f:
            for chunk in rs:
                f.write(chunk)
        print('download {} finish'.format(file_name))
    else:
        print("download: name: {} url:{}, status_code:{} error", file_name, url,
              requests.status_codes)


if __name__ == '__main__':
    parse_img()

