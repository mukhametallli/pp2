import pygame
import sys
import os
from race import *

pygame.init()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# -----------------------------------------
# WINDOW
# -----------------------------------------
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Car Dodge Game")

clock = pygame.time.Clock()
FPS = 60

# -----------------------------------------
# FONTS
# -----------------------------------------
font = pygame.font.SysFont("Arial", 24)
big_font = pygame.font.SysFont("Arial", 40)

# -----------------------------------------
# AUDIO (THIS IS WHERE IT BELONGS)
# -----------------------------------------
pygame.mixer.music.load(
    os.path.join(BASE_DIR, "sounds", "background_music.mp3")
)
pygame.mixer.music.set_volume(0.15)
pygame.mixer.music.play(-1)

coin_sound = pygame.mixer.Sound(
    os.path.join(BASE_DIR, "sounds", "coin_sound.mp3")
)
coin_sound.set_volume(0.9)

crash_sound = pygame.mixer.Sound(
    os.path.join(BASE_DIR, "sounds", "crash_sound.mp3")
)
crash_sound.set_volume(1.0)

# -----------------------------------------
# ASSETS
# -----------------------------------------
player_img = pygame.transform.scale(
    pygame.image.load(os.path.join(BASE_DIR, "images", "player_car.png")),
    (player_w, player_h)
)

enemy_img = pygame.transform.scale(
    pygame.image.load(os.path.join(BASE_DIR, "images", "enemy_car.png")),
    (enemy_w, enemy_h)
)

coin_img = pygame.transform.scale(
    pygame.image.load(os.path.join(BASE_DIR, "images", "coin.png")),
    (coin_size, coin_size)
)

# -----------------------------------------
# STATE
# -----------------------------------------
state = reset_game()
game_over = False

# -----------------------------------------
# LOOP
# -----------------------------------------
running = True

while running:
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if game_over and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                state = reset_game()
                game_over = False
            elif event.key == pygame.K_q:
                running = False

    keys = pygame.key.get_pressed()

    if not game_over:
        state, game_over = update(state, keys, coin_sound, crash_sound)

    draw(
        screen,
        state,
        (player_img, enemy_img, coin_img),
        (font, big_font),
        game_over
    )

    pygame.display.update()

pygame.quit()
sys.exit()