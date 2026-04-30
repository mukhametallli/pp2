import pygame
from paint import *

def main():
    pygame.init()

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Paint App - Clean Layout Edition")
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
                elif event.key == pygame.K_r:
                    current_tool = "rectangle"
                elif event.key == pygame.K_c:
                    current_tool = "circle"
                elif event.key == pygame.K_e:
                    current_tool = "eraser"
                elif event.key == pygame.K_s:
                    current_tool = "square"
                elif event.key == pygame.K_t:
                    current_tool = "r_triangle"
                elif event.key == pygame.K_y:
                    current_tool = "eq_triangle"
                elif event.key == pygame.K_h:
                    current_tool = "rhombus"

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
                    start_pos = clamp_to_canvas(event.pos)
                    last_pos = start_pos

                    cpos = (start_pos[0], start_pos[1] - TOOLBAR_HEIGHT)

                    if current_tool == "brush":
                        pygame.draw.circle(canvas, current_color, cpos, brush_size)
                    elif current_tool == "eraser":
                        pygame.draw.circle(canvas, WHITE, cpos, brush_size)

            elif event.type == pygame.MOUSEMOTION and drawing:

                current_pos = clamp_to_canvas(event.pos)

                c_last = (last_pos[0], last_pos[1] - TOOLBAR_HEIGHT)
                c_curr = (current_pos[0], current_pos[1] - TOOLBAR_HEIGHT)

                if current_tool == "brush":
                    draw_brush(canvas, current_color, c_last, c_curr, brush_size)
                elif current_tool == "eraser":
                    draw_brush(canvas, WHITE, c_last, c_curr, brush_size)

                last_pos = current_pos

            elif event.type == pygame.MOUSEBUTTONUP:

                if start_pos:
                    end_pos = clamp_to_canvas(event.pos)

                    c_start = (start_pos[0], start_pos[1] - TOOLBAR_HEIGHT)
                    c_end = (end_pos[0], end_pos[1] - TOOLBAR_HEIGHT)

                    if current_tool == "square":
                        draw_square(canvas, current_color, c_start, c_end)

                    elif current_tool == "rectangle":
                        pygame.draw.rect(canvas, current_color,
                                         pygame.Rect(c_start[0], c_start[1],
                                                     c_end[0]-c_start[0],
                                                     c_end[1]-c_start[1]), 2)

                    elif current_tool == "circle":
                        r = int(((c_end[0]-c_start[0])**2 + (c_end[1]-c_start[1])**2) ** 0.5)
                        pygame.draw.circle(canvas, current_color, c_start, r, 2)

                    elif current_tool == "r_triangle":
                        draw_right_triangle(canvas, current_color, c_start, c_end)

                    elif current_tool == "eq_triangle":
                        draw_equilateral_triangle(canvas, current_color, c_start, c_end)

                    elif current_tool == "rhombus":
                        draw_rhombus(canvas, current_color, c_start, c_end)

                drawing = False
                start_pos = None
                last_pos = None

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()