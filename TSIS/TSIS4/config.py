# This file stores all main settings for the game.
# We keep them here so other files can use the same values.

# Window size in pixels.
WIDTH = 800
HEIGHT = 600

# One snake cell is 20x20 pixels.
CELL = 20

# Basic game speed. The speed becomes higher when the level grows.
FPS_BASE = 8

# PostgreSQL database settings.
# Change DB_PASSWORD if your PostgreSQL password is different.
DB_NAME = "snake_db"
DB_USER = "postgres"
DB_PASSWORD = "20252025"
DB_HOST = "localhost"
DB_PORT = "5432"

# Colors in RGB format: (Red, Green, Blue).
# These colors are used by Pygame when it draws the screen.
BG = (18, 18, 24)
PANEL = (34, 34, 46)
WHITE = (240, 240, 240)
GRAY = (150, 150, 160)
GREEN = (70, 210, 90)
RED = (220, 55, 55)
DARK_RED = (120, 0, 0)
YELLOW = (240, 210, 70)
BLUE = (70, 140, 255)
PURPLE = (170, 90, 255)
ORANGE = (255, 150, 50)
BLACK = (0, 0, 0)
