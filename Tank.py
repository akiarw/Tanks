import pygame
import os
import sys
import credits
from random import randrange, choice


def restore_program_data():    # инициализация всех глобальных переменных
    global FPS, tile_width, tile_height, WIDTH, HEIGHT, tiles_group, tank_sprites, stealth_group, bullets_sprites
    global menu_group, icons, shoots, explosions_group, screen, start_sound, end_sound, fire_sound, enemy_sound
    FPS = 100
    tile_width = tile_height = 25
    WIDTH, HEIGHT = 1000, 700

    tiles_group = pygame.sprite.Group()
    tank_sprites = pygame.sprite.Group()
    stealth_group = pygame.sprite.Group()
    bullets_sprites = pygame.sprite.Group()
    menu_group = pygame.sprite.Group()
    icons = pygame.sprite.Group()
    shoots = pygame.sprite.Group()
    explosions_group = pygame.sprite.Group()

    screen = pygame.display.set_mode((WIDTH, HEIGHT + 100))
    pygame.init()

    start_sound = pygame.mixer.Sound("sounds/gamestart.ogg")
    end_sound = pygame.mixer.Sound("sounds/gameover.ogg")
    fire_sound = pygame.mixer.Sound("sounds/fire.ogg")
    enemy_sound = pygame.mixer.Sound("sounds/enemy.ogg")
    pygame.mixer.music.load("sounds/background.MP3")
    pygame.mixer.music.set_volume(0.2)


restore_program_data()


class Loads:     #закрузка/выгрузка из файлов

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

    def load_records(self):
        with open("data/records.txt", 'r', encoding='utf8') as filename:
            return list(map(int, filename.read().split()))

    def save_result(self):
        with open("data/records.txt", 'w', encoding='utf8') as filename:
            filename.write(' '.join(list(map(str, game.records))))


class Tile(pygame.sprite.Sprite):     # родитель всех тайлов
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
            Explosion((self.rect.x, self.rect.y))
            self = Empty((self.rect.x, self.rect.y))
            game.walls[num] = [-tile_width, -tile_height]


class Grass(Tile):   # класс для кустов
    def __init__(self, pos):
        super().__init__(pos, 'bush')


class Bricks(Tile):    # класс для кирпичей
    def __init__(self, pos):
        super().__init__(pos, 'wall')
        self.armor = 2


class Metal(Tile):      # класс для металлических блоков
    def __init__(self, pos):
        super().__init__(pos, 'metal')
        self.armor = 7


class Empty(Tile):      # класс для пустоты
    def __init__(self, pos):
        super().__init__(pos, 'empty')


class MainMenu:     # работа  главного меню

    def __init__(self):
        self.name = pygame.sprite.Sprite()
        self.name.image = Loads().load_image('Name.png')
        self.name.rect = self.name.image.get_rect()
        self.name.rect.x, self.name.rect.y = 330, 250

        self.font = pygame.font.Font(None, 30)

        self.play = self.font.render("Play", 1, (255, 255, 255))
        self.pos_play = (400, 400)

        self.create = self.font.render("Credits", 1, (255, 255, 255))
        self.pos_create = (self.pos_play[0], self.pos_play[1] + 50)

        self.exit = self.font.render("Exit", 1, (255, 255, 255))
        self.pos_exit = (self.pos_play[0], self.pos_play[1] + 100)

        self.instruction = self.font.render("", 1, (255, 255, 255))
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
        pygame.display.flip()

    def change_cursor(self, vect):
        if vect == 'down':
            self.arrow.rect.y += 50 if self.arrow.rect.y < self.pos_exit[1] - 5 else 0
        elif vect == 'up':
            self.arrow.rect.y -= 50 if self.arrow.rect.y > self.pos_play[1] - 5 else 0

    def act(self):
        if self.arrow.rect.y == self.pos_play[1] - 5:
            return 'start'
        elif self.arrow.rect.y == self.pos_create[1] - 5:
            return 'credits'
        else:
            return 'exit'

    def cycle(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == 32:
                    act = main_menu.act()
                    if act == 'start':
                        game.in_menu = False
                    elif act == 'credits':
                        credits.Credits().cycle()
                    elif act == 'exit':
                        game.in_menu = game.running = False
                        sys.exit()
                elif event.key in [273, 274]:
                    main_menu.change_cursor(game.vectors[event.key])

            self.draw()


class GameOver:   # класс экрана "Game Over"
    def __init__(self):
        self.font = pygame.font.Font(None, 50)
        self.iters = 0

    def cycle(self):
        self.iters += 1
        if self.iters > 200:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    game.in_go_menu = False

        self.draw()

    def draw(self):
        screen.fill((0, 0, 0))
        screen.blit(pygame.transform.scale(Loads().load_image('game_over.png'), (WIDTH, HEIGHT - 100)), (0, -100))
        screen.blit(self.font.render('Your score:', 1, (255, 255, 255)), (WIDTH // 4, HEIGHT // 2 + 100))
        screen.blit(pygame.font.Font(None, 100).render(str(game.submenu.score), 1, (255, 255, 255)),
                    (WIDTH // 4 + 200, HEIGHT // 2 + 80))
        screen.blit(self.font.render('Best Scores', 1, (255, 255, 255)), (WIDTH - 300, HEIGHT // 2 + 50))
        for i in range(10):
            try:
                record = '#{} - {}'.format(i + 1, game.records[i])
            except IndexError:
                record = '#{} - ////'.format(i + 1)
            screen.blit(pygame.font.Font(None, 35).render(str(record), 1, (255, 255, 255)),
                        (WIDTH - 300, HEIGHT // 2 + 100 + 20 * i))
        pygame.display.flip()

    def add_to_high_scores(self):
        if game.submenu.score:
            game.records.append(game.submenu.score)
            game.records.sort(reverse=True)
            Loads().save_result()


class SubMenu:     # класс для панели состояния игрока
    health_image = pygame.sprite.Sprite()
    health_image.image = pygame.transform.scale(Loads().load_image('health.png'), (20, 20))
    health_image.rect = health_image.image.get_rect()
    health_image.rect.x, health_image.rect.y = 20, HEIGHT + 20

    armor_image = pygame.sprite.Sprite()
    armor_image.image = pygame.transform.scale(Loads().load_image('armor.png'), (20, 20))
    armor_image.rect = armor_image.image.get_rect()
    armor_image.rect.x, armor_image.rect.y = 20, HEIGHT + 50

    def __init__(self):
        self.font = pygame.font.Font(None, 100)
        self.update_stats()
        self.score_pos = (WIDTH - 200, HEIGHT + 20)
        self.score = 0

        icons.add(self.health_image, self.armor_image)

    def draw_chrs(self):
        pygame.draw.rect(screen, pygame.Color('Gray'), (48, HEIGHT + 18, 302, 22), 4)
        pygame.draw.rect(screen, pygame.Color('Gray'), (48, HEIGHT + 48, 302, 22), 4)
        if self.health > 0:
            pygame.draw.rect(screen, (255, 0, 0), (50, HEIGHT + 20, self.health * 3, 20))
        if self.armor > 0:
            pygame.draw.rect(screen, (0, 0, 255), (50, HEIGHT + 50, self.armor * 3, 20))

    def text(self):
        screen.blit(self.text_score, self.score_pos)

    def draw(self):
        pygame.draw.rect(screen, (0, 0, 0), (0, HEIGHT, WIDTH, 100))
        pygame.draw.rect(screen, (255, 255, 255), (0, HEIGHT, WIDTH, 100), 4)
        pygame.draw.rect(screen, (255, 255, 255), (WIDTH // 2 - 1, HEIGHT + 48, 202, 22), 2)

        self.text()
        self.draw_chrs()
        self.update_stats()
        icons.draw(screen)

    def draw_gran(self):
        pygame.draw.rect(screen, (0, 255, 0),
                         (WIDTH // 2 - 2, HEIGHT + 48, game.bonus.green_pos * 2, 22), 2)

    def update_stats(self):
        self.health = int(game.tanks[0].health)
        self.armor = int(game.tanks[0].armor)
        self.score = game.tanks[0].score
        self.text_score = self.font.render(str(self.score), 1, (255, 255, 255))


class Explosion(pygame.sprite.Sprite):   # класс анимации взрывов
    lds = Loads()
    explosion = []
    for i in range(8):
        explosion.append(pygame.transform.scale(lds.load_image('Explosions\\exp{}.png'.format(i + 1)),
                                                (tile_width, tile_height)))

    def __init__(self, coords):
        super().__init__(explosions_group)
        self.step = 0
        self.image = self.explosion[0]
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = coords

    def new_step(self):
        self.step += 1
        try:
            self.image = self.explosion[self.step // 5]
        except IndexError:
            explosions_group.remove(self)


class Shoot(pygame.sprite.Sprite):     # класс анимации огня
    def __init__(self):
        super().__init__(shoots)
        self.otkat = 5
        self.base_fire = pygame.transform.scale(Loads().load_image('Explosions\\fire.png'), (10, 10))
        self.fires = {
            'up': self.base_fire,
            'down': pygame.transform.rotate(self.base_fire, 180),
            'right': pygame.transform.rotate(self.base_fire, 270),
            'left': pygame.transform.rotate(self.base_fire, 90)
        }

    def fir(self, tank_crds, vector):
        self.image = self.fires[vector]
        self.rect = self.image.get_rect()
        tank_crds = list(tank_crds)

        if vector == 'up':
            tank_crds[0] += 10
            tank_crds[1] -= 10
        elif vector == 'down':
            tank_crds[0] += 10
            tank_crds[1] += 30
        elif vector == 'left':
            tank_crds[0] -= 10
            tank_crds[1] += 10
        else:
            tank_crds[0] += 30
            tank_crds[1] += 10

        self.rect.x, self.rect.y = tank_crds


class Bullet(pygame.sprite.Sprite):    # класс анимации снарядов
    base_image = pygame.transform.scale(Loads().load_image('bullet.png'), (5, 10))
    images = {
        'up': base_image,
        'down': pygame.transform.rotate(base_image, 180),
        'right': pygame.transform.rotate(base_image, 270),
        'left': pygame.transform.rotate(base_image, 90)
    }

    def __init__(self, vector, tank, damage):
        super().__init__(bullets_sprites)
        self.tank = tank
        self.vector = vector
        self.speed = 10
        self.image = self.images[vector]
        self.rect = self.image.get_rect()
        self.damage = damage

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
        for i in range(len(game.walls)):
            if Tank.is_peres_rects(None, [self.rect.x, self.rect.y, 5, 5],
                                   [game.walls[i][0], game.walls[i][1], tile_width, tile_height]):
                self.minus()
                return i

        for tank in game.tanks:
            if Tank.is_peres_rects(None, [self.rect.x, self.rect.y, 5, 5],
                                   [tank.rect.x, tank.rect.y, 30, 30]) and tank != self.tank:
                self.minus()
                self.effect(tank)

    def effect(self, tank):
        tank.get_damage(self.damage)

    def minus(self):
        bullets_sprites.remove(self)

    def is_on_grass(self, pos):
        for wall in game.walls:
            if self.is_peres_rects([pos[0], pos[1], 30, 30],
                                   [wall[0], wall[1], tile_width, tile_height]):
                return False
        if 0 > pos[0] or pos[0] + 30 > WIDTH or 0 > pos[1] or pos[1] + 30 > HEIGHT:
            return False
        return True


class Level:    # класс для генерации уровня

    def __init__(self):
        for y in range(len(game.level)):
            for x in range(len(game.level[y])):
                if game.level[y][x] == '.':
                    tiles_group.add(Empty((x * tile_width, y * tile_height)))
                elif game.level[y][x] == '#':
                    tiles_group.add(Bricks((x * tile_width, y * tile_height)))
                    game.walls.append([x * tile_width, y * tile_height])
                    walls_sprts.append(Bricks((x * tile_width, y * tile_height)))
                elif game.level[y][x] == '+':
                    tiles_group.add(Metal((x * tile_width, y * tile_height)))
                    game.walls.append([x * tile_width, y * tile_height])
                    walls_sprts.append(Metal((x * tile_width, y * tile_height)))
                elif game.level[y][x] == '*':
                    stealth_group.add(Grass((x * tile_width, y * tile_height)))
        tank_sprites.add(game.tanks[0])

    def generate_map(self):
        global walls, walls_sprts, tiles_group, stealth_group
        walls, walls_sprts = [], []
        tiles_group, stealth_group = pygame.sprite.Group(), pygame.sprite.Group()
        for y in range(0, HEIGHT // tile_height - 1, 2):
            for x in range(0, WIDTH // tile_width - 1, 2):
                if not self.is_on_tank((x * tile_width, y * tile_height)):
                    znak = choice(['.', '.', '.', '.', '.', '.', '#', '#', '+', '*', '*'])
                else:
                    znak = '.'
                for i in ((0, 0), (1, 0), (0, 1), (1, 1)):
                    game.level[y + i[1]][x + i[0]] = znak
        Level()

    def is_on_tank(self, pos):
        for tank in game.tanks:
            if tank.is_peres_rects([tank.rect.x, tank.rect.y, 30, 30],
                                   [pos[0], pos[1], tile_width * 2, tile_height * 2]):
                return True
        return False


class Tank(pygame.sprite.Sprite):    # класс для пользовательского танка
    tank_image_right = pygame.transform.rotate(pygame.transform.scale(Loads().load_image('tanks/tank.png'), (30, 30)),
                                               90)

    def __init__(self, start_coords, health=100, armor=100, speed=2, damage=10, image='tanks/tank.png'):
        super().__init__(tank_sprites)
        self.tank_image_down = pygame.transform.scale(Loads().load_image(image), (30, 30))
        self.tank_image_up = pygame.transform.rotate(self.tank_image_down, 180)
        self.tank_image_left = pygame.transform.rotate(self.tank_image_down, 270)
        self.tank_image_right = pygame.transform.rotate(self.tank_image_down, 90)
        self.score = 0
        self.speed = speed
        self.health = health
        self.armor = armor
        self.damage = damage
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
        global game
        for tank in game.tanks:
            if self.is_peres_rects([pos[0], pos[1], 30, 30],
                                   [tank.rect.x, tank.rect.y, 30, 30]) and tank != self:
                return False

        for wall in game.walls:
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

    def destroy(self):
        Explosion((self.rect.x, self.rect.y))
        tank_sprites.remove(self)
        if self == game.tanks[0]:
            game.running = False
        game.tanks.remove(self)

        game.injure = False
        game.corrosion = False

        game.tanks[0].score += 1
        game.respawn.append(100)
        if game.bonus:
            game.bonus.quest_completed()

    def get_damage(self, damage):
        if self.armor > 0:
            self.armor -= int(damage * 0.75)
            self.health -= int(damage * 0.25)
        else:
            self.health -= damage
        if self.health <= 0:
            self.destroy()

    def is_hided(self):
        for bush in stealth_group:
            if bush.rect.x < self.rect.x < bush.rect.x + tile_width * 2 - 30 and \
                    bush.rect.y < self.rect.y < bush.rect.y + tile_height * 2 - 30:
                return True
        return False


class Enemy(Tank):      # класс вражеских танков
    def __init__(self, target, picture):
        super().__init__(self.spawn(), 30, 0, 1, image=picture)
        self.fire_sound = fire_sound
        self.last_coords = [None] * 5
        self.evector = None
        self.otkat = 0
        self.damage = 10
        self.target = target
        self.ox, self.oy = 100, 100

    def vect_change(self, ox, oy):
        if abs(ox) > abs(oy):
            if ox > 0:
                self.evector = 'left'
            else:
                self.evector = 'right'
        elif abs(ox) < abs(oy):
            if oy > 0:
                self.evector = 'up'
            else:
                self.evector = 'down'

    def action(self):
        if not self.target.is_hided():
            self.ox = self.rect.x - self.target.rect.x
            self.oy = self.rect.y - self.target.rect.y
        if self.ox in range(-15, 16) or self.oy in range(-15, 16) or not self.is_moving():
            self.vect_change(self.ox, self.oy)
            if self.otkat < 0 and self.evector:
                self.fire_sound.play()
                Shoot().fir((self.rect.x, self.rect.y), self.evector)
                Bullet(self.evector, self, self.damage).shoot((self.rect.x + 13, self.rect.y + 13))
                self.otkat = 60
            self.evector = None
        if not self.evector:
            self.vect_change(self.ox, self.oy)

        self.move(self.evector)

    def spawn(self):
        x, y = randrange(200, 900), randrange(200, 650)
        while not self.is_on_grass((x, y)):
            x, y = randrange(200, 900), randrange(200, 700)
        enemy_sound.play()
        return x, y

    def is_moving(self):
        self.last_coords.append([self.rect.x, self.rect.y])
        self.last_coords.pop(0)
        for crds in self.last_coords:
            if crds != self.last_coords[0]:
                return True
        return False


class Bonus(pygame.sprite.Sprite):  # система бонусов

    def __init__(self, time, image=Tile.tile_images['empty']):
        super().__init__(icons)
        self.green_pos = randrange(30, 81)
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = WIDTH // 2, HEIGHT + 20
        self.base_time = time // self.green_pos
        self.time = self.base_time

    def timer(self):
        self.time -= 1
        return self.time

    def draw_time(self):
        self.percent = int(self.time / self.base_time * 100)

        if self.green_pos < self.percent:
            color = (190, 190, 190)
        else:
            color = (255 - int(self.percent * 2.5), int(self.percent * 2.5), 0)

        pygame.draw.rect(screen, color, (WIDTH // 2, HEIGHT + 50, self.percent * 2, 20))

    def quest_completed(self, status='pass'):
        self.time = 0
        icons.remove(self)
        game.bonus = None
        game.bonus_quest = 0
        if status == 'pass' and self.percent < self.green_pos:
            self.effect()
        elif status == 'fail':
            self.debuff()


class MedComplect(Bonus):    # бонус здоровья
    def __init__(self, time):
        super().__init__(time, SubMenu.health_image.image)

    def effect(self):
        game.tanks[0].health = 100

    def debuff(self):
        game.injure = True


class RepairComplect(Bonus):      # бонус восстановления брони
    def __init__(self, time):
        super().__init__(time, SubMenu.armor_image.image)

    def effect(self):
        game.tanks[0].armor = 100

    def debuff(self):
        game.corrosion = True


class Game:   # основной игровой класс

    def __init__(self):
        pass

    def restore_data(self):
        self.corrosion = False
        self.injure = False

        self.fire_sound = fire_sound
        self.tanks_count = 5  # не больше 5!!!
        self.records = Loads().load_records()
        self.in_go_menu = True
        self.vector = None
        self.walls = []
        self.walls_sprts = []

        self.respawn = []

        self.bonus_quest = 0
        self.bonus = None
        self.base_time_for_quest = 48000

        self.clock = pygame.time.Clock()

        self.tanks = [Tank((500, 500))]

        for i in range(self.tanks_count):
            self.tanks.append(Enemy(self.tanks[0], "tanks/tank{}.png".format(i + 1)))

        self.level = []
        for y in range(HEIGHT // tile_height):
            self.level.append([])
            for x in range(WIDTH // tile_width):
                self.level[y].append('.')
        self.the_map = Level()
        self.the_map.generate_map()

        self.submenu = SubMenu()

        self.napr = 'up'
        self.vectors = {
            273: 'up',
            274: 'down',
            275: 'right',
            276: 'left'
        }
        self.running = True
        self.in_menu = True

    def cycle(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == 32:
                    self.fire_sound.play()
                    Shoot().fir((self.tanks[0].rect.x, self.tanks[0].rect.y), self.vector if self.vector else self.napr)
                    Bullet(self.vector if self.vector else self.napr, self.tanks[0], self.tanks[0].damage).shoot(
                        (self.tanks[0].rect.x + 13, self.tanks[0].rect.y + 13))
                else:
                    self.vector = self.vectors.get(event.key, None)

            if event.type == pygame.KEYUP:
                if self.vectors.get(event.key, None) == self.vector and self.vector:
                    self.napr = self.vector
                    self.vector = None

        for i in range(len(self.respawn)):
            self.respawn[i] -= 1
            if not self.respawn[i]:
                self.tanks.append(Enemy(target=self.tanks[0], picture="tanks/tank{}.png".format(len(self.tanks) - 1)))

        for sh in shoots:
            sh.otkat -= 1
            if sh.otkat < 0:
                shoots.remove(sh)

        for tank in self.tanks[1:]:
            tank.action()
            tank.otkat -= 1

        if self.vector:
            self.tanks[0].move(self.vector)

        for exp in explosions_group:
            exp.new_step()

        self.submenu.draw()
        tiles_group.draw(screen)
        bullets_sprites.draw(screen)
        tank_sprites.draw(screen)
        shoots.draw(screen)
        explosions_group.draw(screen)
        stealth_group.draw(screen)

        if self.injure:
            screen.blit(main_menu.font.render('inj', 1, (255, 100, 0)),
                        (self.submenu.health_image.rect.x + 350, self.submenu.health_image.rect.y))
            if self.tanks[0].health > 0:
                self.tanks[0].health -= 0.1
            else:
                self.tanks[0].destroy()

        if self.corrosion:
            screen.blit(main_menu.font.render('cor', 1, (200, 190, 0)),
                        (self.submenu.armor_image.rect.x + 350, self.submenu.armor_image.rect.y))
            if self.tanks[0].armor:
                self.tanks[0].armor -= 0.1

        if self.bonus_quest <= 0:
            if self.bonus:
                self.bonus.quest_completed('fail')
            elif not randrange(0, 100):
                self.bonus = choice([MedComplect, RepairComplect])(self.base_time_for_quest)
                self.bonus_quest = self.bonus.time
        elif self.bonus_quest > 0:
            self.bonus_quest = self.bonus.timer()
            self.bonus.draw_time()
            self.submenu.draw_gran()

        if self.tanks[0].health <= 80:
            for i in range(0, int(81 - self.tanks[0].health), 2):
                pygame.draw.rect(screen, (255, 0, 0), (i, i, WIDTH - i * 2, HEIGHT - i * 2), 1)

        pygame.display.flip()
        self.clock.tick(FPS)
        for bullet in bullets_sprites:
            bullet.move()


while True:
    game = Game()
    game.restore_data()

    main_menu = MainMenu()
    game_over = GameOver()

    start_sound.play()

    main_menu.draw()
    while game.in_menu:
        main_menu.cycle()

    start_sound.stop()
    pygame.mixer.music.play()

    while game.running:
        try:
            game.cycle()
        except IndexError:
            game.running = False

    pygame.mixer.music.stop()

    end_sound.play()
    game_over.draw()
    game_over.add_to_high_scores()
    while game.in_go_menu:
        game_over.cycle()
    end_sound.stop()
    restore_program_data()
