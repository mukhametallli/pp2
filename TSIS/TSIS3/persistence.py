# This file works with JSON files.
# JSON files save settings and leaderboard data.
import json
import os


# File with game settings.
SETTINGS_FILE = "settings.json"

# File with best scores.
LEADERBOARD_FILE = "leaderboard.json"


# Default settings. These are used if settings.json does not exist or is broken.
DEFAULT_SETTINGS = {
    "sound": True,
    "car_color": "blue",
    "difficulty": "normal"
}


def load_settings():
    """Load settings from settings.json."""

    # If the settings file does not exist, create it with default settings.
    if not os.path.exists(SETTINGS_FILE):
        save_settings(DEFAULT_SETTINGS)
        return DEFAULT_SETTINGS.copy()

    try:
        # Open settings.json and read data from it.
        with open(SETTINGS_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)

        # Start with default settings.
        settings = DEFAULT_SETTINGS.copy()

        # Add saved settings over default settings.
        settings.update(data)

        # Return ready settings.
        return settings

    except Exception:
        # If file has an error, reset settings to default.
        save_settings(DEFAULT_SETTINGS)
        return DEFAULT_SETTINGS.copy()


def save_settings(settings):
    """Save settings to settings.json."""

    # Open file in write mode and save settings as JSON.
    with open(SETTINGS_FILE, "w", encoding="utf-8") as file:
        json.dump(settings, file, indent=4)


def load_leaderboard():
    """Load scores from leaderboard.json."""

    # If leaderboard file does not exist, create an empty leaderboard.
    if not os.path.exists(LEADERBOARD_FILE):
        save_leaderboard([])
        return []

    try:
        # Open leaderboard.json and read data.
        with open(LEADERBOARD_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)

        # Leaderboard must be a list.
        if isinstance(data, list):
            return data

        # If data is not a list, return empty list.
        return []

    except Exception:
        # If file has an error, reset leaderboard.
        save_leaderboard([])
        return []


def save_leaderboard(scores):
    """Save scores to leaderboard.json."""

    # Save score list in JSON format.
    with open(LEADERBOARD_FILE, "w", encoding="utf-8") as file:
        json.dump(scores, file, indent=4)


def add_score(name, score, distance, coins):
    """Add a new score and keep only top 10 results."""

    # Load old scores.
    scores = load_leaderboard()

    # Add new result to the list.
    scores.append({
        "name": name,
        "score": int(score),
        "distance": int(distance),
        "coins": int(coins)
    })

    # Sort scores from biggest score to smallest score.
    scores.sort(key=lambda item: item["score"], reverse=True)

    # Save only the best 10 scores.
    save_leaderboard(scores[:10])
