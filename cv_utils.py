# -*- coding: utf_8 -*-
import numpy as np


def calcDistPoint2Point(p1, p2):
    return np.sqrt((p1.x - p2.x)**2 + (p1.y - p2.y)**2 + (p1.z - p2.z)**2)


def calcDistPoint2xyz(p1, x, y, z):
    return np.sqrt((p1.x - x)**2 + (p1.y - y)**2 + (p1.z - z)**2)


def calcPlane(A, B, C):
    # https://keisan.casio.jp/exec/system/1202458197
    vAB = (B.x - A.x, B.y - A.y, B.z - A.z)
    vAC = (C.x - A.x, C.y - A.y, C.z - A.z)
    a = (B.y - A.y)*(C.z - A.z) - (C.y - A.y)*(B.z - A.z)
    b = (B.z - A.z)*(C.x - A.x) - (C.z - A.z)*(B.x - A.x)
    c = (B.x - A.x)*(C.y - A.y) - (C.x - A.x)*(B.y - A.y)
    d = -(a*A.x + b*A.y + c*A.z)
    return [a, b, c, d]


def calcDistPoint2Plane(p0, p1, p2, p3):
    # https://hiraocafe.com/note/plane_equation.html
    abcd = calcPlane(p1, p2, p3)
    return np.abs(abcd[0]*p0.x + abcd[1]*p0.y + abcd[2]*p0.z + abcd[3]) / np.sqrt(abcd[0]**2 + abcd[1]**2 + abcd[2]**2)


def judgeHand(f0, f1, f2, f3, f4):
    if f0 == "o" and f1 == "o" and f2 == "o" and f3 == "o" and f4 == "o":
        return "paper"
    if f0 == "x" and f1 == "o" and f2 == "o" and f3 == "x" and f4 == "x":
        return "scissors"
    if f0 == "x" and f1 == "x" and f2 == "x" and f3 == "x" and f4 == "x":
        return "rock"


def estFingerStatus(landmark, bpoints, th):
    mx = (landmark[0].x + landmark[5].x + landmark[17].x) / 3
    my = (landmark[0].y + landmark[5].y + landmark[17].y) / 3
    mz = (landmark[0].z + landmark[5].z + landmark[17].z) / 3

    baseDist = calcDistPoint2Point(landmark[bpoints[0]], landmark[bpoints[1]])
    finger0 = calcDistPoint2xyz(landmark[4], mx, my, mz) / baseDist
    finger1 = calcDistPoint2xyz(landmark[8], mx, my, mz) / baseDist
    finger2 = calcDistPoint2xyz(landmark[12], mx, my, mz) / baseDist
    finger3 = calcDistPoint2xyz(landmark[16], mx, my, mz) / baseDist
    finger4 = calcDistPoint2xyz(landmark[20], mx, my, mz) / baseDist

    f0 = f1 = f2 = f3 = f4 = "x"
    if finger0 > th*1.2:
        f0 = "o"
    if finger1 > th:
        f1 = "o"
    if finger2 > th:
        f2 = "o"
    if finger3 > th:
        f3 = "o"
    if finger4 > th:
        f4 = "o"

    myHand = judgeHand(f0, f1, f2, f3, f4)

    # print(f1, f2, f3, f4, "|", finger1, finger2, finger3, finger4)
    print("finger 0-4:", f0, f1, f2, f3, f4, "|", myHand)

    return myHand

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
