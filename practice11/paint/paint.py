import pygame
import colorsys

# -------------------------
# SETTINGS
# -------------------------
WIDTH, HEIGHT = 900, 650
TOOLBAR_HEIGHT = 150

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
DARK_GRAY = (80, 80, 80)

RED = (255, 0, 0)
GREEN = (0, 180, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (160, 32, 240)
ORANGE = (255, 140, 0)

COLOR_OPTIONS = [BLACK, RED, GREEN, BLUE, YELLOW, PURPLE, ORANGE]


# -------------------------
# HELPERS
# -------------------------
def draw_text(screen, text, x, y, font, color=BLACK):
    img = font.render(text, True, color)
    screen.blit(img, (x, y))


def create_color_palette(width, height):
    palette = pygame.Surface((width, height))
    for x in range(width):
        for y in range(height):
            h = x / width
            s = 1
            v = 1 - (y / height)
            r, g, b = colorsys.hsv_to_rgb(h, s, v)
            palette.set_at((x, y), (int(r*255), int(g*255), int(b*255)))
    return palette


def clamp_to_canvas(pos):
    x, y = pos
    return max(0, min(WIDTH - 1, x)), max(TOOLBAR_HEIGHT, min(HEIGHT - 1, y))


def draw_brush(surface, color, start, end, radius):
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    steps = max(abs(dx), abs(dy))

    if steps == 0:
        pygame.draw.circle(surface, color, start, radius)
        return

    for i in range(steps + 1):
        x = int(start[0] + dx * i / steps)
        y = int(start[1] + dy * i / steps)
        pygame.draw.circle(surface, color, (x, y), radius)


# -------------------------
# SHAPES
# -------------------------
def draw_square(surface, color, start, end, width=2):
    size = min(abs(end[0]-start[0]), abs(end[1]-start[1]))
    pygame.draw.rect(surface, color,
                     pygame.Rect(start[0], start[1], size, size), width)


def draw_right_triangle(surface, color, start, end, width=2):
    x1, y1 = start
    x2, y2 = end
    pygame.draw.polygon(surface, color, [(x1, y1), (x1, y2), (x2, y2)], width)


def draw_equilateral_triangle(surface, color, start, end, width=2):
    x1, y1 = start
    x2, y2 = end

    base = x2 - x1
    height = abs(base) * 0.866

    points = [
        (x1, y2),
        (x2, y2),
        (x1 + base / 2, y2 - height)
    ]

    pygame.draw.polygon(surface, color, points, width)


def draw_rhombus(surface, color, start, end, width=2):
    x1, y1 = start
    x2, y2 = end

    mx = (x1 + x2) // 2
    my = (y1 + y2) // 2

    points = [
        (mx, y1),
        (x2, my),
        (mx, y2),
        (x1, my)
    ]

    pygame.draw.polygon(surface, color, points, width)


# -------------------------
# TOOLBAR
# -------------------------
def draw_toolbar(screen, current_tool, current_color, brush_size,
                 font, palette, palette_rect):

    pygame.draw.rect(screen, GRAY, (0, 0, WIDTH, TOOLBAR_HEIGHT))
    pygame.draw.line(screen, BLACK, (0, TOOLBAR_HEIGHT), (WIDTH, TOOLBAR_HEIGHT), 2)

    # ---------------- TOOL GRID ----------------
    tools = ["brush", "rectangle", "circle", "eraser",
             "square", "r_triangle", "eq_triangle", "rhombus", "clear"]

    tool_buttons = {}

    btn_w, btn_h = 95, 28
    cols = 5

    for i, tool in enumerate(tools):
        row = i // cols
        col = i % cols

        x = 10 + col * (btn_w + 8)
        y = 10 + row * (btn_h + 6)

        rect = pygame.Rect(x, y, btn_w, btn_h)
        tool_buttons[tool] = rect

        pygame.draw.rect(screen,
                         DARK_GRAY if current_tool == tool else WHITE,
                         rect)
        pygame.draw.rect(screen, BLACK, rect, 2)

        draw_text(screen, tool[:9], x + 5, y + 5, font,
                  WHITE if current_tool == tool else BLACK)

    # ---------------- COLOR PRESETS ----------------
    color_buttons = []
    x, y = 10, 85

    for color in COLOR_OPTIONS:
        rect = pygame.Rect(x, y, 32, 22)
        color_buttons.append((rect, color))

        pygame.draw.rect(screen, color, rect)
        pygame.draw.rect(screen, BLACK, rect, 3 if color == current_color else 1)

        x += 38

    # ---------------- HSV PALETTE ----------------
    screen.blit(palette, palette_rect.topleft)
    pygame.draw.rect(screen, BLACK, palette_rect, 2)

    # ---------------- STATUS AREA (FIXED) ----------------
    preview_rect = pygame.Rect(WIDTH - 70, 15, 45, 45)
    pygame.draw.rect(screen, current_color, preview_rect)
    pygame.draw.rect(screen, BLACK, preview_rect, 2)

    status_x = WIDTH - 220
    status_y = 95

    status_bg = pygame.Rect(status_x - 10, status_y - 5, 200, 45)
    pygame.draw.rect(screen, WHITE, status_bg)
    pygame.draw.rect(screen, BLACK, status_bg, 1)

    draw_text(screen, f"Tool: {current_tool}", status_x, status_y, font)
    draw_text(screen, f"Size: {brush_size}", status_x, status_y + 18, font)

    return tool_buttons, color_buttons