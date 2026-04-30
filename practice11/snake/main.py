import pygame
import random
import sys
from snake import Snake, UP, DOWN, LEFT, RIGHT

pygame.init()

WIDTH, HEIGHT = 400, 400
CELL = 10

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake (now with consequences)")
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

def game_over_screen(score):
    while True:
        screen.fill(BLACK)

        text1 = big_font.render("GAME OVER", True, RED)
        text2 = font.render(f"Score: {score}", True, WHITE)
        text3 = font.render("Press R to Restart or Q to Quit", True, GRAY)

        screen.blit(text1, (80, 140))
        screen.blit(text2, (150, 200))
        screen.blit(text3, (40, 250))

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

    # Poison system
    poison = None
    poison_timer = 0
    POISON_DURATION = 80
    POISON_CHANCE = 0.02

    score = 0
    SPEED = 10

    while True:
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
        if poison is None:
            if random.random() < POISON_CHANCE:
                poison = random_pos(snake.snake)
                poison_timer = POISON_DURATION
        else:
            poison_timer -= 1
            if poison_timer <= 0:
                poison = None

        head = snake.snake[-1]

        grow = False
        shrink = False

        # -------- FOOD / POISON --------
        if head == food:
            grow = True
            score += 1
            food = random_pos(snake.snake)

        elif poison is not None and head == poison:
            shrink = True
            score = max(0, score - 1)
            poison = None

        alive = snake.move(grow=grow, shrink=shrink)

        if not alive:
            game_over_screen(score)
            return

        # -------- DRAW --------
        screen.fill(BLACK)

        # food
        pygame.draw.rect(screen, RED, (*food, CELL, CELL))

        # poison
        if poison is not None:
            pygame.draw.rect(screen, VIOLET, (*poison, CELL, CELL))

        # snake
        for part in snake.snake[:-1]:
            screen.blit(snake.skin, part)
        screen.blit(snake.head, snake.snake[-1])

        # score
        score_text = font.render(f"Score: {score}", True, WHITE)
        screen.blit(score_text, (10, 10))

        pygame.display.update()

# -------- START GAME --------
while True:
    main()