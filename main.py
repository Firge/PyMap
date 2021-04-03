import requests
import os
import pygame
import itertools
import sys
pygame.init()
screen = pygame.display.set_mode((600, 450))


class Button(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__(buttons)
        self.image = pygame.surface.Surface((0, 0))
        self.hover_image = pygame.surface.Surface((0, 0))
        self.rect = self.image.get_rect()
        self.function = lambda: None
        self.hover = False

    def resize(self, width, height):
        self.rect.width = width
        self.rect.height = height

    def move(self, x, y):
        self.rect.x = x
        self.rect.y = y

    def connect(self, function):
        self.function = function

    def update(self, *args, **kwargs):
        if args and args[0].type == pygame.MOUSEBUTTONUP and self.rect.collidepoint(args[0].pos):
            self.function()
        if args and args[0].type == pygame.MOUSEMOTION:
            if self.hover:
                if not self.rect.collidepoint(args[0].pos):
                    self.hover = False
                    self.image, self.hover_image = self.hover_image, self.image
            else:
                if self.rect.collidepoint(args[0].pos):
                    self.hover = True
                    self.image, self.hover_image = self.hover_image, self.image


    def set_surface(self, surface: pygame.surface.Surface):
        self.image = surface
        self.rect.width, self.rect.height = self.image.get_size()

    def set_hover_surface(self, surface: pygame.surface.Surface):
        self.hover_image = surface


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    im = pygame.image.load(fullname)
    if colorkey is not None:
        im = im.convert()
        if colorkey == -1:
            colorkey = im.get_at((0, 0))
        im.set_colorkey(colorkey)
    else:
        im = im.convert_alpha()
    return im



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


def next_view():
    global view, image
    view = next(views)
    image = image_by_coords([str(x) for x in coords], spn=sizes[delta], l=view)



coords = (135.071915, 48.480225)
sizes = ["90,90", "50,50", "40,40", "20,20", "10,10", "5,5",
         "2.5,2.5", "1,1", "0.5,0.5", "0.25,0.25", "0.15,0.15",
         "0.1,0.1", "0.05,0.05", "0.025,0.025", "0.01,0.01",
         "0.005,0.005", "0.0025,0.0025", "0.001,0.001", "0.0005,0.0005"]
views = itertools.cycle(['map', 'sat', 'sat,skl'])
buttons = pygame.sprite.Group()
view_button = Button()
view_button.set_surface(load_image('view_button.png'))
view_button.set_hover_surface(load_image('view_button_hover.png'))
view_button.connect(next_view)
view_button.move(548, 12)
delta = 9
view = next(views)
image = image_by_coords([str(x) for x in coords], spn=sizes[delta])
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_PAGEUP:
                if delta == 18:
                    continue
                delta += 1
                image = image_by_coords([str(x) for x in coords], spn=sizes[delta], l=view)
            elif event.key == pygame.K_PAGEDOWN:
                if delta == 0:
                    continue
                delta -= 1
                image = image_by_coords([str(x) for x in coords], spn=sizes[delta], l=view)
            elif event.key == pygame.K_UP:
                dlt = float(sizes[delta].split(',')[0])
                if coords[1] + dlt >= 90 - dlt:
                    continue
                coords = (coords[0], coords[1] + dlt)
                image = image_by_coords([str(x) for x in coords], spn=sizes[delta], l=view)
            elif event.key == pygame.K_DOWN:
                dlt = float(sizes[delta].split(',')[0])
                if coords[1] - dlt <= -90 + dlt:
                    continue
                coords = (coords[0], coords[1] - dlt)
                image = image_by_coords([str(x) for x in coords], spn=sizes[delta], l=view)
            elif event.key == pygame.K_LEFT:
                dlt = float(sizes[delta].split(',')[0])
                coords = ((coords[0] - dlt * 1.5 + 180) % 360 - 180, coords[1])
                image = image_by_coords([str(x) for x in coords], spn=sizes[delta], l=view)
            elif event.key == pygame.K_RIGHT:
                dlt = float(sizes[delta].split(',')[0])
                coords = ((coords[0] + dlt * 1.5 + 180) % 360 - 180, coords[1])
                image = image_by_coords([str(x) for x in coords], spn=sizes[delta], l=view)
        elif event.type == pygame.MOUSEBUTTONUP:
            buttons.update(event)
        elif event.type == pygame.MOUSEMOTION:
            buttons.update(event)
        elif event.type == pygame.QUIT:
            running = False
    screen.blit(image, (0, 0))
    buttons.draw(screen)
    pygame.display.flip()
pygame.quit()
