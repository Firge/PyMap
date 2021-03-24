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
sizes = ["90,90", "50,50", "40,40", "20,20", "10,10", "5,5",
         "2.5,2.5", "1,1", "0.5,0.5", "0.25,0.25", "0.15,0.15",
         "0.1,0.1", "0.05,0.05", "0.025,0.025", "0.01,0.01",
         "0.005,0.005", "0.0025,0.0025", "0.001,0.001", "0.0005,0.0005"]
delta = 9
pygame.init()
screen = pygame.display.set_mode((600, 450))
image = image_by_coords([str(x) for x in coords], spn=sizes[delta])
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_PAGEUP:
                if delta == 18:
                    continue
                delta += 1
                image = image_by_coords([str(x) for x in coords], spn=sizes[delta])
            elif event.key == pygame.K_PAGEDOWN:
                if delta == 0:
                    continue
                delta -= 1
                image = image_by_coords([str(x) for x in coords], spn=sizes[delta])
            elif event.key == pygame.K_UP:
                dlt = float(sizes[delta].split(',')[0])
                if coords[1] + dlt >= 90 - dlt:
                    continue
                coords = (coords[0], coords[1] + dlt)
                print(coords)
                image = image_by_coords([str(x) for x in coords], spn=sizes[delta])
            elif event.key == pygame.K_DOWN:
                dlt = float(sizes[delta].split(',')[0])
                if coords[1] - dlt <= -90 + dlt:
                    continue
                coords = (coords[0], coords[1] - dlt)
                image = image_by_coords([str(x) for x in coords], spn=sizes[delta])
            elif event.key == pygame.K_LEFT:
                dlt = float(sizes[delta].split(',')[0])
                coords = ((coords[0] - dlt * 1.5 + 180) % 360 - 180, coords[1])
                image = image_by_coords([str(x) for x in coords], spn=sizes[delta])
            elif event.key == pygame.K_RIGHT:
                dlt = float(sizes[delta].split(',')[0])
                coords = ((coords[0] + dlt * 1.5 + 180) % 360 - 180, coords[1])
                image = image_by_coords([str(x) for x in coords], spn=sizes[delta])
        elif event.type == pygame.QUIT:
            running = False
    screen.blit(image, (0, 0))
    pygame.display.flip()
pygame.quit()
