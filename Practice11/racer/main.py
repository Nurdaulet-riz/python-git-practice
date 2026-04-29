import pygame
import sys
from pygame.locals import *
import random
import time

pygame.init()

FPS = 60
FramePerSec = pygame.time.Clock()
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 180, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 215, 0)
ORANGE = (255, 140, 0)

SPEED = 5
SCORE = 0
COINS = 0
COINS_FOR_SPEED_UP = 5  

font = pygame.font.SysFont("Verdana", 60)
font_small = pygame.font.SysFont("Verdana", 18)
game_over = font.render("Game Over", True, BLACK)

background = pygame.image.load("AnimatedStreet.png")

DISPLAYSURF = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
DISPLAYSURF.fill(WHITE)
pygame.display.set_caption("Racer Practice 11")

class Enemy(pygame.sprite.Sprite):

    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("Enemy.png")
        self.rect = self.image.get_rect()
        self.rect.center = (random.randint(40, SCREEN_WIDTH - 40), 0)

    def move(self):
        global SCORE
        self.rect.move_ip(0, SPEED)

        if self.rect.top > SCREEN_HEIGHT:
            SCORE += 1
            self.rect.top = 0
            self.rect.center = (random.randint(40, SCREEN_WIDTH - 40), 0)


class Player(pygame.sprite.Sprite):

    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("Player.png")
        self.rect = self.image.get_rect()
        self.rect.center = (160, 520)

    def move(self):
        pressed_keys = pygame.key.get_pressed()

        if self.rect.left > 0 and pressed_keys[K_LEFT]:
            self.rect.move_ip(-5, 0)

        if self.rect.right < SCREEN_WIDTH and pressed_keys[K_RIGHT]:
            self.rect.move_ip(5, 0)


class Coin(pygame.sprite.Sprite):

    def __init__(self):
        super().__init__()
        self.weight = 1
        self.image = None
        self.rect = None
        self.respawn()

    def create_image(self):
        if self.weight == 1:
            radius = 11
            color = YELLOW
        elif self.weight == 2:
            radius = 15
            color = ORANGE
        else:
            radius = 19
            color = GREEN

        self.image = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, color, (radius, radius), radius)
        pygame.draw.circle(self.image, BLACK, (radius, radius), radius, 2)

        text = font_small.render(str(self.weight), True, BLACK)
        self.image.blit(text, (radius - text.get_width() // 2,
                               radius - text.get_height() // 2))

    def respawn(self):
        self.weight = random.choice([1, 2, 3])
        self.create_image()

        self.rect = self.image.get_rect()
        self.rect.center = (random.randint(40, SCREEN_WIDTH - 40),
                            random.randint(-300, -30))

    def move(self):
        self.rect.move_ip(0, SPEED)
        if self.rect.top > SCREEN_HEIGHT:
            self.respawn()


P1 = Player()
E1 = Enemy()
C1 = Coin()

enemies = pygame.sprite.Group()
enemies.add(E1)

coins = pygame.sprite.Group()
coins.add(C1)

all_sprites = pygame.sprite.Group()
all_sprites.add(P1)
all_sprites.add(E1)
all_sprites.add(C1)


while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

    DISPLAYSURF.blit(background, (0, 0))
    score_text = font_small.render(f"Score: {SCORE}", True, BLACK)
    coins_text = font_small.render(f"Coins: {COINS}", True, BLACK)
    speed_text = font_small.render(f"Speed: {SPEED}", True, BLACK)
    DISPLAYSURF.blit(score_text, (10, 10))
    DISPLAYSURF.blit(coins_text, (10, 35))
    DISPLAYSURF.blit(speed_text, (10, 60))

    for entity in all_sprites:
        DISPLAYSURF.blit(entity.image, entity.rect)
        entity.move()

    collected_coin = pygame.sprite.spritecollideany(P1, coins)
    if collected_coin:
        COINS += collected_coin.weight
        SCORE += collected_coin.weight * 5
        collected_coin.respawn()

        if COINS % COINS_FOR_SPEED_UP == 0:
            SPEED += 1

    if pygame.sprite.spritecollideany(P1, enemies):
        pygame.mixer.Sound("crash.wav").play()
        time.sleep(0.5)

        DISPLAYSURF.fill(RED)
        DISPLAYSURF.blit(game_over, (30, 250))
        pygame.display.update()

        for entity in all_sprites:
            entity.kill()

        time.sleep(2)
        pygame.quit()
        sys.exit()

    pygame.display.update()
    FramePerSec.tick(FPS)
