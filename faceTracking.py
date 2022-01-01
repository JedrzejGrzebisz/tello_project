import cv2
from djitellopy import Tello
import numpy as np
import time

# Inicjalizacja drona
#myTelloDrone = Tello()
#myTelloDrone.connect()
#myTelloDrone.streamoff()
#myTelloDrone.streamon()
#myTelloDrone.takeoff()

# Komenda wyzerowania prędkości
#myTelloDrone.send_rc_control(0, 0, 0, 0)

# Wymiary okna kamery
w = 480
h = 320

pid_yaw = [0.4, 0, 0.4]
pid_ud = [0.4, 0, 0.4]
pid_fb = [0.4, 0, 0.4]
pError_yaw = 0
pError_ud = 0
pError_fb = 0


def findingFace(img):
    faceCascade = cv2.CascadeClassifier("res/haarcascade_frontalface_default.xml")
    grayImg = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    allFaces = faceCascade.detectMultiScale(grayImg, 1.1, 6)

    myFaceCenterList = []
    myFaceAreaList = []
    for (x, y, local_w, local_h) in allFaces:
        cv2.rectangle(img, (x, y), (x+local_w, y+local_h), (0, 255, 0), 2)
        centerX = x + int(local_w/2)
        centerY = y + int(local_h/2)
        faceArea = int(local_w * local_h)
        cv2.circle(img, (centerX, centerY), 5, (255, 0, 0), cv2.FILLED)
        # Lista dla wszystkich znalezionych twarzy(bo może się pojawić więcej niż jedna w kamerze)
        myFaceCenterList.append([centerX, centerY])
        myFaceAreaList.append(faceArea)
        #print("Środek twarzy:", centerX, centerY, "Pole twarzy:", faceArea)
    if len(myFaceCenterList) != 0: # Warunek że jest co najmniej jedna twarz na kamerze
        maxFaceIndex = myFaceAreaList.index(max(myFaceAreaList)) # Szukamy największej twarzy - ta będzie śledzona
        return img, [myFaceCenterList[maxFaceIndex], myFaceAreaList[maxFaceIndex]] # Zwracamy obraz kamery i dane do śledzenia
    else:
        return img, [[0, 0], 0] # Brak twarzy to zerowe parametry


def trackingFace(trackingInfo, w, h, pid_yaw, pError_yaw, pid_ud, pError_ud, pid_fb, pError_fb):
    centerX, centerY = trackingInfo[0]
    faceArea = trackingInfo[1]
    #PID of yaw velocity
    yaw_error = centerX - int(w/2)
    yaw_vel = pid_yaw[0] * yaw_error + pid_yaw[2] * (yaw_error - pError_yaw)
    yaw_vel = int(np.clip(yaw_vel, -50, 50))
    #PID of up/down velocity
    ud_error = int(h/2) - centerY
    ud_vel = pid_ud[0] * ud_error + pid_ud[2] * (ud_error - pError_ud)
    ud_vel = int(np.clip(ud_vel, -50, 50))
    #PID of forward/backward velocity

    #Sprawdzenie czy wykryto jakąkolwiek twarz
    if centerX == 0 or centerY == 0 or faceArea == 0:
        yaw_vel = 0
        ud_vel = 0

    # myTello.send_rc_control(0, 0, ud_vel, yaw_vel)
    print(yaw_vel, ud_vel, faceArea)
    return yaw_error, ud_error

cap = cv2.VideoCapture(0)
# Pętla główna programu
while True:
    #img = myTelloDrone.get_frame_read().frame
    success, img = cap.read()
    img = cv2.resize(img, (w, h))
    img, info = findingFace(img)
    pError_yaw, pError_ud = trackingFace(info, w, h, pid_yaw, pError_yaw, pid_ud, pError_ud, pid_fb, pError_fb)
    cv2.imshow("Kamera", img)
    cv2.waitKey(1)
