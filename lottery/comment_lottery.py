#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
#   Author  :   XueWeiHan
#   E-mail  :   595666367@qq.com
#   Date    :   2020-10-16 23:42
#   Desc    :   微信留言抽奖
import datetime
import random

import pandas as pd

print("开始抽奖的时间：{}".format(datetime.datetime.now()))
df = pd.read_excel("/Users/xueweihan/Downloads/HelloGitHub.xlsx")
print("留言总数：{}".format(len(df)))
name_set = set(df["留言者昵称"])
print("留言总人数：{}".format(len(name_set)))
if "HelloGitHub" in name_set:
    name_set.remove("HelloGitHub")
print("参与抽奖人数：{}".format(len(name_set)))
# choices 有放回，sample 无放回
result = random.sample(name_set, 5)
print("中奖用户：{}".format("、".join(result)))
print("结束抽奖时间：{}".format(datetime.datetime.now()))