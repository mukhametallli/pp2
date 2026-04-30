import pygame
import random
import sys
from snake import Snake, UP, DOWN, LEFT, RIGHT

pygame.init()

WIDTH, HEIGHT = 400, 400
CELL = 10

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake (Level System Edition)")
clock = pygame.time.Clock()

# Colors
RED = (255, 0, 0)
VIOLET = (148, 0, 211)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (150, 150, 150)

font = pygame.font.SysFont("Arial", 24)
big_font = pygame.font.SysFont("Arial", 48)


def random_pos(snake_body):
    while True:
        pos = (random.randrange(0, WIDTH, CELL),
               random.randrange(0, HEIGHT, CELL))
        if pos not in snake_body:
            return pos


def game_over_screen(score, level):
    while True:
        screen.fill(BLACK)

        screen.blit(big_font.render("GAME OVER", True, RED), (80, 120))
        screen.blit(font.render(f"Score: {score}", True, WHITE), (140, 190))
        screen.blit(font.render(f"Level: {level}", True, WHITE), (140, 220))
        screen.blit(font.render("Press R to Restart or Q to Quit", True, GRAY), (40, 270))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return
                elif event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()


def main():
    snake = Snake()
    food = random_pos(snake.snake)

    poison = None
    poison_timer = 0
    POISON_DURATION = 80
    POISON_CHANCE = 0.02

    score = 0
    food_count = 0
    level = 1
    SPEED = 10

    running = True

    while running:
        clock.tick(SPEED)

        # -------- INPUT --------
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and snake.direction != DOWN:
                    snake.direction = UP
                elif event.key == pygame.K_DOWN and snake.direction != UP:
                    snake.direction = DOWN
                elif event.key == pygame.K_LEFT and snake.direction != RIGHT:
                    snake.direction = LEFT
                elif event.key == pygame.K_RIGHT and snake.direction != LEFT:
                    snake.direction = RIGHT

        # -------- POISON SPAWN --------
        if poison is None and random.random() < POISON_CHANCE:
            poison = random_pos(snake.snake)
            poison_timer = POISON_DURATION

        if poison:
            poison_timer -= 1
            if poison_timer <= 0:
                poison = None

        head = snake.snake[-1]

        grow = False
        shrink = False

        # -------- FOOD --------
        if head == food:
            grow = True
            score += 1
            food_count += 1
            food = random_pos(snake.snake)

            # LEVEL UP
            if food_count == 5:
                level += 1
                food_count = 0
                SPEED += 2

        # -------- POISON --------
        elif poison is not None and head == poison:
            shrink = True
            score = max(0, score - 1)
            poison = None

        # -------- MOVE --------
        if not snake.move(grow=grow, shrink=shrink):
            game_over_screen(score, level)
            return

        # -------- DRAW --------
        screen.fill(BLACK)

        pygame.draw.rect(screen, RED, (*food, CELL, CELL))

        if poison:
            pygame.draw.rect(screen, VIOLET, (*poison, CELL, CELL))

        for part in snake.snake[:-1]:
            screen.blit(snake.skin, part)
        screen.blit(snake.head, snake.snake[-1])

        screen.blit(font.render(f"Score: {score}", True, WHITE), (10, 10))
        screen.blit(font.render(f"Level: {level}", True, WHITE), (10, 35))

        pygame.display.update()


# -------- START GAME LOOP --------
while True:
    main()