#!/usr/bin/env python
# -*- coding: utf-8 -*-
import random
import time
from rosbridge_tcp import RosBridgeTCP
from ros_utils import build_ros_array_msg


def judge(robot_hand_type, your_hand_type):
    if your_hand_type == robot_hand_type:
        return "even"
    elif robot_hand_type == "Rock" and your_hand_type == "Scissors":
        return "win"
    elif robot_hand_type == "Paper" and your_hand_type == "Rock":
        return "win"
    elif robot_hand_type == "Scissors" and your_hand_type == "Paper":
        return "win"
    return "lose"


def main():
    ros_bridge_tcp = RosBridgeTCP()
    # publisher from windows
    topic_name_from_win = "/from_windows_a"
    advertise_msg = {
        "op": "advertise",
        "topic": topic_name_from_win,
        "type": "std_msgs/String"
    }
    ros_bridge_tcp.send_message(advertise_msg)
    # subscribe to ros topic
    topic_name_from_ros = "/from_ros_a"
    subscribe_msg = {
        "op": "subscribe",
        "topic": topic_name_from_ros,
        "type": "std_msgs/String"
    }
    ros_bridge_tcp.send_message(subscribe_msg)
    print("Waiting ROS message...")
    message_from_ros = ros_bridge_tcp.wait_message()
    if message_from_ros:
        print("Receive from ROS:" + message_from_ros)
    # Start image processing, open camera.
    hand_types = ["Rock", "Paper", "Scissors"]
    tm = time.time()
    while time.time() - tm < 5:
        # Detect hand type
        pass
    hand_type = random.choice(hand_types)  # Dummy code
    # Finish image processing, close camera.

    # Send your hand type to ROS, and wait ROS robot's hand type.
    pub_msg = {
        "op": "publish",
        "topic": topic_name_from_win,
        "msg": {"data": hand_type}
    }
    message_from_ros = ros_bridge_tcp.wait_response(pub_msg, hand_types, 30)
    if message_from_ros:
        print("Receive from ROS:" + message_from_ros)

    # Judge
    result = judge(message_from_ros, hand_type)
    pub_msg = {
        "op": "publish",
        "topic": topic_name_from_win,
        "msg": {"data": result}
    }
    # Send game result to ROS.
    ros_bridge_tcp.wait_response(pub_msg, timeout=5)

    try:
        ros_bridge_tcp.terminate()
        ros_bridge_tcp = None
    except Exception as e:
        print(str(e))


if __name__ == '__main__':
    main()
