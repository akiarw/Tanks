import pygame
import os

FPS = 100
tile_width = tile_height = 50
WIDTH, HEIGHT = 1000, 700
tiles_group = pygame.sprite.Group()
tank_sprites = pygame.sprite.Group()
bullets_sprites = pygame.sprite.Group()
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
        super().__init__(tiles_group)
        self.image = Tile.tile_images[t_type]
        self.rect = self.image.get_rect()
        self.rect.x = pos[0]
        self.rect.y = pos[1]

    def destroy(self, num):
        self.armor -= 1
        if not self.armor:
            self = Grass((self.rect.x, self.rect.y))
            walls[num] = [-tile_width, -tile_height]



class Grass(Tile):
    def __init__(self, pos):
        super().__init__(pos, 'empty')


class Bricks(Tile):
    def __init__(self, pos):
        super().__init__(pos, 'wall')
        self.armor = 3


class Metal(Tile):
    def __init__(self, pos):
        super().__init__(pos, 'metal')
        self.armor = 10


class Bullet(pygame.sprite.Sprite):
    base_image = pygame.transform.scale(Loads().load_image('bullet.png'), (10, 20))
    images = {
        'up': base_image,
        'down': pygame.transform.rotate(base_image, 180),
        'right': pygame.transform.rotate(base_image, 270),
        'left': pygame.transform.rotate(base_image, 90)
    }

    def __init__(self, vector):
        super().__init__(bullets_sprites)
        self.vector = vector
        self.speed = 10
        self.image = self.images[vector]
        self.rect = self.image.get_rect()

    def shoot(self, tank_pos):
        self.rect.x, self.rect.y = tank_pos

    def move(self):

        num_of_block = self.is_flown()
        if type(num_of_block) == int:
            walls_sprts[num_of_block].destroy(num_of_block)

        if self.vector == 'up':
            self.rect.y -= self.speed
        elif self.vector == 'down':
            self.rect.y += self.speed
        elif self.vector == 'left':
            self.rect.x -= self.speed
        elif self.vector == 'right':
            self.rect.x += self.speed
        if 0 > self.rect.x or self.rect.x > WIDTH or 0 > self.rect.y or self.rect.y > HEIGHT:
            self.minus()

    def is_flown(self):
        for i in range(len(walls)):
            if Tank.is_peres_rects(None, [self.rect.x, self.rect.y, 10, 10], [walls[i][0], walls[i][1], 50, 50]):
                self.minus()
                print(i)
                return i

    def minus(self):
        bullets_sprites.remove(self)

    def is_on_grass(self, pos):
        for wall in walls:
            if self.is_peres_rects([pos[0], pos[1], 30, 30],
                                   [wall[0], wall[1], tile_width, tile_height]):
                return False
        if 0 > pos[0] or pos[0] + 30 > WIDTH or 0 > pos[1] or pos[1] + 30 > HEIGHT:
            return False
        return True


class Level:

    def __init__(self, level):
        for y in range(len(level)):
            for x in range(len(level[y])):
                if level[y][x] in ['.', ' ']:
                    tiles_group.add(Grass((x * tile_width, y * tile_height)))
                elif level[y][x] == '#':
                    tiles_group.add(Bricks((x * tile_width, y * tile_height)))
                    walls.append([x * tile_width, y * tile_height])
                    walls_sprts.append(Bricks((x * tile_width, y * tile_height)))
                elif level[y][x] == '+':
                    tiles_group.add(Metal((x * tile_width, y * tile_height)))
                    walls.append([x * tile_width, y * tile_height])
                    walls_sprts.append(Metal((x * tile_width, y * tile_height)))

    def generate_map(self):
        tank_sprites.add(my_tank)


class Tank(pygame.sprite.Sprite):
    tank_image_down = pygame.transform.scale(Loads().load_image('tank.png'), (30, 30))
    tank_image_up = pygame.transform.rotate(tank_image_down, 180)
    tank_image_left = pygame.transform.rotate(tank_image_down, 270)
    tank_image_right = pygame.transform.rotate(tank_image_down, 90)

    def __init__(self):
        super().__init__(tank_sprites)
        self.speed = 1
        self.image = self.tank_image_up
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = 500, 500

    def move(self, vector):
        if vector == 'left':
            self.image = self.tank_image_left
            if self.is_on_grass((self.rect.x - self.speed, self.rect.y)):
                self.rect.x -= self.speed
        elif vector == 'right':
            self.image = self.tank_image_right
            if self.is_on_grass((self.rect.x + self.speed, self.rect.y)):
                self.rect.x += self.speed
        elif vector == 'up':
            self.image = self.tank_image_up
            if self.is_on_grass((self.rect.x, self.rect.y - self.speed)):
                self.rect.y -= self.speed
        elif vector == 'down':
            self.image = self.tank_image_down
            if self.is_on_grass((self.rect.x, self.rect.y + self.speed)):
                self.rect.y += self.speed

    def is_on_grass(self, pos):
        for wall in walls:
            if self.is_peres_rects([pos[0], pos[1], 30, 30],
                                   [wall[0], wall[1], tile_width, tile_height]):
                return False
        if 0 > pos[0] or pos[0] + 30 > WIDTH or 0 > pos[1] or pos[1] + 30 > HEIGHT:
            return False
        return True

    def is_peres_rects(self, rct1, rct2):
        if rct1[0] > rct2[0]:
            rct1, rct2 = rct2, rct1
        if rct2[0] in range(rct1[0], sum(rct1[::2]) + 1):
            if rct1[1] > rct2[1]:
                rct1, rct2 = rct2, rct1
            if rct2[1] in range(rct1[1], sum(rct1[1::2]) + 1):
                return True
        return False


walls = []
walls_sprts = []
clock = pygame.time.Clock()
level = Loads().load_level('level.txt')
map = Level(level)
my_tank = Tank()
running = True
moving = False
vector = 'up'
while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            moving = True
            if event.key == 276:
                vector = 'left'
            elif event.key == 275:
                vector = 'right'
            elif event.key == 273:
                vector = 'up'
            elif event.key == 274:
                vector = 'down'
            elif event.key == 32:
                Bullet(vector).shoot((my_tank.rect.x + 10, my_tank.rect.y + 10))
                moving = False

        if event.type == pygame.KEYUP:
            moving = False

    if moving:
        my_tank.move(vector)
    map.generate_map()
    tiles_group.draw(screen)
    bullets_sprites.draw(screen)
    tank_sprites.draw(screen)
    for bullet in bullets_sprites:
        bullet.move()
    pygame.display.flip()
    clock.tick(FPS)
