import pygame
from ball import Ball
 
 
# Constants

WIDTH, HEIGHT = 600, 500
FPS           = 60
WHITE         = (255, 255, 255)
BLACK         = (0,   0,   0)
LIGHT_GRAY    = (230, 230, 230)
 
 
def draw_grid(surface: pygame.Surface):
    for x in range(0, WIDTH, 40):
        pygame.draw.line(surface, LIGHT_GRAY, (x, 0), (x, HEIGHT), 1)
    for y in range(0, HEIGHT, 40):
        pygame.draw.line(surface, LIGHT_GRAY, (0, y), (WIDTH, y), 1)
 
 
def draw_hud(surface: pygame.Surface, ball: Ball, font: pygame.font.Font):
    info = font.render(
        f"Position  x:{ball.x:>4}  y:{ball.y:>4}   |   Arrow keys to move   |   Q to quit",
        True, (100, 100, 100)
    )
    surface.blit(info, (10, 6))
 
 
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Moving Ball")
 
    font  = pygame.font.SysFont("Arial", 14)
    ball  = Ball(WIDTH, HEIGHT)
    clock = pygame.time.Clock()
 
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
 
            # Keyboard input
            if event.type == pygame.KEYDOWN:
                if   event.key == pygame.K_UP:    ball.move_up()
                elif event.key == pygame.K_DOWN:  ball.move_down()
                elif event.key == pygame.K_LEFT:  ball.move_left()
                elif event.key == pygame.K_RIGHT: ball.move_right()
                elif event.key == pygame.K_q:     running = False
 
        # Rendering
        screen.fill(WHITE)
        draw_grid(screen)
        draw_hud(screen, ball, font)
 
        # Screen border
        pygame.draw.rect(screen, BLACK, (0, 0, WIDTH, HEIGHT), 2)
 
        ball.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)
 
    pygame.quit()
 
 
if __name__ == "__main__":
    main()
 