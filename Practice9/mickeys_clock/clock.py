import pygame
import os
import datetime

_image_library = {}


def get_image(path):
    global _image_library
    image = _image_library.get(path)
    if image is None:
        canonicalized_path = path.replace('/', os.sep).replace('\\', os.sep)
        image = pygame.image.load(canonicalized_path)
        _image_library[path] = image
    return image


class Mickey_clock:
    def __init__(self):
        self.width = 800
        self.height = 600
        self.CENTER = (self.width // 2, self.height // 2)

        self.font = pygame.font.SysFont("Lucida Grande", 48, bold=True)
        self.luminisent = (255, 164, 32)

        self.front = pygame.transform.scale(get_image("images/clock.png"), (self.width, self.height))
        self.min_hand = pygame.transform.smoothscale(get_image("images/min_hand.png"), (800, 600))
        self.sec_hand = pygame.transform.smoothscale(get_image("images/sec_hand.png"), (800, 600))

    def get_current_time(self):
        now = datetime.datetime.now()
        return now.minute, now.second

    def calculate_angle(self, minute, second):
            sec_angle = -second * 6 + 60
            min_angle = -(minute + second / 60) * 6 -45
            return min_angle, sec_angle
    def rotate_hand(self, screen, image, angle, pivot, offset):
        rotated_image = pygame.transform.rotate(image, angle)
        rotated_offset = offset.rotate(-angle)
        rect = rotated_image.get_rect(center=(pivot[0] - rotated_offset.x,
                                          pivot[1] - rotated_offset.y))
        screen.blit(rotated_image, rect)
    
    def output_time(self, screen, minute, second):
        time_str = f"{minute:02}:{second:02}"
        text_surface = self.font.render(time_str, True, self.luminisent)
        text_rect = text_surface.get_rect(center=(self.CENTER[0], self.height - 29))
        screen.blit(text_surface, text_rect)

    def draw(self, screen):
        minute, second = self.get_current_time()
        min_angle, sec_angle = self.calculate_angle(minute, second)
        screen.blit(self.front, (0, 0))
         # Центр часов (где плечи)
        pivot = self.CENTER

    # ⚠️ ВАЖНО: эти значения нужно подобрать под твою картинку
    # они задают где у руки "плечо" внутри PNG

    # Минутная рука (левая)
        min_offset = pygame.math.Vector2(0, 0)

    # Секундная рука (правая)
        sec_offset = pygame.math.Vector2(0, 0)

        self.rotate_hand(screen, self.min_hand, min_angle, pivot, min_offset)
        self.rotate_hand(screen, self.sec_hand, sec_angle, pivot, sec_offset)

        self.output_time(screen, minute, second)