# -*- coding: utf-8 -*-
# Author : hejianxin
# Time : 2021/7/13 11:05 上午
import requests
import uuid
from conf.config import Config
import datetime


for task_id in range(1, 3):
    run_date = datetime.datetime.now() + datetime.timedelta(seconds=10)
    json_data = {
        "id": str(uuid.uuid4()),
        "func": "scheduler:check_task",
        "trigger": "date",
        "run_date": run_date.strftime("%Y-%m-%d %H:%M:%S"),
        "kwargs": {"task_id": task_id}
    }
    print(requests.post(f"http://{Config.SCHEDULER_HOST}:{Config.SCHEDULER_PORT}/scheduler/jobs", json=json_data).content)
