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
W celu uruchomienia aplikacji należy pobrać katalog projektowy, a następnie w środowisku Python wraz z przedstawionymi wcześniej bibliotekami uruchomić plik [faceTracking](https://github.com/JedrzejGrzebisz/tello_project/blob/master/faceTracking.py). Jednocześnie należy pamiętać o połączeniu się poprzez wi-fi z dronem DJI(nie jest wymagana żadna dodatkowa konfiguracja połączenia).

```
git clone https://github.com/JedrzejGrzebisz/tello_project.git
cd tello_project
python3 ./faceTracking.py
```

## Realizacja aplikacji

## Rezultaty działania

Ruch drona góra/dół:

![gora_dol](https://user-images.githubusercontent.com/71281671/152399144-8b5f4db8-3582-4d66-a0d8-90dcaa7aedb9.gif)


## Autorzy

- [Jędrzej Grzebisz](https://github.com/JedrzejGrzebisz)
- [Kacper Jabłoński](https://github.com/Djabollos)
