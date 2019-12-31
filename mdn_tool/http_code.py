#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
#   Author  :   XueWeiHan
#   E-mail  :   595666367@qq.com
#   Date    :   2019-12-31
#   Desc    :   查询 HTTP code 解释
import json
import textwrap

import fire


def read_file(file_name):
    with open(file_name, 'r', encoding='utf-8') as fb:
        file_data = fb.read()
        status_code_data = json.loads(file_data)
    return status_code_data


STATUS_CODE = read_file('status_code.json')
STATUS_CODE_TEMPLATE = """
\x1b[1m\x1b[36m{code} {info}\x1b[0m\x1b[0m
\x1b[32m{desc}\x1b[0m
"""[1:]


class StatusCode(object):
    def __init__(self, code=0, info=''):
        self.code = str(code)
        self.info = info.upper()
    
    def message(self):
        info_list = STATUS_CODE.values()
        for info_item in info_list:
            data_list = info_item['item_list']
            for fi_data in data_list:
                desc = fi_data['description']
                desc = textwrap.fill(desc, 30)
                if self.code == fi_data['number'] or self.info == fi_data[
                    'info']:
                    result = STATUS_CODE_TEMPLATE.format(
                        code=fi_data['number'], info=fi_data['info'],
                        desc=desc)
                    return result
        
        else:
            return '\x1b[31m未查到 {} 对应信息。\x1b[0m'.format(self.code)


if __name__ == '__main__':
    fire.Fire(StatusCode)
