import pygame
from persistence import load_leaderboard, load_settings, save_settings
from racer import RacerGame, SCREEN_HEIGHT, SCREEN_WIDTH
from ui import Button, draw_text

pygame.init()
pygame.display.set_caption("RACER")

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 24)
big_font = pygame.font.SysFont("Arial", 48, bold=True)

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (235, 235, 235)
BLUE = (40, 120, 220)
RED = (220, 40, 40)
GREEN = (30, 150, 60)
YELLOW = (255, 220, 0)

settings = load_settings()
username = "Player"


def get_username() -> str:
    name = ""
    active = True
    while active:
        clock.tick(60)
        screen.fill(GRAY)
        draw_text(screen, "Enter your name", big_font, BLACK, SCREEN_WIDTH // 2, 190, center=True)
        draw_text(screen, name + "|", font, BLUE, SCREEN_WIDTH // 2, 285, center=True)
        draw_text(screen, "Press Enter to start", font, BLACK, SCREEN_WIDTH // 2, 360, center=True)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return name.strip() or "Player"
                if event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                elif len(name) < 12 and event.unicode.isprintable():
                    name += event.unicode


def main_menu() -> str:
    buttons = {
        "play": Button(140, 230, 220, 48, "Play"),
        "leaderboard": Button(140, 295, 220, 48, "Leaderboard"),
        "settings": Button(140, 360, 220, 48, "Settings"),
        "quit": Button(140, 425, 220, 48, "Quit"),
    }

    while True:
        clock.tick(60)
        screen.fill(GRAY)
        draw_text(screen, "RACER", big_font, RED, SCREEN_WIDTH // 2, 120, center=True)
        draw_text(screen, "Advanced Driving", font, BLACK, SCREEN_WIDTH // 2, 175, center=True)
        for button in buttons.values():
            button.draw(screen, font)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            for state, button in buttons.items():
                if button.clicked(event):
                    return state


def leaderboard_screen() -> str:
    back_button = Button(140, 610, 220, 48, "Back")

    while True:
        clock.tick(60)
        screen.fill(GRAY)
        draw_text(screen, "Leaderboard Top 10", big_font, BLACK, SCREEN_WIDTH // 2, 65, center=True)
        leaderboard = load_leaderboard()

        y = 135
        draw_text(screen, "Rank   Name        Score     Distance", font, BLACK, 55, y)
        y += 38
        if not leaderboard:
            draw_text(screen, "No scores yet", font, BLACK, SCREEN_WIDTH // 2, y + 60, center=True)
        for i, entry in enumerate(leaderboard[:10], start=1):
            line = f"{i:>2}.    {entry['name']:<10} {entry['score']:<8} {entry['distance']} m"
            draw_text(screen, line, font, BLACK, 55, y)
            y += 38

        back_button.draw(screen, font)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if back_button.clicked(event):
                return "menu"


def settings_screen() -> str:
    global settings

    sound_button = Button(130, 210, 240, 45, "")
    difficulty_button = Button(130, 305, 240, 45, "")
    back_button = Button(140, 520, 220, 48, "Back")

    difficulty_options = ["easy", "normal", "hard"]

    while True:
        clock.tick(60)
        screen.fill(GRAY)
        draw_text(screen, "Settings", big_font, BLACK, SCREEN_WIDTH // 2, 80, center=True)

        sound_button.text = f"Sound: {'ON' if settings['sound'] else 'OFF'}"
        difficulty_button.text = f"Difficulty: {settings['difficulty']}"

        draw_text(screen, "Click buttons to change settings", font, BLACK, SCREEN_WIDTH // 2, 150, center=True)
        sound_button.draw(screen, font)
        difficulty_button.draw(screen, font)
        back_button.draw(screen, font)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if sound_button.clicked(event):
                settings["sound"] = not settings["sound"]
                save_settings(settings)
            if difficulty_button.clicked(event):
                idx = difficulty_options.index(settings["difficulty"])
                settings["difficulty"] = difficulty_options[(idx + 1) % len(difficulty_options)]
                save_settings(settings)
            if back_button.clicked(event):
                return "menu"


def main() -> None:
    global username
    state = "menu"

    while state != "quit":
        if state == "menu":
            state = main_menu()
        elif state == "play":
            username = get_username()
            if username == "quit":
                state = "quit"
            else:
                game = RacerGame(screen, settings, username)
                state = game.run()
        elif state == "leaderboard":
            state = leaderboard_screen()
        elif state == "settings":
            state = settings_screen()

    pygame.quit()


if __name__ == "__main__":
    main()
