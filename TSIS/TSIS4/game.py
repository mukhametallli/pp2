# This file contains the main Snake game logic.
# Here we move the snake, create food, create poison, create power-ups, and draw the game.

import json
import os
import random
import pygame
from config import *

# File where user settings are saved.
SETTINGS_FILE = "settings.json"


def load_settings():
    # Default settings. They are used if settings.json does not exist.
    default = {"snake_color": list(GREEN), "grid": True, "sound": False}

    # If there is no settings file, create it and return default settings.
    if not os.path.exists(SETTINGS_FILE):
        save_settings(default)
        return default

    try:
        # Open settings.json and read saved settings.
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Add saved settings to default settings.
        default.update(data)
    except Exception:
        # If there is an error, use default settings.
        pass

    return default


def save_settings(settings):
    # Save settings to settings.json.
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2)


class SnakeGame:
    # This class stores and controls one game.
    def __init__(self, username, personal_best, settings):
        # Save player name, best score, and settings.
        self.username = username
        self.personal_best = personal_best
        self.settings = settings

        # Start a new game.
        self.reset()

    def reset(self):
        # Put the snake at the start position.
        # Each part is a cell: (x, y).
        self.snake = [(8, 8), (7, 8), (6, 8)]

        # Snake moves to the right at the start.
        self.direction = (1, 0)
        self.next_direction = (1, 0)

        # Start values for score and level.
        self.score = 0
        self.level = 1
        self.food_eaten = 0
        self.game_over = False

        # Empty objects at the start.
        self.obstacles = []
        self.food = None
        self.poison = None
        self.powerup = None
        self.active_powerup = None
        self.active_until = 0
        self.shield = False

        # Create first food, poison, and power-up.
        self.spawn_food()
        self.spawn_poison()
        self.spawn_powerup()

    def cells(self):
        # Return all cells where objects can appear.
        # We do not use borders and top panel.
        return [(x, y) for x in range(1, WIDTH // CELL - 1) for y in range(2, HEIGHT // CELL - 1)]

    def occupied(self):
        # Make a set of cells that are already busy.
        blocked = set(self.snake) | set(self.obstacles)

        # Add food, poison, and power-up positions if they exist.
        if self.food:
            blocked.add(self.food["pos"])
        if self.poison:
            blocked.add(self.poison["pos"])
        if self.powerup:
            blocked.add(self.powerup["pos"])

        return blocked

    def random_free_cell(self):
        # Find all free cells.
        free = [c for c in self.cells() if c not in self.occupied()]

        # Return a random free cell. If there is no free cell, return (5, 5).
        return random.choice(free) if free else (5, 5)

    def spawn_food(self):
        # Create normal food.
        now = pygame.time.get_ticks()

        # Food can give 1, 2, or 3 points value.
        weights = [(1, YELLOW), (2, ORANGE), (3, PURPLE)]
        value, color = random.choice(weights)

        # Food disappears after 7 seconds.
        self.food = {"pos": self.random_free_cell(), "value": value, "color": color, "expires": now + 7000}

    def spawn_poison(self):
        # Poison appears with 65% chance.
        if random.random() < 0.65:
            # Poison disappears after 8 seconds.
            self.poison = {"pos": self.random_free_cell(), "expires": pygame.time.get_ticks() + 8000}
        else:
            self.poison = None

    def spawn_powerup(self):
        # Create a power-up only if there is no other power-up active.
        if self.powerup is None and self.active_powerup is None and random.random() < 0.55:
            # Power-up can be speed, slow, or shield.
            kind = random.choice(["speed", "slow", "shield"])
            color = {"speed": BLUE, "slow": PURPLE, "shield": WHITE}[kind]

            # Power-up disappears after 8 seconds.
            self.powerup = {"pos": self.random_free_cell(), "kind": kind, "color": color, "expires": pygame.time.get_ticks() + 8000}

    def place_obstacles_for_level(self):
        # Obstacles start from level 3.
        if self.level < 3:
            self.obstacles = []
            return

        # Keep cells near the snake head safe.
        head = self.snake[0]
        safe_zone = {(head[0] + dx, head[1] + dy) for dx in range(-2, 3) for dy in range(-2, 3)}

        # More level means more obstacles, but maximum is 35.
        count = min(5 + self.level * 2, 35)
        self.obstacles = []
        tries = 0

        # Try to place obstacles in free cells.
        while len(self.obstacles) < count and tries < 500:
            tries += 1
            pos = self.random_free_cell()

            # Do not put obstacles near the head or inside the snake.
            if pos in safe_zone or pos in self.snake:
                continue

            self.obstacles.append(pos)

    def current_fps(self):
        # FPS means game speed.
        # Higher level makes the game faster.
        fps = FPS_BASE + self.level
        now = pygame.time.get_ticks()

        # Speed power-up makes the snake faster.
        if self.active_powerup == "speed" and now < self.active_until:
            fps += 5

        # Slow power-up makes the snake slower.
        if self.active_powerup == "slow" and now < self.active_until:
            fps = max(4, fps - 4)

        return fps

    def set_direction(self, dx, dy):
        # Change snake direction.
        # The snake cannot turn directly back into itself.
        if (dx, dy) != (-self.direction[0], -self.direction[1]):
            self.next_direction = (dx, dy)

    def trigger_collision(self):
        # This function runs when the snake hits something.
        if self.shield:
            # Shield saves the player one time.
            self.shield = False
            self.active_powerup = None
            return False

        # Without shield, the game ends.
        self.game_over = True
        return True

    def update(self):
        # This function updates the game one step.
        now = pygame.time.get_ticks()

        # If food time is over, create new food.
        if self.food and now > self.food["expires"]:
            self.spawn_food()

        # If poison time is over, create new poison or remove it.
        if self.poison and now > self.poison["expires"]:
            self.spawn_poison()

        # If power-up time is over, remove it and maybe create a new one.
        if self.powerup and now > self.powerup["expires"]:
            self.powerup = None
            self.spawn_powerup()

        # Stop speed or slow power-up after 5 seconds.
        if self.active_powerup in ("speed", "slow") and now > self.active_until:
            self.active_powerup = None

        # Use the next direction chosen by the player.
        self.direction = self.next_direction

        # Get current snake head position.
        hx, hy = self.snake[0]

        # Calculate new head position.
        nx, ny = hx + self.direction[0], hy + self.direction[1]
        new_head = (nx, ny)

        # Check collisions with border, snake body, and obstacles.
        border_hit = nx <= 0 or ny <= 1 or nx >= WIDTH // CELL - 1 or ny >= HEIGHT // CELL - 1
        self_hit = new_head in self.snake
        obstacle_hit = new_head in self.obstacles

        if border_hit or self_hit or obstacle_hit:
            # If shield is not active, the game ends.
            if self.trigger_collision():
                return

            # If shield saved the player, keep the head in the same place.
            new_head = self.snake[0]

        # Add new head to the snake.
        self.snake.insert(0, new_head)
        grew = False

        # Check if snake ate food.
        if self.food and new_head == self.food["pos"]:
            # Add score. Food value can be 1, 2, or 3.
            self.score += self.food["value"] * 10
            self.food_eaten += 1
            grew = True

            # Every 4 foods, level becomes higher.
            if self.food_eaten % 4 == 0:
                self.level += 1
                self.place_obstacles_for_level()

            # Create new objects after eating food.
            self.spawn_food()
            if random.random() < 0.6:
                self.spawn_poison()
            self.spawn_powerup()

        # Check if snake ate poison.
        if self.poison and new_head == self.poison["pos"]:
            # Poison removes 2 parts from the snake tail.
            for _ in range(2):
                if len(self.snake) > 1:
                    self.snake.pop()

            self.poison = None

            # If snake is too short, game ends.
            if len(self.snake) <= 1:
                self.game_over = True
                return

        # Check if snake took a power-up.
        if self.powerup and new_head == self.powerup["pos"]:
            kind = self.powerup["kind"]
            self.powerup = None
            self.active_powerup = kind

            if kind == "shield":
                # Shield protects from one collision.
                self.shield = True
                self.active_until = 0
            else:
                # Speed and slow work for 5 seconds.
                self.active_until = now + 5000

            # Give bonus score for power-up.
            self.score += 15

        # If snake did not eat food, remove the tail.
        # This makes the snake move without growing.
        if not grew:
            self.snake.pop()

    def draw(self, screen, font, small_font):
        # Draw background.
        screen.fill(BG)

        # Draw grid if setting is ON.
        if self.settings.get("grid", True):
            for x in range(0, WIDTH, CELL):
                pygame.draw.line(screen, (28, 28, 35), (x, 40), (x, HEIGHT))
            for y in range(40, HEIGHT, CELL):
                pygame.draw.line(screen, (28, 28, 35), (0, y), (WIDTH, y))

        # Draw top panel with player information.
        pygame.draw.rect(screen, PANEL, (0, 0, WIDTH, 40))
        info = f"Player: {self.username}   Score: {self.score}   Level: {self.level}   Best: {self.personal_best}"
        screen.blit(small_font.render(info, True, WHITE), (12, 10))

        # Draw active power-up text.
        if self.active_powerup:
            if self.active_powerup == "shield":
                text = "Power-up: Shield active"
            else:
                remain = max(0, (self.active_until - pygame.time.get_ticks()) // 1000)
                text = f"Power-up: {self.active_powerup} {remain}s"
            screen.blit(small_font.render(text, True, YELLOW), (560, 10))

        # Draw game border.
        pygame.draw.rect(screen, GRAY, (0, 40, WIDTH, HEIGHT - 40), 2)

        # Draw obstacles.
        for pos in self.obstacles:
            pygame.draw.rect(screen, GRAY, (pos[0] * CELL, pos[1] * CELL, CELL, CELL))

        # Draw food.
        if self.food:
            pygame.draw.rect(screen, self.food["color"], (self.food["pos"][0] * CELL, self.food["pos"][1] * CELL, CELL, CELL))

        # Draw poison.
        if self.poison:
            pygame.draw.rect(screen, DARK_RED, (self.poison["pos"][0] * CELL, self.poison["pos"][1] * CELL, CELL, CELL))

        # Draw power-up as a circle.
        if self.powerup:
            pygame.draw.circle(screen, self.powerup["color"], (self.powerup["pos"][0] * CELL + CELL // 2, self.powerup["pos"][1] * CELL + CELL // 2), CELL // 2)

        # Get snake color from settings.
        snake_color = tuple(self.settings.get("snake_color", list(GREEN)))

        # Draw every snake part.
        for i, pos in enumerate(self.snake):
            # If shield is active, snake head becomes white.
            color = WHITE if i == 0 and self.shield else snake_color
            pygame.draw.rect(screen, color, (pos[0] * CELL, pos[1] * CELL, CELL, CELL), border_radius=4)
