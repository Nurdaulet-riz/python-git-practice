import pygame
import random
import sys

pygame.init()

CELL = 20
COLS, ROWS = 30, 25
GAME_W = COLS * CELL
GAME_H = ROWS * CELL
HUD_H = 45
WIDTH = GAME_W
HEIGHT = GAME_H + HUD_H
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (50, 200, 50)
DARK_GREEN = (30, 130, 30)
RED = (220, 50, 50)
ORANGE = (255, 150, 0)
PURPLE = (160, 60, 220)
WALL_COL = (100, 100, 100)
GRAY = (40, 40, 40)
YELLOW = (255, 220, 0)

FOODS_PER_LEVEL = 3
BASE_INTERVAL = 120
FOOD_LIFETIME = 5000

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake Practice 11")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 22, bold=True)
small_font = pygame.font.SysFont("Arial", 16, bold=True)

class Food:
    
    def __init__(self, snake):
        self.respawn(snake)

    def respawn(self, snake):
        while True:
            self.pos = (random.randint(1, COLS - 2), random.randint(1, ROWS - 2))
            if self.pos not in snake:
                break

        self.weight = random.choice([1, 2, 3])
        self.created_time = pygame.time.get_ticks()

    def is_expired(self):
        return pygame.time.get_ticks() - self.created_time > FOOD_LIFETIME

    def time_left(self):
        left = FOOD_LIFETIME - (pygame.time.get_ticks() - self.created_time)
        return max(0, left // 1000 + 1)

    def draw(self):
        x, y = self.pos
        cx = x * CELL + CELL // 2
        cy = y * CELL + CELL // 2

        color = RED if self.weight == 1 else ORANGE if self.weight == 2 else PURPLE
        pygame.draw.circle(screen, color, (cx, cy), CELL // 2 - 2)

        text = small_font.render(str(self.weight), True, WHITE)
        screen.blit(text, (cx - text.get_width() // 2, cy - text.get_height() // 2))


def run_game():
    snake = [(COLS // 2, ROWS // 2),
             (COLS // 2 - 1, ROWS // 2),
             (COLS // 2 - 2, ROWS // 2)]
    direction = (1, 0)
    next_dir = (1, 0)
    food = Food(snake)

    score = 0
    level = 1
    foods_eaten = 0
    grow_cells = 0
    move_interval = BASE_INTERVAL
    move_timer = 0
    game_over = False

    while True:
        dt = clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:
                if game_over:
                    if event.key == pygame.K_r:
                        return True
                else:
                    if event.key == pygame.K_UP and direction != (0, 1):
                        next_dir = (0, -1)
                    elif event.key == pygame.K_DOWN and direction != (0, -1):
                        next_dir = (0, 1)
                    elif event.key == pygame.K_LEFT and direction != (1, 0):
                        next_dir = (-1, 0)
                    elif event.key == pygame.K_RIGHT and direction != (-1, 0):
                        next_dir = (1, 0)

        if not game_over:
            if food.is_expired():
                food.respawn(snake)

            move_timer += dt
            if move_timer >= move_interval:
                move_timer = 0
                direction = next_dir
                head = (snake[0][0] + direction[0], snake[0][1] + direction[1])

                if head[0] <= 0 or head[0] >= COLS - 1 or head[1] <= 0 or head[1] >= ROWS - 1:
                    game_over = True
                elif head in snake:
                    game_over = True
                else:
                    snake.insert(0, head)

                    if head == food.pos:
                        score += food.weight * 10
                        foods_eaten += 1
                        grow_cells += food.weight
                        food.respawn(snake)

                        if foods_eaten % FOODS_PER_LEVEL == 0:
                            level += 1
                            move_interval = max(40, BASE_INTERVAL - (level - 1) * 15)

                    if grow_cells > 0:
                        grow_cells -= 1
                    else:
                        snake.pop()

        screen.fill(GRAY)
        pygame.draw.rect(screen, BLACK, (0, 0, GAME_W, GAME_H))

        for x in range(COLS):
            pygame.draw.rect(screen, WALL_COL, (x * CELL, 0, CELL, CELL))
            pygame.draw.rect(screen, WALL_COL, (x * CELL, (ROWS - 1) * CELL, CELL, CELL))
        for y in range(1, ROWS - 1):
            pygame.draw.rect(screen, WALL_COL, (0, y * CELL, CELL, CELL))
            pygame.draw.rect(screen, WALL_COL, ((COLS - 1) * CELL, y * CELL, CELL, CELL))

        for i, (x, y) in enumerate(snake):
            color = GREEN if i == 0 else DARK_GREEN
            pygame.draw.rect(screen, color,
                             (x * CELL + 1, y * CELL + 1, CELL - 2, CELL - 2),
                             border_radius=4)

        food.draw()

        hud_y = GAME_H + 10
        screen.blit(font.render(f"Score: {score}", True, WHITE), (10, hud_y))
        lvl = font.render(f"Level: {level}", True, YELLOW)
        timer = font.render(f"Food: {food.time_left()}s", True, WHITE)
        screen.blit(lvl, (GAME_W // 2 - lvl.get_width() // 2, hud_y))
        screen.blit(timer, (GAME_W - timer.get_width() - 10, hud_y))

        if game_over:
            overlay = pygame.Surface((GAME_W, GAME_H), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 160))
            screen.blit(overlay, (0, 0))
            t1 = font.render("GAME OVER", True, RED)
            t2 = font.render("Press R to restart", True, WHITE)
            screen.blit(t1, (GAME_W // 2 - t1.get_width() // 2, GAME_H // 2 - 30))
            screen.blit(t2, (GAME_W // 2 - t2.get_width() // 2, GAME_H // 2 + 15))

        pygame.display.flip()


def main():
    while run_game():
        pass
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
