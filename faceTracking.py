import cv2
from djitellopy import tello
import numpy as np
import keyboard
import time

# Inicjalizacja drona
myTelloDrone = tello.Tello()
myTelloDrone.connect()
myTelloDrone.streamoff()
myTelloDrone.streamon()
myTelloDrone.takeoff()
# Sprawdzenie poziomu baterii
print(myTelloDrone.get_battery())
# Wyzerowanie początkowych prędkości
myTelloDrone.send_rc_control(0, 0, 0, 0)

# Zdefiniowanie wymiarów okna kamery
w = 480
h = 320

# Parametry regulatora PID dla ruchu obrotowego oraz w osi z
pid_yaw = [0.4, 0, 0.4]
pid_ud = [0.4, 0, 0.4]
# Wyzerowania początkowego błędu ruchu
pError_yaw = 0
pError_ud = 0

# Zakres braku ruchu w osi x(przód/tył) - powierzchnia wykrytej twarzy
fbRange = [4000, 6000]


# Funkcja znajdująca twarz na kamerze, przekazywany jako parametr obraz z kamery
def findingFace(img):
    # Standardowy proces rozpoznawania twarzy wykorzystujący blibliotekę opencv i klasyfikator haar
    faceCascade = cv2.CascadeClassifier("res/haarcascade_frontalface_default.xml")
    grayImg = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    allFaces = faceCascade.detectMultiScale(grayImg, 1.1, 6)

    myFaceCenterList = []
    myFaceAreaList = []
    # Zaznaczenie wszystkich znalezionych twarzy(prostokąty) oraz punktu centralnego danej twarzy
    for (x, y, local_w, local_h) in allFaces:
        cv2.rectangle(img, (x, y), (x + local_w, y + local_h), (0, 255, 0), 2)
        centerX = x + int(local_w / 2)
        centerY = y + int(local_h / 2)
        faceArea = int(local_w * local_h)
        cv2.circle(img, (centerX, centerY), 5, (255, 0, 0), cv2.FILLED)
        # Dodanie współrzędnych twarzy oraz pola powierzchni do odpowiednich list
        myFaceCenterList.append([centerX, centerY])
        myFaceAreaList.append(faceArea)
    # Warunek obecności co najmniej jednej twarzy na kamerze
    if len(myFaceCenterList) != 0:
        # Szukamy największej twarzy na kamerze - ta będzie śledzona
        maxFaceIndex = myFaceAreaList.index(max(myFaceAreaList))
        # Zwracamy obraz kamery i dane do śledzenia(pole powierzchni, punkt środkowy)
        return img, [myFaceCenterList[maxFaceIndex], myFaceAreaList[maxFaceIndex]]
    else:
        # Brak twarzy - zwracamy zerowe parametry
        return img, [[0, 0], 0]


# Funkcja śledząca twarz na kamerze
def trackingFace(trackingInfo, w, h, pid_yaw, pError_yaw, pid_ud, pError_ud):
    # Odczyt paraemtrów do śledzenia
    centerX, centerY = trackingInfo[0]
    faceArea = trackingInfo[1]
    # Obliczenie prędkości ruchu obrotowego drona - regulator PD, ograniczenie do zakresu -50/50
    yaw_error = centerX - int(w / 2)
    yaw_vel = pid_yaw[0] * yaw_error + pid_yaw[2] * (yaw_error - pError_yaw)
    yaw_vel = int(np.clip(yaw_vel, -50, 50))
    # Obliczenie prędkości ruchu w osi z drona - regulator PD, ograniczenie do zakresu -50/50
    ud_error = int(h / 2) - centerY
    ud_vel = pid_ud[0] * ud_error + pid_ud[2] * (ud_error - pError_ud)
    ud_vel = int(np.clip(ud_vel, -50, 50))
    # Obliczenie prędkości ruchu w osi x drona - regulator histerezowy(trójpołożeniowy), prędkości -15,0,15
    if fbRange[0] <= faceArea <= fbRange[1]:
        fb_vel = 0
    elif faceArea > fbRange[1] and faceArea != 0:
        fb_vel = -15
    elif faceArea < fbRange[0] and faceArea != 0:
        fb_vel = 15
    else:
        fb_vel = 0
    # Wyzerowanie prędkości przy braku wykrytej twarzy
    if centerX == 0 or centerY == 0 or faceArea == 0:
        yaw_vel = 0
        ud_vel = 0
        fb_vel = 0
    # Wysłanie komend z prędkościami do drona
    myTelloDrone.send_rc_control(0, fb_vel, ud_vel, yaw_vel)
    # Wyświetlenie aktualnych prędkości w konsoli
    print(fb_vel, yaw_vel, ud_vel, faceArea)
    # Zwracanie błędu regulacji ruchu obrotowego oraz w osi z
    return yaw_error, ud_error


# Pętla główna programu
while True:
    # Odczyt obrazu z kamery drona, skalowanie okna kamery na ekranie
    img = myTelloDrone.get_frame_read().frame
    img = cv2.resize(img, (w, h))
    # Wyszukiwanie twarzy na kamerze
    img, info = findingFace(img)
    # Śledzenie twarzy z kamery
    pError_yaw, pError_ud = trackingFace(info, w, h, pid_yaw, pError_yaw, pid_ud, pError_ud)
    # Wyświetlenie obrazu z kamery na ekranie
    cv2.imshow("Kamera", img)
    # Zapis zdjęcia z kamery przyciskiem "z"
    if keyboard.is_pressed('z'):
        cv2.imwrite(f"zdj/{time.time()}.jpg", img)
        time.sleep(0.3)
    # Awaryjne lądowanie dronem przyciskiem "q"
    if cv2.waitKey(1) & 0xFF == ord('q'):
        myTelloDrone.send_rc_control(0, 0, 0, 0)
        myTelloDrone.streamoff()
        myTelloDrone.land()
        break
# Zamknięnie okna kamery
cv2.destroyAllWindows()
