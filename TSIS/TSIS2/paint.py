from __future__ import annotations

# STEP 1: Import needed modules.
# math is used for circles.
# sys is used to close the program.
# Path is used when we save the picture.
import math
import sys
from pathlib import Path

# STEP 2: Import pygame.
# Pygame is the main library for the window, mouse, keyboard, and drawing.
import pygame

# STEP 3: Import helper functions and constants from tools.py.
from tools import BRUSH_SIZES, CANVAS_BG, PALETTE, clamp_point, draw_button, draw_gradient, flood_fill, save_canvas


# STEP 4: Start pygame.
pygame.init()

# STEP 5: Set the window size and layout sizes.
SCREEN_W = 1320
SCREEN_H = 840
TOP_PANEL_H = 260

# STEP 6: Set the canvas position.
CANVAS_X = 8
CANVAS_Y = TOP_PANEL_H + 8
CANVAS_W = SCREEN_W - 16
CANVAS_H = SCREEN_H - CANVAS_Y - 8

# STEP 7: Create the main window.
screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("TSIS 2 Paint - Extended Drawing Tools")

# STEP 8: Create the game clock.
clock = pygame.time.Clock()

# STEP 9: Create fonts for text.
font = pygame.font.Font(None, 34)
small_font = pygame.font.Font(None, 30)
text_font = pygame.font.Font(None, 38)

# STEP 10: Create the drawing canvas.
canvas = pygame.Surface((CANVAS_W, CANVAS_H))
canvas.fill(CANVAS_BG)

# STEP 11: List all drawing tools.
tools = [
    "pencil",
    "line",
    "rectangle",
    "circle",
    "eraser",
    "fill",
    "text",
    "square",
    "r_triangular",
    "eq_triangle",
    "rhombus",
]

# STEP 12: Keyboard shortcuts for tools.
# Size uses 1, 2, 3. Shape shortcuts use letters to avoid conflict.
tool_shortcuts = {
    pygame.K_p: "pencil",
    pygame.K_l: "line",
    pygame.K_r: "rectangle",
    pygame.K_c: "circle",
    pygame.K_e: "eraser",
    pygame.K_f: "fill",
    pygame.K_t: "text",
    pygame.K_s: "square",
    pygame.K_q: "r_triangular",
    pygame.K_w: "eq_triangle",
    pygame.K_h: "rhombus",
}

# STEP 13: Set default tool, size, and color.
active_tool = "pencil"
active_size = BRUSH_SIZES[2]
active_color = (0, 0, 0)

# STEP 14: Variables for drawing.
drawing = False
last_pos: tuple[int, int] | None = None
start_pos: tuple[int, int] | None = None
preview_pos: tuple[int, int] | None = None

# STEP 15: Variables for the text tool.
text_mode = False
text_pos: tuple[int, int] | None = None
current_text = ""
cursor_visible = True
cursor_timer = 0

# STEP 16: Rectangles for clickable buttons.
tool_buttons: dict[str, pygame.Rect] = {}
color_buttons: list[tuple[pygame.Rect, tuple[int, int, int]]] = []
size_buttons: dict[int, pygame.Rect] = {}
clear_button: pygame.Rect | None = None
save_button: pygame.Rect | None = None

# STEP 17: Rectangle for the gradient color picker.
gradient_rect = pygame.Rect(995, 80, 295, 88)


def canvas_rect() -> pygame.Rect:
    # STEP 18: Return the canvas area as a rectangle.
    return pygame.Rect(CANVAS_X, CANVAS_Y, CANVAS_W, CANVAS_H)


def in_canvas(pos: tuple[int, int]) -> bool:
    # STEP 19: Check if the mouse is inside the canvas.
    return canvas_rect().collidepoint(pos)


def to_canvas_pos(pos: tuple[int, int]) -> tuple[int, int]:
    # STEP 20: Convert screen mouse position to canvas position.
    return clamp_point((pos[0] - CANVAS_X, pos[1] - CANVAS_Y), CANVAS_W, CANVAS_H)


def make_shape_rect(a: tuple[int, int], b: tuple[int, int], force_square: bool = False) -> pygame.Rect:
    # STEP 21: Make a rectangle from two points.
    x1, y1 = a
    x2, y2 = b

    if force_square:
        side = min(abs(x2 - x1), abs(y2 - y1))
        x2 = x1 + side * (1 if x2 >= x1 else -1)
        y2 = y1 + side * (1 if y2 >= y1 else -1)

    return pygame.Rect(min(x1, x2), min(y1, y2), abs(x2 - x1), abs(y2 - y1))


def triangle_points(kind: str, a: tuple[int, int], b: tuple[int, int]) -> list[tuple[int, int]]:
    # STEP 22: Make points for triangle shapes.
    rect = make_shape_rect(a, b)

    if kind == "r_triangular":
        return [(rect.left, rect.bottom), (rect.left, rect.top), (rect.right, rect.bottom)]

    return [(rect.centerx, rect.top), (rect.left, rect.bottom), (rect.right, rect.bottom)]


def rhombus_points(a: tuple[int, int], b: tuple[int, int]) -> list[tuple[int, int]]:
    # STEP 23: Make points for a rhombus.
    rect = make_shape_rect(a, b)
    return [
        (rect.centerx, rect.top),
        (rect.right, rect.centery),
        (rect.centerx, rect.bottom),
        (rect.left, rect.centery),
    ]


def draw_shape(target: pygame.Surface, tool: str, start: tuple[int, int], end: tuple[int, int]) -> None:
    # STEP 24: Draw selected shape on the target surface.
    # Every shape uses active_size as the line width.
    if tool == "line":
        pygame.draw.line(target, active_color, start, end, active_size)

    elif tool == "rectangle":
        pygame.draw.rect(target, active_color, make_shape_rect(start, end), width=active_size)

    elif tool == "square":
        pygame.draw.rect(target, active_color, make_shape_rect(start, end, True), width=active_size)

    elif tool == "circle":
        radius = int(math.dist(start, end))
        pygame.draw.circle(target, active_color, start, max(1, radius), active_size)

    elif tool in {"r_triangular", "eq_triangle"}:
        pygame.draw.polygon(target, active_color, triangle_points(tool, start, end), width=active_size)

    elif tool == "rhombus":
        pygame.draw.polygon(target, active_color, rhombus_points(start, end), width=active_size)


def draw_interface() -> None:
    # STEP 25: Draw the top panel, buttons, colors, sizes, and info box.
    global tool_buttons, color_buttons, size_buttons, clear_button, save_button

    pygame.draw.rect(screen, (198, 198, 198), (0, 0, SCREEN_W, TOP_PANEL_H))
    pygame.draw.line(screen, (150, 150, 150), (0, TOP_PANEL_H), (SCREEN_W, TOP_PANEL_H), 2)

    # Tool buttons.
    tool_buttons = {}
    names = [
        ("pencil", 12, 50),
        ("line", 165, 50),
        ("rectangle", 318, 50),
        ("circle", 471, 50),
        ("eraser", 624, 50),
        ("fill", 777, 50),
        ("text", 12, 102),
        ("square", 165, 102),
        ("r_triangular", 318, 102),
        ("eq_triangle", 471, 102),
        ("rhombus", 624, 102),
    ]

    for name, x, y in names:
        rect = pygame.Rect(x, y, 140, 42)
        tool_buttons[name] = rect
        draw_button(screen, rect, name, small_font, active_tool == name)

    # Clear and save buttons.
    clear_button = pygame.Rect(777, 102, 140, 42)
    save_button = pygame.Rect(930, 102, 140, 42)
    draw_button(screen, clear_button, "clear", small_font, False)
    draw_button(screen, save_button, "save", small_font, False)

    # Color buttons.
    color_buttons = []
    for idx, color in enumerate(PALETTE):
        rect = pygame.Rect(12 + idx * 56, 178, 46, 34)
        pygame.draw.rect(screen, color, rect)
        pygame.draw.rect(screen, (0, 0, 0), rect, width=2)

        if color == active_color:
            pygame.draw.rect(screen, (255, 255, 255), rect.inflate(-8, -8), width=2)

        color_buttons.append((rect, color))

    # Size buttons. Keys 1, 2, 3 use these same levels.
    size_buttons = {}
    for idx, level in enumerate((1, 2, 3)):
        rect = pygame.Rect(430 + idx * 65, 178, 55, 34)
        size_buttons[level] = rect
        label = f"{level}:{BRUSH_SIZES[level]}"
        draw_button(screen, rect, label, small_font, active_size == BRUSH_SIZES[level])

    # Gradient color picker.
    draw_gradient(screen, gradient_rect)
    pygame.draw.rect(screen, (0, 0, 0), gradient_rect, width=2)

    # Current color box.
    color_box = pygame.Rect(gradient_rect.right - 72, gradient_rect.y - 8, 68, 68)
    pygame.draw.rect(screen, active_color, color_box)
    pygame.draw.rect(screen, (0, 0, 0), color_box, width=2)

    # Info box.
    info = pygame.Rect(980, 183, 320, 66)
    pygame.draw.rect(screen, (255, 255, 255), info)
    pygame.draw.rect(screen, (70, 70, 70), info, width=2)
    screen.blit(small_font.render(f"Tool: {active_tool}", True, (0, 0, 0)), (info.x + 14, info.y + 10))
    screen.blit(small_font.render(f"Size: {active_size} px", True, (0, 0, 0)), (info.x + 14, info.y + 36))

    # Short help line.
    help_text = "Keys: 1/2/3 size | P pencil | L line | F fill | T text | Ctrl+S save"
    screen.blit(small_font.render(help_text, True, (0, 0, 0)), (12, 225))


def draw_canvas_frame() -> None:
    # STEP 26: Draw canvas on the screen.
    rect = canvas_rect()
    screen.blit(canvas, (CANVAS_X, CANVAS_Y))
    pygame.draw.rect(screen, (0, 0, 0), rect, width=2)


def draw_preview() -> None:
    # STEP 27: Show live preview for line and shapes before mouse release.
    if drawing and start_pos and preview_pos and active_tool not in {"pencil", "eraser", "fill", "text"}:
        preview = pygame.Surface((CANVAS_W, CANVAS_H), pygame.SRCALPHA)
        draw_shape(preview, active_tool, start_pos, preview_pos)
        screen.blit(preview, (CANVAS_X, CANVAS_Y))


def draw_text_preview() -> None:
    # STEP 28: Show typed text before Enter is pressed.
    if not text_mode or text_pos is None:
        return

    text_surface = text_font.render(current_text, True, active_color)
    screen.blit(text_surface, (CANVAS_X + text_pos[0], CANVAS_Y + text_pos[1]))

    if cursor_visible:
        cursor_x = CANVAS_X + text_pos[0] + text_surface.get_width() + 2
        cursor_y = CANVAS_Y + text_pos[1]
        pygame.draw.line(screen, active_color, (cursor_x, cursor_y), (cursor_x, cursor_y + text_surface.get_height()), 2)


def confirm_text() -> None:
    # STEP 29: Render typed text permanently onto the canvas.
    global text_mode, text_pos, current_text

    if text_mode and text_pos is not None and current_text:
        text_surface = text_font.render(current_text, True, active_color)
        canvas.blit(text_surface, text_pos)

    text_mode = False
    text_pos = None
    current_text = ""


def cancel_text() -> None:
    # STEP 30: Cancel text input without drawing it.
    global text_mode, text_pos, current_text

    text_mode = False
    text_pos = None
    current_text = ""


def start_drawing(pos: tuple[int, int]) -> None:
    # STEP 31: Start drawing when mouse button is pressed.
    global drawing, last_pos, start_pos, preview_pos

    drawing = True
    last_pos = pos
    start_pos = pos
    preview_pos = pos


def end_drawing(pos: tuple[int, int]) -> None:
    # STEP 32: Finish drawing when mouse button is released.
    global drawing, last_pos, start_pos, preview_pos

    if start_pos and active_tool not in {"pencil", "eraser", "fill", "text"}:
        draw_shape(canvas, active_tool, start_pos, pos)

    drawing = False
    last_pos = None
    start_pos = None
    preview_pos = None


def handle_keydown(event: pygame.event.Event) -> None:
    # STEP 33: Handle keyboard actions.
    global active_tool, active_size, current_text, cursor_visible

    # Text mode has special keyboard logic.
    if text_mode:
        if event.key == pygame.K_RETURN:
            confirm_text()
            return
        if event.key == pygame.K_ESCAPE:
            cancel_text()
            return
        if event.key == pygame.K_BACKSPACE:
            current_text = current_text[:-1]
            return
        if event.unicode:
            current_text += event.unicode
            cursor_visible = True
            return

    # Ctrl + S or Cmd + S saves the picture.
    if (event.mod & pygame.KMOD_CTRL or event.mod & pygame.KMOD_META) and event.key == pygame.K_s:
        path = save_canvas(canvas, Path("."))
        print(f"Saved: {path}")
        return

    # Keys 1, 2, 3 change brush size.
    if event.key in (pygame.K_1, pygame.K_2, pygame.K_3):
        active_size = BRUSH_SIZES[{pygame.K_1: 1, pygame.K_2: 2, pygame.K_3: 3}[event.key]]
        return

    # Tool shortcuts.
    if event.key in tool_shortcuts:
        active_tool = tool_shortcuts[event.key]
        return

    # Backspace clears canvas.
    if event.key == pygame.K_BACKSPACE:
        canvas.fill(CANVAS_BG)
        return

    # Escape closes the program when text tool is not active.
    if event.key == pygame.K_ESCAPE:
        pygame.quit()
        sys.exit()


def handle_mouse_down(event: pygame.event.Event) -> None:
    # STEP 34: Handle mouse click.
    global active_tool, active_color, active_size, text_mode, text_pos, current_text

    pos = event.pos

    if clear_button and clear_button.collidepoint(pos):
        canvas.fill(CANVAS_BG)
        cancel_text()
        return

    if save_button and save_button.collidepoint(pos):
        path = save_canvas(canvas, Path("."))
        print(f"Saved: {path}")
        return

    for name, rect in tool_buttons.items():
        if rect.collidepoint(pos):
            active_tool = name
            cancel_text()
            return

    for level, rect in size_buttons.items():
        if rect.collidepoint(pos):
            active_size = BRUSH_SIZES[level]
            return

    for rect, color in color_buttons:
        if rect.collidepoint(pos):
            active_color = color
            return

    if gradient_rect.collidepoint(pos):
        active_color = screen.get_at(pos)[:3]
        return

    if in_canvas(pos):
        local = to_canvas_pos(pos)

        if active_tool == "fill":
            flood_fill(canvas, local, active_color)
            return

        if active_tool == "text":
            text_mode = True
            text_pos = local
            current_text = ""
            return

        cancel_text()
        start_drawing(local)


def handle_mouse_up(event: pygame.event.Event) -> None:
    # STEP 35: Stop drawing when mouse button is released.
    if drawing:
        local = to_canvas_pos(event.pos) if in_canvas(event.pos) else preview_pos or start_pos
        if local:
            end_drawing(local)


def handle_mouse_motion(event: pygame.event.Event) -> None:
    # STEP 36: Draw while mouse is moving.
    global last_pos, preview_pos

    if not drawing or not in_canvas(event.pos):
        return

    local = to_canvas_pos(event.pos)

    # Pencil and eraser draw immediately.
    if active_tool in {"pencil", "eraser"} and last_pos is not None:
        draw_color = CANVAS_BG if active_tool == "eraser" else active_color
        pygame.draw.line(canvas, draw_color, last_pos, local, active_size)
        pygame.draw.circle(canvas, draw_color, local, max(1, active_size // 2))
        last_pos = local
    else:
        # Line and shapes only show live preview while dragging.
        preview_pos = local


def main() -> None:
    # STEP 37: Main program loop.
    global cursor_visible, cursor_timer

    while True:
        screen.fill((255, 255, 255))
        draw_interface()
        draw_canvas_frame()
        draw_preview()
        draw_text_preview()

        # Cursor blinking for text tool.
        cursor_timer += clock.get_time()
        if cursor_timer >= 500:
            cursor_visible = not cursor_visible
            cursor_timer = 0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                handle_keydown(event)

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                handle_mouse_down(event)

            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                handle_mouse_up(event)

            elif event.type == pygame.MOUSEMOTION:
                handle_mouse_motion(event)

        pygame.display.flip()
        clock.tick(120)


# STEP 38: Start the program.
if __name__ == "__main__":
    main()
