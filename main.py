import sys
import pygame
import requests
from PIL import Image
from io import BytesIO
from constants import GEOCODE_API_URL, STATIC_API_URL, GEOCODE_API_KEY
import typing


def geocoder_get_longitude_and_latitude(address: str) -> typing.Tuple[float, float]:
    geocoder_params = {
        "apikey": GEOCODE_API_KEY,
        "geocode": address,
        "format": "json"
    }

    response = requests.get(GEOCODE_API_URL, params=geocoder_params)

    if not response:
        raise ValueError(f"Request execution: {response.status_code} ({response.reason}) on {response.url}")

    json_response = response.json()
    toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
    toponym_coordinates = toponym["Point"]["pos"]
    toponym_longitude, toponym_latitude = toponym_coordinates.split(" ")
    return toponym_longitude, toponym_latitude


def geocoder_get_ll_and_spn(address: str) -> typing.Tuple[typing.Tuple[float, float],
                                                          typing.Tuple[float, float]]:
    geocoder_params = {
        "apikey": GEOCODE_API_KEY,
        "geocode": address,
        "format": "json"
    }

    response = requests.get(GEOCODE_API_URL, params=geocoder_params)

    if not response:
        raise ValueError(f"Request execution: {response.status_code} ({response.reason}) on {response.url}")

    json_response = response.json()
    toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
    toponym_coordinates = toponym["Point"]["pos"]
    toponym_longitude, toponym_latitude = toponym_coordinates.split(" ")
    envelope = toponym["boundedBy"]["Envelope"]
    l, b = envelope["lowerCorner"].split(" ")
    r, t = envelope["upperCorner"].split(" ")
    dx = abs(float(r) - float(l)) / 2
    dy = abs(float(b) - float(t)) / 2
    return (toponym_longitude, toponym_latitude), (dx, dy)


def get_map_image(**kwargs) -> Image:
    response = requests.get(GEOCODE_API_URL, params=kwargs)
    return Image.open(BytesIO(response.content))


def save_map_image(filename: str = "map.png", **kwargs) -> None:
    response = requests.get(STATIC_API_URL, params=kwargs)
    if not response:
        raise ValueError(f"Request execution: {response.status_code} ({response.reason}) on {response.url}")
    with open(filename, "wb") as file:
        file.write(response.content)


def show_map_using_pillow(img: Image) -> None:
    img.show()


def show_map_using_pygame(filename: str) -> None:
    pygame.init()
    screen = pygame.display.set_mode((600, 450))
    screen.blit(pygame.image.load(filename), (0, 0))
    pygame.display.flip()
    while pygame.event.wait().type != pygame.QUIT:
        pass


if __name__ == "__main__":
    toponym_to_find = " ".join(sys.argv[1:])

    ll, spn = geocoder_get_ll_and_spn(toponym_to_find)
    params = {
        "ll": ",".join(map(str, ll)),
        "spn": ",".join(map(str, spn)),
        "l": "map",
        "pt": ",".join(map(str, ll)) + f",pm2lbl57"
    }
    fname = "map.png"
    save_map_image(fname, **params)
    show_map_using_pygame(fname)
