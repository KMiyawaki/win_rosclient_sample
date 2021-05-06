#!/usr/bin/env python
# -*- coding: utf-8 -*-
from rosbridge_tcp import RosBridgeTCP
from ros_utils import build_ros_array_msg
import cv2
import mediapipe as mp


#        8   12  16  20
#        |   |   |   |
#        7   11  15  19
#    4   |   |   |   |
#    |   6   10  14  18
#    3   |   |   |   |
#    |   5---9---13--17
#    2    \         /
#     \    \       /
#      1    \     /
#       \    \   /
#        ------0-

def main():
    mp_drawing = mp.solutions.drawing_utils
    mp_hands = mp.solutions.hands
    cap = cv2.VideoCapture(0)############

    ros_bridge_tcp = RosBridgeTCP()
    topic_name = "/from_windows"
    advertise_msg = {
        "op": "advertise",
        "topic": topic_name,
        "type": "std_msgs/String"
    }
    ros_bridge_tcp.send_message(advertise_msg)

    with mp_hands.Hands(
        min_detection_confidence=0.7,
        min_tracking_confidence=0.7) as hands:
        while cap.isOpened():
            success, image = cap.read()
            if not success:
                print("Ignoring empty camera frame.")
                continue

            image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
            image.flags.writeable = False
            results = hands.process(image)

            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            x = y = 0
            if results.multi_hand_landmarks:
                x = results.multi_hand_landmarks[0].landmark[9].x
                y = results.multi_hand_landmarks[0].landmark[9].y
                for hand_landmarks in results.multi_hand_landmarks:
                    mp_drawing.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            if y == 0 and x == 0:
                command = 'a'
            elif y < 0.5 and x < 0.5: #upper-left
                command = 'forward'
            elif y < 0.5 and x >= 0.5: #upper-right
                command = 'right'
            elif y >= 0.5 and x < 0.5: #lower-left
                command = 'left'
            else:
                command = 'back'
            
            pub_msg = {
                "op": "publish",
                "topic": topic_name,
                "msg": {"data": command}
            }
            ros_bridge_tcp.send_message(pub_msg)
            print(command)
            #print("Sending ros message: " + str(pub_msg))

            cv2.imshow('MediaPipe Hands', image)
            if cv2.waitKey(5) & 0xFF == 27:
                break
    cap.release()
    pub_msg = {
        "op": "publish",
        "topic": topic_name,
        "msg": {"data": 'a'}
    }
    ros_bridge_tcp.send_message(pub_msg)

    try:
        ros_bridge_tcp.terminate()
        ros_bridge_tcp = None
    except Exception as e:
        print(str(e))


if __name__ == '__main__':
    main()
