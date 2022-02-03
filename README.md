# Projekt z wykorzystaniem drona DJI Ryze Tello - śledzenie twarzy
Identyfikacja i Sterowanie Robotami Latającymi

## Opis projektu
Celem zrealizowanego projektu było utworznie programu znajdującego zastosowanie jako element nadzoru wizyjnego wykorzystujący bezzałogowy statek powietrzny DJI Ryze Tello. Zadaniem drona było wykrycie na obrazie z wbudowanej kamery twarzy, a następnie jej śledzenie z możliwością wykonania zdjęcia w dowolnej chwili lotu. Projekt wykonany został w języku Python z wykorzystaniem paczek wymienionych w kolejnym punkcie.

## Wymagane biblioteki
Dla poprawnego działania aplikacji wymagany jest [Python](https://www.python.org/downloads/) w wersji >= 3.7.6 oraz dostęp do następujących paczek:

- [DJITelloPy](https://pypi.org/project/djitellopy/)
- [opencv](https://pypi.org/project/opencv-python/) w wersji 4.4.0.40
- [numpy](https://pypi.org/project/numpy/)
- [keyboard](https://pypi.org/project/keyboard/)
- [time](https://docs.python.org/3/library/time.html)

## Uruchomienie aplikacji
W celu uruchomienia aplikacji należy pobrać katalog projektowy, a następnie w środowisku Python wraz z przedstawionymi wcześniej bibliotekami uruchomić plik [faceTracking.py](https://github.com/JedrzejGrzebisz/tello_project/blob/master/faceTracking.py). Jednocześnie należy pamiętać o połączeniu się poprzez wi-fi z dronem DJI(nie jest wymagana żadna dodatkowa konfiguracja połączenia).

```
git clone https://github.com/JedrzejGrzebisz/tello_project.git
cd tello_project
python3 ./faceTracking.py
```

## Realizacja aplikacji
Realizacja aplikacji opiera się w głownej mierze na wykorzystaniu biblioteki *opencv* w celu wykrywania twarzy na kamerze wbudowanej w drona, a następnie na śledzeniu jej poprzez wykorzystanie komend zadających prędkość z bilioteki *DJITelloPy* w osiach x(ruch przód/tył), z(ruch góra/dół) oraz z(obrót lewo/prawo). Prędkości wyznaczane są przy pomocy regulatórw PD(ruchy w osi z) lub regulacji trójpołożeniowej(ruch w osi x).

### Inicjalizacja drona
Dzięki zastosowaniu biblioteki *DJITelloPy* proces inicjalizacji drona został bardzo uproszczony i po uprzednim połączeniu się z Tello poprzez wi-fi wymagane jest jedynie stworzenie obiektu zaimportowanej klasy *djitellopy*, a następnie połączenie się metodą ```connect()```, w stworzonym programie etap inicjalizacji dodatkowo zawiera zrestartowanie transmisji z kamery, wzniesienie się drona w powietrze oraz wyzerowanie prędkości we wszystkich osiach. Więcej informacji na temat wykorzystania bilioteki *DJITelloPy* można znaleźć na dedykowanym githubie: [DJITelloPy](https://github.com/damiafuentes/DJITelloPy).

```python
myTelloDrone = tello.Tello()
myTelloDrone.connect()
myTelloDrone.streamoff()
myTelloDrone.streamon()
myTelloDrone.takeoff()
myTelloDrone.send_rc_control(0, 0, 0, 0)
```

### Wykrywanie twarzy
Proces wykrywania twarzy został zrealizowany poprzez bibliotekę *opencv* i ogólnodostępny klasyfikator Haaro-podobny. W kodzie funckją odpowiedzialną za tą część jest ```findingFace()```, ktora poprzez zastosowanie standardowej procedury wykrywania obiektów z kamery znajduje twarze, rysując w okół nich prostokąty i zaznaczając punkt centralny. Z funkcji zwracana jest informacja o położeniu oraz polu powierzchni największej twarzy znajdującej się na ekranie aby sprecyzować która z możliwie kilku wykrytych ma zostać śledzona(założone zostało, że ma to być twarz najbliższa kamerze drona).

### Śledzenie twarzy
Funckja odpowiedzialna za śledzenie twarzy ```trackingFace()``` opiera się na danych dotyczących lokalizacji twarzy na obrazie oraz jej pola powierzchni wyznaczonych przez funkcję ```findingFace()```. W celu obliczenia prędkości jakie należy zadać w konkretnych osiach wykorzystane zostało zaimplementowanie regulatorów PD oraz regulatora trójpołożeniowy:

```python
pid_yaw = [0.4, 0, 0.4]
pid_ud = [0.4, 0, 0.4]
# Ruch obrotowy
yaw_error = centerX - int(w / 2)
yaw_vel = pid_yaw[0] * yaw_error + pid_yaw[2] * (yaw_error - pError_yaw)
yaw_vel = int(np.clip(yaw_vel, -50, 50))
# Ruch góra/dół
ud_error = int(h / 2) - centerY
ud_vel = pid_ud[0] * ud_error + pid_ud[2] * (ud_error - pError_ud)
ud_vel = int(np.clip(ud_vel, -50, 50))
# Ruch przód/tył
fbRange = [4000, 6000]
if fbRange[0] <= faceArea <= fbRange[1]:
    fb_vel = 0
elif faceArea > fbRange[1] and faceArea != 0:
    fb_vel = -15
elif faceArea < fbRange[0] and faceArea != 0:
    fb_vel = 15
else:
    fb_vel = 0
    
if centerX == 0 or centerY == 0 or faceArea == 0:
    yaw_vel = 0
    ud_vel = 0
    fb_vel = 0
myTelloDrone.send_rc_control(0, fb_vel, ud_vel, yaw_vel)
```

Wybrane nastawy regulatora PD oraz zadawane prędkości zostały wybrane doświadczalnie w celu ograniczenia gwałtownych ruchów drona, przy jednocześnie zachowanej odpowiedniej dynamice śledzenia. W przypadku braku wykrywania twarzy na kamerze prędkości drona były zerowane.

### Pętla główna programu
Pętla główna programu zawiera w sobie odczyt obrazu z kamery drona oraz jego skalowanie, następnie wywoływane są dwie omawiane wcześniej funkcje i wyświetlony obraz z kamery. Dodatkową funkcjonalnością zaimplementowaną w pętli jest możliwość wykonania w dowolnej chwili zdjęcia poprzez kamerę z wykorzystaniem przycisku **z** na klawiaturze oraz mozliwość wylądowania dronem poprzez przycisk **q**, co jednocześnie prowadzi do wyjścia z pętli oraz zakończenia pracy programu.

```python
while True:
    img = myTelloDrone.get_frame_read().frame
    img = cv2.resize(img, (w, h))
    img, info = findingFace(img)
    pError_yaw, pError_ud = trackingFace(info, w, h, pid_yaw, pError_yaw, pid_ud, pError_ud)
    cv2.imshow("Kamera", img)
    if keyboard.is_pressed('z'):
        cv2.imwrite(f"zdj/{time.time()}.jpg", img)
        time.sleep(0.3)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        myTelloDrone.send_rc_control(0, 0, 0, 0)
        myTelloDrone.streamoff()
        myTelloDrone.land()
        break
```

### Działanie programu z perspektywy komputera
Po uruchmieniu aplikacji i kilku sekundach inicjalizacji drona uruchomiony zostanie obraz z kamery i rozpoczęty proces śledzenia, który przedstawiony został w kolejnym punkcie. Dodatkowo w konsoli *pythona* na bieżąco wyświetlana jest informacja o trzech zadawanych prędkościach(kolejno przód/tył, obrót, góra/dół) dla drona oraz informacja o aktualnie wyliczanym polu powierzchni twarzy, co jest przydatne w celu określenia kiedy dron zacznie zbliżać się lub oddalać od wykrytej twarzy(regulacja trójpołożeniowa).

Obraz z kamery drona:

![kamera](https://user-images.githubusercontent.com/64974963/152412132-8f4c43ff-54b9-4c22-96b7-07322d0ef66a.png)

Obraz z konsoli:

![konsola](https://user-images.githubusercontent.com/64974963/152412409-abaac261-57e3-4da5-bf65-3745ab712b7a.png)

## Rezultaty działania

Lot drona góra/dół:

![gora_dol](https://user-images.githubusercontent.com/71281671/152399144-8b5f4db8-3582-4d66-a0d8-90dcaa7aedb9.gif)

Obrót drona lewo/prawo:

![obrot](https://user-images.githubusercontent.com/71281671/152399610-47af7e2e-7d3b-4287-8c8a-7b4418d51b62.gif)

Lot drona przód/tył:

![przod_tyl](https://user-images.githubusercontent.com/71281671/152399693-2299b6cd-e37a-40b7-a2e9-ea8545077363.gif)

Film prezentujący efekt działania programu(z perspektywy osoby trzeciej): [Nagranie z kamery zewnętrznej](https://github.com/JedrzejGrzebisz/tello_project/blob/master/video/Prezentacja_rzeczywista.mp4)

Film prezentujący efekt działania programu(z perspektywy drona): [Nagranie z kamery drona](https://github.com/JedrzejGrzebisz/tello_project/blob/master/video/Prezentacja_programistyczna.mp4)

## Autorzy

- [Jędrzej Grzebisz](https://github.com/JedrzejGrzebisz)
- [Kacper Jabłoński](https://github.com/Djabollos)
