import pygame
import os

tile_width = tile_height = 50
WIDTH, HEIGHT = 1000, 700
tiles_group = pygame.sprite.Group()
all_sprites = pygame.sprite.Group()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.init()


class Loads:

    def __init__(self):
        pass

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
        'wall': lds.load_image('bricks.png'),
        'metal': lds.load_image('metal.png')
    }

    def __init__(self, pos, t_type):
        super().__init__(tiles_group, all_sprites)
        self.image = pygame.transform.scale(Tile.tile_images[t_type], (tile_width, tile_height))
        self.rect = self.image.get_rect()
        self.rect.x = pos[0]
        self.rect.y = pos[1]


class Level:

    def __init__(self):
        pass

    def generate_level(self, level):
        for y in range(len(level)):
            for x in range(len(level[y])):
                if level[y][x] == '.':
                    self.t_type = 'empty'
                elif level[y][x] == '#':
                    self.t_type = 'wall'
                elif level[y][x] == '+':
                    self.t_type = 'metal'
                tiles_group.add(Tile((x * tile_width, y * tile_height), self.t_type))


level = Loads().load_level('level.txt')
running = True
while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    Level().generate_level(level)
    tiles_group.draw(screen)
    pygame.display.flip()
