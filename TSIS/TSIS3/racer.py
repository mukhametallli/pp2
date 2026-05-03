# This file has the main racer game logic.
# It controls the player car, traffic, obstacles, coins, power-ups, score, and road.

import random
from pathlib import Path

import pygame
from persistence import add_score

# Window size and FPS.
WIDTH = 500
HEIGHT = 700
FPS = 60
# Road position and road lanes.
ROAD_LEFT = 80
ROAD_RIGHT = 420
ROAD_WIDTH = ROAD_RIGHT - ROAD_LEFT
LANES = [120, 200, 280, 360]
FINISH_DISTANCE = 5000

# Colors in RGB format.
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
ROAD = (55, 55, 55)
GRASS = (40, 130, 60)
YELLOW = (235, 205, 60)
RED = (210, 50, 50)
BLUE = (60, 120, 230)
GREEN = (50, 190, 90)
ORANGE = (240, 140, 45)
PURPLE = (150, 90, 220)
GRAY = (120, 120, 120)
DARK = (25, 25, 25)
BROWN = (115, 70, 35)
CYAN = (70, 220, 230)

# Car color names. The settings file uses these names.
CAR_COLORS = {
    "blue": BLUE,
    "red": RED,
    "green": GREEN,
    "yellow": YELLOW,
    "purple": PURPLE
}

# Difficulty settings. Smaller traffic/obstacle numbers mean more objects appear.
DIFFICULTY = {
    "easy": {"speed": 4, "traffic": 95, "obstacle": 150},
    "normal": {"speed": 5, "traffic": 75, "obstacle": 120},
    "hard": {"speed": 6, "traffic": 55, "obstacle": 90}
}

# Sound files. Put racer.mp3 and crash.mp3 in the same folder as racer.py
# or inside an assets/ folder. The code checks both places.
BASE_DIR = Path(__file__).resolve().parent
MUSIC_PATHS = [BASE_DIR / "assets" / "racer.mp3", BASE_DIR / "racer.mp3"]
CRASH_PATHS = [BASE_DIR / "assets" / "crash.mp3", BASE_DIR / "crash.mp3"]


# This class stores the player's car.
class Player:
    def __init__(self, color_name):
        # Create the car rectangle: x, y, width, height.
        self.rect = pygame.Rect(WIDTH // 2 - 20, HEIGHT - 110, 40, 70)
        # Player movement speed.
        self.speed = 6
        self.color_name = color_name
        self.color = CAR_COLORS.get(color_name, BLUE)
        # Shield is False at the start.
        self.shield = False

    def update(self, keys):
        # Move the player when keyboard keys are pressed.
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.rect.x += self.speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.rect.y -= self.speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.rect.y += self.speed

        # Do not let the car leave the road and screen.
        self.rect.left = max(self.rect.left, ROAD_LEFT + 5)
        self.rect.right = min(self.rect.right, ROAD_RIGHT - 5)
        self.rect.top = max(self.rect.top, 80)
        self.rect.bottom = min(self.rect.bottom, HEIGHT - 15)

    def draw(self, screen):
        # Draw the player's car body.
        pygame.draw.rect(screen, self.color, self.rect, border_radius=8)
        pygame.draw.rect(screen, WHITE, (self.rect.x + 8, self.rect.y + 10, 24, 16), border_radius=4)
        pygame.draw.rect(screen, BLACK, (self.rect.x + 6, self.rect.y + 50, 8, 14))
        pygame.draw.rect(screen, BLACK, (self.rect.x + 26, self.rect.y + 50, 8, 14))
        # Draw blue shield circle if shield is active.
        if self.shield:
            pygame.draw.ellipse(screen, CYAN, self.rect.inflate(20, 20), 3)


# This class is for traffic cars and road obstacles.
class FallingObject:
    def __init__(self, kind, x, y, w, h, color, speed):
        # Object type: traffic, barrier, oil, pothole, bump, or nitro_strip.
        self.kind = kind
        self.rect = pygame.Rect(x, y, w, h)
        self.color = color
        self.speed = speed
        self.created = pygame.time.get_ticks()

    def update(self, extra_speed=0):
        # Move the object down.
        self.rect.y += self.speed + extra_speed

    def draw(self, screen):
        # Draw every object in its own style.
        if self.kind == "traffic":
            pygame.draw.rect(screen, self.color, self.rect, border_radius=8)
            pygame.draw.rect(screen, WHITE, (self.rect.x + 7, self.rect.y + 8, self.rect.w - 14, 14), border_radius=4)
        elif self.kind == "barrier":
            pygame.draw.rect(screen, ORANGE, self.rect, border_radius=5)
            pygame.draw.line(screen, WHITE, self.rect.topleft, self.rect.bottomright, 4)
        elif self.kind == "oil":
            pygame.draw.ellipse(screen, BLACK, self.rect)
            pygame.draw.ellipse(screen, DARK, self.rect.inflate(-8, -8))
        elif self.kind == "pothole":
            pygame.draw.ellipse(screen, BROWN, self.rect)
            pygame.draw.ellipse(screen, BLACK, self.rect.inflate(-8, -8), 2)
        elif self.kind == "bump":
            pygame.draw.rect(screen, YELLOW, self.rect, border_radius=5)
            pygame.draw.line(screen, BLACK, (self.rect.left, self.rect.centery), (self.rect.right, self.rect.centery), 3)
        elif self.kind == "nitro_strip":
            pygame.draw.rect(screen, CYAN, self.rect, border_radius=5)
            pygame.draw.polygon(screen, WHITE, [
                (self.rect.centerx - 8, self.rect.y + 8),
                (self.rect.centerx + 8, self.rect.centery),
                (self.rect.centerx - 8, self.rect.bottom - 8)
            ])
        else:
            pygame.draw.rect(screen, self.color, self.rect)


# This class is for coins and power-ups.
class Collectible:
    def __init__(self, kind, x, y, value=1):
        # Object type: traffic, barrier, oil, pothole, bump, or nitro_strip.
        self.kind = kind
        self.rect = pygame.Rect(x, y, 28, 28)
        self.value = value
        self.speed = 4
        self.created = pygame.time.get_ticks()
        # Item disappears after 6500 milliseconds.
        self.timeout = 6500

    def update(self, extra_speed=0):
        # Move the object down.
        self.rect.y += self.speed + extra_speed

    def expired(self):
        # Check if the item stayed too long on the screen.
        return pygame.time.get_ticks() - self.created > self.timeout

    def draw(self, screen):
        if self.kind == "coin":
            color = YELLOW if self.value == 1 else ORANGE if self.value == 2 else PURPLE
            pygame.draw.circle(screen, color, self.rect.center, 14)
            pygame.draw.circle(screen, WHITE, self.rect.center, 14, 2)
            small_font = pygame.font.SysFont(None, 20)
            label = small_font.render(str(self.value), True, BLACK)
            screen.blit(label, label.get_rect(center=self.rect.center))
        elif self.kind == "nitro":
            pygame.draw.rect(screen, CYAN, self.rect, border_radius=7)
            pygame.draw.polygon(screen, WHITE, [(self.rect.x + 9, self.rect.y + 5), (self.rect.x + 20, self.rect.y + 14), (self.rect.x + 9, self.rect.y + 23)])
        elif self.kind == "shield":
            pygame.draw.circle(screen, CYAN, self.rect.center, 14)
            pygame.draw.circle(screen, WHITE, self.rect.center, 10, 3)
        elif self.kind == "repair":
            pygame.draw.rect(screen, GREEN, self.rect, border_radius=7)
            pygame.draw.rect(screen, WHITE, (self.rect.centerx - 4, self.rect.y + 6, 8, 16))
            pygame.draw.rect(screen, WHITE, (self.rect.x + 6, self.rect.centery - 4, 16, 8))


# This class controls one full race.
class RacerGame:
    def __init__(self, screen, clock, username, settings):
        # Save screen, clock, name, and settings from main.py.
        self.screen = screen
        self.clock = clock
        self.username = username or "Player"
        self.settings = settings
        self.font = pygame.font.SysFont(None, 28)
        self.big_font = pygame.font.SysFont(None, 56)
        self.crash_sound = None

        # Prepare sound effects and background music.
        self.load_sounds()

        # Prepare all game variables.
        self.reset()

    def sound_enabled(self):
        # Return True if sound is turned on in settings.json.
        return self.settings.get("sound", True)

    def find_existing_file(self, paths):
        # Find the first sound file that really exists.
        for path in paths:
            if path.exists():
                return path
        return None

    def load_sounds(self):
        # Load crash sound. If file is missing, game still works without sound.
        if not self.sound_enabled():
            return

        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()

            crash_path = self.find_existing_file(CRASH_PATHS)
            if crash_path:
                self.crash_sound = pygame.mixer.Sound(str(crash_path))
                self.crash_sound.set_volume(0.8)

        except pygame.error:
            self.crash_sound = None

    def start_background_music(self):
        # Start racer.mp3 as background music during the race.
        if not self.sound_enabled():
            return

        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()

            music_path = self.find_existing_file(MUSIC_PATHS)
            if music_path:
                pygame.mixer.music.load(str(music_path))
                pygame.mixer.music.set_volume(0.35)
                pygame.mixer.music.play(-1)

        except pygame.error:
            pass

    def stop_background_music(self):
        # Stop music when the race ends.
        if pygame.mixer.get_init():
            pygame.mixer.music.stop()

    def play_crash_sound(self):
        # Play crash sound once when the player has a real crash.
        if self.sound_enabled() and self.crash_sound:
            self.crash_sound.play()

    def reset(self):
        # Start a new race and reset all variables.
        # Read selected difficulty from settings.
        difficulty = self.settings.get("difficulty", "normal")
        data = DIFFICULTY.get(difficulty, DIFFICULTY["normal"])
        self.base_speed = data["speed"]
        self.traffic_rate = data["traffic"]
        self.obstacle_rate = data["obstacle"]
        # Create player car with selected color.
        self.player = Player(self.settings.get("car_color", "blue"))
        # Lists store all moving objects on the road.
        self.traffic = []
        self.obstacles = []
        self.collectibles = []
        self.road_lines_y = 0
        # Score and progress values.
        self.distance = 0
        self.coins = 0
        self.score = 0
        # Current power-up information.
        self.active_power = None
        self.power_end_time = 0
        self.running = True
        self.game_over_reason = "Game Over"
        self.saved_score = False

    def safe_x(self):
        # Choose a safe x position for a new traffic car.
        for _ in range(20):
            x = random.choice(LANES) - 20
            spawn_rect = pygame.Rect(x, -90, 42, 75)
            if abs(spawn_rect.centerx - self.player.rect.centerx) > 55 or self.player.rect.y < HEIGHT - 220:
                return x
        return random.choice(LANES) - 20

    def spawn_traffic(self):
        # Randomly create traffic cars. More distance means more traffic.
        scaling = min(35, int(self.distance / 250))
        rate = max(22, self.traffic_rate - scaling)
        if random.randint(1, rate) == 1:
            x = self.safe_x()
            self.traffic.append(FallingObject("traffic", x, -90, 42, 75, random.choice([RED, BLUE, GREEN, PURPLE]), self.base_speed + 1))

    def spawn_obstacle(self):
        # Randomly create road obstacles. More distance means more obstacles.
        scaling = min(45, int(self.distance / 180))
        rate = max(25, self.obstacle_rate - scaling)
        if random.randint(1, rate) == 1:
            kind = random.choice(["barrier", "oil", "pothole", "bump", "nitro_strip"])
            x = random.choice(LANES) - 22
            size = (45, 30) if kind != "barrier" else (55, 28)
            self.obstacles.append(FallingObject(kind, x, -50, size[0], size[1], GRAY, self.base_speed))

    def spawn_collectible(self):
        # Randomly create coins and power-ups.
        if random.randint(1, 70) == 1:
            value = random.choices([1, 2, 5], weights=[70, 25, 5])[0]
            x = random.choice(LANES) - 14
            self.collectibles.append(Collectible("coin", x, -35, value))
        if random.randint(1, 360) == 1:
            kind = random.choice(["nitro", "shield", "repair"])
            x = random.choice(LANES) - 14
            self.collectibles.append(Collectible(kind, x, -35))

    def activate_power(self, kind):
        # Turn on nitro, shield, or repair.
        now = pygame.time.get_ticks()
        if kind == "nitro":
            self.active_power = "Nitro"
            self.power_end_time = now + 4000
        elif kind == "shield":
            self.active_power = "Shield"
            self.power_end_time = 0
            self.player.shield = True
        elif kind == "repair":
            self.active_power = "Repair"
            self.power_end_time = now + 800
            if self.obstacles:
                self.obstacles.pop(0)
            else:
                self.score += 100

    def update_power(self):
        # Turn off timed power-ups when their time is over.
        now = pygame.time.get_ticks()
        if self.active_power == "Nitro" and now > self.power_end_time:
            self.active_power = None
        if self.active_power == "Repair" and now > self.power_end_time:
            self.active_power = None

    def collision_hit(self):
        # Return True if collision should end the game.
        if self.player.shield:
            self.player.shield = False
            self.active_power = None
            return False
        return True

    def update(self):
        # Update all game logic once per frame.
        # Read pressed keys and move the player.
        keys = pygame.key.get_pressed()
        self.player.update(keys)
        self.update_power()

        # Nitro gives extra speed.
        extra_speed = 4 if self.active_power == "Nitro" else 0
        current_speed = self.base_speed + extra_speed + int(self.distance / 1200)
        self.road_lines_y = (self.road_lines_y + current_speed) % 45
        self.distance += current_speed / 10

        # Create new random objects.
        self.spawn_traffic()
        self.spawn_obstacle()
        self.spawn_collectible()

        # Move traffic cars and obstacles down.
        for obj in self.traffic + self.obstacles:
            obj.update(extra_speed // 2)
        for item in self.collectibles:
            item.update(extra_speed // 2)

        # Remove objects that left the screen.
        self.traffic = [obj for obj in self.traffic if obj.rect.top < HEIGHT + 100]
        self.obstacles = [obj for obj in self.obstacles if obj.rect.top < HEIGHT + 100]
        self.collectibles = [item for item in self.collectibles if item.rect.top < HEIGHT + 50 and not item.expired()]

        # Check collision with traffic cars.
        for car in self.traffic:
            if self.player.rect.colliderect(car.rect):
                if self.collision_hit():
                    self.play_crash_sound()
                    self.running = False
                    self.game_over_reason = "Crashed into traffic"
                else:
                    car.rect.y = HEIGHT + 200

        # Check collision with obstacles.
        for obstacle in self.obstacles:
            if self.player.rect.colliderect(obstacle.rect):
                if obstacle.kind in ["oil", "pothole", "bump"]:
                    self.player.rect.y += 18
                    if obstacle.kind == "oil":
                        self.player.rect.x += random.choice([-35, 35])
                    obstacle.rect.y = HEIGHT + 200
                elif obstacle.kind == "nitro_strip":
                    self.activate_power("nitro")
                    obstacle.rect.y = HEIGHT + 200
                else:
                    if self.collision_hit():
                        self.play_crash_sound()
                        self.running = False
                        self.game_over_reason = "Hit a barrier"
                    else:
                        obstacle.rect.y = HEIGHT + 200

        # Check if player collected coins or power-ups.
        for item in self.collectibles:
            if self.player.rect.colliderect(item.rect):
                if item.kind == "coin":
                    self.coins += item.value
                    self.score += item.value * 50
                else:
                    if self.active_power is None or self.active_power == "Repair":
                        self.activate_power(item.kind)
                item.rect.y = HEIGHT + 200

        # Calculate score from coins and distance.
        self.score = int(self.coins * 50 + self.distance * 2)
        if self.active_power == "Nitro":
            self.score += 1

        # End race if finish distance is reached.
        if self.distance >= FINISH_DISTANCE:
            self.running = False
            self.game_over_reason = "Finish reached!"

    def draw_road(self):
        # Draw grass, road, borders, and lane lines.
        self.screen.fill(GRASS)
        pygame.draw.rect(self.screen, ROAD, (ROAD_LEFT, 0, ROAD_WIDTH, HEIGHT))
        pygame.draw.line(self.screen, WHITE, (ROAD_LEFT, 0), (ROAD_LEFT, HEIGHT), 4)
        pygame.draw.line(self.screen, WHITE, (ROAD_RIGHT, 0), (ROAD_RIGHT, HEIGHT), 4)
        for lane_x in [160, 240, 320]:
            for y in range(-45, HEIGHT, 45):
                pygame.draw.rect(self.screen, WHITE, (lane_x, y + self.road_lines_y, 6, 25))

    def draw_hud(self):
        # Draw name, score, coins, distance, and power-up text.
        remaining = max(0, FINISH_DISTANCE - int(self.distance))
        lines = [
            f"Name: {self.username}",
            f"Score: {int(self.score)}",
            f"Coins: {self.coins}",
            f"Distance: {int(self.distance)} m",
            f"Remaining: {remaining} m"
        ]
        for i, text in enumerate(lines):
            image = self.font.render(text, True, WHITE)
            self.screen.blit(image, (10, 10 + i * 24))

        if self.active_power:
            if self.active_power == "Nitro":
                time_left = max(0, (self.power_end_time - pygame.time.get_ticks()) // 1000)
                power_text = f"Power: Nitro {time_left}s"
            elif self.active_power == "Shield":
                power_text = "Power: Shield"
            else:
                power_text = "Power: Repair"
            image = self.font.render(power_text, True, CYAN)
            self.screen.blit(image, (285, 10))

    def draw(self):
        # Draw everything on the screen.
        self.draw_road()
        for obj in self.obstacles:
            obj.draw(self.screen)
        for car in self.traffic:
            car.draw(self.screen)
        for item in self.collectibles:
            item.draw(self.screen)
        self.player.draw(self.screen)
        self.draw_hud()

    def save_score_once(self):
        # Save score only one time to avoid duplicates.
        if not self.saved_score:
            add_score(self.username, self.score, self.distance, self.coins)
            self.saved_score = True

    def run(self):
        # Main game loop. It runs until the race ends.
        self.start_background_music()

        try:
            while self.running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.stop_background_music()
                        pygame.quit()
                        raise SystemExit
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                        self.running = False
                        self.game_over_reason = "Stopped"
                self.update()
                self.draw()
                pygame.display.flip()
                self.clock.tick(FPS)
        finally:
            self.stop_background_music()

        self.save_score_once()
        return {
            "reason": self.game_over_reason,
            "score": int(self.score),
            "distance": int(self.distance),
            "coins": int(self.coins)
        }
