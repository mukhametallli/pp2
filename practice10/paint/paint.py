import pygame
import colorsys

# -------------------------
# SETTINGS
# -------------------------
WIDTH, HEIGHT = 900, 650
TOOLBAR_HEIGHT = 160   # FIXED SIZE

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
# TOOLBAR
# -------------------------
def draw_toolbar(screen, current_tool, current_color, brush_size,
                 font, palette, palette_rect):

    pygame.draw.rect(screen, GRAY, (0, 0, WIDTH, TOOLBAR_HEIGHT))
    pygame.draw.line(screen, BLACK, (0, TOOLBAR_HEIGHT), (WIDTH, TOOLBAR_HEIGHT), 2)

    # Tools
    tools = ["brush", "rectangle", "circle", "eraser", "clear"]
    tool_buttons = {}

    btn_w, btn_h = 110, 28

    for i, tool in enumerate(tools):
        rect = pygame.Rect(10 + i*(btn_w+8), 10, btn_w, btn_h)
        tool_buttons[tool] = rect

        pygame.draw.rect(screen,
                         DARK_GRAY if current_tool == tool else WHITE,
                         rect)
        pygame.draw.rect(screen, BLACK, rect, 2)

        draw_text(screen, tool.capitalize(), rect.x+8, rect.y+5, font,
                  WHITE if current_tool == tool else BLACK)

    # Colors
    color_buttons = []
    x, y = 10, 55

    for color in COLOR_OPTIONS:
        rect = pygame.Rect(x, y, 32, 22)
        color_buttons.append((rect, color))

        pygame.draw.rect(screen, color, rect)
        pygame.draw.rect(screen, BLACK, rect, 3 if color == current_color else 1)

        x += 38

    # Palette
    screen.blit(palette, palette_rect.topleft)
    pygame.draw.rect(screen, BLACK, palette_rect, 2)

    # Preview + status
    pygame.draw.rect(screen, current_color, (WIDTH-70, 15, 45, 45))
    pygame.draw.rect(screen, BLACK, (WIDTH-70, 15, 45, 45), 2)

    draw_text(screen, f"Tool: {current_tool}", WIDTH-220, 95, font)
    draw_text(screen, f"Size: {brush_size}", WIDTH-220, 115, font)

    return tool_buttons, color_buttons