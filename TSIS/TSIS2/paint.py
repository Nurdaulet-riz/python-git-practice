import pygame
import sys
import math
from collections import deque
from datetime import datetime

pygame.init()

PANEL_W = 180
CANVAS_W = 740
HEIGHT = 600
WIDTH = CANVAS_W + PANEL_W
FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
DARK = (70, 70, 70)
PANEL_BG = (230, 230, 230)
LIGHT_BLUE = (190, 220, 255)

PALETTE = [
    BLACK, WHITE, (200, 0, 0),
    (0, 180, 0), (0, 0, 200), (255, 165, 0),
    (128, 0, 128), (0, 180, 180), (255, 20, 147),
    (139, 69, 19), (128, 128, 128), (255, 255, 0),
]

TOOLS = [
    "Pencil", "Line", "Rect", "Circle", "Square",
    "RightTri", "EqTri", "Rhombus", "Fill", "Text", "Eraser"
]

BRUSH_SIZES = [2, 5, 10]

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("TSIS 2 Paint")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 16)
text_font = pygame.font.SysFont("Arial", 28)

TOOL_RECTS = {
    tool: pygame.Rect(CANVAS_W + 10, 30 + i * 34, 160, 28)
    for i, tool in enumerate(TOOLS)
}

COLOR_RECTS = [
    pygame.Rect(CANVAS_W + 10 + (i % 4) * 40, 420 + (i // 4) * 40, 34, 34)
    for i in range(len(PALETTE))
]

SIZE_RECTS = [
    pygame.Rect(CANVAS_W + 10 + i * 52, 545, 45, 30)
    for i in range(len(BRUSH_SIZES))
]


def clamp_to_canvas(pos):
    x, y = pos
    x = max(0, min(CANVAS_W - 1, x))
    y = max(0, min(HEIGHT - 1, y))
    return x, y


def save_canvas(canvas):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"paint_{timestamp}.png"
    pygame.image.save(canvas, filename)
    print(f"Canvas saved as {filename}")
    return filename


def flood_fill(surface, start_pos, fill_color):
    x, y = start_pos
    target_color = surface.get_at((x, y))
    fill_color = pygame.Color(*fill_color)

    if target_color == fill_color:
        return

    queue = deque([(x, y)])
    visited = set()

    while queue:
        px, py = queue.popleft()

        if (px, py) in visited:
            continue
        if px < 0 or px >= CANVAS_W or py < 0 or py >= HEIGHT:
            continue
        if surface.get_at((px, py)) != target_color:
            continue

        surface.set_at((px, py), fill_color)
        visited.add((px, py))

        queue.append((px + 1, py))
        queue.append((px - 1, py))
        queue.append((px, py + 1))
        queue.append((px, py - 1))


def make_rect(start, end):
    x1, y1 = start
    x2, y2 = end
    return pygame.Rect(min(x1, x2), min(y1, y2), abs(x2 - x1), abs(y2 - y1))


def draw_shape(surface, tool, start, end, color, size):
    x1, y1 = start
    x2, y2 = clamp_to_canvas(end)

    if tool == "Line":
        pygame.draw.line(surface, color, (x1, y1), (x2, y2), size)

    elif tool == "Rect":
        pygame.draw.rect(surface, color, make_rect(start, (x2, y2)), size)

    elif tool == "Circle":
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
        radius = max(1, int(math.hypot(x2 - x1, y2 - y1) // 2))
        pygame.draw.circle(surface, color, (cx, cy), radius, size)

    elif tool == "Square":
        side = max(abs(x2 - x1), abs(y2 - y1))
        sx = x1 + side if x2 >= x1 else x1 - side
        sy = y1 + side if y2 >= y1 else y1 - side
        pygame.draw.rect(surface, color, make_rect(start, clamp_to_canvas((sx, sy))), size)

    elif tool == "RightTri":
        points = [(x1, y1), (x1, y2), (x2, y2)]
        pygame.draw.polygon(surface, color, points, size)

    elif tool == "EqTri":
        side = abs(x2 - x1)
        height = int(side * math.sqrt(3) / 2)
        direction = 1 if y2 >= y1 else -1
        left = min(x1, x2)
        right = max(x1, x2)
        top = y1
        points = [(left, top), (right, top), ((left + right) // 2, top + direction * height)]
        pygame.draw.polygon(surface, color, points, size)

    elif tool == "Rhombus":
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
        points = [(cx, y1), (x2, cy), (cx, y2), (x1, cy)]
        pygame.draw.polygon(surface, color, points, size)


def draw_panel(tool, color_idx, size_idx, saved_message):
    pygame.draw.rect(screen, PANEL_BG, (CANVAS_W, 0, PANEL_W, HEIGHT))
    pygame.draw.line(screen, DARK, (CANVAS_W, 0), (CANVAS_W, HEIGHT), 2)

    screen.blit(font.render("Tools:", True, BLACK), (CANVAS_W + 10, 8))
    for t, r in TOOL_RECTS.items():
        bg = DARK if t == tool else GRAY
        fg = WHITE if t == tool else BLACK
        pygame.draw.rect(screen, bg, r, border_radius=5)
        screen.blit(font.render(t, True, fg), (r.x + 8, r.y + 6))

    screen.blit(font.render("Colors:", True, BLACK), (CANVAS_W + 10, 398))
    for i, r in enumerate(COLOR_RECTS):
        pygame.draw.rect(screen, PALETTE[i], r)
        border = 3 if i == color_idx else 1
        pygame.draw.rect(screen, BLACK, r, border)

    screen.blit(font.render("Size 1/2/3:", True, BLACK), (CANVAS_W + 10, 522))
    for i, r in enumerate(SIZE_RECTS):
        bg = LIGHT_BLUE if i == size_idx else GRAY
        pygame.draw.rect(screen, bg, r, border_radius=5)
        label = font.render(str(BRUSH_SIZES[i]), True, BLACK)
        screen.blit(label, (r.centerx - label.get_width() // 2, r.centery - label.get_height() // 2))

    hint = font.render("Ctrl+S save", True, BLACK)
    screen.blit(hint, (CANVAS_W + 10, 580))

    if saved_message:
        msg = font.render(saved_message, True, (0, 120, 0))
        screen.blit(msg, (10, HEIGHT - 25))


def main():
    canvas = pygame.Surface((CANVAS_W, HEIGHT))
    canvas.fill(WHITE)

    tool = "Pencil"
    color_idx = 0
    size_idx = 1  
    drawing = False
    start = None
    last_pos = None
    text_active = False
    text_pos = None
    current_text = ""
    saved_message = ""
    saved_message_timer = 0

    running = True
    while running:
        clock.tick(FPS)
        size = BRUSH_SIZES[size_idx]
        current_color = PALETTE[color_idx]

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                keys = pygame.key.get_pressed()

                if event.key == pygame.K_s and (keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]):
                    filename = save_canvas(canvas)
                    saved_message = f"Saved: {filename}"
                    saved_message_timer = FPS * 2

                elif event.key == pygame.K_1:
                    size_idx = 0
                elif event.key == pygame.K_2:
                    size_idx = 1
                elif event.key == pygame.K_3:
                    size_idx = 2

                elif text_active:
                    if event.key == pygame.K_RETURN:
                        text_surface = text_font.render(current_text, True, current_color)
                        canvas.blit(text_surface, text_pos)
                        text_active = False
                        current_text = ""
                        text_pos = None
                    elif event.key == pygame.K_ESCAPE:
                        text_active = False
                        current_text = ""
                        text_pos = None
                    elif event.key == pygame.K_BACKSPACE:
                        current_text = current_text[:-1]
                    else:
                        current_text += event.unicode

            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos

                if mx < CANVAS_W:
                    if tool == "Fill":
                        flood_fill(canvas, (mx, my), current_color)
                    elif tool == "Text":
                        text_active = True
                        text_pos = (mx, my)
                        current_text = ""
                    else:
                        drawing = True
                        start = (mx, my)
                        last_pos = (mx, my)

                        if tool == "Pencil":
                            pygame.draw.circle(canvas, current_color, (mx, my), size // 2)
                        elif tool == "Eraser":
                            pygame.draw.circle(canvas, WHITE, (mx, my), size * 2)
                else:
                    for t, r in TOOL_RECTS.items():
                        if r.collidepoint(mx, my):
                            tool = t
                            text_active = False

                    for i, r in enumerate(COLOR_RECTS):
                        if r.collidepoint(mx, my):
                            color_idx = i

                    for i, r in enumerate(SIZE_RECTS):
                        if r.collidepoint(mx, my):
                            size_idx = i

            if event.type == pygame.MOUSEMOTION and drawing:
                mx, my = event.pos
                if mx < CANVAS_W and last_pos:
                    if tool == "Pencil":
                        pygame.draw.line(canvas, current_color, last_pos, (mx, my), size)
                        last_pos = (mx, my)
                    elif tool == "Eraser":
                        pygame.draw.line(canvas, WHITE, last_pos, (mx, my), size * 3)
                        last_pos = (mx, my)

            if event.type == pygame.MOUSEBUTTONUP and drawing:
                mx, my = pygame.mouse.get_pos()
                end = clamp_to_canvas((mx, my))

                if tool in ("Line", "Rect", "Circle", "Square", "RightTri", "EqTri", "Rhombus") and start:
                    draw_shape(canvas, tool, start, end, current_color, size)

                drawing = False
                start = None
                last_pos = None

        display = canvas.copy()
        if drawing and start and tool in ("Line", "Rect", "Circle", "Square", "RightTri", "EqTri", "Rhombus"):
            end = clamp_to_canvas(pygame.mouse.get_pos())
            draw_shape(display, tool, start, end, current_color, size)

        if text_active and text_pos is not None:
            preview_text = current_text + "|"
            text_surface = text_font.render(preview_text, True, current_color)
            display.blit(text_surface, text_pos)

        screen.blit(display, (0, 0))

        if saved_message_timer > 0:
            saved_message_timer -= 1
        else:
            saved_message = ""

        draw_panel(tool, color_idx, size_idx, saved_message)
        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
