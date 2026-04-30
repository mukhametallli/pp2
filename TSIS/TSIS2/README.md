# TSIS 2: Paint Application — Extended Drawing Tools

## Features

- Pencil/freehand drawing
- Straight line with live preview
- Brush sizes: 2 px, 5 px, 10 px
- Rectangle, circle, square, right triangle, equilateral triangle, rhombus
- Eraser
- Color picker
- Flood-fill tool
- Text tool
- Save canvas with `Ctrl+S` or `Cmd+S`

## Controls

- Click toolbar buttons to choose a tool.
- Press `1`, `2`, `3` to change brush size.
- Use `Ctrl+S` / `Cmd+S` to save the canvas.
- Text tool:
  - Click canvas to place text.
  - Type text.
  - Press `Enter` to confirm.
  - Press `Escape` to cancel.

## Run

```bash
pip install pygame
python3 paint.py
```

## GitHub structure

```text
TSIS2/
├── paint.py
├── tools.py
├── README.md
└── assets/
```
