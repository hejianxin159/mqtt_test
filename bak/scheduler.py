# -*- coding: utf-8 -*-
# Author : hejianxin
# Time : 2021/6/21 9:08 上午
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from flask import Flask
from flask_apscheduler import APScheduler


class Config(object):
    # 配置执行job
    # JOBS = [
    #     {
    #         'id': 'job1',
    #         'func': 'scheduler:job1',
    #         'args': (1, 2),
    #         'trigger': 'interval',
    #         'seconds': 10
    #     }
    # ]
    # 存储位置
    # SCHEDULER_JOBSTORES = {
    #     'default': SQLAlchemyJobStore(url='sqlite://')
    # }
    # 线程池配置
    SCHEDULER_EXECUTORS = {
        'default': {'type': 'threadpool', 'max_workers': 20}
    }

    SCHEDULER_JOB_DEFAULTS = {
        'coalesce': False,
        'max_instances': 3
    }
    # 调度器开关
    SCHEDULER_API_ENABLED = True


def job1(a, b):
    print(str(a) + ' ' + str(b))


if __name__ == '__main__':
    app = Flask(__name__)
    app.config.from_object(Config())

    scheduler = APScheduler()
    # 注册app
    scheduler.init_app(app)
    scheduler.start()

    app.run()


# import requests
# import time
# add_url = 'http://127.0.0.1:5000/scheduler/jobs'
# delete_url = 'http://127.0.0.1:5000/scheduler/jobs/114'
#
# #
# # data = {
# #         'id': '111',
# #         'func': 'BGPScheduler:bgp_job_func',
# #         'trigger': 'interval',
# #         'seconds': 4,
# #         'args': {'name': 'name'}
# # }
#
# #未对称发布
# data_bgp_job_func = {
#         'id': '111',
#         'func': 'BGPScheduler:bgp_job_func',
#         'trigger': 'cron',
#         'hour': 6,
# }
# a = requests.post(add_url, json=data_bgp_job_func).text
# print(a)
#
# #med异常
# data_med = {
#         'id': '112',
#         'func': 'BGPScheduler:med_error',
#         'trigger': 'cron',
#         'hour': 8,
# }
# b = requests.post(add_url, json=data_med).text
# print(b)
#
# #originator_id异常
# data_originator = {
#         'id': '113  ',
#         'func': 'BGPScheduler:originator_id',
#         'trigger': 'cron',
#         'hour': 7,
# }
# c = requests.post(add_url, json=data_originator).text
# print c
#
#
# data_flow = {
#         'id': '114',
#         'func':'IGPScheduler:get_scheduler_flow',
#         'trigger': 'interval',
#         'minutes': 5,
# }
# d = requests.post(add_url, json=data_flow).text
# print d
#
#
#
