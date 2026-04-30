# TSIS 3: Racer Game

Advanced Pygame racer with traffic, obstacles, power-ups, settings and leaderboard.

## Run

```bash
python3 main.py
```

If Pygame is missing:

```bash
python3 -m pip install pygame
```

## Controls

- Arrow keys or WASD — move car
- Escape — stop current race / go back from some screens
- Mouse — press menu buttons

## Implemented features

- Lane hazards and safe path decisions
- Dynamic traffic cars
- Random road obstacles: barriers, oil, potholes, speed bumps
- Dynamic road event: nitro strip
- Safe spawn logic away from player
- Difficulty scaling by distance
- Collectible power-ups: Nitro, Shield, Repair
- Only one active power-up at a time
- Power-up timeout for uncollected items
- Score from distance and coins
- Distance meter and remaining distance
- Username entry before game
- Local top 10 leaderboard in `leaderboard.json`
- Main Menu, Leaderboard, Settings, Game Over screens
- Settings saved in `settings.json`

## Suggested Git commands

```bash
git add TSIS3
git commit -m "Add TSIS3 advanced racer game"
git push
```
