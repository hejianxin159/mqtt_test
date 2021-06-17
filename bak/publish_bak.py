# -*- coding: utf-8 -*-
# Author : hejianxin
# Time : 2021/6/16 5:38 下午
import paho.mqtt.client as mqtt
import json


client_id = "75b994c0-578b65a4"


def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")


def on_message(client, userdata, msg):
    print("主题:"+msg.topic+" 消息:"+str(msg.payload.decode('utf-8')))


def on_disconnect(client, userdata, rc):
    if rc != 0:
        print("Unexpected disconnection %s" % rc)


def on_publish(client, userdata, mid):
    print("publish", mid)


def on_subscribe(client, userdata, mid, granted_qos):
    print("On Subscribed: qos = %d" % granted_qos)


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.on_publish = on_publish
client.on_disconnect = on_disconnect
client.on_subscribe = on_subscribe
client.username_pw_set("netmon", "netmon")
client.connect("10.28.25.213", 1883, 60)

data = {
  "client_id": client_id,
  "version": "0.2",
  "cmd": "update_face",
  "per_id": "ff00ff1hjx",
  "face_id": "ff00ffhjx",
  "per_name": "hejx2",
  "idcardNum": "135234",
  "img_url": "http://10.28.25.213:8080/IMG_2560.jpeg",
}

# 重启
# data = {
#   "client_id": client_id,
#   "version": "0.2",
#   "cmd": "reboot_cam"
# }

# print(data)

# client.publish(f"face/{client_id}/request", payload=json.dumps(data), qos=0)
client.publish(f"face/request", payload=json.dumps(data), qos=0)
# client.subscribe("face/request")
client.loop_forever()
