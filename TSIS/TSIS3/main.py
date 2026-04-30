# Import the Pygame library. We use it to make the game window and draw objects.
import pygame

# Import the main game class and important game constants from racer.py.
from racer import RacerGame, WIDTH, HEIGHT, FPS, CAR_COLORS

# Import functions for saving and loading data from JSON files.
from persistence import load_settings, save_settings, load_leaderboard

# Import ready UI tools and colors from ui.py.
from ui import Button, draw_text, draw_panel, WHITE, BLACK, GRAY, BLUE, GREEN, RED, YELLOW


# Start all Pygame modules.
pygame.init()

# Set the title of the game window.
pygame.display.set_caption("TSIS3 Racer Game")

# Create the game screen with width and height from racer.py.
screen = pygame.display.set_mode((WIDTH, HEIGHT))

# Clock controls the FPS. It helps the game run smoothly.
clock = pygame.time.Clock()


# Create fonts for normal text, big text, and small text.
FONT = pygame.font.SysFont(None, 32)
BIG_FONT = pygame.font.SysFont(None, 60)
SMALL_FONT = pygame.font.SysFont(None, 24)


# Load saved settings from settings.json.
settings = load_settings()

# Default player name.
username = "Player"


def ask_username():
    """Ask the player to type a name before the race starts."""
    global username

    # This variable stores the text typed by the player.
    text = ""

    # This loop works while the name screen is open.
    active = True
    while active:
        # Fill background with dark color.
        screen.fill((30, 30, 30))

        # Draw title text.
        draw_text(screen, "Enter your name", BIG_FONT, WHITE, center=(WIDTH // 2, 180))

        # Draw input box.
        pygame.draw.rect(screen, WHITE, (100, 280, 300, 50), 2, border_radius=8)

        # Show typed name. If empty, show Player.
        draw_text(screen, text or "Player", FONT, WHITE, center=(WIDTH // 2, 305))

        # Show instruction.
        draw_text(screen, "Press Enter to start", SMALL_FONT, YELLOW, center=(WIDTH // 2, 370))

        # Check all user actions: closing window and keyboard typing.
        for event in pygame.event.get():
            # If player closes the window, stop the program.
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit

            # If a keyboard key is pressed.
            if event.type == pygame.KEYDOWN:
                # Enter saves the name and closes this screen.
                if event.key == pygame.K_RETURN:
                    username = text.strip() or "Player"
                    active = False

                # Backspace deletes the last letter.
                elif event.key == pygame.K_BACKSPACE:
                    text = text[:-1]

                # Add typed character if name is shorter than 12 symbols.
                elif len(text) < 12 and event.unicode.isprintable():
                    text += event.unicode

        # Update the screen.
        pygame.display.flip()

        # Keep the game at selected FPS.
        clock.tick(FPS)


def main_menu():
    """Show the main menu with buttons."""

    # Create menu buttons.
    buttons = [
        Button((150, 230, 200, 55), "Play", FONT, GREEN),
        Button((150, 300, 200, 55), "Leaderboard", FONT, BLUE),
        Button((150, 370, 200, 55), "Settings", FONT, GRAY),
        Button((150, 440, 200, 55), "Quit", FONT, RED)
    ]

    # Menu loop. It works until player quits or starts another screen.
    while True:
        # Draw background.
        screen.fill((25, 25, 35))

        # Draw game title and subtitle.
        draw_text(screen, "TSIS 3 RACER", BIG_FONT, WHITE, center=(WIDTH // 2, 120))
        draw_text(screen, "Advanced Driving, Power-Ups & Leaderboard", SMALL_FONT, YELLOW, center=(WIDTH // 2, 165))

        # Draw every button.
        for button in buttons:
            button.draw(screen)

        # Check player actions.
        for event in pygame.event.get():
            # Close program if the window is closed.
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit

            # Play button: ask name, start race, then show game over screen.
            if buttons[0].clicked(event):
                ask_username()
                result = RacerGame(screen, clock, username, settings).run()
                game_over_screen(result)

            # Leaderboard button: open leaderboard screen.
            if buttons[1].clicked(event):
                leaderboard_screen()

            # Settings button: open settings screen.
            if buttons[2].clicked(event):
                settings_screen()

            # Quit button: close the game.
            if buttons[3].clicked(event):
                pygame.quit()
                raise SystemExit

        # Update the screen and control FPS.
        pygame.display.flip()
        clock.tick(FPS)


def leaderboard_screen():
    """Show the best 10 scores from leaderboard.json."""

    # Create Back button.
    back = Button((165, 615, 170, 50), "Back", FONT, GRAY)

    # Leaderboard screen loop.
    while True:
        screen.fill((22, 22, 30))
        draw_text(screen, "Top 10 Leaderboard", BIG_FONT, WHITE, center=(WIDTH // 2, 70))

        # Load scores from JSON file.
        scores = load_leaderboard()

        # Draw a panel for the table.
        draw_panel(screen, pygame.Rect(45, 125, 410, 460))

        # Draw table header.
        headers = "Rank   Name        Score     Distance"
        draw_text(screen, headers, SMALL_FONT, YELLOW, topleft=(70, 150))

        # Draw each saved score. Only top 10 are shown.
        for i, item in enumerate(scores[:10], start=1):
            row = f"{i:<5} {item['name'][:10]:<10} {item['score']:<8} {item['distance']}m"
            draw_text(screen, row, SMALL_FONT, WHITE, topleft=(70, 180 + i * 34))

        # If there are no scores, show this message.
        if not scores:
            draw_text(screen, "No scores yet", FONT, WHITE, center=(WIDTH // 2, 350))

        # Draw Back button.
        back.draw(screen)

        # Check events.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit

            # Go back to menu if Back is clicked or Escape is pressed.
            if back.clicked(event) or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                return

        pygame.display.flip()
        clock.tick(FPS)


def settings_screen():
    """Show settings and allow the player to change them."""
    global settings

    # Create setting buttons.
    sound_button = Button((120, 170, 260, 50), "", FONT, BLUE)
    difficulty_button = Button((120, 245, 260, 50), "", FONT, GREEN)
    color_button = Button((120, 320, 260, 50), "", FONT, GRAY)
    back = Button((165, 610, 170, 50), "Save & Back", FONT, RED)

    # Possible difficulty values.
    difficulties = ["easy", "normal", "hard"]

    # Possible car colors from racer.py.
    colors = list(CAR_COLORS.keys())

    # Settings screen loop.
    while True:
        screen.fill((28, 28, 36))
        draw_text(screen, "Settings", BIG_FONT, WHITE, center=(WIDTH // 2, 80))

        # Update button text from current settings.
        sound_button.text = f"Sound: {'ON' if settings['sound'] else 'OFF'}"
        difficulty_button.text = f"Difficulty: {settings['difficulty']}"
        color_button.text = f"Car color: {settings['car_color']}"

        # Draw buttons.
        sound_button.draw(screen)
        difficulty_button.draw(screen)
        color_button.draw(screen)
        back.draw(screen)

        # Draw instructions.
        draw_text(screen, "Click buttons to change options", SMALL_FONT, YELLOW, center=(WIDTH // 2, 410))
        draw_text(screen, "Settings are saved to settings.json", SMALL_FONT, WHITE, center=(WIDTH // 2, 445))

        # Check events.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit

            # Turn sound on or off.
            if sound_button.clicked(event):
                settings["sound"] = not settings["sound"]

            # Change difficulty to the next option.
            if difficulty_button.clicked(event):
                index = difficulties.index(settings["difficulty"])
                settings["difficulty"] = difficulties[(index + 1) % len(difficulties)]

            # Change car color to the next option.
            if color_button.clicked(event):
                index = colors.index(settings["car_color"])
                settings["car_color"] = colors[(index + 1) % len(colors)]

            # Save settings and go back.
            if back.clicked(event) or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                save_settings(settings)
                return

        pygame.display.flip()
        clock.tick(FPS)


def game_over_screen(result):
    """Show final result after the race."""

    # Create Retry and Main Menu buttons.
    retry = Button((90, 520, 140, 55), "Retry", FONT, GREEN)
    menu = Button((270, 520, 140, 55), "Main Menu", FONT, BLUE)

    # Game over screen loop.
    while True:
        screen.fill((35, 25, 25))

        # Show the reason why the race ended.
        draw_text(screen, result["reason"], BIG_FONT, WHITE, center=(WIDTH // 2, 130))

        # Draw result panel.
        draw_panel(screen, pygame.Rect(85, 210, 330, 230))

        # Show score, distance, and coins.
        draw_text(screen, f"Score: {result['score']}", FONT, WHITE, center=(WIDTH // 2, 250))
        draw_text(screen, f"Distance: {result['distance']} m", FONT, WHITE, center=(WIDTH // 2, 305))
        draw_text(screen, f"Coins: {result['coins']}", FONT, WHITE, center=(WIDTH // 2, 360))

        # Draw buttons.
        retry.draw(screen)
        menu.draw(screen)

        # Check events.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit

            # Retry starts a new game.
            if retry.clicked(event):
                ask_username()
                new_result = RacerGame(screen, clock, username, settings).run()
                result.update(new_result)

            # Main Menu returns to menu.
            if menu.clicked(event):
                return

        pygame.display.flip()
        clock.tick(FPS)


# This starts the program only when we run main.py directly.
if __name__ == "__main__":
    main_menu()
