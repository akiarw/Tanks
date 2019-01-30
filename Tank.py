import pygame


class Loads:
    WIDTH, HEIGHT = 550, 550
    tile_width = tile_height = 50

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

        max_width = Loads.WIDTH // Loads.tile_width
        max_height = Loads.HEIGHT // Loads.tile_height

        return list(map(lambda x: [i for i in x.ljust(max_width, '.')], level_map)) + [['.'] * max_width] * (
                max_height - len(level_map))


class Tile(pygame.sprite.Sprite):
    lds = Loads()
    tile_images = {
        'empty': lds.load_image('grass.png'),
        'wall': lds.load_image('bricks.png'),
        'metal': lds.load_image('metal.png')
    }

    def __init__(self, pos, t_type, tiles_group, all_sprites):
        super().__init__(tiles_group, all_sprites)
        self.image = pygame.transform.scale(Tile.tile_images[t_type], (Loads.tile_width, Loads.tile_height))
        self.rect = self.image.get_rect()
        self.rect.x = pos[0]
        self.rect.y = pos[1]


class Level:

    def __init__(self, tiles_group, all_sprites):
        self.tiles_group = tiles_group
        self.all_sprites = all_sprites

    def generate_level(self, level):
        for y in range(len(level)):
            for x in range(len(level[y])):
                if level[y][x] == '.':
                    self.t_type = 'empty'
                elif level[y][x] == '#':
                    self.t_type = 'wall'
                elif level[y][x] == '+':
                    self.t_type = 'metal'
                self.tiles_group.add(
                    Tile((x * Loads.tile_width, y * Loads.tile_height), self.t_type, self.tiles_group,
                         self.all_sprites))
