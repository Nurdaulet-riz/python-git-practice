import pygame
import sys
import math

pygame.init()

PANEL_W = 180
CANVAS_W = 740
HEIGHT = 600
WIDTH = CANVAS_W + PANEL_W
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
DARK = (70, 70, 70)
PANEL_BG = (230, 230, 230)
PALETTE = [
    BLACK, WHITE, (200, 0, 0),
    (0, 180, 0), (0, 0, 200), (255, 165, 0),
    (128, 0, 128), (0, 180, 180), (255, 20, 147),
    (139, 69, 19), (128, 128, 128), (255, 255, 0),
]

TOOLS = [
    "Pencil", "Rect", "Circle", "Eraser",
    "Square", "Right triangle", "Eq triangle", "Rhombus"
]

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Paint Practice 11")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 15)

TOOL_RECTS = {
    tool: pygame.Rect(CANVAS_W + 10, 30 + i * 34, 160, 28)
    for i, tool in enumerate(TOOLS)
}

COLOR_RECTS = [
    pygame.Rect(CANVAS_W + 10 + (i % 3) * 50, 330 + (i // 3) * 46, 40, 40)
    for i in range(len(PALETTE))
]

MINUS_RECT = pygame.Rect(CANVAS_W + 65, 540, 28, 28)
PLUS_RECT = pygame.Rect(CANVAS_W + 100, 540, 28, 28)


def draw_panel(tool, color_idx, size):
    pygame.draw.rect(screen, PANEL_BG, (CANVAS_W, 0, PANEL_W, HEIGHT))
    pygame.draw.line(screen, DARK, (CANVAS_W, 0), (CANVAS_W, HEIGHT), 2)

    screen.blit(font.render("Tools:", True, BLACK), (CANVAS_W + 10, 8))
    for t, r in TOOL_RECTS.items():
        bg = DARK if t == tool else GRAY
        fg = WHITE if t == tool else BLACK
        pygame.draw.rect(screen, bg, r, border_radius=5)
        screen.blit(font.render(t, True, fg), (r.x + 8, r.y + 6))

    screen.blit(font.render("Colors:", True, BLACK), (CANVAS_W + 10, 308))
    for i, r in enumerate(COLOR_RECTS):
        pygame.draw.rect(screen, PALETTE[i], r)
        border = 3 if i == color_idx else 1
        pygame.draw.rect(screen, BLACK, r, border)

    screen.blit(font.render(f"Size: {size}", True, BLACK), (CANVAS_W + 10, 515))
    for btn, label in [(MINUS_RECT, "-"), (PLUS_RECT, "+")]:
        pygame.draw.rect(screen, GRAY, btn, border_radius=4)
        screen.blit(font.render(label, True, BLACK), (btn.x + 9, btn.y + 5))


def clamp_to_canvas(x, y):
    return min(max(x, 0), CANVAS_W - 1), min(max(y, 0), HEIGHT - 1)


def get_square_rect(start, end):
    x1, y1 = start
    x2, y2 = end
    side = min(abs(x2 - x1), abs(y2 - y1))
    x = x1 if x2 >= x1 else x1 - side
    y = y1 if y2 >= y1 else y1 - side
    return pygame.Rect(x, y, side, side)


def get_equilateral_points(start, end):
    x1, y1 = start
    x2, y2 = end
    side = abs(x2 - x1)
    height = int(side * math.sqrt(3) / 2)

    sign_x = 1 if x2 >= x1 else -1
    sign_y = 1 if y2 >= y1 else -1

    p1 = (x1, y1)
    p2 = (x1 + sign_x * side, y1)
    p3 = (x1 + sign_x * side // 2, y1 + sign_y * height)
    return [p1, p2, p3]

def get_rhombus_points(start, end):
    x1, y1 = start
    x2, y2 = end
    left, right = min(x1, x2), max(x1, x2)
    top, bottom = min(y1, y2), max(y1, y2)
    mid_x = (left + right) // 2
    mid_y = (top + bottom) // 2

    return [(mid_x, top), (right, mid_y), (mid_x, bottom), (left, mid_y)]

def draw_shape_preview(surface, tool, start, end, color, size):
    x1, y1 = start
    x2, y2 = clamp_to_canvas(*end)

    if tool == "Rect":
        rect = pygame.Rect(min(x1, x2), min(y1, y2), abs(x2 - x1), abs(y2 - y1))
        pygame.draw.rect(surface, color, rect, size)

    elif tool == "Circle":
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
        radius = max(1, int(math.hypot(x2 - x1, y2 - y1) // 2))
        pygame.draw.circle(surface, color, (cx, cy), radius, size)

    elif tool == "Square":
        rect = get_square_rect(start, (x2, y2))
        pygame.draw.rect(surface, color, rect, size)

    elif tool == "Right triangle":
        points = [(x1, y1), (x2, y1), (x1, y2)]
        pygame.draw.polygon(surface, color, points, size)

    elif tool == "Eq triangle":
        points = get_equilateral_points(start, (x2, y2))
        pygame.draw.polygon(surface, color, points, size)

    elif tool == "Rhombus":
        points = get_rhombus_points(start, (x2, y2))
        pygame.draw.polygon(surface, color, points, size)


def main():
    canvas = pygame.Surface((CANVAS_W, HEIGHT))
    canvas.fill(WHITE)

    tool = "Pencil"
    color_idx = 0
    size = 5
    drawing = False
    start = None

    while True:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos

                if mx < CANVAS_W:
                    drawing = True
                    start = (mx, my)
                    last_pos = (mx,my)
                    if tool == "Pencil":
                        pygame.draw.circle(canvas, PALETTE[color_idx], (mx, my), size)
                    elif tool == "Eraser":
                        pygame.draw.circle(canvas, WHITE, (mx, my), size * 3)

                else:
                    for t, r in TOOL_RECTS.items():
                        if r.collidepoint(mx, my):
                            tool = t

                    for i, r in enumerate(COLOR_RECTS):
                        if r.collidepoint(mx, my):
                            color_idx = i

                    if PLUS_RECT.collidepoint(mx, my):
                        size = min(50, size + 2)
                    if MINUS_RECT.collidepoint(mx, my):
                        size = max(1, size - 2)

            if event.type == pygame.MOUSEMOTION and drawing:
                mx, my = event.pos
                if mx < CANVAS_W:
                    if tool == "Pencil":
                        pygame.draw.line(canvas, PALETTE[color_idx], last_pos, (mx, my), size * 2)
                        last_pos = (mx, my)                  
                    elif tool == "Eraser":
                        pygame.draw.line(canvas, WHITE, last_pos, (mx, my), size * 3)
                        last_pos = (mx, my)
            if event.type == pygame.MOUSEBUTTONUP and drawing:
                mx, my = pygame.mouse.get_pos()

                if tool in ("Rect", "Circle", "Square", "Right triangle", "Eq triangle", "Rhombus") and start:
                    draw_shape_preview(canvas, tool, start, (mx, my), PALETTE[color_idx], size)

                drawing = False
                start = None
                
        display = canvas.copy()

        if drawing and start and tool in ("Rect", "Circle", "Square", "Right triangle", "Eq triangle", "Rhombus"):
            mx, my = pygame.mouse.get_pos()
            draw_shape_preview(display, tool, start, (mx, my), PALETTE[color_idx], size)

        screen.blit(display, (0, 0))
        draw_panel(tool, color_idx, size)
        pygame.display.flip()


if __name__ == "__main__":
    main()
