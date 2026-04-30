import pygame
from paint import *

def main():
    pygame.init()

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Paint App - Fixed Shapes Edition")
    clock = pygame.time.Clock()

    font = pygame.font.SysFont("Arial", 18)

    canvas = pygame.Surface((WIDTH, HEIGHT - TOOLBAR_HEIGHT))
    canvas.fill(WHITE)

    palette = create_color_palette(200, 60)
    palette_rect = pygame.Rect(WIDTH - 220, 20, 200, 60)

    current_tool = "brush"
    current_color = BLACK
    brush_size = 5

    drawing = False
    start_pos = None
    last_pos = None

    running = True

    while running:
        screen.fill(WHITE)

        tool_buttons, color_buttons = draw_toolbar(
            screen, current_tool, current_color, brush_size,
            font, palette, palette_rect
        )

        screen.blit(canvas, (0, TOOLBAR_HEIGHT))

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:

                if event.key == pygame.K_ESCAPE:
                    running = False

                elif event.key == pygame.K_b:
                    current_tool = "brush"

                elif event.key == pygame.K_e:
                    current_tool = "eraser"

                elif event.key == pygame.K_r:
                    current_tool = "rectangle"

                elif event.key == pygame.K_c:
                    current_tool = "circle"

                elif event.key in (pygame.K_PLUS, pygame.K_EQUALS):
                    brush_size = min(50, brush_size + 1)

                elif event.key == pygame.K_MINUS:
                    brush_size = max(1, brush_size - 1)

            elif event.type == pygame.MOUSEBUTTONDOWN:

                if event.pos[1] < TOOLBAR_HEIGHT:

                    for tool, rect in tool_buttons.items():
                        if rect.collidepoint(event.pos):
                            if tool == "clear":
                                canvas.fill(WHITE)
                            else:
                                current_tool = tool

                    for rect, color in color_buttons:
                        if rect.collidepoint(event.pos):
                            current_color = color

                    if palette_rect.collidepoint(event.pos):
                        px = event.pos[0] - palette_rect.x
                        py = event.pos[1] - palette_rect.y
                        current_color = palette.get_at((px, py))

                else:
                    drawing = True
                    start_pos = (event.pos[0], event.pos[1] - TOOLBAR_HEIGHT)
                    last_pos = start_pos

                    # brush / eraser immediate dot
                    if current_tool == "brush":
                        pygame.draw.circle(canvas, current_color, start_pos, brush_size)
                    elif current_tool == "eraser":
                        pygame.draw.circle(canvas, WHITE, start_pos, brush_size)

            elif event.type == pygame.MOUSEMOTION and drawing:

                current_pos = (event.pos[0], event.pos[1] - TOOLBAR_HEIGHT)

                if current_tool == "brush":
                    pygame.draw.line(
                        canvas,
                        current_color,
                        last_pos,
                        current_pos,
                        brush_size * 2
                    )

                elif current_tool == "eraser":
                    pygame.draw.line(
                        canvas,
                        WHITE,
                        last_pos,
                        current_pos,
                        brush_size * 2
                    )

                last_pos = current_pos

            elif event.type == pygame.MOUSEBUTTONUP:

                if start_pos:
                    end_pos = (event.pos[0], event.pos[1] - TOOLBAR_HEIGHT)

                    x1, y1 = start_pos
                    x2, y2 = end_pos


# RECTANGLE
                    if current_tool == "rectangle":
                        rect = pygame.Rect(
                            min(x1, x2),
                            min(y1, y2),
                            abs(x2 - x1),
                            abs(y2 - y1)
                        )
                        pygame.draw.rect(canvas, current_color, rect, 2)

                    # CIRCLE
                    elif current_tool == "circle":
                        radius = int(((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5)
                        pygame.draw.circle(canvas, current_color, start_pos, radius, 2)

                drawing = False
                start_pos = None
                last_pos = None

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()