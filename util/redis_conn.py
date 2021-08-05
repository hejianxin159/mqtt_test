# -*- coding: utf-8 -*-
# Author : hejianxin
# Time : 2021/7/13 5:43 下午
import redis
from conf.config import Config


def redis_conn():
    return redis.Redis(host=Config.REDIS_HOST, port=Config.REDIS_PORT, decode_responses=True)


redis_store = redis_conn()
