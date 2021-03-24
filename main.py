import requests
import os
import pygame
import math


def data_by_address(address):
    geocoder_server = 'http://geocode-maps.yandex.ru/1.x/'
    geocoder_params = {
        "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
        "geocode": address,
        "format": "json"}
    response = requests.get(geocoder_server, params=geocoder_params)
    json_response = response.json()
    data = json_response["response"]["GeoObjectCollection"][
        "featureMember"][0]["GeoObject"]
    return data


def parse_geocoder_data(data):
    bounded = data['boundedBy']['Envelope']
    lower = tuple(map(float, bounded['lowerCorner'].split()))
    upper = tuple(map(float, bounded['upperCorner'].split()))
    delta = upper[0] - lower[0], upper[1] - lower[1]
    ret = {'address': data['metaDataProperty']['GeocoderMetaData']['Address']['formatted'],
           'coords': tuple(map(float, data['Point']['pos'].split())),
           'delta': delta}
    return ret


def lonlat_distance(a, b):
    degree_to_meters_factor = 111.3 * 1000
    a_lon, a_lat = a
    b_lon, b_lat = b
    radians_lattitude = math.radians((a_lat + b_lat) / 2.)
    lat_lon_factor = math.cos(radians_lattitude)
    dx = abs(a_lon - b_lon) * degree_to_meters_factor * lat_lon_factor
    dy = abs(a_lat - b_lat) * degree_to_meters_factor
    distance = math.sqrt(dx * dx + dy * dy)
    return distance


def image_by_coords(coords, **kwargs):
    map_server = 'https://static-maps.yandex.ru/1.x/'
    map_params = {
        "l": 'map',
        "ll": ','.join(coords)}
    map_params.update(kwargs)
    response = requests.get(map_server, params=map_params)
    map_file = "map.png"
    with open(map_file, "wb") as file:
        file.write(response.content)
        file.close()
    image = pygame.image.load(map_file)
    os.remove(map_file)
    return image


coords = (135.071915, 48.480225)
sizes = ["0.25,0.25"]
delta = "0.25,0.25"
pygame.init()
screen = pygame.display.set_mode((600, 450))
image = image_by_coords([str(x) for x in coords], spn=delta)
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    screen.blit(image, (0, 0))
    pygame.display.flip()
pygame.quit()
