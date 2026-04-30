import pygame

UP = 0
DOWN = 1
LEFT = 2
RIGHT = 3

CELL = 10
WIDTH = 400
HEIGHT = 400


class Snake:
    def __init__(self):
        self.snake = [(200, 200), (210, 200), (220, 200)]
        self.direction = RIGHT

        self.skin = pygame.Surface((CELL, CELL))
        self.skin.fill((255, 255, 255))

        self.head = pygame.Surface((CELL, CELL))
        self.head.fill((200, 200, 200))

    def move(self, grow=False, shrink=False):
        x, y = self.snake[-1]

        if self.direction == RIGHT:
            new_head = (x + CELL, y)
        elif self.direction == LEFT:
            new_head = (x - CELL, y)
        elif self.direction == UP:
            new_head = (x, y - CELL)
        else:
            new_head = (x, y + CELL)

        # wall collision
        if not (0 <= new_head[0] < WIDTH and 0 <= new_head[1] < HEIGHT):
            return False

        # self collision
        if new_head in self.snake:
            return False

        self.snake.append(new_head)

        if not grow:
            self.snake.pop(0)

        if shrink and len(self.snake) > 1:
            self.snake.pop(0)

        return True