# -*- coding: utf-8 -*-
# Author : hejianxin
# Time : 2021/7/14 11:47 上午
from util.set_cache import redis_store, set_clock_cache
import datetime
from models.models import db_session, NewClockIn, Camera, ClockRecord


def update_work_time():
    # 自动同步时间
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    # today = "2021-05-14"
    yesterday = (datetime.datetime.strptime(today, "%Y-%m-%d") - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    for yesterday_info in db_session.query(NewClockIn).filter(NewClockIn.work_time == yesterday):
        # 昨天的数据
        if yesterday_info.out_time == None:
            # 查找今天是否有数据
            today_obj = db_session.query(NewClockIn).filter(NewClockIn.labour_roster == yesterday_info.labour_roster,
                                                            NewClockIn.work_time == today).first()
            if today_obj:
                # 今天有数据且今天的in有数据，昨天的数据有问题，修改状态
                if today_obj.in_time:
                    yesterday_info.status = "error"
                continue
            clock_obj = NewClockIn.objects.create(
                work_time=today,
                type=yesterday_info.type,
                labour_roster=yesterday_info.resource_id,
                in_time=yesterday_info.in_time,
                jet_lag=1,
            )
            # 设置缓存key
            set_clock_cache(yesterday_info.resource_id, clock_obj.id)


def clock_record(data):
    # 打卡考勤记录
    body = data["body"]
    # 人员resource id
    person_resource_id = body["per_id"]
    camera_sn = body["sn"]
    # 人员类型
    user_type = PersonType.objects.filter(labour_roster=person_resource_id).first()
    # clock in 的resource id
    query_resource_id = redis_store.get(person_resource_id)
    if not user_type:
        return
    camera = Camera.objects.filter(sn=camera_sn).first()
    if not camera:
        return
    # 校验数据
    # 如果找不到缓存key
    now = datetime.datetime.now()
    today = now.strftime("%Y-%m-%d")
    if not query_resource_id:
        clock_obj = NewClockIn.objects.filter(labour_roster=person_resource_id,
                                              work_time=today).first()
        # 没有数据的情况下
        if not clock_obj:
            clock_obj = NewClockIn(
                work_time=today,
                type=user_type.type,
                labour_roster=person_resource_id,
                jet_lag=1,
            )
        if camera.direction == 0 and not clock_obj:
            # 没有数据且摄像头为进入
            clock_obj.in_time = now
        else:
            # 修改out数据
            clock_obj.out_time = now
        clock_obj.save()
        # 设置缓存
        set_clock_cache(person_resource_id, clock_obj.id)
    else:
        clock_obj = NewClockIn.objects.filter(resource_id=query_resource_id,
                                              work_time=today).first()
        if camera.direction == 1:
            clock_obj.out_time = datetime.datetime.now()
        else:
            # 如果为in且in的数据不是今天的的就报错
            if clock_obj.in_time.strftime("%Y-%m-%d") != today:
                NewClockIn.objects.filter(labour_roster=person_resource_id,
                                          work_time=clock_obj.work_time - datetime.timedelta(days=1)).update(
                    {
                        "clock_status": "ERROR"
                    }
                )
                clock_obj.in_time = now
        clock_obj.save()
    # 存储流水数据
    ClockRecord.objects.create(
        work_time=today,
        type=user_type.type,
        direction=0 if camera.direction == "IN" else 1,
        punch_clock_time=now
    )


data = {
    "type": "face_result",
    "flag": "offline_face_result",
    "body": {
        "e_imgurl": "http:com/20190907/8080078b-c30d4f7b_1567816001_95_101.jpg",
        "e_imgsize": 159792,
        "matched": 95,
        "name": "k",
        "per_id": "ff928524d374455199d6d87b41d5f8bd",
        "role": 1,
        "usec": 1567816001,
        "idcard": "fffffffffffffff",
        "sn": "ffffffff",
        "hat": 1,
        "mask": 1,
        "tep": 37.23,
        "img_data": "base64数据",
        "per_id_base64": "ffffffffff",
        "name_base64": "ffffffff"
    }
}

clock_record(data)

