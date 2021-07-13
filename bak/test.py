# -*- coding: utf-8 -*-
# Author : hejianxin
# Time : 2021/6/23 2:32 下午
import requests
data = {
        'id': '111',
        'func': 'scheduler:job1',
        'trigger': 'interval',
        'seconds': 4,
        'args': (1, 2),
}


res = requests.post("http://127.0.0.1:5000/scheduler/jobs", json=data)
print(res.text)
