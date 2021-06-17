# # -*- coding: utf-8 -*-
# # Author : hejianxin
# # Time : 2021/6/16 4:11 下午
#
# import paho.mqtt.client as mqtt
#
# def on_connect(client, userdata, flags, rc):
#     print("Connected with result code: " + str(rc))
#
# def on_message(client, userdata, msg):
#     print(msg.topic + " " + str(msg.payload))
#
# client = mqtt.Client("123")
# client.on_connect = on_connect
# client.on_message = on_message
#
# client.connect('10.28.25.213', 1883, 600) # 600为keepalive的时间间隔
# client.username_pw_set("netmon", "netmon")
#
# client.subscribe('fifa', qos=0)
#
# client.loop_forever() # 保持连接


# import paho.mqtt.client as mqtt
#
# MQTTHOST = "10.28.25.213"
# MQTTPORT = 1883
# mqttClient = mqtt.Client()
# mqttClient.username_pw_set("netmon", "netmon")
#
#
# # 连接MQTT服务器
# def on_mqtt_connect():
#     mqttClient.connect(MQTTHOST, MQTTPORT, 60)
#     mqttClient.loop_start()
#
#
# # publish 消息
# def on_publish(topic, payload, qos):
#     mqttClient.publish(topic, payload, qos)
#
#
# # 消息处理函数
# def on_message_come(lient, userdata, msg):
#     print(msg.topic + " " + ":" + str(msg.payload))
#
#
# # subscribe 消息
# def on_subscribe():
#     mqttClient.subscribe("/server", 1)
#     mqttClient.on_message = on_message_come  # 消息到来处理函数
#
#
# def main():
#     on_mqtt_connect()
#     # on_publish("/server", "Hello Python!", 1)
#     on_subscribe()
#     while True:
#         pass
#
#
# if __name__ == '__main__':
#     main()

# from connect_mqtt import mqtt_client, topic
#
#
# # 消息处理函数
# def on_message_come(lient, userdata, msg):
#     print(msg.topic + " " + ":" + str(msg.payload))
#
#
# # mqtt_client = connect()
# mqtt_client.publish(topic, "hello python", 1)
# mqtt_client.loop_start()
#
# mqtt_client.subscribe(topic, 1)
# mqtt_client.on_message = on_message_come
#
# # 阻塞方法
# # mqtt_client.loop_start()
# mqtt_client.loop_forever()
# # while True:
# #     pass
# # -*- coding: utf-8 -*-
# # Author : hejianxin
# # Time : 2021/6/16 4:01 下午
# # import paho.mqtt.client as mqtt
# #
# # def on_connect(client, userdata, flags, rc):
# #     print("Connected with result code: " + str(rc))
# #
# # def on_message(client, userdata, msg):
# #     print(msg.topic + " " + str(msg.payload))
# #
# # client = mqtt.Client()
# # client.on_connect = on_connect
# # client.on_message = on_message
# #
# # client.connect('10.28.25.213', 1883, 600) # 600为keepalive的时间间隔
# # client.username_pw_set("netmon", "netmon")
# #
# # client.publish('topic2', payload='amaziqweqeqweng', qos=0)
#
# import paho.mqtt.client as mqtt
#
# HOST = "10.28.25.213"
# PORT = 1883
#
#
# def test():
#     client = mqtt.Client()
#     client.username_pw_set("netmon", "netmon")
#     client.connect(HOST, PORT, 60)
#
#     client.publish("chat", "hello liefyuan", 2)  # 发布一个主题为'chat',内容为‘hello liefyuan’的信息
#     client.loop_forever()
#
#
# if __name__ == '__main__':
#     test()
# # -*- coding: utf-8 -*-
# # Author : hejianxin
# # Time : 2021/6/16 4:11 下午
#
# import paho.mqtt.client as mqtt
#
# def on_connect(client, userdata, flags, rc):
#     print("Connected with result code: " + str(rc))
#
# def on_message(client, userdata, msg):
#     print(msg.topic + " " + str(msg.payload))
#
# client = mqtt.Client("123")
# client.on_connect = on_connect
# client.on_message = on_message
#
# client.connect('10.28.25.213', 1883, 600) # 600为keepalive的时间间隔
# client.username_pw_set("netmon", "netmon")
#
# client.subscribe('fifa', qos=0)
#
# client.loop_forever() # 保持连接

#
# import paho.mqtt.client as mqtt
#
# MQTTHOST = "10.28.25.213"
# MQTTPORT = 1883
# mqttClient = mqtt.Client()
# mqttClient.username_pw_set("netmon", "netmon")
#
#
# # 连接MQTT服务器
# def on_mqtt_connect():
#     mqttClient.connect(MQTTHOST, MQTTPORT, 60)
#     mqttClient.loop_start()
#
#
# # publish 消息
# def on_publish(topic, payload, qos):
#     mqttClient.publish(topic, payload, qos)
#
#
# # 消息处理函数
# def on_message_come(lient, userdata, msg):
#     print(msg.topic + " " + ":" + str(msg.payload))
#
#
# # subscribe 消息
# def on_subscribe():
#     mqttClient.subscribe("/server", 1)
#     mqttClient.on_message = on_message_come  # 消息到来处理函数
#
#
# def main():
#     on_mqtt_connect()
#     on_publish("/server", "Hello Python!", 1)
#     # on_subscribe()
#     while True:
#         pass
#
#
# if __name__ == '__main__':
#     main()

import paho.mqtt.client as mqtt
import json
import time

HOST = "10.28.25.213"
PORT = 1883
client_id = "75b994c0-578b65a4"
username = "netmon"
password = "netmon"


def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    # client.subscribe("face/sn/request")         # 订阅消息


def on_message(client, userdata, msg):
    print("主题:"+msg.topic+" 消息:"+str(msg.payload.decode('utf-8')))


def on_subscribe(client, userdata, mid, granted_qos):
    print("On Subscribed: qos = %d" % granted_qos)


def on_disconnect(client, userdata, rc):
    if rc != 0:
        print("Unexpected disconnection %s" % rc)


def on_publish(client, userdata, mid):
    print("publish", mid)


data = {
  "client_id": client_id,
  # "cmd_id": "ffffffff",
  "version": "0.2",
  "cmd": "create_face",
  "per_id": "ff00ff",
  "face_id": "ff00ff",
  "per_name": "hejx",
  "idcardNum": "123456",
  "img_url": "http://10.28.25.213:8080/IMG_1227.JPG",
  "idcardper": "51102419999999171x",
  # "s_time": 0, //启用日期时间戳(可选)
  # "e_time" //有效日期时间戳(可选)
  # "per_type": 0, //0：普通人员 2：黑名单人员(可选)
  # "usr_type": 0 //权限类型，取值 0 - 5，默认 0(可选)
}
param = json.dumps(data)
client = mqtt.Client(client_id)
client.username_pw_set(username, password)
client.on_connect = on_connect
client.on_message = on_message
client.on_subscribe = on_subscribe
client.on_disconnect = on_disconnect
client.connect(HOST, PORT, 60)
# client.publish("face/sn/request", payload=param, qos=0)     # 发送消息
client.loop_forever()

