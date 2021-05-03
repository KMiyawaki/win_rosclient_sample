import cv2
import numpy as np
import mediapipe as mp
from collections import deque
import statistics as stic
from cv_utils import calcDistPoint2Point, calcDistPoint2Plane, calcDistPoint2xyz, calcPlane, judgeHand, estFingerStatus


# def estFingerStatus_tmp(landmark, bpoints, th):
#     baseDist = calcDistPoint2Point(landmark[bpoints[0]], landmark[bpoints[1]])
#     finger1 = calcDistPoint2Plane(landmark[6], landmark[5], landmark[17], landmark[0]) / baseDist
#     finger2 = calcDistPoint2Plane(landmark[10], landmark[5], landmark[17], landmark[0]) / baseDist
#     finger3 = calcDistPoint2Plane(landmark[14], landmark[5], landmark[17], landmark[0]) / baseDist
#     finger4 = calcDistPoint2Plane(landmark[18], landmark[5], landmark[17], landmark[0]) / baseDist

#     f1 = f2 = f3 = f4 = "o"
#     if finger1 > th:
#         f1 = "x"
#     if finger2 > th:
#         f2 = "x"
#     if finger3 > th:
#         f3 = "x"
#     if finger4 > th:
#         f4 = "x"
#     print(f1, f2, f3, f4, "|", finger1, finger2, finger3, finger4)


def main():
    mp_drawing = mp.solutions.drawing_utils
    mp_hands = mp.solutions.hands

    myHands = deque([], 30)

    # For webcam input:
    cap = cv2.VideoCapture(0)
    with mp_hands.Hands(
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5) as hands:
        while cap.isOpened():
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
                cv2.putText(image, myHand, (50, 50),
                            cv2.FONT_HERSHEY_COMPLEX, 1.0, (0, 0, 255), 2)
                for hand_landmarks in results.multi_hand_landmarks:
                    mp_drawing.draw_landmarks(
                        image, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            cv2.imshow('Rock-Paper-Scissors', image)
            if cv2.waitKey(5) & 0xFF == 27:
                break
    cap.release()


if __name__ == '__main__':
    main()
