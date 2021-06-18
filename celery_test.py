# -*- coding: utf-8 -*-
# Author : hejianxin
# Time : 2021/6/17 4:43 下午

from celery_task.celery_task import subscrible_all, is_online_subscrible, subscrible_business
client_id = "75b994c0-578b65a4"


# subscrible_all.delay()
import copy
client_list = []
# subscrible_business.delay(client_id)
# subscrible_business.delay(client_id)
# subscrible_business.delay(client_id)
for i in range(200):
    subscrible_business.delay(client_id)
# subscrible_all.delay()
