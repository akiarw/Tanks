import pygame
import os

FPS = 100
tile_width = tile_height = 25
WIDTH, HEIGHT = 1000, 700

tiles_group = pygame.sprite.Group()
tank_sprites = pygame.sprite.Group()
stealth_group = pygame.sprite.Group()
bullets_sprites = pygame.sprite.Group()
menu_group = pygame.sprite.Group()
icons = pygame.sprite.Group()

screen = pygame.display.set_mode((WIDTH, HEIGHT + 100))
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
        'empty': pygame.transform.scale(lds.load_image('asphalt.png'), (tile_width, tile_height)),
        'wall': pygame.transform.scale(lds.load_image('bricks.png'), (tile_width, tile_height)),
        'metal': pygame.transform.scale(lds.load_image('metal.png'), (tile_width, tile_height)),
        'bush': pygame.transform.scale(lds.load_image('grass.jpg'), (tile_width, tile_height))
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
            self = Empty((self.rect.x, self.rect.y))
            walls[num] = [-tile_width, -tile_height]


class Grass(Tile):
    def __init__(self, pos):
        super().__init__(pos, 'bush')


class Bricks(Tile):
    def __init__(self, pos):
        super().__init__(pos, 'wall')
        self.armor = 2


class Metal(Tile):
    def __init__(self, pos):
        super().__init__(pos, 'metal')
        self.armor = 7


class Empty(Tile):
    def __init__(self, pos):
        super().__init__(pos, 'empty')


class MainMenu:

    def __init__(self):
        self.name = pygame.sprite.Sprite()
        self.name.image = Loads().load_image('Name.png')
        self.name.rect = self.name.image.get_rect()
        self.name.rect.x, self.name.rect.y = 330, 250

        self.__font = pygame.font.Font(None, 30)

        self.play = self.__font.render("Play", 1, (255, 255, 255))
        self.pos_play = (400, 400)

        self.create = self.__font.render("Create player's map", 1, (255, 255, 255))
        self.pos_create = (self.pos_play[0], self.pos_play[1] + 50)

        self.exit = self.__font.render("Exit", 1, (255, 255, 255))
        self.pos_exit = (self.pos_play[0], self.pos_play[1] + 100)

        self.instruction = self.__font.render("*instructions*", 1, (255, 255, 255))
        self.pos_instruction = (800, 200)

        self.arrow = pygame.sprite.Sprite()
        self.arrow.image = Tank.tank_image_right
        self.arrow.rect = self.arrow.image.get_rect()
        self.arrow.rect.x, self.arrow.rect.y = self.pos_play[0] - 50, self.pos_play[1] - 5

        menu_group.add(self.arrow)
        menu_group.add(self.name)

    def draw(self):
        screen.fill((0, 0, 0))
        screen.blit(self.play, self.pos_play)
        screen.blit(self.create, self.pos_create)
        screen.blit(self.exit, self.pos_exit)
        screen.blit(self.instruction, self.pos_instruction)
        menu_group.draw(screen)

    def change_cursor(self, vect):
        if vect == 'down':
            self.arrow.rect.y += 50 if self.arrow.rect.y < self.pos_exit[1] - 5 else 0
        elif vect == 'up':
            self.arrow.rect.y -= 50 if self.arrow.rect.y > self.pos_play[1] - 5 else 0

    def act(self):
        if self.arrow.rect.y == self.pos_play[1] - 5:
            return 'start'
        elif self.arrow.rect.y == self.pos_create[1] - 5:
            return 'create'
        else:
            return 'exit'


class SubMenu:
    health_image = pygame.sprite.Sprite()
    health_image.image = pygame.transform.scale(Loads().load_image('health.png'), (20, 20))
    health_image.rect = health_image.image.get_rect()
    health_image.rect.x, health_image.rect.y = 20, HEIGHT + 20

    armor_image = pygame.sprite.Sprite()
    armor_image.image = pygame.transform.scale(Loads().load_image('armor.png'), (20, 20))
    armor_image.rect = armor_image.image.get_rect()
    armor_image.rect.x, armor_image.rect.y = 20, HEIGHT + 50

    def __init__(self):
        self.health = tanks[0].health
        self.armor = tanks[0].armor
        icons.add(self.health_image, self.armor_image)

    def draw_chrs(self):
        pygame.draw.rect(screen, pygame.Color('Gray'), (48, HEIGHT + 18, 302, 22), 4)
        pygame.draw.rect(screen, pygame.Color('Gray'), (48, HEIGHT + 48, 302, 22), 4)
        if self.health > 0:
            pygame.draw.rect(screen, (255, 0, 0), (50, HEIGHT + 20, self.health * 3, 20))
        if self.armor > 0:
            pygame.draw.rect(screen, (0, 0, 255), (50, HEIGHT + 50, self.armor * 3, 20))

    def draw(self):
        pygame.draw.rect(screen, (0, 0, 0), (0, HEIGHT, WIDTH, 100))
        self.draw_chrs()
        icons.draw(screen)

    def update_stats(self):
        self.health = tanks[0].health
        self.armor = tanks[0].armor


class Bullet(pygame.sprite.Sprite):
    base_image = pygame.transform.scale(Loads().load_image('bullet.png'), (5, 10))
    images = {
        'up': base_image,
        'down': pygame.transform.rotate(base_image, 180),
        'right': pygame.transform.rotate(base_image, 270),
        'left': pygame.transform.rotate(base_image, 90)
    }

    def __init__(self, vector, num_of_tank):
        super().__init__(bullets_sprites)
        self.num_of_tank = num_of_tank
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
            if Tank.is_peres_rects(None, [self.rect.x, self.rect.y, 5, 5],
                                   [walls[i][0], walls[i][1], tile_width, tile_height]):
                self.minus()
                return i

        for i in range(len(tanks)):
            if Tank.is_peres_rects(None, [self.rect.x, self.rect.y, 5, 5],
                                   [tanks[i].rect.x, tanks[i].rect.y, 30, 30]) and self.num_of_tank != i:
                self.minus()
                tanks[i].get_damage(10)

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
                if level[y][x] == '.':
                    tiles_group.add(Empty((x * tile_width, y * tile_height)))
                elif level[y][x] == '#':
                    tiles_group.add(Bricks((x * tile_width, y * tile_height)))
                    walls.append([x * tile_width, y * tile_height])
                    walls_sprts.append(Bricks((x * tile_width, y * tile_height)))
                elif level[y][x] == '+':
                    tiles_group.add(Metal((x * tile_width, y * tile_height)))
                    walls.append([x * tile_width, y * tile_height])
                    walls_sprts.append(Metal((x * tile_width, y * tile_height)))
                elif level[y][x] == '*':
                    stealth_group.add(Grass((x * tile_width, y * tile_height)))
        tank_sprites.add(tanks[0])


class Tank(pygame.sprite.Sprite):
    tank_image_down = pygame.transform.scale(Loads().load_image('tank.png'), (30, 30))
    tank_image_up = pygame.transform.rotate(tank_image_down, 180)
    tank_image_left = pygame.transform.rotate(tank_image_down, 270)
    tank_image_right = pygame.transform.rotate(tank_image_down, 90)

    def __init__(self, start_coords):
        super().__init__(tank_sprites)
        self.speed = 1
        self.health = 100
        self.armor = 100
        self.image = self.tank_image_up
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = start_coords

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
        for tank in tanks:
            if self.is_peres_rects([pos[0], pos[1], 30, 30],
                                   [tank.rect.x, tank.rect.y, 30, 30]) and tank != self:
                return False

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

    def is_ok(self, tank_num):
        if self.health <= 0:
            self.destroy(tank_num)
            return False
        return True

    def destroy(self, tank_num):
        tank_sprites.remove(self)
        tanks[tank_num] = None

    def get_damage(self, damage, ):
        if self.armor > 0:
            self.armor -= int(damage * 0.75)
            self.health -= int(damage * 0.25)
        else:
            self.health -= damage


walls = []
walls_sprts = []

clock = pygame.time.Clock()

level = Loads().load_level('level.txt')

main_menu = MainMenu()
tanks = [Tank((500, 500))]
tanks.append(Tank((600, 600)))
in_menu = True
the_map = Level(level)
submenu = SubMenu()

napr = 'up'
vectors = {
    273: 'up',
    274: 'down',
    275: 'right',
    276: 'left'
}
running = True

'''while in_menu:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            in_menu = running = False

        if event.type == pygame.KEYDOWN:
            if event.key == 32:
                act = main_menu.act()
                if act == 'start':
                    in_menu = False
                elif act == 'exit':
                    in_menu = running = False
            elif event.key in [273, 274]:
                main_menu.change_cursor(vectors[event.key])

    main_menu.draw()
    pygame.display.flip()'''

vector = None

while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == 32:
                Bullet(vector if vector else napr, 0).shoot((tanks[0].rect.x + 13, tanks[0].rect.y + 13))
            else:
                vector = vectors.get(event.key, None)

        if event.type == pygame.KEYUP:
            if vectors.get(event.key, None) == vector and vector:
                napr = vector
                vector = None

    submenu.update_stats()
    submenu.draw()
    if vector:
        tanks[0].move(vector)
    tiles_group.draw(screen)
    bullets_sprites.draw(screen)
    tank_sprites.draw(screen)
    stealth_group.draw(screen)
    pygame.display.flip()
    clock.tick(FPS)
    for bullet in bullets_sprites:
        bullet.move()
