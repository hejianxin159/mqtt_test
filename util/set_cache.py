# -*- coding: utf-8 -*-
# Author : hejianxin
# Time : 2021/7/14 11:48 上午
from util.redis_conn import redis_store
import time
import datetime


def set_clock_cache(person_resource_id, clock_resource_id):
    # 设置clock in缓存，当天24点过期
    now_time = datetime.datetime.now()
    now_seconds = time.mktime(now_time.timetuple())
    expire_time = datetime.datetime.strptime(f"{now_time.year}-{now_time.month}-{now_time.day} 23:59:59",
                                             "%Y-%m-%d %H:%M:%S")
    expire_seconds = time.mktime(expire_time.timetuple())
    redis_store.set(person_resource_id,
                    clock_resource_id)
    redis_store.expire(person_resource_id, int(expire_seconds + 1 - now_seconds))
