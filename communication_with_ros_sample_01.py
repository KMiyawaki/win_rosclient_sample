#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
from rosbridge_tcp import RosBridgeTCP
from utils import build_ros_array_msg


def main():
    ros_bridge_tcp = RosBridgeTCP()
    # publisher from windows
    topic_name_from_win = "/from_windows"
    advertise_msg = {
        "op": "advertise",
        "topic": topic_name_from_win,
        "type": "std_msgs/String"
    }
    ros_bridge_tcp.send_message(advertise_msg)
    # subscribe to ros topic
    topic_name_from_ros = "/from_ros"
    subscribe_msg = {
        "op": "subscribe",
        "topic": topic_name_from_ros,
        "type": "std_msgs/String"
    }
    ros_bridge_tcp.send_message(subscribe_msg)
    tm = time.time()
    received = 0
    while time.time() - tm < 40 and received < 10:
        messages = ros_bridge_tcp.wait()
        received += len(messages)
        for m in messages:
            print(str(m))
    for i in range(0, 10):
        message = "Hello this is windows " + str(i)
        pub_msg = {
            "op": "publish",
            "topic": topic_name_from_win,
            "msg": {"data": message}
        }
        ros_bridge_tcp.send_message(pub_msg)
        print("Sending ros message: " + str(pub_msg))
        time.sleep(1)

    try:
        ros_bridge_tcp.terminate()
        ros_bridge_tcp = None
    except Exception as e:
        print(str(e))


if __name__ == '__main__':
    main()
