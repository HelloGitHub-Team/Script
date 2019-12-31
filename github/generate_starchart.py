#!/usr/bin/env python
# -*- coding:utf-8 -*-
#   
#   Author  :   XueWeiHan
#   E-mail  :   595666367@qq.com
#   Date    :   2019-09-18 22:45
#   Desc    :   生成星图脚本
import time
import datetime
from collections import OrderedDict

import pygal
from pygal.style import Style
import requests


class GitHubRepositories(object):
    def __init__(self, name, token, per_page=100, max_star_limit=10000,
                 min_star_limit=10, create_days_limit=10, mode='count',
                 time_node_count=1):
        self.name = name
        self.token = token
        self.limit_remaining = 0
        self.reset_limit_time = None
        self.per_page = per_page
        self.info = None
        self.stargazers = set()
        self.max_star_limit = max_star_limit
        self.min_star_limit = min_star_limit
        self.create_days_limit = create_days_limit
        self.star_map = OrderedDict()
        self.days_count = None
        self.mode = mode  # 展示star总和('count'), 还是star的增量('change')
        self.time_node_count = time_node_count
        self.x_node_list = None  # x轴为时间
        self.y_node_list = None  # y轴为数量
        # 默认为当前时间
        self.max_date_str = datetime.datetime.now().strftime('%Y-%m-%d')
        # 项目创建时间
        self.min_date_str = None
        # 停止请求数据
        self.end_request = False
        self.interval_days = None  # 显示x轴的时间两个点应相隔几天

    @property
    def headers(self):
        # token 授权
        return {
            'Authorization': 'token {}'.format(self.token)
        }

    @staticmethod
    def fix_time(time_str, rtype='time'):
        # github 返回的时间是 ISO 8601 规则的时间（0时区），下面转化成北京时间（+8时区）
        epoch_time = datetime.datetime.strptime(time_str,
                                                '%Y-%m-%dT%H:%M:%SZ')
        epoch_time = epoch_time + datetime.timedelta(hours=8)
        if rtype == 'time':
            epoch_time_str = epoch_time.date().strftime('%Y-%m-%d %H:%M:%S')
        else:
            epoch_time_str = epoch_time.date().strftime('%Y-%m-%d')
        return epoch_time_str

    def get_repo_info(self):
        url = 'https://api.github.com/repos/{}'.format(self.name)
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            self.limit_remaining = int(response.headers['X-RateLimit-Remaining'])
            self.reset_limit_time = datetime.datetime.fromtimestamp(
                int(response.headers['X-RateLimit-Reset'])).strftime(
                "%Y-%m-%d %H:%M:%S")
            self.info = response.json()
            # 项目名字标准化
            self.name = self.info['full_name']
            # 把info中的时间转化成北京时间
            self.min_date_str = self.fix_time(self.info['created_at'],
                                              rtype='date')
            self.info['created_at'] = self.fix_time(self.info['created_at'])
            self.info['updated_at'] = self.fix_time(self.info['updated_at'])
            self.info['pushed_at'] = self.fix_time(self.info['pushed_at'])

    def generate_all_stargazers_urls(self):
        """
        请求所有的 stargazers api url
        """
        all_stargazers_urls = []
        stargazers_count = self.info['stargazers_count']
        stargazers_url_format = 'https://api.github.com/repos/{}/stargazers?' \
                                'page={}&per_page={}'
        page_count = int(stargazers_count / self.per_page) + 1
        for i in range(1, page_count + 1):
            all_stargazers_urls.append(stargazers_url_format.format(
                self.name, i, self.per_page))
        return all_stargazers_urls

    def parse_stargazers_data(self, stargazers_data):
        for fi_data in stargazers_data:
            # 根据 star 时间数据聚合到天
            epoch_date_str = self.fix_time(fi_data['starred_at'], 'date')
            epoch_date = datetime.datetime.strptime(epoch_date_str, '%Y-%m-%d')
            max_date = datetime.datetime.strptime(self.max_date_str, '%Y-%m-%d')
            if epoch_date > max_date:
                self.end_request = True
                break
            self.stargazers.add(fi_data['user']['id'])
            if epoch_date_str in self.star_map:
                self.star_map[epoch_date_str] += 1
            else:
                self.star_map[epoch_date_str] = 1

    def get_stargazer(self, req_s, url, headers):
        rs = req_s.get(url, headers=headers)
        self.parse_stargazers_data(rs.json())

    def get_all_stargazers(self):
        """
        请求所有的 stargazers api url
        """
        all_stargazers_urls = self.generate_all_stargazers_urls()
        if self.limit_remaining < len(all_stargazers_urls):
            msg = '当前时次请求数量超出'
            print(msg)
            raise Exception(msg)
        else:
            self.limit_remaining -= len(all_stargazers_urls)
        headers = self.headers
        headers['Accept'] = 'application/vnd.github.v3.star+json'
        s = requests.session()
        for stargazers_url in all_stargazers_urls:
            if not self.end_request:
                print(stargazers_url, self.end_request)
                self.get_stargazer(s, stargazers_url, headers)
        # lock = threading.Lock()
        # threads = [threading.Thread(target=self.get_stargazer,
        #                             args=(s, stargazers_url, headers, lock))
        #            for stargazers_url in all_stargazers_urls]
        # [thread.start() for thread in threads]
        # [thread.join() for thread in threads]
        # del s
        print('request limit remaining: {}'.format(self.limit_remaining))

    def make_time_node(self):
        max_date = datetime.datetime.strptime(self.max_date_str, '%Y-%m-%d')
        min_date = datetime.datetime.strptime(self.min_date_str, '%Y-%m-%d')
        date_list = [self.min_date_str]
        self.days_count = (max_date - min_date).days  # 该项目共创建了多少天
        self.interval_days = self.days_count / self.time_node_count
        flag_date = max_date - datetime.timedelta(days=self.interval_days)
        tmp_date = min_date
        # 生成所有的 x_node(时间节点)
        while tmp_date < flag_date:
            date_node = tmp_date + datetime.timedelta(days=self.interval_days)
            tmp_date = date_node
            date_list.append(date_node.strftime('%Y-%m-%d'))
        date_list.append(self.max_date_str)
        self.x_node_list = date_list

    def make_value_node(self):
        min_date = datetime.datetime.strptime(self.min_date_str, '%Y-%m-%d')
        # 初始化结果dict，防止某段时间的数为空造成异常
        result_data = {date_node: 0 for date_node in self.x_node_list}
        for k, v in self.star_map.items():
            starred_datetime = datetime.datetime.strptime(k, '%Y-%m-%d')
            # 把原始数据的日期对应到node轴，并把value累加（原始数据聚合到x轴的量级）
            date_index = int((starred_datetime - min_date).days / self.interval_days)
            if (starred_datetime - min_date).days % self.interval_days:
                date_index += 1
            result_k = self.x_node_list[date_index]
            result_data[result_k] += v

        if self.mode == 'count':
            # 某x轴上日期时的star总数
            for index, x_node in enumerate(self.x_node_list):
                if index != 0:
                    result_data[x_node] += result_data[
                        self.x_node_list[index - 1]]

        self.y_node_list = [result_data[fi_x_node] for fi_x_node in
            self.x_node_list]

    def init(self):
        start_time = time.time()
        self.get_repo_info()
        error_msg = '项目名称：{}，生成失败原因：'.format(self.name)
        if self.info:
            created_datetime = datetime.datetime.strptime(
                self.info['created_at'], '%Y-%m-%d %H:%M:%S')
            created_days = (datetime.datetime.now() - created_datetime).days
            if created_days < self.create_days_limit:
                error_msg += '不支持创建天数小于 {} 天的项目'.format(self.create_days_limit)
                raise Exception(error_msg)
            elif self.info['stargazers_count'] > self.max_star_limit:
                error_msg += '暂不支持 star 数量大于 {} 的项目'.format(self.max_star_limit)
                raise Exception(error_msg)
            elif self.info['stargazers_count'] < self.min_star_limit:
                error_msg += '暂不支持 star 数量小于 {} 的项目'.format(self.min_star_limit)
                raise Exception(error_msg)
            elif not self.limit_remaining:
                error_msg += '（测试阶段）请求数达到限制次数'
                raise Exception(error_msg)
            else:
                try:
                    self.get_all_stargazers()
                    self.make_time_node()
                    self.make_value_node()
                except Exception as e:
                    raise e
        else:
            error_msg += '未找到项目'
            raise Exception(error_msg)
        print('Get {} data speed time: {}'.format(
            self.name, time.time() - start_time))


class GenerateStarSVG(object):
    @staticmethod
    def make_svg(svg_type, x_nodes, y_nodes):
        # 参数分别修改：x轴描述旋转角度、圆角、颜色（Python 蓝）
        line_chart = pygal.Line(x_label_rotation=20, tooltip_border_radius=10,
                                background='transparent',
                                plot_background='transparent',
                                style=Style(colors=('#376fa0',)))
        line_chart.x_labels = x_nodes
        line_chart.add("Star", y_nodes)
        if svg_type == 'uri':
            return line_chart.render_data_uri()
        elif svg_type == 'svg':
            line_chart.render_to_file('local.svg')


def main(config, repo_name='521xueweihan/HelloGitHub'):
    _g = GitHubRepositories(repo_name, config['token'],
                            per_page=config['per_page'],
                            max_star_limit=config['max_star_limit'],
                            min_star_limit=config['min_star_limit'],
                            create_days_limit=config['create_days_limit'])
    _g.init()
    starchart = {
        'repo_name': _g.info['full_name'],
        'repo_url': _g.info['html_url'],
        'repo_created_at': _g.info['created_at'],
        'days_count': _g.days_count,
        'star_count': len(_g.stargazers),
        'y_nodes': _g.y_node_list,
        'x_nodes': _g.x_node_list,
        'create_time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    return starchart


if __name__ == '__main__':
    config = {
        'token': 'xxxx',
        'per_page': 100,
        'max_star_limit': 200000,
        'min_star_limit': 10,
        'create_days_limit': 10,
    }
    g = GitHubRepositories('username/project_name', config['token'],
                           per_page=config['per_page'],
                           max_star_limit=config['max_star_limit'],
                           min_star_limit=config['min_star_limit'],
                           create_days_limit=config['create_days_limit'])
    g.init()
    svg = GenerateStarSVG()
    svg.make_svg('svg', g.x_node_list, g.y_node_list)

