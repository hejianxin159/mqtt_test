# -*- coding: utf-8 -*-
# Author : hejianxin
# Time : 2021/6/17 5:37 下午
class Config:
    DB_USER = "root"
    DB_PASSWORD = "123456"
    DB_HOST = "10.28.25.213"
    DB_PORT = 3306
    RESOURCE_DB_NAME = "rc_app"

    IMAGE_PREFIX = 'http://10.28.25.213/f/'
    SOURCE_FILE_DIR_PREFIX = "/opt/rc-app/api/data/thumbnail"
    REMOTE_FILE_DIR_PREFIX = "/opt/rc-app/api/data/face"

    SCHEDULER_HOST = "127.0.0.1"
    SCHEDULER_PORT = 5000

    MQTT_HOST = "10.28.25.213"
    MQTT_PORT = 1883
    MQTT_USERNAME = "netmon"
    MQTT_PASSWORD = "netmon"

    REDIS_HOST = "10.28.25.213"
    REDIS_PORT = 6379
