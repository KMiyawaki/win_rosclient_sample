#!/usr/bin/env python
# -*- coding: utf-8 -*-
import random
import time
from rosbridge_tcp import RosBridgeTCP
from ros_utils import build_ros_array_msg


def judge(robot_direction_type, your_face_direction):
    if robot_direction_type == your_face_direction:
        return "win"
    return "lose"


def main():
    ros_bridge_tcp = RosBridgeTCP()
    # publisher from windows
    topic_name_from_win = "/from_windows_b"
    advertise_msg = {
        "op": "advertise",
        "topic": topic_name_from_win,
        "type": "std_msgs/String"
    }
    ros_bridge_tcp.send_message(advertise_msg)
    # subscribe to ros topic
    topic_name_from_ros = "/from_ros_b"
    subscribe_msg = {
        "op": "subscribe",
        "topic": topic_name_from_ros,
        "type": "std_msgs/String"
    }
    ros_bridge_tcp.send_message(subscribe_msg)
    # Clear ROS message
    message_from_ros = ""
    while not message_from_ros:
        messages = ros_bridge_tcp.wait()
        if messages:
            message_from_ros = messages[0]['msg']['data']
            print("Receive from ROS:" + message_from_ros)
    # Start image processing, open camera.
    face_directions = ["up", "down", "left", "right"]
    tm = time.time()
    while time.time() - tm < 5:
        # Detect hand type
        pass
    face_direction = random.choice(face_directions)  # Dummy code
    # Finish image processing, close camera.

    # Reset timer and clear ROS message
    message_from_ros = ""
    tm = time.time()
    while time.time() - tm < 30 and not message_from_ros:
        pub_msg = {
            "op": "publish",
            "topic": topic_name_from_win,
            "msg": {"data": face_direction}
        }
        ros_bridge_tcp.send_message(pub_msg)
        print("Sending ros message: " + str(pub_msg))
        time.sleep(1)
        messages = ros_bridge_tcp.wait()
        if messages and messages[0]['msg']['data'] in face_directions:
            message_from_ros = messages[0]['msg']['data']
            print("Receive from ROS:" + message_from_ros)

    # Judge
    result = judge(message_from_ros, face_direction)
    while time.time() - tm < 10:
        pub_msg = {
            "op": "publish",
            "topic": topic_name_from_win,
            "msg": {"data": result}
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
