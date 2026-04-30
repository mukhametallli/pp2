import pygame
import random
import os

WIDTH = 360
HEIGHT = 640

player_w, player_h = 70, 120
enemy_w, enemy_h = 70, 120
coin_size = 30

player_speed = 6
coin_speed = 5

GREEN = (34, 139, 34)
ROAD_GRAY = (60, 60, 60)
LINE_WHITE = (240, 240, 240)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 215, 0)


def spawn_coin(enemy_rect):
    while True:
        x = random.randint(0, WIDTH - coin_size)
        y = random.randint(-400, -100)
        coin_rect = pygame.Rect(x, y, coin_size, coin_size)
        if not coin_rect.colliderect(enemy_rect):
            return x, y


def reset_game():
    ex = random.randint(0, WIDTH - enemy_w)
    ey = -150

    enemy_rect = pygame.Rect(ex, ey, enemy_w, enemy_h)
    cx, cy = spawn_coin(enemy_rect)

    return {
        "player_x": WIDTH // 2 - player_w // 2,
        "player_y": HEIGHT - 150,
        "enemy_x": ex,
        "enemy_y": ey,
        "enemy_speed": 4,
        "coin_x": cx,
        "coin_y": cy,
        "score": 0,
        "coins": 0
    }


def update(state, keys, coin_sound, crash_sound):
    game_over = False

    # player movement
    if keys[pygame.K_LEFT] and state["player_x"] > 0:
        state["player_x"] -= player_speed

    if keys[pygame.K_RIGHT] and state["player_x"] < WIDTH - player_w:
        state["player_x"] += player_speed

    # enemy
    state["enemy_y"] += state["enemy_speed"]

    if state["enemy_y"] > HEIGHT:
        state["enemy_y"] = -150
        state["enemy_x"] = random.randint(0, WIDTH - enemy_w)
        state["score"] += 1
        state["enemy_speed"] += 0.15

    enemy_rect = pygame.Rect(state["enemy_x"], state["enemy_y"], enemy_w, enemy_h)

    # coin
    state["coin_y"] += coin_speed
    if state["coin_y"] > HEIGHT:
        state["coin_x"], state["coin_y"] = spawn_coin(enemy_rect)

    player_rect = pygame.Rect(state["player_x"], state["player_y"], player_w, player_h)
    coin_rect = pygame.Rect(state["coin_x"], state["coin_y"], coin_size, coin_size)

    # crash
    if player_rect.colliderect(enemy_rect):
        crash_sound.play()
        game_over = True

    # coin collect
    if player_rect.colliderect(coin_rect):
        state["coins"] += 1
        coin_sound.play()
        state["coin_x"], state["coin_y"] = spawn_coin(enemy_rect)

    return state, game_over


def draw(screen, state, assets, fonts, game_over):
    player_img, enemy_img, coin_img = assets
    font, big_font = fonts

    screen.fill(GREEN)

    pygame.draw.rect(screen, ROAD_GRAY, (80, 0, 200, HEIGHT))
    pygame.draw.line(screen, LINE_WHITE, (140, 0), (140, HEIGHT), 3)
    pygame.draw.line(screen, LINE_WHITE, (220, 0), (220, HEIGHT), 3)

    screen.blit(player_img, (state["player_x"], state["player_y"]))
    screen.blit(enemy_img, (state["enemy_x"], state["enemy_y"]))
    screen.blit(coin_img, (state["coin_x"], state["coin_y"]))

    screen.blit(font.render(f"Score: {state['score']}", True, BLACK), (10, 10))
    screen.blit(font.render(f"Coins: {state['coins']}", True, BLACK), (10, 40))

    if game_over:
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(120)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))

        screen.blit(big_font.render("GAME OVER", True, YELLOW), (70, 180))
        screen.blit(font.render("R = Restart", True, WHITE), (120, 380))
        screen.blit(font.render("Q = Quit", True, WHITE), (130, 420))