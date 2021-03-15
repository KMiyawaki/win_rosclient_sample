#!/usr/bin/env python
# -*- coding: utf-8 -*-
from rosbridge_tcp import RosBridgeTCP
from utils import build_ros_array_msg


def main():
    ros_bridge_tcp = RosBridgeTCP()
    topic_name = "/from_windows"
    advertise_msg = {
        "op": "advertise",
        "topic": topic_name,
        "type": "std_msgs/String"
    }
    ros_bridge_tcp.send_message(advertise_msg)
    command = input("command ? > ")
    while command != "q":
        pub_msg = {
            "op": "publish",
            "topic": topic_name,
            "msg": {"data": command}
        }
        ros_bridge_tcp.send_message(pub_msg)
        print("Sending ros message: " + str(pub_msg))
        command = input("command ? > ")
    try:
        ros_bridge_tcp.terminate()
        ros_bridge_tcp = None
    except Exception as e:
        print(str(e))


if __name__ == '__main__':
    main()
