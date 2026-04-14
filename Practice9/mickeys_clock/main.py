import pygame
from clock import Mickey_clock

pygame.init()

mickey_clock = Mickey_clock()
clock = pygame.time.Clock()
screen = pygame.display.set_mode((mickey_clock.width, mickey_clock.height))
pygame.display.set_caption("Mickey's clock")

run = True
while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            run = False

    mickey_clock.draw(screen)

    pygame.display.flip()
    clock.tick(1)

pygame.quit()