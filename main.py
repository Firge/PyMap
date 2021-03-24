import requests
import os
import pygame
import math


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

delta = 10
pygame.init()
screen = pygame.display.set_mode((600, 450))
image = image_by_coords([str(x) for x in coords], z=str(delta))
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_PAGEUP:
                if delta == 19:
                    continue
                delta += 1
                image = image_by_coords([str(x) for x in coords], z=str(delta))
            elif event.key == pygame.K_PAGEDOWN:
                if delta == 0:
                    continue
                delta -= 1
                image = image_by_coords([str(x) for x in coords], z=str(delta))
        elif event.type == pygame.QUIT:
            running = False
    screen.blit(image, (0, 0))
    pygame.display.flip()
pygame.quit()
