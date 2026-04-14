import pygame
import os
from player import Music_player

pygame.init()
pygame.mixer.init()

screen = pygame.display.set_mode((700, 400))
pygame.display.set_caption("Music player")

white = (255, 255, 255)
black = (0, 0, 0)

font = pygame.font.SysFont(None, 36)
small_font = pygame.font.SysFont(None, 28)

player = Music_player("music/sample_tracks")
clock = pygame.time.Clock()

run = True
while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            run = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                player.play()
            elif event.key == pygame.K_s:
                player.stop()
            elif event.key == pygame.K_n:
                player.next()
            elif event.key == pygame.K_b:
                player.previous()
            elif event.key == pygame.K_q:
                run = False
    
    screen.fill(white)

    title_text = font.render("Music Player", True, black)
    track_text = small_font.render(f"Current track: {player.get_name()}", True, black)
    controls_text = small_font.render("p=Play  s=Stop  n=Next  b=Back  q=Quit", True, black)

    screen.blit(title_text, (250, 80))
    screen.blit(track_text, (120, 160))
    screen.blit(controls_text, (160, 240))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()