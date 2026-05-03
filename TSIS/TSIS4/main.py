# This is the main file of the Snake game.
# Run this file to start the game.
# It controls menus, screens, buttons, and the main game loop.

import sys
import os
import pygame
from config import *
from db import init_db, save_result, get_top_scores, get_personal_best
from game import SnakeGame, load_settings, save_settings

# Start Pygame.
pygame.init()

# Start mixer for background music.
# If sound cannot be loaded, the game still works.
try:
    pygame.mixer.init()
except pygame.error as e:
    print("Sound warning:", e)

# Background music file.
MUSIC_FILE = os.path.join("assets", "snake.mp3")


def start_background_music():
    # Start snake background music if Sound is ON in settings.
    if not settings.get("sound", False):
        pygame.mixer.music.stop()
        return

    try:
        if os.path.exists(MUSIC_FILE) and not pygame.mixer.music.get_busy():
            pygame.mixer.music.load(MUSIC_FILE)
            pygame.mixer.music.set_volume(0.35)
            pygame.mixer.music.play(-1)  # -1 means repeat forever.
    except pygame.error as e:
        print("Music warning:", e)


def stop_background_music():
    # Stop background music.
    try:
        pygame.mixer.music.stop()
    except pygame.error:
        pass


# Create the game window.
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("TSIS4 Snake — PostgreSQL Edition")

# Clock controls FPS.
clock = pygame.time.Clock()

# Fonts for big and small text.
font = pygame.font.SysFont("arial", 32)
small_font = pygame.font.SysFont("arial", 20)

# Load settings from settings.json.
settings = load_settings()
start_background_music()

# Default player name.
username = "Player"

# This variable helps save result only one time after Game Over.
last_result_saved = False


def draw_button(text, rect, mouse):
    # Draw one button.
    # If mouse is on the button, make it lighter.
    color = (70, 70, 90) if rect.collidepoint(mouse) else PANEL

    # Draw button rectangle and border.
    pygame.draw.rect(screen, color, rect, border_radius=10)
    pygame.draw.rect(screen, WHITE, rect, 2, border_radius=10)

    # Draw text in the center of the button.
    label = small_font.render(text, True, WHITE)
    screen.blit(label, label.get_rect(center=rect.center))

    # Return rect so we can check mouse clicks later.
    return rect


def text_center(text, y, fnt=font, color=WHITE):
    # Draw text in the center of the screen.
    img = fnt.render(text, True, color)
    screen.blit(img, img.get_rect(center=(WIDTH // 2, y)))


def username_input():
    # This screen lets the player type their username.
    global username
    active = True
    name = username

    while active:
        mouse = pygame.mouse.get_pos()
        screen.fill(BG)

        # Draw title.
        text_center("Enter username", 150)

        # Draw input box.
        box = pygame.Rect(250, 230, 300, 48)
        pygame.draw.rect(screen, PANEL, box, border_radius=8)
        pygame.draw.rect(screen, WHITE, box, 2, border_radius=8)
        screen.blit(font.render(name, True, WHITE), (box.x + 12, box.y + 8))

        # Draw Start button.
        start_btn = draw_button("Start", pygame.Rect(320, 320, 160, 45), mouse)
        text_center("Type your name and press Enter", 410, small_font, GRAY)

        pygame.display.flip()

        # Read user actions.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # Keyboard input.
            if event.type == pygame.KEYDOWN:
                # Enter saves the name.
                if event.key == pygame.K_RETURN and name.strip():
                    username = name.strip()[:50]
                    return
                # Backspace deletes one letter.
                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                # Add typed character to the name.
                elif len(name) < 50 and event.unicode.isprintable():
                    name += event.unicode

            # Mouse click on Start button also saves the name.
            if event.type == pygame.MOUSEBUTTONDOWN and start_btn.collidepoint(event.pos) and name.strip():
                username = name.strip()[:50]
                return

        clock.tick(30)


def main_menu():
    # Main menu screen.
    global username

    while True:
        mouse = pygame.mouse.get_pos()
        screen.fill(BG)

        # Draw menu title and current username.
        text_center("TSIS4 Snake", 90)
        text_center(f"Username: {username}", 140, small_font, YELLOW)

        # Draw all menu buttons.
        buttons = {
            "play": draw_button("Play", pygame.Rect(300, 200, 200, 45), mouse),
            "leaderboard": draw_button("Leaderboard", pygame.Rect(300, 260, 200, 45), mouse),
            "settings": draw_button("Settings", pygame.Rect(300, 320, 200, 45), mouse),
            "quit": draw_button("Quit", pygame.Rect(300, 380, 200, 45), mouse),
        }

        text_center("Click username line to change name", 470, small_font, GRAY)
        pygame.display.flip()

        # Check clicks and close button.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                # Play opens username input first, then starts game.
                if buttons["play"].collidepoint(event.pos):
                    username_input()
                    return "play"

                # Open leaderboard screen.
                if buttons["leaderboard"].collidepoint(event.pos):
                    return "leaderboard"

                # Open settings screen.
                if buttons["settings"].collidepoint(event.pos):
                    return "settings"

                # Quit the program.
                if buttons["quit"].collidepoint(event.pos):
                    pygame.quit()
                    sys.exit()

                # Click on username text to change name.
                if 110 <= event.pos[1] <= 160:
                    username_input()

        clock.tick(30)


def leaderboard_screen():
    # Leaderboard screen shows top 10 scores from PostgreSQL.
    try:
        rows = get_top_scores()
    except Exception as e:
        # If database has an error, show a short error message instead of crashing.
        rows = [("DB error", 0, 0, str(e)[:16])]

    while True:
        mouse = pygame.mouse.get_pos()
        screen.fill(BG)

        text_center("Top 10 Leaderboard", 60)

        # Draw table headers.
        headers = ["#", "Name", "Score", "Level", "Date"]
        xs = [70, 130, 330, 440, 530]
        for x, h in zip(xs, headers):
            screen.blit(small_font.render(h, True, YELLOW), (x, 110))

        # Draw every score row.
        for i, row in enumerate(rows, 1):
            y = 110 + i * 35
            values = [str(i), str(row[0]), str(row[1]), str(row[2]), str(row[3])]
            for x, v in zip(xs, values):
                screen.blit(small_font.render(v[:18], True, WHITE), (x, y))

        # Back button returns to main menu.
        back = draw_button("Back", pygame.Rect(320, 520, 160, 45), mouse)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and back.collidepoint(event.pos):
                return

        clock.tick(30)


def settings_screen():
    # Settings screen changes grid, sound, and snake color.
    global settings

    # Available snake colors.
    colors = [[70, 210, 90], [70, 140, 255], [240, 210, 70], [170, 90, 255]]

    while True:
        mouse = pygame.mouse.get_pos()
        screen.fill(BG)

        text_center("Settings", 70)

        # Buttons for grid and sound.
        grid_btn = draw_button(f"Grid: {'ON' if settings['grid'] else 'OFF'}", pygame.Rect(290, 150, 220, 45), mouse)
        sound_btn = draw_button(f"Sound: {'ON' if settings['sound'] else 'OFF'}", pygame.Rect(290, 210, 220, 45), mouse)

        # Draw snake color choices.
        text_center("Snake color", 305, small_font, WHITE)
        color_rects = []
        for i, c in enumerate(colors):
            r = pygame.Rect(260 + i * 70, 335, 45, 45)
            pygame.draw.rect(screen, tuple(c), r, border_radius=6)

            # Selected color has a thicker border.
            pygame.draw.rect(screen, WHITE, r, 3 if settings["snake_color"] == c else 1, border_radius=6)
            color_rects.append((r, c))

        # Save button.
        save_back = draw_button("Save & Back", pygame.Rect(300, 440, 200, 45), mouse)
        pygame.display.flip()

        # Read clicks.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                # Turn grid ON or OFF.
                if grid_btn.collidepoint(event.pos):
                    settings["grid"] = not settings["grid"]

                # Turn sound ON or OFF.
                # When Sound is ON, snake.mp3 plays in the background.
                elif sound_btn.collidepoint(event.pos):
                    settings["sound"] = not settings["sound"]
                    save_settings(settings)
                    if settings["sound"]:
                        start_background_music()
                    else:
                        stop_background_music()

                # Save settings and go back.
                elif save_back.collidepoint(event.pos):
                    save_settings(settings)
                    return

                # Change snake color.
                for rect, color in color_rects:
                    if rect.collidepoint(event.pos):
                        settings["snake_color"] = color

        clock.tick(30)


def game_over_screen(game):
    # This screen appears after player loses.
    global last_result_saved

    # Save result only once.
    if not last_result_saved:
        try:
            save_result(game.username, game.score, game.level)
        except Exception:
            # If database error happens, do not crash the game.
            pass
        last_result_saved = True

    # New best score is old best or current score.
    best = max(game.personal_best, game.score)

    while True:
        mouse = pygame.mouse.get_pos()
        screen.fill(BG)

        # Draw game over information.
        text_center("Game Over", 100, font, RED)
        text_center(f"Score: {game.score}", 180, small_font)
        text_center(f"Level reached: {game.level}", 215, small_font)
        text_center(f"Personal best: {best}", 250, small_font, YELLOW)

        # Buttons after game over.
        retry = draw_button("Retry", pygame.Rect(300, 330, 200, 45), mouse)
        menu = draw_button("Main Menu", pygame.Rect(300, 390, 200, 45), mouse)
        pygame.display.flip()

        # Check button clicks.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if retry.collidepoint(event.pos):
                    return "retry"
                if menu.collidepoint(event.pos):
                    return "menu"

        clock.tick(30)


def run_game():
    # This function runs the actual snake game.
    global last_result_saved
    last_result_saved = False

    # Make sure background music is playing if Sound is ON.
    start_background_music()

    # Get player's personal best from database.
    try:
        best = get_personal_best(username)
    except Exception:
        best = 0

    # Create a new SnakeGame object.
    game = SnakeGame(username, best, settings)

    # Create a custom timer event for snake movement.
    move_event = pygame.USEREVENT + 1
    pygame.time.set_timer(move_event, int(1000 / game.current_fps()))

    while True:
        # Read all events.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # Keyboard controls.
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    game.set_direction(0, -1)
                elif event.key == pygame.K_DOWN:
                    game.set_direction(0, 1)
                elif event.key == pygame.K_LEFT:
                    game.set_direction(-1, 0)
                elif event.key == pygame.K_RIGHT:
                    game.set_direction(1, 0)
                elif event.key == pygame.K_ESCAPE:
                    return "menu"

            # Move snake when timer event happens.
            if event.type == move_event and not game.game_over:
                game.update()

                # Update timer because speed can change by level or power-up.
                pygame.time.set_timer(move_event, int(1000 / game.current_fps()))

        # Draw the game every frame.
        game.draw(screen, font, small_font)
        pygame.display.flip()

        # If game is over, show Game Over screen.
        if game.game_over:
            choice = game_over_screen(game)

            # Start new game if player clicks Retry.
            if choice == "retry":
                last_result_saved = False
                game = SnakeGame(username, max(best, game.score), settings)
            else:
                return "menu"

        clock.tick(60)


def main():
    # Prepare database when the program starts.
    try:
        init_db()
    except Exception as e:
        # If database has a problem, show warning in terminal.
        # The game can still open, but leaderboard may not work.
        print("Database warning:", e)

    # Main program loop.
    while True:
        state = main_menu()

        # Open screen based on menu choice.
        if state == "play":
            run_game()
        elif state == "leaderboard":
            leaderboard_screen()
        elif state == "settings":
            settings_screen()


# Start the program only when this file is run directly.
if __name__ == "__main__":
    main()
