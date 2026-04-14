import pygame
from ball import Ball

pygame.init()

width = 800
height = 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Moving red ball")
white = (255, 255, 255)
red = (255, 0, 0)
ball = Ball(width // 2, height // 2, 25, red, width, height)
clock = pygame.time.Clock()
run = True

while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
    pressed = pygame.key.get_pressed()
    if pressed[pygame.K_UP]: ball.move_up()
    if pressed[pygame.K_DOWN]: ball.move_down()
    if pressed[pygame.K_LEFT]: ball.move_left()
    if pressed[pygame.K_RIGHT]: ball.move_right()

    screen.fill(white)
    ball.draw(screen)
    pygame.display.flip()
    clock.tick(60)

pygame.quit()