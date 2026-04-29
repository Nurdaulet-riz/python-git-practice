import json
import os
import random
import sys

import pygame

from db import get_leaderboard, get_personal_best, init_db, save_game_session

pygame.init()

CELL = 20
COLS, ROWS = 30, 25
GAME_W = COLS * CELL
GAME_H = ROWS * CELL
HUD_H = 55
WIDTH = GAME_W
HEIGHT = GAME_H + HUD_H
FPS = 60

FOODS_PER_LEVEL = 3
BASE_INTERVAL = 120
FOOD_LIFETIME = 5000
POWERUP_LIFETIME = 8000
POWERUP_DURATION = 5000
POWERUP_SPAWN_CHANCE = 0.004
POISON_SPAWN_CHANCE = 0.006

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (35, 35, 35)
LIGHT_GRAY = (100, 100, 100)
DARK_GRAY = (20, 20, 20)
GREEN = (50, 200, 50)
DARK_GREEN = (30, 130, 30)
RED = (220, 50, 50)
DARK_RED = (120, 0, 0)
ORANGE = (255, 150, 0)
PURPLE = (160, 60, 220)
YELLOW = (255, 220, 0)
BLUE = (60, 150, 255)
CYAN = (70, 230, 230)
PINK = (255, 80, 180)
WALL_COL = (100, 100, 100)
OBSTACLE_COL = (140, 140, 140)

SETTINGS_FILE = "settings.json"

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("TSIS4 Snake Game")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 22, bold=True)
small_font = pygame.font.SysFont("Arial", 16, bold=True)
big_font = pygame.font.SysFont("Arial", 38, bold=True)


def load_settings():
    default = {
        "snake_color": [50, 200, 50],
        "grid_overlay": True,
        "sound": False,
    }
    if not os.path.exists(SETTINGS_FILE):
        save_settings(default)
        return default

    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)
        default.update(data)
        return default
    except Exception:
        return default


def save_settings(settings):
    with open(SETTINGS_FILE, "w", encoding="utf-8") as file:
        json.dump(settings, file, indent=2)


def draw_text(text, fnt, color, center):
    surf = fnt.render(text, True, color)
    rect = surf.get_rect(center=center)
    screen.blit(surf, rect)
    return rect


def draw_button(rect, text, mouse_pos):
    color = LIGHT_GRAY if rect.collidepoint(mouse_pos) else (70, 70, 70)
    pygame.draw.rect(screen, color, rect, border_radius=10)
    pygame.draw.rect(screen, WHITE, rect, 2, border_radius=10)
    draw_text(text, font, WHITE, rect.center)


def random_free_cell(snake, obstacles, forbidden=None):
    forbidden = forbidden or set()
    used = set(snake) | set(obstacles) | set(forbidden)
    for _ in range(1000):
        pos = (random.randint(1, COLS - 2), random.randint(1, ROWS - 2))
        if pos not in used:
            return pos
    return None


class Food:
    def __init__(self, snake, obstacles):
        self.pos = None
        self.weight = 1
        self.created_time = 0
        self.respawn(snake, obstacles)

    def respawn(self, snake, obstacles, forbidden=None):
        self.pos = random_free_cell(snake, obstacles, forbidden)
        self.weight = random.choice([1, 2, 3])
        self.created_time = pygame.time.get_ticks()

    def is_expired(self):
        return pygame.time.get_ticks() - self.created_time > FOOD_LIFETIME

    def time_left(self):
        left = FOOD_LIFETIME - (pygame.time.get_ticks() - self.created_time)
        return max(0, left // 1000 + 1)

    def draw(self):
        if not self.pos:
            return
        x, y = self.pos
        cx = x * CELL + CELL // 2
        cy = y * CELL + CELL // 2
        color = RED if self.weight == 1 else ORANGE if self.weight == 2 else PURPLE
        pygame.draw.circle(screen, color, (cx, cy), CELL // 2 - 2)
        text = small_font.render(str(self.weight), True, WHITE)
        screen.blit(text, (cx - text.get_width() // 2, cy - text.get_height() // 2))


class PoisonFood:
    def __init__(self):
        self.pos = None
        self.created_time = 0

    def spawn(self, snake, obstacles, forbidden):
        self.pos = random_free_cell(snake, obstacles, forbidden)
        self.created_time = pygame.time.get_ticks()

    def clear(self):
        self.pos = None

    def draw(self):
        if not self.pos:
            return
        x, y = self.pos
        pygame.draw.rect(screen, DARK_RED, (x * CELL + 3, y * CELL + 3, CELL - 6, CELL - 6), border_radius=6)
        draw_text("P", small_font, WHITE, (x * CELL + CELL // 2, y * CELL + CELL // 2))


class PowerUp:
    TYPES = ["speed", "slow", "shield"]

    def __init__(self):
        self.pos = None
        self.kind = None
        self.created_time = 0

    def spawn(self, snake, obstacles, forbidden):
        self.pos = random_free_cell(snake, obstacles, forbidden)
        self.kind = random.choice(self.TYPES)
        self.created_time = pygame.time.get_ticks()

    def clear(self):
        self.pos = None
        self.kind = None

    def is_expired(self):
        return self.pos and pygame.time.get_ticks() - self.created_time > POWERUP_LIFETIME

    def draw(self):
        if not self.pos:
            return
        x, y = self.pos
        color = BLUE if self.kind == "speed" else CYAN if self.kind == "slow" else PINK
        pygame.draw.circle(screen, color, (x * CELL + CELL // 2, y * CELL + CELL // 2), CELL // 2 - 2)
        label = "F" if self.kind == "speed" else "S" if self.kind == "slow" else "#"
        draw_text(label, small_font, BLACK, (x * CELL + CELL // 2, y * CELL + CELL // 2))


class SnakeGame:
    def __init__(self, username, settings):
        self.username = username
        self.settings = settings
        self.personal_best = get_personal_best(username)
        self.result_saved = False
        self.reset()

    def reset(self):
        self.snake = [(COLS // 2, ROWS // 2), (COLS // 2 - 1, ROWS // 2), (COLS // 2 - 2, ROWS // 2)]
        self.direction = (1, 0)
        self.next_dir = (1, 0)
        self.score = 0
        self.level = 1
        self.foods_eaten = 0
        self.grow_cells = 0
        self.base_interval = BASE_INTERVAL
        self.move_timer = 0
        self.obstacles = []
        self.food = Food(self.snake, self.obstacles)
        self.poison = PoisonFood()
        self.powerup = PowerUp()
        self.speed_effect = None
        self.speed_effect_until = 0
        self.shield = False
        self.game_over = False

    def current_interval(self):
        interval = max(40, self.base_interval - (self.level - 1) * 15)
        now = pygame.time.get_ticks()
        if self.speed_effect and now > self.speed_effect_until:
            self.speed_effect = None
        if self.speed_effect == "speed":
            return max(25, int(interval * 0.65))
        if self.speed_effect == "slow":
            return int(interval * 1.5)
        return interval

    def set_level_obstacles(self):
        if self.level < 3:
            self.obstacles = []
            return
        count = min(6 + self.level * 2, 35)
        self.obstacles = []
        protected = self.safe_zone_around_head()
        for _ in range(count):
            pos = random_free_cell(self.snake, self.obstacles, protected)
            if pos:
                self.obstacles.append(pos)

    def safe_zone_around_head(self):
        hx, hy = self.snake[0]
        cells = set()
        for dx in range(-2, 3):
            for dy in range(-2, 3):
                nx, ny = hx + dx, hy + dy
                if 1 <= nx < COLS - 1 and 1 <= ny < ROWS - 1:
                    cells.add((nx, ny))
        return cells

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and self.direction != (0, 1):
                self.next_dir = (0, -1)
            elif event.key == pygame.K_DOWN and self.direction != (0, -1):
                self.next_dir = (0, 1)
            elif event.key == pygame.K_LEFT and self.direction != (1, 0):
                self.next_dir = (-1, 0)
            elif event.key == pygame.K_RIGHT and self.direction != (-1, 0):
                self.next_dir = (1, 0)

    def update(self, dt):
        if self.game_over:
            return

        now = pygame.time.get_ticks()
        forbidden = {self.food.pos} if self.food.pos else set()
        if self.poison.pos:
            forbidden.add(self.poison.pos)
        if self.powerup.pos:
            forbidden.add(self.powerup.pos)

        if self.food.is_expired():
            self.food.respawn(self.snake, self.obstacles, forbidden)

        if not self.poison.pos and random.random() < POISON_SPAWN_CHANCE:
            self.poison.spawn(self.snake, self.obstacles, forbidden)
        if self.poison.pos and now - self.poison.created_time > FOOD_LIFETIME:
            self.poison.clear()

        if not self.powerup.pos and random.random() < POWERUP_SPAWN_CHANCE:
            self.powerup.spawn(self.snake, self.obstacles, forbidden)
        if self.powerup.is_expired():
            self.powerup.clear()

        self.move_timer += dt
        if self.move_timer < self.current_interval():
            return
        self.move_timer = 0
        self.direction = self.next_dir
        head = (self.snake[0][0] + self.direction[0], self.snake[0][1] + self.direction[1])

        collision = (
            head[0] <= 0 or head[0] >= COLS - 1 or
            head[1] <= 0 or head[1] >= ROWS - 1 or
            head in self.snake or
            head in self.obstacles
        )
        if collision:
            if self.shield:
                self.shield = False
                return
            self.end_game()
            return

        self.snake.insert(0, head)

        if head == self.food.pos:
            self.score += self.food.weight * 10
            self.foods_eaten += 1
            self.grow_cells += self.food.weight
            self.food.respawn(self.snake, self.obstacles, {self.poison.pos, self.powerup.pos})
            if self.foods_eaten % FOODS_PER_LEVEL == 0:
                self.level += 1
                self.set_level_obstacles()

        if head == self.poison.pos:
            self.poison.clear()
            for _ in range(2):
                if len(self.snake) > 1:
                    self.snake.pop()
            if len(self.snake) <= 1:
                self.end_game()
                return

        if head == self.powerup.pos:
            if self.powerup.kind == "speed":
                self.speed_effect = "speed"
                self.speed_effect_until = now + POWERUP_DURATION
            elif self.powerup.kind == "slow":
                self.speed_effect = "slow"
                self.speed_effect_until = now + POWERUP_DURATION
            elif self.powerup.kind == "shield":
                self.shield = True
            self.powerup.clear()

        if self.grow_cells > 0:
            self.grow_cells -= 1
        else:
            self.snake.pop()

    def end_game(self):
        self.game_over = True
        if not self.result_saved:
            save_game_session(self.username, self.score, self.level)
            self.personal_best = max(self.personal_best, self.score)
            self.result_saved = True

    def draw_grid(self):
        if not self.settings.get("grid_overlay", True):
            return
        for x in range(0, GAME_W, CELL):
            pygame.draw.line(screen, (35, 35, 35), (x, 0), (x, GAME_H))
        for y in range(0, GAME_H, CELL):
            pygame.draw.line(screen, (35, 35, 35), (0, y), (GAME_W, y))

    def draw(self):
        screen.fill(GRAY)
        pygame.draw.rect(screen, BLACK, (0, 0, GAME_W, GAME_H))
        self.draw_grid()

        for x in range(COLS):
            pygame.draw.rect(screen, WALL_COL, (x * CELL, 0, CELL, CELL))
            pygame.draw.rect(screen, WALL_COL, (x * CELL, (ROWS - 1) * CELL, CELL, CELL))
        for y in range(1, ROWS - 1):
            pygame.draw.rect(screen, WALL_COL, (0, y * CELL, CELL, CELL))
            pygame.draw.rect(screen, WALL_COL, ((COLS - 1) * CELL, y * CELL, CELL, CELL))

        for x, y in self.obstacles:
            pygame.draw.rect(screen, OBSTACLE_COL, (x * CELL + 1, y * CELL + 1, CELL - 2, CELL - 2), border_radius=3)

        snake_color = tuple(self.settings.get("snake_color", GREEN))
        for i, (x, y) in enumerate(self.snake):
            color = snake_color if i == 0 else DARK_GREEN
            pygame.draw.rect(screen, color, (x * CELL + 1, y * CELL + 1, CELL - 2, CELL - 2), border_radius=4)

        self.food.draw()
        self.poison.draw()
        self.powerup.draw()

        hud_y = GAME_H + 8
        screen.blit(font.render(f"User: {self.username}", True, WHITE), (8, hud_y))
        screen.blit(font.render(f"Score: {self.score}", True, WHITE), (135, hud_y))
        screen.blit(font.render(f"Level: {self.level}", True, YELLOW), (260, hud_y))
        screen.blit(font.render(f"Best: {self.personal_best}", True, CYAN), (370, hud_y))
        screen.blit(font.render(f"Food: {self.food.time_left()}s", True, WHITE), (485, hud_y))
        status = "Shield" if self.shield else self.speed_effect or ""
        if status:
            screen.blit(small_font.render(status, True, PINK), (8, GAME_H + 36))


class App:
    def __init__(self):
        init_db()
        self.settings = load_settings()
        self.username = "Player"
        self.state = "menu"
        self.game = None
        self.message = "Enter username and press Play"

    def run(self):
        while True:
            if self.state == "menu":
                self.main_menu()
            elif self.state == "game":
                self.play_game()
            elif self.state == "leaderboard":
                self.leaderboard_screen()
            elif self.state == "settings":
                self.settings_screen()
            elif self.state == "game_over":
                self.game_over_screen()

    def main_menu(self):
        buttons = {
            "play": pygame.Rect(210, 220, 180, 42),
            "leaderboard": pygame.Rect(210, 275, 180, 42),
            "settings": pygame.Rect(210, 330, 180, 42),
            "quit": pygame.Rect(210, 385, 180, 42),
        }
        input_rect = pygame.Rect(160, 155, 280, 38)

        while self.state == "menu":
            mouse = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_BACKSPACE:
                        self.username = self.username[:-1]
                    elif event.key == pygame.K_RETURN:
                        self.start_game()
                    elif len(self.username) < 20 and event.unicode.isprintable():
                        self.username += event.unicode
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if buttons["play"].collidepoint(mouse):
                        self.start_game()
                    elif buttons["leaderboard"].collidepoint(mouse):
                        self.state = "leaderboard"
                    elif buttons["settings"].collidepoint(mouse):
                        self.state = "settings"
                    elif buttons["quit"].collidepoint(mouse):
                        self.quit()

            screen.fill(DARK_GRAY)
            draw_text("SNAKE GAME", big_font, GREEN, (WIDTH // 2, 85))
            draw_text("Username:", font, WHITE, (WIDTH // 2, 135))
            pygame.draw.rect(screen, BLACK, input_rect, border_radius=8)
            pygame.draw.rect(screen, WHITE, input_rect, 2, border_radius=8)
            draw_text(self.username or "type username", font, WHITE, input_rect.center)
            for key, rect in buttons.items():
                label = key.title() if key != "leaderboard" else "Leaderboard"
                draw_button(rect, label, mouse)
            draw_text(self.message, small_font, YELLOW, (WIDTH // 2, 465))
            pygame.display.flip()
            clock.tick(FPS)

    def start_game(self):
        self.username = self.username.strip() or "Player"
        self.game = SnakeGame(self.username, self.settings)
        self.state = "game"

    def play_game(self):
        while self.state == "game":
            dt = clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.state = "menu"
                self.game.handle_event(event)

            self.game.update(dt)
            self.game.draw()
            pygame.display.flip()

            if self.game.game_over:
                self.state = "game_over"

    def game_over_screen(self):
        retry = pygame.Rect(200, 310, 200, 45)
        menu = pygame.Rect(200, 370, 200, 45)
        while self.state == "game_over":
            mouse = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit()
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if retry.collidepoint(mouse):
                        self.start_game()
                    elif menu.collidepoint(mouse):
                        self.state = "menu"
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        self.start_game()
                    elif event.key == pygame.K_ESCAPE:
                        self.state = "menu"

            screen.fill(DARK_GRAY)
            draw_text("GAME OVER", big_font, RED, (WIDTH // 2, 110))
            draw_text(f"Final score: {self.game.score}", font, WHITE, (WIDTH // 2, 175))
            draw_text(f"Level reached: {self.game.level}", font, YELLOW, (WIDTH // 2, 215))
            draw_text(f"Personal best: {self.game.personal_best}", font, CYAN, (WIDTH // 2, 255))
            draw_button(retry, "Retry", mouse)
            draw_button(menu, "Main Menu", mouse)
            pygame.display.flip()
            clock.tick(FPS)

    def leaderboard_screen(self):
        back = pygame.Rect(215, 455, 170, 42)
        rows = get_leaderboard(10)
        while self.state == "leaderboard":
            mouse = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.state = "menu"
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if back.collidepoint(mouse):
                        self.state = "menu"

            screen.fill(DARK_GRAY)
            draw_text("LEADERBOARD", big_font, YELLOW, (WIDTH // 2, 55))
            headers = ["#", "Username", "Score", "Level", "Date"]
            xs = [35, 90, 250, 345, 430]
            for x, h in zip(xs, headers):
                screen.blit(small_font.render(h, True, WHITE), (x, 105))
            y = 135
            if not rows:
                draw_text("No saved scores yet", font, WHITE, (WIDTH // 2, 230))
            for i, row in enumerate(rows, start=1):
                username, score, level, played_at = row
                data = [str(i), username[:14], str(score), str(level), played_at]
                for x, value in zip(xs, data):
                    screen.blit(small_font.render(value, True, WHITE), (x, y))
                y += 30
            draw_button(back, "Back", mouse)
            pygame.display.flip()
            clock.tick(FPS)

    def settings_screen(self):
        grid_btn = pygame.Rect(190, 150, 220, 42)
        sound_btn = pygame.Rect(190, 205, 220, 42)
        color_btn = pygame.Rect(190, 260, 220, 42)
        save_btn = pygame.Rect(190, 380, 220, 42)
        colors = [[50, 200, 50], [60, 150, 255], [255, 220, 0], [255, 80, 180], [255, 150, 0]]
        color_index = 0
        if self.settings.get("snake_color") in colors:
            color_index = colors.index(self.settings["snake_color"])

        while self.state == "settings":
            mouse = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.state = "menu"
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if grid_btn.collidepoint(mouse):
                        self.settings["grid_overlay"] = not self.settings.get("grid_overlay", True)
                    elif sound_btn.collidepoint(mouse):
                        self.settings["sound"] = not self.settings.get("sound", False)
                    elif color_btn.collidepoint(mouse):
                        color_index = (color_index + 1) % len(colors)
                        self.settings["snake_color"] = colors[color_index]
                    elif save_btn.collidepoint(mouse):
                        save_settings(self.settings)
                        self.state = "menu"

            screen.fill(DARK_GRAY)
            draw_text("SETTINGS", big_font, WHITE, (WIDTH // 2, 80))
            draw_button(grid_btn, f"Grid: {'ON' if self.settings.get('grid_overlay') else 'OFF'}", mouse)
            draw_button(sound_btn, f"Sound: {'ON' if self.settings.get('sound') else 'OFF'}", mouse)
            draw_button(color_btn, "Change Snake Color", mouse)
            pygame.draw.rect(screen, tuple(self.settings.get("snake_color", GREEN)), (270, 325, 60, 35), border_radius=8)
            pygame.draw.rect(screen, WHITE, (270, 325, 60, 35), 2, border_radius=8)
            draw_button(save_btn, "Save & Back", mouse)
            pygame.display.flip()
            clock.tick(FPS)

    def quit(self):
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    App().run()
