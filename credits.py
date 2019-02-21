import pygame

WIDTH = 1000
HEIGHT = 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.init()


class Credits:
    def __init__(self):
        pygame.mixer.music.load("sounds/credits.MP3")
        pygame.mixer.music.set_volume(0.2)
        pygame.mixer.music.play()
        screen.fill((0, 0, 0))
        pygame.font.init()
        zfont = pygame.font.SysFont('Microsoft Monotype Corsiva', 50)
        ourfont = pygame.font.SysFont('Microsoft Monotype Corsiva', 40)
        screen.blit(zfont.render('Создатели:', 1, (255, 255, 255)), (400, 20))
        screen.blit(ourfont.render('Смирнов Александр', 1, (255, 255, 255)), (350, 180))
        screen.blit(ourfont.render('Кирюшин Арсений', 1, (255, 255, 255)), (355, 280))
        screen.blit(ourfont.render('Мадамкин Виталий', 1, (255, 255, 255)), (355, 380))
        pygame.display.flip()

    def cycle(self):
        running = True
        while running:
            Credits()
            for event in pygame.event.get():
                if event.type in [pygame.QUIT, pygame.KEYDOWN]:
                    running = False
            pygame.display.flip()
        pygame.mixer.music.stop()
