import pygame
import os

tile_width = tile_height = 50
WIDTH, HEIGHT = 1000, 700
tiles_group = pygame.sprite.Group()
all_sprites = pygame.sprite.Group()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.init()


class Loads:

    def load_image(self, name, colorkey=None):
        fullname = os.path.join('data', name)
        try:
            image = pygame.image.load(fullname)
        except pygame.error as message:
            print('Cannot load image:', name)
            raise SystemExit(message)
        image = image.convert_alpha()
        if colorkey is not None:

            if colorkey is -1:
                colorkey = image.get_at((0, 0))
            image.set_colorkey(colorkey)
        return image

    def load_level(self, filename):
        filename = "data/" + filename
        with open(filename, 'r') as mapFile:
            level_map = [line.strip() for line in mapFile]

        max_width = WIDTH // tile_width
        max_height = HEIGHT // tile_height

        return list(map(lambda x: [i for i in x.ljust(max_width, '.')], level_map)) + [['.'] * max_width] * (
                max_height - len(level_map))


class Tile(pygame.sprite.Sprite):
    lds = Loads()
    tile_images = {
        'empty': pygame.transform.scale(lds.load_image('grass.jpg'), (tile_width, tile_height)),
        'wall': pygame.transform.scale(lds.load_image('bricks.png'), (tile_width, tile_height)),
        'metal': pygame.transform.scale(lds.load_image('metal.png'), (tile_width, tile_height)),
    }

    def __init__(self, pos, t_type):
        super().__init__(tiles_group, all_sprites)
        self.image = Tile.tile_images[t_type]
        self.rect = self.image.get_rect()
        self.rect.x = pos[0]
        self.rect.y = pos[1]


class Grass(Tile):
    def __init__(self, pos):
        super().__init__(pos, 'empty')


class Bricks(Tile):
    def __init__(self, pos):
        super().__init__(pos, 'wall')


class Metal(Tile):
    def __init__(self, pos):
        super().__init__(pos, 'metal')


class Level:

    def generate_level(self, level):
        global tiles_group, all_sprites
        tiles_group = pygame.sprite.Group()
        all_sprites = pygame.sprite.Group()
        for y in range(len(level)):
            for x in range(len(level[y])):
                if level[y][x] in ['.', ' ']:
                    tiles_group.add(Grass((x * tile_width, y * tile_height)))
                elif level[y][x] == '#':
                    tiles_group.add(Bricks((x * tile_width, y * tile_height)))
                elif level[y][x] == '+':
                    tiles_group.add(Metal((x * tile_width, y * tile_height)))
        all_sprites.add(my_tank)


class Tank(pygame.sprite.Sprite):
    tank_image_down = pygame.transform.scale(Loads().load_image('tank.png'), (tile_width - 20, tile_height - 20))
    tank_image_up = pygame.transform.rotate(tank_image_down, 180)
    tank_image_left = pygame.transform.rotate(tank_image_down, 270)
    tank_image_right = pygame.transform.rotate(tank_image_down, 90)

    def __init__(self):
        super().__init__(all_sprites)
        self.speed = 1
        self.image = self.tank_image_up
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = 500, 500

    def move(self, vector):
        if vector == 'left':
            self.rect.x -= self.speed
            self.image = self.tank_image_left
        elif vector == 'right':
            self.rect.x += self.speed
            self.image = self.tank_image_right
        elif vector == 'up':
            self.rect.y -= self.speed
            self.image = self.tank_image_up
        elif vector == 'down':
            self.rect.y += self.speed
            self.image = self.tank_image_down


level = Loads().load_level('level.txt')
my_tank = Tank()
running = True
moving = False
while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            vector = 'left' if event.key == 276 else 'right' if event.key == 275 else 'up' \
                if event.key == 273 else 'down' if event.key == 274 else None
            moving = True

        if event.type == pygame.KEYUP:
            moving = False

    if moving:
        my_tank.move(vector)
    Level().generate_level(level)
    all_sprites.draw(screen)
    pygame.display.flip()
