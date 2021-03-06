# -*- coding: utf-8 -*-
# Author : hejianxin
# Time : 2021/6/17 5:37 下午
import datetime
from conf.config import Config
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, SmallInteger, DateTime, func, Boolean, Float, Date
import uuid
from sqlalchemy.orm import sessionmaker, scoped_session


engine = create_engine(
    f"mysql+pymysql://{Config.DB_USER}:{Config.DB_PASSWORD}@{Config.DB_HOST}:{Config.DB_PORT}/{Config.RESOURCE_DB_NAME}",

)
db_session = sessionmaker(bind=engine)
db_session = scoped_session(db_session)

callback_session = sessionmaker(bind=engine)
callback_session = callback_session()
Base = declarative_base()


def gen_id():
    return uuid.uuid4().hex


class Camera(Base):
    """相机"""
    __tablename__ = "camera_camera"

    id = Column(Integer, autoincrement=True, primary_key=True)
    resource_id = Column(String(36), default=gen_id)
    project_id = Column(String(36), nullable=True)
    name = Column(String(50), nullable=True)    # 设备名称
    device_no = Column(String(40), nullable=True)  # 设备编号（关联具体设备）
    camera_status = Column(SmallInteger)  # 0:未启用、1：启用、2：初始启用、待完全同步
    type = Column(SmallInteger, default=0)  # 0 施工区 1 办公区
    online = Column(SmallInteger, default=0)  # 0离线 1在线
    direction = Column(SmallInteger, default=0)  # 业务数据 (0：进场、1：出场)
    status = Column(SmallInteger, default=1)
    created_time = Column(DateTime, default=datetime.datetime.now)
    modified_time = Column(DateTime, default=datetime.datetime.now)


class Attachment(Base):
    __tablename__ = "attachment"

    id = Column(String(32), default=gen_id, primary_key=True)
    project_id = Column(String(32), nullable=True)

    top_parent_id = Column(String(32), nullable=True)  # 顶级父ID (顶级目录的top_parent_id为None)
    parent_id = Column(String(32), nullable=True)  # 直接父级ID (顶级目录的parent_id为None)
    creator_id = Column(String(32), nullable=True)  # 创建人ID
    name = Column(String(300), nullable=False, default='')  # 文件或目录名称
    path = Column(String(500), nullable=True)  # 文件或目录在磁盘上的路径(目录原则上没有path，即根目录)

    is_root = Column(Boolean, default=True)  # 是否是顶级目录(参与权限控制) 不需要是否可以删除的字段,顶级目录不可删除
    is_dir = Column(Boolean, default=False)  # 是否为文件夹(True: 文件夹; False: 文件)
    is_img = Column(Boolean, default=False)  # 是否为图片(True: 文件夹; False: 文件)
    file_type = Column(String(20), nullable=False, default='')  # 文件类型
    size = Column(String(20), nullable=False, default='')  # 文件大小
    pixel_w = Column(Integer, nullable=False, default=0)  # 像素(px), 宽
    pixel_h = Column(Integer, nullable=False, default=0)  # 像素(px), 高
    from_date = Column(DateTime, default=datetime.datetime.now)
    update_date = Column(DateTime, default=datetime.datetime.now)
    remark = Column(String(300), nullable=False, default='')  # 备注


class MqttTask(Base):
    __tablename__ = "mqtt_task"

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(String(36), nullable=True)
    person_resource = Column(String(36))                # 关联花名册人
    person_type = Column(SmallInteger, default=0)       # 0 roster 1 staff  2 访客
    person_name = Column(String(32), nullable=True)     # 人员名字
    work_type = Column(String(32), nullable=True)       # 岗位， 工种
    attachment_id = Column(String(36), nullable=True)   # 图片的id
    camera_id = Column(String(36), nullable=True)       # 相机的uuid
    task_status = Column(SmallInteger, default=0)       # 0未操作 1 成功 2 失败 3 操作中
    picture_status = Column(SmallInteger, default=0)    # 0 未操作 1 新增 2 更新
    status = Column(SmallInteger, default=1)            # 数据状态
    operate_code = Column(String(8), nullable=True)     # 操作状态码
    operate_remark = Column(String(64), nullable=True)  # 操作信息
    create_time = Column(DateTime, default=datetime.datetime.now)   # 创建时间

    def delete_horizontal(self):
        return self.person_resource.replace('-', '')


WORKER_TYPE = (
    (0, 'LABOUR'),
    (1, 'VISITOR'),
    (2, 'STAFF'),
)


def today():
    return datetime.datetime.now().date().strftime("%Y-%m-%d")


class NewClockIn(Base):
    __tablename__ = "new_clock_in"
    """劳务上下工"""
    id = Column(Integer, primary_key=True, autoincrement=True)
    status = Column(SmallInteger, default=1)
    project_id = Column(String(36), nullable=True)
    work_time = Column(Date, default=today)  # 代表的日期
    type = Column(SmallInteger, default=0)  # 业务类别（LABOUR：劳务、STAFF：管理人员、VISITOR：访客）
    labour_roster = Column(String(36), nullable=True)    # 关联花名册
    work_type = Column(String(32), nullable=True)       # 岗位， 工种
    in_time = Column(DateTime, nullable=True)  # 上工时间  首次进场时间
    out_time = Column(DateTime, nullable=True)  # 下工时间  末次出场时间
    clock_status = Column(String(16), default='NO')  # 状态（NO：未上工、IN：上工中、END：已下工、ERROR：异常状态、TO_TIME）

    am_temperature = Column(Float, default=0)  # 体温 上午
    pm_temperature = Column(Float, default=0)  # 体温 下午

    jet_lag = Column(SmallInteger, default=0)  # 分钟（有上下班时间后，计划时间差，用于计算是否有效）
    created_time = Column(DateTime, default=datetime.datetime.now)
    modified_time = Column(DateTime, default=datetime.datetime.now)
    resource_id = Column(String(36), nullable=True, default=gen_id)


class ClockRecord(Base):
    __tablename__ = "clock_record"
    """进入详细情况, 一次完整的进出，用于统计当天工时"""
    id = Column(Integer, primary_key=True, autoincrement=True)
    status = Column(SmallInteger, default=1)
    project_id = Column(String(36), nullable=True)
    clock_in_id = Column(String(36), nullable=True)
    work_time = Column(Date, default=today)  # 代表的日期
    labour_roster = Column(String(36), nullable=True)    # 关联花名册
    type = Column(SmallInteger, default=0)  # 业务类别（LABOUR：劳务、STAFF：管理人员、VISITOR：访客）
    punch_clock_time = Column(DateTime, default=datetime.datetime.now)  # 具体时间时间
    direction = Column(Float, default=0)  # 0 in 1 out
    created_time = Column(DateTime, default=datetime.datetime.now)
    modified_time = Column(DateTime, default=datetime.datetime.now)
    file_path = Column(String(128), nullable=True)
    clock_method = Column(SmallInteger, default=0)  # 0 人脸 1 移动打卡 2
    camera_id = Column(String(36))
    resource_id = Column(String(36), default=gen_id)


if __name__ == '__main__':
    # ClockRecord.__table__.drop(engine)
    # ClockRecord.__table__.create(engine)
    # MqttTask.__table__.drop(engine)
    # MqttTask.__table__.create(engine)
    # Camera.__table__.drop(engine)
    # Camera.__table__.create(engine)
    # Attachment.__table__.drop(engine)
    # Attachment.__table__.create(engine)
    # # #
    # project_id = 'ecabe97c-84ae-480a-baaa-59970617873e'
    # # camera1 = Camera(name='test01', device_no="75b994c0-578b65a4", camera_status=0, online=0, direction="IN", project_id=project_id)
    # # camera2 = Camera(name='test02', device_no="b1da57e8-7fb982c4", camera_status=0, online=0, direction="OUT", project_id=project_id)
    # # db_session.add(camera1)
    # # db_session.add(camera2)
    # person_resource1 = 'd0dd27b7-fe5f-41c5-9179-2e71d8b0d7e1'
    # person_resource2 = 'd0dd27b7-fe5f-41c5-9179-2e71d8b0d7e2'
    # attachment_id1 = '00948613-12b1-4d2b-ac46-fe1950b3b629'
    # attachment_id2 = '7b7c3c3f-c1b6-4a6f-9a88-185edc809ce5'
    #
    # task1 = MqttTask(project_id=project_id, person_resource=person_resource1, person_name='贺建鑫',
    #                  attachment_id=attachment_id1, camera_sn='7c6145b09fba497886aac20015162a8c')
    # task2 = MqttTask(project_id=project_id, person_resource=person_resource2, person_name='贺建鑫',
    #                  attachment_id=attachment_id2, camera_sn='0e69bd94acca4191a684ae50d7cb66d0')
    # db_session.add(task1)
    # db_session.add(task2)
    # db_session.commit()

    #
    # picture1 = Attachment(name="hejx", url="http://10.28.25.213:8080/IMG_1227.jpeg", project_id=project_id)
    # # picture2 = Attachment(name="hejx", url="http://10.28.25.213:8080/IMG_1227.JPG", project_id=project_id)
    # # picture3 = Attachment(name="hejx", url="http://10.28.25.213:8080/IMG_2559.jpeg", project_id=project_id)
    # picture4 = Attachment(name="hejx", url="http://10.28.25.213:8080/IMG_2560.jpeg", project_id=project_id)
    # db_session.add(picture1)
    # # db_session.add(picture2)
    # # db_session.add(picture3)
    # db_session.add(picture4)
    # db_session.commit()
    # db_session.commit()
    class ConfigurationCenter(Base):
        __tablename__ = 'configuration_center'

        id = Column(Integer, primary_key=True, autoincrement=True)
        status = Column(SmallInteger, default=1)
        creator_id = Column(String(32), nullable=True)  # 创建人ID
        created_time = Column(DateTime, default=datetime.datetime.now)
        modified_time = Column(DateTime, default=datetime.datetime.now)
        remark = Column(String(300), nullable=False, default='')  # 备注
        resource_id = Column(String(36), default=gen_id)
        # 项目
        project_id = Column(String(36), default=gen_id)
        # 公司
        company_id = Column(String(36), default=gen_id)

        project_level = Column(SmallInteger, default=1)
        type = Column(SmallInteger, default=1)
        way = Column(String(36), default=gen_id)
        call_notifys = Column(String(300), nullable=False, default='')  # 备注
        using_state = Column(SmallInteger, default=1)
        call_cycle = Column(SmallInteger, default=1)
        month_day = Column(SmallInteger, default=1)
        quarter_month = Column(SmallInteger, default=1)
        quarter_day = Column(SmallInteger, default=1)
        week_day = Column(SmallInteger, default=1)
        day_time = Column(String(36), default=gen_id)
        pm_25 = Column(Float())
        noise_value = Column(Float())
        # 通用
        days = Column(SmallInteger, default=1)
        rate = Column(SmallInteger, default=1)
        pass_time = Column(String(36), default=gen_id)
    ConfigurationCenter.__table__.create(engine)
