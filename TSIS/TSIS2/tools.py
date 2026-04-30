from __future__ import annotations

# STEP 1: Import helper modules.
# deque is used for flood fill.
# datetime is used for save file names.
# Path is used for folders.
from collections import deque
from datetime import datetime
from pathlib import Path

# STEP 2: Import pygame.
import pygame


# STEP 3: Canvas background color.
CANVAS_BG = (255, 255, 255)

# STEP 4: Main color palette.
PALETTE = [
    (0, 0, 0),        # black
    (255, 0, 0),      # red
    (0, 180, 0),      # green
    (0, 0, 255),      # blue
    (255, 255, 0),    # yellow
    (170, 35, 220),   # purple
    (255, 135, 0),    # orange
]

# STEP 5: Brush size levels.
BRUSH_SIZES = {
    1: 2,
    2: 5,
    3: 10,
}


def draw_button(screen: pygame.Surface, rect: pygame.Rect, label: str, font: pygame.font.Font, selected: bool = False) -> None:
    # STEP 6: Draw one button.
    # If selected is True, the button becomes dark.
    fill = (76, 76, 76) if selected else (255, 255, 255)
    text_color = (255, 255, 255) if selected else (0, 0, 0)

    pygame.draw.rect(screen, fill, rect)
    pygame.draw.rect(screen, (0, 0, 0), rect, width=3)

    text = font.render(label, True, text_color)
    screen.blit(text, text.get_rect(center=rect.center))


def draw_gradient(screen: pygame.Surface, rect: pygame.Rect) -> None:
    # STEP 7: Draw a simple rainbow gradient.
    # The user can click it to choose a color.
    for x in range(rect.width):
        hue = x / max(1, rect.width - 1)
        color = pygame.Color(0)
        color.hsva = (hue * 360, 100, 100, 100)

        for y in range(rect.height):
            value = 1 - y / max(1, rect.height - 1) * 0.55
            c = (int(color.r * value), int(color.g * value), int(color.b * value))
            screen.set_at((rect.x + x, rect.y + y), c)


def clamp_point(pos: tuple[int, int], width: int, height: int) -> tuple[int, int]:
    # STEP 8: Keep a point inside the canvas.
    x = max(0, min(width - 1, pos[0]))
    y = max(0, min(height - 1, pos[1]))
    return x, y


def flood_fill(surface: pygame.Surface, start_pos: tuple[int, int], new_color: tuple[int, int, int]) -> None:
    # STEP 9: Fill an area with a new color.
    # This function is kept for project logic.
    width, height = surface.get_size()
    x, y = start_pos

    if not (0 <= x < width and 0 <= y < height):
        return

    target = surface.get_at((x, y))
    replacement = pygame.Color(*new_color)

    if target == replacement:
        return

    queue: deque[tuple[int, int]] = deque([(x, y)])

    while queue:
        px, py = queue.pop()

        if not (0 <= px < width and 0 <= py < height):
            continue

        if surface.get_at((px, py)) != target:
            continue

        surface.set_at((px, py), replacement)

        queue.append((px + 1, py))
        queue.append((px - 1, py))
        queue.append((px, py + 1))
        queue.append((px, py - 1))


def save_canvas(surface: pygame.Surface, folder: Path | str = ".") -> Path:
    # STEP 10: Save the canvas as a PNG image.
    folder_path = Path(folder)
    folder_path.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    filename = folder_path / f"canvas_{timestamp}.png"

    pygame.image.save(surface, str(filename))
    return filename
