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


class Input(pygame.sprite.Sprite):
    def __init__(self):
        self.font = pygame.font.SysFont('Times New Roman', 14)
        super().__init__(buttons)
        self.text = ''
        self.image = pygame.surface.Surface((0, 0))
        self.box = pygame.surface.Surface((0, 0))
        self.rect = self.image.get_rect()
        self.active = False
        self.cursor = pygame.surface.Surface((1, 0))
        self.hover = False

    def resize(self, width, height):
        self.rect.size = width, height
        self.box = pygame.surface.Surface((width, height))
        self.box.fill((255, 255, 255), (0, 0, width, height))
        pygame.draw.rect(self.box, (230, 230, 230), (0, 0, width, height), 1)
        self.image = self.box.copy()
        self.cursor = pygame.surface.Surface((1, self.font.get_height()))
        self.cursor.fill((0, 0, 0))

    def move(self, x, y):
        self.rect.x = x
        self.rect.y = y

    def update(self, *args, **kwargs):
        if args and args[0].type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            else:
                self.text = self.text + event.unicode
            self.image = self.box.copy()
            self.image.blit(self.font.render(self.text, False, (0, 0, 0)),
                            (5, (self.rect.height - self.font.get_height()) // 2))
            self.image.blit(self.cursor, (self.font.size(self.text)[0] + 4,
                                          (self.rect.height - self.font.get_height()) // 2))
        elif args and args[0].type == pygame.MOUSEBUTTONDOWN:
            self.image = self.box.copy()
            self.image.blit(self.font.render(self.text, False, (0, 0, 0)),
                            (5, (self.rect.height - self.font.get_height()) // 2))
            if self.rect.collidepoint(args[0].pos):
                self.active = True
                self.image.blit(self.cursor, (self.font.size(self.text)[0] + 4,
                                              (self.rect.height - self.font.get_height()) // 2))
            else:
                self.active = False
        elif args and args[0].type == pygame.MOUSEMOTION:
            if self.rect.collidepoint(args[0].pos):
                if not self.hover:
                    self.hover = True
                    cursor = pygame.cursors.compile(pygame.cursors.textmarker_strings)
                    pygame.mouse.set_cursor((8, 16), (0, 0), *cursor)
            elif self.hover:
                self.hover = False
                pygame.mouse.set_cursor(*pygame.cursors.arrow)

        elif not args:
            self.image = self.box.copy()


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
    if map_params['pt'] is None:
        map_params.pop('pt')
    response = requests.get(map_server, params=map_params)
    map_file = "map.png"
    with open(map_file, "wb") as file:
        file.write(response.content)
        file.close()
    image = pygame.image.load(map_file)
    os.remove(map_file)
    return image


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


def next_view():
    global view, image
    view = next(views)
    image = image_by_coords([str(x) for x in coords], spn=sizes[delta], l=view)


def search():
    global image, coords, pt
    try:
        data = parse_geocoder_data(data_by_address(box.text))
    except Exception:
        return
    print(data)
    coords = data['coords']
    pt = f"{coords[0]},{coords[1]},pm2rdm"
    image = image_by_coords([str(x) for x in coords], spn=sizes[delta], l=view, pt=pt)


def delete():
    global pt, image
    box.text = ''
    box.update()
    pt = None
    image = image_by_coords([str(x) for x in coords], spn=sizes[delta], l=view, pt=pt)


pygame.mouse.set_cursor(*pygame.cursors.arrow)
coords = (135.071915, 48.480225)
sizes = ["90,90", "50,50", "40,40", "20,20", "10,10", "5,5",
         "2.5,2.5", "1,1", "0.5,0.5", "0.25,0.25", "0.15,0.15",
         "0.1,0.1", "0.05,0.05", "0.025,0.025", "0.01,0.01",
         "0.005,0.005", "0.0025,0.0025", "0.001,0.001", "0.0005,0.0005"]
views = itertools.cycle(['map', 'sat', 'sat,skl'])
pt = None

buttons = pygame.sprite.Group()

view_button = Button()
view_button.set_surface(load_image('view_button.png'))
view_button.set_hover_surface(load_image('view_button_hover.png'))
view_button.connect(next_view)
view_button.move(548, 12)

search_button = Button()
search_button.set_surface(load_image('search_button.png'))
search_button.set_hover_surface(load_image('search_button_hover.png'))
search_button.connect(search)
search_button.move(212, 12)

delete_button = Button()
delete_button.set_surface(load_image('delete_button.png'))
delete_button.set_hover_surface(load_image('delete_button_hover.png'))
delete_button.connect(delete)
delete_button.move(252, 12)

box = Input()
box.move(12, 12)
box.resize(200, 40)

delta = 9
view = next(views)
image = image_by_coords([str(x) for x in coords], spn=sizes[delta], pt=pt)
running = True
while running:
    for event in pygame.event.get():
        buttons.update(event)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_PAGEUP:
                if delta == 18:
                    continue
                delta += 1
                image = image_by_coords([str(x) for x in coords], spn=sizes[delta], l=view, pt=pt)
            elif event.key == pygame.K_PAGEDOWN:
                if delta == 0:
                    continue
                delta -= 1
                image = image_by_coords([str(x) for x in coords], spn=sizes[delta], l=view, pt=pt)
            elif event.key == pygame.K_UP:
                dlt = float(sizes[delta].split(',')[0])
                if coords[1] + dlt >= 90 - dlt:
                    continue
                coords = (coords[0], coords[1] + dlt)
                image = image_by_coords([str(x) for x in coords], spn=sizes[delta], l=view, pt=pt)
            elif event.key == pygame.K_DOWN:
                dlt = float(sizes[delta].split(',')[0])
                if coords[1] - dlt <= -90 + dlt:
                    continue
                coords = (coords[0], coords[1] - dlt)
                image = image_by_coords([str(x) for x in coords], spn=sizes[delta], l=view, pt=pt)
            elif event.key == pygame.K_LEFT:
                dlt = float(sizes[delta].split(',')[0])
                coords = ((coords[0] - dlt * 1.5 + 180) % 360 - 180, coords[1])
                image = image_by_coords([str(x) for x in coords], spn=sizes[delta], l=view, pt=pt)
            elif event.key == pygame.K_RIGHT:
                dlt = float(sizes[delta].split(',')[0])
                coords = ((coords[0] + dlt * 1.5 + 180) % 360 - 180, coords[1])
                image = image_by_coords([str(x) for x in coords], spn=sizes[delta], l=view, pt=pt)
        elif event.type == pygame.QUIT:
            running = False
    screen.blit(image, (0, 0))
    buttons.draw(screen)
    pygame.display.flip()
pygame.quit()
