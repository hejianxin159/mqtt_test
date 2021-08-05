# -*- coding: utf-8 -*-
# Author : hejianxin
# Time : 2021/6/21 9:08 上午
from flask import Flask
from flask_apscheduler import APScheduler
from conf.config import Config
from models.models import db_session, MqttTask


scheduler = APScheduler()

app = Flask(__name__)


def check_task(task_id):
    task = db_session.query(MqttTask).filter(MqttTask.id == task_id).first()
    if not task:
        return
    if task.task_status == 3:
        task.task_status = 2
        db_session.add(task)
    db_session.commit()


if __name__ == '__main__':
    scheduler.api_enabled = True
    scheduler.init_app(app)
    scheduler.start()
    app.run(debug=True, host=Config.SCHEDULER_HOST, port=Config.SCHEDULER_PORT)
