#!/usr/bin/env python
# -*- coding: utf-8 -*-
import random
import time
import cv2
import mediapipe as mp
import numpy as np
import statistics as stic
from collections import deque
from rosbridge_tcp import RosBridgeTCP
from ros_utils import build_ros_array_msg
from cv_utils import calcDistPoint2Point, calcDistPoint2Plane, calcDistPoint2xyz, calcPlane, judgeHand, estFingerStatus


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


def game_rps(timeout=30):
    mp_drawing = mp.solutions.drawing_utils
    mp_hands = mp.solutions.hands

    myHands = deque([], 30)
    tm = time.time()
    myHand = None
    # For webcam input:
    cap = cv2.VideoCapture(0)
    with mp_hands.Hands(
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5) as hands:
        while cap.isOpened() and time.time() - tm <= timeout:
            success, image = cap.read()
            if not success:
                print("Ignoring empty camera frame.")
                continue

            image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
            image.flags.writeable = False
            results = hands.process(image)

            # Draw the hand annotations on the image.
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            if results.multi_hand_landmarks:
                myHands.append(estFingerStatus(
                    results.multi_hand_landmarks[0].landmark, [5, 17], 1.1))
                myHand = stic.mode(myHands)
                text = "No hand type detected"
                if myHand:
                    text = "Push ESC key to send your hand type '" + myHand + "'"
                cv2.putText(image, text, (50, 50),
                            cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 0, 255), 1)
                for hand_landmarks in results.multi_hand_landmarks:
                    mp_drawing.draw_landmarks(
                        image, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            cv2.imshow('Rock-Paper-Scissors', image)
            if cv2.waitKey(5) & 0xFF == 27 and myHand is not None:
                break
    cap.release()
    return myHand


def main():
    ros_bridge_tcp = RosBridgeTCP()
    # publisher from windows
    topic_name_from_win = "/from_windows_rps"
    advertise_msg = {
        "op": "advertise",
        "topic": topic_name_from_win,
        "type": "std_msgs/String"
    }
    ros_bridge_tcp.send_message(advertise_msg)
    # subscribe to ros topic
    topic_name_from_ros = "/from_ros_rps"
    subscribe_msg = {
        "op": "subscribe",
        "topic": topic_name_from_ros,
        "type": "std_msgs/String"
    }
    ros_bridge_tcp.send_message(subscribe_msg)
    print("Waiting ROS message...")
    message_from_ros = ros_bridge_tcp.wait_response()
    if message_from_ros:
        print("Receive from ROS:" + message_from_ros)
    # Start image processing, open camera.
    hand_types = ["rock", "paper", "scissors"]
    hand_type = game_rps(30)
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
    ros_bridge_tcp.wait_response(pub_msg, timeout=10)

    try:
        ros_bridge_tcp.terminate()
        ros_bridge_tcp = None
    except Exception as e:
        print(str(e))


if __name__ == '__main__':
    main()
