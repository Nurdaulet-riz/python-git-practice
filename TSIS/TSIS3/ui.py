import pygame
from typing import Tuple

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (180, 180, 180)
DARK_GRAY = (60, 60, 60)
BLUE = (40, 120, 220)
YELLOW = (255, 215, 0)


class Button:

    def __init__(self, x: int, y: int, w: int, h: int, text: str):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text

    def draw(self, surface: pygame.Surface, font: pygame.font.Font) -> None:
        mouse_pos = pygame.mouse.get_pos()
        color = BLUE if self.rect.collidepoint(mouse_pos) else GRAY
        pygame.draw.rect(surface, color, self.rect, border_radius=10)
        pygame.draw.rect(surface, BLACK, self.rect, 2, border_radius=10)

        label = font.render(self.text, True, BLACK)
        surface.blit(label, label.get_rect(center=self.rect.center))

    def clicked(self, event: pygame.event.Event) -> bool:
        return event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos)


def draw_text(surface: pygame.Surface, text: str, font: pygame.font.Font,
              color: Tuple[int, int, int], x: int, y: int, center: bool = False) -> None:
    label = font.render(text, True, color)
    rect = label.get_rect()
    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)
    surface.blit(label, rect)
