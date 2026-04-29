import os
import random
import time
from dataclasses import dataclass
from typing import List, Optional, Tuple
import pygame
from persistence import save_score
from ui import Button, draw_text

SCREEN_WIDTH = 500
SCREEN_HEIGHT = 700
ROAD_LEFT = 60
ROAD_WIDTH = 380
ROAD_RIGHT = ROAD_LEFT + ROAD_WIDTH
LANES = 4
LANE_W = ROAD_WIDTH // LANES
FPS = 60
FINISH_DISTANCE = 3000
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (90, 90, 90)
DARK_GRAY = (40, 40, 40)
GREEN = (30, 150, 60)
RED = (220, 40, 40)
BLUE = (40, 120, 230)
YELLOW = (255, 220, 0)
ORANGE = (255, 150, 0)
PURPLE = (150, 70, 220)
CYAN = (0, 220, 220)
BROWN = (120, 70, 30)

DIFFICULTY = {
    "easy": {"speed": 4.0, "traffic": 1.15, "obstacles": 1.35},
    "normal": {"speed": 5.0, "traffic": 1.0, "obstacles": 1.0},
    "hard": {"speed": 6.2, "traffic": 0.75, "obstacles": 0.8},
}

ASSET_DIR = os.path.join(os.path.dirname(__file__), "assets")
PLAYER_IMAGE = os.path.join(ASSET_DIR, "Player.png")
ENEMY_IMAGE = os.path.join(ASSET_DIR, "Enemy.png")


def load_asset_image(path: str, size: Tuple[int, int]) -> Optional[pygame.Surface]:
    try:
        image = pygame.image.load(path).convert_alpha()
        return pygame.transform.smoothscale(image, size)
    except (pygame.error, FileNotFoundError):
        return None


@dataclass
class FloatingText:
    text: str
    x: int
    y: int
    timer: int = 60

    def update(self):
        self.y -= 1
        self.timer -= 1


class Player(pygame.sprite.Sprite):

    def __init__(self):
        super().__init__()
        self.base_image = load_asset_image(PLAYER_IMAGE, (42, 70))
        self.image = self.base_image.copy() if self.base_image else pygame.Surface((42, 70), pygame.SRCALPHA)
        self.speed = 6
        self.shield = False
        self.draw_car()
        self.rect = self.image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 95))

    def draw_car(self) -> None:
        if self.base_image:
            self.image = self.base_image.copy()
        else:
            self.image.fill((0, 0, 0, 0))
            pygame.draw.rect(self.image, BLUE, (6, 6, 30, 58), border_radius=8)
            pygame.draw.rect(self.image, WHITE, (12, 14, 18, 14), border_radius=4)
            pygame.draw.rect(self.image, BLACK, (0, 12, 8, 16), border_radius=3)
            pygame.draw.rect(self.image, BLACK, (34, 12, 8, 16), border_radius=3)
            pygame.draw.rect(self.image, BLACK, (0, 44, 8, 16), border_radius=3)
            pygame.draw.rect(self.image, BLACK, (34, 44, 8, 16), border_radius=3)
        if self.shield:
            pygame.draw.circle(self.image, CYAN, (21, 35), 34, 3)

    def move(self) -> None:
        keys = pygame.key.get_pressed()
        if (keys[pygame.K_LEFT] or keys[pygame.K_a]) and self.rect.left > ROAD_LEFT:
            self.rect.x -= self.speed
        if (keys[pygame.K_RIGHT] or keys[pygame.K_d]) and self.rect.right < ROAD_RIGHT:
            self.rect.x += self.speed
        if (keys[pygame.K_UP] or keys[pygame.K_w]) and self.rect.top > 80:
            self.rect.y -= self.speed
        if (keys[pygame.K_DOWN] or keys[pygame.K_s]) and self.rect.bottom < SCREEN_HEIGHT - 20:
            self.rect.y += self.speed

    def set_shield(self, value: bool) -> None:
        self.shield = value
        self.draw_car()


class TrafficCar(pygame.sprite.Sprite):

    def __init__(self, speed: float, forbidden_rect: pygame.Rect):
        super().__init__()
        self.image = load_asset_image(ENEMY_IMAGE, (44, 70))
        if self.image is None:
            self.image = pygame.Surface((44, 70), pygame.SRCALPHA)
            color = random.choice([RED, ORANGE, PURPLE, (30, 180, 180)])
            pygame.draw.rect(self.image, color, (6, 6, 32, 58), border_radius=8)
            pygame.draw.rect(self.image, WHITE, (12, 44, 20, 12), border_radius=4)
            pygame.draw.rect(self.image, BLACK, (0, 12, 8, 16), border_radius=3)
            pygame.draw.rect(self.image, BLACK, (36, 12, 8, 16), border_radius=3)
            pygame.draw.rect(self.image, BLACK, (0, 44, 8, 16), border_radius=3)
            pygame.draw.rect(self.image, BLACK, (36, 44, 8, 16), border_radius=3)
        self.rect = self.image.get_rect()
        self.speed = speed
        self.safe_spawn(forbidden_rect)

    def safe_spawn(self, forbidden_rect: pygame.Rect) -> None:
        for _ in range(20):
            lane = random.randint(0, LANES - 1)
            x = ROAD_LEFT + lane * LANE_W + LANE_W // 2
            y = random.randint(-400, -80)
            self.rect.center = (x, y)
            if not self.rect.colliderect(forbidden_rect.inflate(80, 250)):
                return

    def update(self, road_speed: float) -> None:
        self.rect.y += int(self.speed + road_speed)
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()


class Coin(pygame.sprite.Sprite):

    def __init__(self, forbidden_rect: pygame.Rect):
        super().__init__()
        self.weight = random.choice([1, 2, 3])
        self.create_image()
        self.rect = self.image.get_rect()
        self.spawn(forbidden_rect)

    def create_image(self) -> None:
        radius = {1: 10, 2: 14, 3: 18}[self.weight]
        color = {1: YELLOW, 2: ORANGE, 3: GREEN}[self.weight]
        self.image = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, color, (radius, radius), radius)
        pygame.draw.circle(self.image, BLACK, (radius, radius), radius, 2)
        font = pygame.font.SysFont("Arial", 16, bold=True)
        text = font.render(str(self.weight), True, BLACK)
        self.image.blit(text, text.get_rect(center=(radius, radius)))

    def spawn(self, forbidden_rect: pygame.Rect) -> None:
        lane = random.randint(0, LANES - 1)
        self.rect.center = (ROAD_LEFT + lane * LANE_W + LANE_W // 2, random.randint(-600, -50))
        if self.rect.colliderect(forbidden_rect.inflate(80, 250)):
            self.rect.y -= 300

    def update(self, road_speed: float) -> None:
        self.rect.y += int(road_speed)
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()


class Obstacle(pygame.sprite.Sprite):

    def __init__(self, kind: str, forbidden_rect: pygame.Rect, moving: bool = False):
        super().__init__()
        self.kind = kind
        self.moving = moving
        self.move_dir = random.choice([-1, 1])
        self.image = pygame.Surface((70, 38), pygame.SRCALPHA)
        self.make_image()
        self.rect = self.image.get_rect()
        self.spawn(forbidden_rect)

    def make_image(self) -> None:
        self.image.fill((0, 0, 0, 0))
        if self.kind == "barrier":
            pygame.draw.rect(self.image, RED, (2, 8, 66, 22), border_radius=4)
            pygame.draw.line(self.image, WHITE, (8, 28), (28, 8), 5)
            pygame.draw.line(self.image, WHITE, (34, 28), (56, 8), 5)
        elif self.kind == "oil":
            pygame.draw.ellipse(self.image, BLACK, (5, 8, 60, 24))
            pygame.draw.ellipse(self.image, DARK_GRAY, (18, 13, 28, 10))
        elif self.kind == "pothole":
            pygame.draw.ellipse(self.image, BROWN, (7, 8, 58, 24))
            pygame.draw.ellipse(self.image, BLACK, (18, 12, 34, 15))
        elif self.kind == "bump":
            pygame.draw.rect(self.image, YELLOW, (2, 12, 66, 14), border_radius=8)
            pygame.draw.line(self.image, BLACK, (12, 12), (4, 26), 3)
            pygame.draw.line(self.image, BLACK, (34, 12), (26, 26), 3)
            pygame.draw.line(self.image, BLACK, (56, 12), (48, 26), 3)
        elif self.kind == "nitro_strip":
            pygame.draw.rect(self.image, CYAN, (3, 7, 64, 24), border_radius=6)
            pygame.draw.polygon(self.image, WHITE, [(20, 10), (45, 19), (20, 28)])

    def spawn(self, forbidden_rect: pygame.Rect) -> None:
        for _ in range(20):
            lane = random.randint(0, LANES - 1)
            self.rect.center = (ROAD_LEFT + lane * LANE_W + LANE_W // 2, random.randint(-700, -80))
            if not self.rect.colliderect(forbidden_rect.inflate(90, 250)):
                return

    def update(self, road_speed: float) -> None:
        self.rect.y += int(road_speed)
        if self.moving:
            self.rect.x += self.move_dir * 2
            if self.rect.left < ROAD_LEFT or self.rect.right > ROAD_RIGHT:
                self.move_dir *= -1
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()


class PowerUp(pygame.sprite.Sprite):

    def __init__(self, kind: str, forbidden_rect: pygame.Rect):
        super().__init__()
        self.kind = kind
        self.lifetime = 420 
        self.image = pygame.Surface((42, 42), pygame.SRCALPHA)
        self.make_image()
        self.rect = self.image.get_rect()
        self.spawn(forbidden_rect)

    def make_image(self) -> None:
        self.image.fill((0, 0, 0, 0))
        color = {"Nitro": CYAN, "Shield": PURPLE, "Repair": GREEN}[self.kind]
        pygame.draw.circle(self.image, color, (21, 21), 20)
        pygame.draw.circle(self.image, BLACK, (21, 21), 20, 2)
        letter = {"Nitro": "N", "Shield": "S", "Repair": "R"}[self.kind]
        font = pygame.font.SysFont("Arial", 24, bold=True)
        text = font.render(letter, True, WHITE)
        self.image.blit(text, text.get_rect(center=(21, 21)))

    def spawn(self, forbidden_rect: pygame.Rect) -> None:
        lane = random.randint(0, LANES - 1)
        self.rect.center = (ROAD_LEFT + lane * LANE_W + LANE_W // 2, random.randint(-800, -100))
        if self.rect.colliderect(forbidden_rect.inflate(100, 250)):
            self.rect.y -= 300

    def update(self, road_speed: float) -> None:
        self.rect.y += int(road_speed)
        self.lifetime -= 1
        if self.rect.top > SCREEN_HEIGHT or self.lifetime <= 0:
            self.kill()


class RacerGame:

    def __init__(self, screen: pygame.Surface, settings: dict, username: str):
        self.screen = screen
        self.settings = settings
        self.username = username or "Player"
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 22)
        self.big_font = pygame.font.SysFont("Arial", 48, bold=True)
        self.player = Player()

        difficulty = settings.get("difficulty", "normal")
        diff = DIFFICULTY.get(difficulty, DIFFICULTY["normal"])
        self.base_speed = diff["speed"]
        self.traffic_delay = int(105 * diff["traffic"])
        self.obstacle_delay = int(130 * diff["obstacles"])

        self.traffic = pygame.sprite.Group()
        self.coins = pygame.sprite.Group()
        self.obstacles = pygame.sprite.Group()
        self.powerups = pygame.sprite.Group()

        self.score = 0
        self.coins_count = 0
        self.distance = 0
        self.frame = 0
        self.road_offset = 0
        self.active_power: Optional[str] = None
        self.power_timer = 0
        self.finish = False
        self.floating_texts: List[FloatingText] = []
        self.slow_timer = 0

    def current_speed(self) -> float:
        speed = self.base_speed + self.distance / 800
        if self.active_power == "Nitro":
            speed += 3.5
        if self.slow_timer > 0:
            speed *= 0.55
        return speed

    def spawn_objects(self) -> None:
        self.frame += 1
        scaling = max(0.55, 1 - self.distance / 6000)

        if self.frame % 65 == 0:
            self.coins.add(Coin(self.player.rect))

        if self.frame % max(28, int(self.traffic_delay * scaling)) == 0:
            self.traffic.add(TrafficCar(random.uniform(1.0, 2.5), self.player.rect))

        if self.frame % max(35, int(self.obstacle_delay * scaling)) == 0:
            kind = random.choice(["barrier", "oil", "pothole", "bump", "nitro_strip"])
            moving = random.random() < 0.25 and kind == "barrier"
            self.obstacles.add(Obstacle(kind, self.player.rect, moving))

        if self.frame % 480 == 0:
            self.powerups.add(PowerUp(random.choice(["Nitro", "Shield", "Repair"]), self.player.rect))

    def draw_road(self) -> None:
        self.screen.fill(GREEN)
        pygame.draw.rect(self.screen, GRAY, (ROAD_LEFT, 0, ROAD_WIDTH, SCREEN_HEIGHT))
        pygame.draw.rect(self.screen, DARK_GRAY, (ROAD_LEFT - 8, 0, 8, SCREEN_HEIGHT))
        pygame.draw.rect(self.screen, DARK_GRAY, (ROAD_RIGHT, 0, 8, SCREEN_HEIGHT))

        self.road_offset = (self.road_offset + int(self.current_speed())) % 60
        for lane in range(1, LANES):
            x = ROAD_LEFT + lane * LANE_W
            for y in range(-60 + self.road_offset, SCREEN_HEIGHT, 60):
                pygame.draw.rect(self.screen, WHITE, (x - 3, y, 6, 32))

        finish_y = SCREEN_HEIGHT - int(FINISH_DISTANCE - self.distance)
        if 0 < finish_y < SCREEN_HEIGHT:
            pygame.draw.rect(self.screen, WHITE, (ROAD_LEFT, finish_y, ROAD_WIDTH, 10))
            draw_text(self.screen, "FINISH", self.font, BLACK, SCREEN_WIDTH // 2, finish_y - 20, center=True)

    def draw_hud(self) -> None:
        remaining = max(0, FINISH_DISTANCE - int(self.distance))
        pygame.draw.rect(self.screen, (245, 245, 245), (0, 0, SCREEN_WIDTH, 70))
        draw_text(self.screen, f"Name: {self.username}", self.font, BLACK, 10, 8)
        draw_text(self.screen, f"Score: {int(self.score)}", self.font, BLACK, 10, 35)
        draw_text(self.screen, f"Coins: {self.coins_count}", self.font, BLACK, 155, 35)
        draw_text(self.screen, f"Distance: {int(self.distance)} m", self.font, BLACK, 285, 8)
        draw_text(self.screen, f"Left: {remaining} m", self.font, BLACK, 285, 35)

        if self.active_power:
            seconds = max(0, self.power_timer // FPS)
            label = f"Power: {self.active_power}"
            if self.active_power == "Nitro":
                label += f" {seconds}s"
            draw_text(self.screen, label, self.font, PURPLE, 155, 8)

    def apply_powerup(self, kind: str) -> None:
        if self.active_power:
            return
        self.active_power = kind
        if kind == "Nitro":
            self.power_timer = random.randint(3, 5) * FPS
            self.score += 50
        elif kind == "Shield":
            self.power_timer = 999999
            self.player.set_shield(True)
            self.score += 25
        elif kind == "Repair":
            self.score += 75
            nearest = None
            for obstacle in self.obstacles:
                if nearest is None or obstacle.rect.y > nearest.rect.y:
                    nearest = obstacle
            if nearest:
                nearest.kill()
            self.active_power = None
            self.power_timer = 0
        self.floating_texts.append(FloatingText(kind, self.player.rect.centerx, self.player.rect.top))

    def update_powerup_timer(self) -> None:
        if self.active_power:
            self.power_timer -= 1
            if self.active_power == "Nitro" and self.power_timer <= 0:
                self.active_power = None
                self.power_timer = 0
        if self.slow_timer > 0:
            self.slow_timer -= 1

    def handle_collisions(self) -> bool:
        for coin in pygame.sprite.spritecollide(self.player, self.coins, True):
            self.coins_count += coin.weight
            self.score += coin.weight * 20
            self.floating_texts.append(FloatingText(f"+{coin.weight}", coin.rect.centerx, coin.rect.y))

        for powerup in pygame.sprite.spritecollide(self.player, self.powerups, True):
            self.apply_powerup(powerup.kind)

        traffic_hit = pygame.sprite.spritecollideany(self.player, self.traffic)
        if traffic_hit:
            if self.active_power == "Shield":
                traffic_hit.kill()
                self.active_power = None
                self.power_timer = 0
                self.player.set_shield(False)
            else:
                return False

        obstacle_hit = pygame.sprite.spritecollideany(self.player, self.obstacles)
        if obstacle_hit:
            if obstacle_hit.kind == "nitro_strip":
                obstacle_hit.kill()
                if not self.active_power:
                    self.active_power = "Nitro"
                    self.power_timer = 3 * FPS
            elif obstacle_hit.kind in ("oil", "pothole", "bump"):
                obstacle_hit.kill()
                self.slow_timer = 120
                self.score = max(0, self.score - 25)
            elif obstacle_hit.kind == "barrier":
                if self.active_power == "Shield":
                    obstacle_hit.kill()
                    self.active_power = None
                    self.power_timer = 0
                    self.player.set_shield(False)
                else:
                    return False

        return True

    def update_floating_texts(self) -> None:
        for text in self.floating_texts[:]:
            text.update()
            if text.timer <= 0:
                self.floating_texts.remove(text)

    def draw_floating_texts(self) -> None:
        for text in self.floating_texts:
            draw_text(self.screen, text.text, self.font, YELLOW, text.x, text.y, center=True)

    def run(self) -> str:
        running = True
        while running:
            self.clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "quit"
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    return "menu"

            road_speed = self.current_speed()
            self.distance += road_speed * 0.12
            self.score += road_speed * 0.05
            self.spawn_objects()
            self.update_powerup_timer()

            self.player.move()
            self.traffic.update(road_speed)
            self.obstacles.update(road_speed)
            self.coins.update(road_speed)
            self.powerups.update(road_speed)
            self.update_floating_texts()

            if not self.handle_collisions() or self.distance >= FINISH_DISTANCE:
                save_score(self.username, int(self.score), int(self.distance), self.coins_count)
                return self.game_over_screen()

            self.draw_road()
            self.traffic.draw(self.screen)
            self.obstacles.draw(self.screen)
            self.coins.draw(self.screen)
            self.powerups.draw(self.screen)
            self.screen.blit(self.player.image, self.player.rect)
            self.draw_hud()
            self.draw_floating_texts()
            pygame.display.flip()

        return "menu"

    def game_over_screen(self) -> str:
        retry_button = Button(140, 430, 220, 48, "Retry")
        menu_button = Button(140, 495, 220, 48, "Main Menu")

        while True:
            self.screen.fill((235, 235, 235))
            title = "FINISHED!" if self.distance >= FINISH_DISTANCE else "GAME OVER"
            draw_text(self.screen, title, self.big_font, RED, SCREEN_WIDTH // 2, 150, center=True)
            draw_text(self.screen, f"Score: {int(self.score)}", self.font, BLACK, SCREEN_WIDTH // 2, 230, center=True)
            draw_text(self.screen, f"Distance: {int(self.distance)} m", self.font, BLACK, SCREEN_WIDTH // 2, 265, center=True)
            draw_text(self.screen, f"Coins: {self.coins_count}", self.font, BLACK, SCREEN_WIDTH // 2, 300, center=True)
            draw_text(self.screen, "Saved to leaderboard.json", self.font, BLACK, SCREEN_WIDTH // 2, 345, center=True)
            retry_button.draw(self.screen, self.font)
            menu_button.draw(self.screen, self.font)
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "quit"
                if retry_button.clicked(event):
                    return "play"
                if menu_button.clicked(event):
                    return "menu"
