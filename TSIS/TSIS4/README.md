# TSIS 4: Snake Game — Database Integration & Advanced Gameplay

## Features

- PostgreSQL tables: `players`, `game_sessions`
- Username entry in Pygame
- Auto-save game result after Game Over
- Top 10 leaderboard from PostgreSQL
- Personal best display during gameplay
- Weighted disappearing food
- Poison food that shortens the snake by 2 segments
- Power-ups: speed boost, slow motion, shield
- Obstacles starting from Level 3
- Settings saved in `settings.json`: snake color, grid, sound
- Background music: `assets/snake.mp3`
- Screens: Main Menu, Game Over, Leaderboard, Settings

## Files

```text
TSIS4/
├── main.py
├── game.py
├── db.py
├── config.py
├── settings.json
├── README.md
└── assets/
    └── snake.mp3
```

## Installation

```bash
pip install pygame psycopg2-binary
```

## PostgreSQL setup

Open `config.py` and change these values if your PostgreSQL user/password are different:

```python
DB_NAME = "snake_db"
DB_USER = "postgres"
DB_PASSWORD = "postgres"
DB_HOST = "localhost"
DB_PORT = "5432"
```

The program automatically creates the database tables:

```sql
CREATE TABLE players (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL
);

CREATE TABLE game_sessions (
    id SERIAL PRIMARY KEY,
    player_id INTEGER REFERENCES players(id),
    score INTEGER NOT NULL,
    level_reached INTEGER NOT NULL,
    played_at TIMESTAMP DEFAULT NOW()
);
```

## Run

```bash
python3 main.py
```

## Controls

- Arrow keys — move snake
- Escape — return to menu during gameplay
- Mouse — menu/settings buttons
- Settings → Sound ON/OFF — background snake music

## GitHub commands

```bash
git add TSIS4
git commit -m "Add TSIS4 Snake with PostgreSQL leaderboard and power-ups"
git push
```
