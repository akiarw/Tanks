import pygame
import sys
import os

FPS = 50
WIDTH, HEIGHT = 550, 550
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))


class Images:
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

    def start_screen(self):
        intro_text = ["ЗАСТАВКА", "",
                      "Правила игры",
                      "Если в правилах несколько строк,",
                      "приходится выводить их построчно"]

        fon = pygame.transform.scale(self.load_image('fon.jpg'), (WIDTH, HEIGHT))
        screen.blit(fon, (0, 0))
        font = pygame.font.Font(None, 30)
        text_coord = 50
        for line in intro_text:
            string_rendered = font.render(line, 1, pygame.Color('black'))
            intro_rect = string_rendered.get_rect()
            text_coord += 10
            intro_rect.top = text_coord
            intro_rect.x = 10
            text_coord += intro_rect.height
            screen.blit(string_rendered, intro_rect)


class Level:
    def __init__(self):
        self.image = Images()
        self.tile_images = {'wall': self.image.load_image('wall.png'),
                            'empty': self.image.load_image('grass.png'),
                            'metal_wall': self.image.load_image('metal_wall.png')}

        self.player_image = self.image.load_image('tank.png')
        self.tile_width = self.tile_height = 20

    def load_level(self, filename):
        filename = "data/" + filename
        with open(filename, 'r') as mapFile:
            level_map = [line.strip() for line in mapFile]

        # и подсчитываем максимальную длину
        max_width = WIDTH // self.tile_width
        max_height = HEIGHT // self.tile_height

        return list(map(lambda x: [i for i in x.ljust(max_width, '.')], level_map)) + [['.'] * max_width] * (
                max_height - len(level_map))

    


    def ret_tile_images(self):
        return self.tile_images

    def ret_tile_size(self):
        return self.tile_width, self.tile_height


class Game:
    def __init__(self):
        pass

    def terminate(self):
        pygame.quit()
        sys.exit()
