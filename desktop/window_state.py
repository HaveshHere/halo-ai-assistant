"""Persist and restore the desktop window's geometry between launches.

Kept deliberately separate from the Streamlit UI: this only remembers the
size and position of the native host window, never anything about Halo's pages.
"""

import json
import os
from pathlib import Path

DEFAULT_WIDTH = 1440
DEFAULT_HEIGHT = 900
MIN_WIDTH = 1100
MIN_HEIGHT = 700


def state_file_path():
    appdata = os.getenv("APPDATA")
    base = Path(appdata) if appdata else Path.home()
    return base / "Halo" / "window_state.json"


def load_state():
    path = state_file_path()

    if not path.exists():
        return {"width": DEFAULT_WIDTH, "height": DEFAULT_HEIGHT, "x": None, "y": None, "maximized": False}

    try:
        data = json.loads(path.read_text())
    except (json.JSONDecodeError, OSError):
        return {"width": DEFAULT_WIDTH, "height": DEFAULT_HEIGHT, "x": None, "y": None, "maximized": False}

    width = data.get("width", DEFAULT_WIDTH)
    height = data.get("height", DEFAULT_HEIGHT)

    if not isinstance(width, int) or width < MIN_WIDTH:
        width = DEFAULT_WIDTH
    if not isinstance(height, int) or height < MIN_HEIGHT:
        height = DEFAULT_HEIGHT

    x = data.get("x")
    y = data.get("y")
    if not isinstance(x, int):
        x = None
    if not isinstance(y, int):
        y = None

    return {"width": width, "height": height, "x": x, "y": y, "maximized": bool(data.get("maximized", False))}


def clamp_state_to_bounds(state, max_width, max_height, work_left=0, work_top=0):
    width = min(state["width"], max_width)
    height = min(state["height"], max_height)
    max_x = work_left + max_width - width
    max_y = work_top + max_height - height
    x = state.get("x")
    y = state.get("y")

    if isinstance(x, int):
        x = min(max(x, work_left), max_x)
    if isinstance(y, int):
        y = min(max(y, work_top), max_y)

    return {
        "width": width,
        "height": height,
        "x": x,
        "y": y,
        "maximized": state["maximized"],
    }


def save_state(width, height, maximized=False, x=None, y=None):
    path = state_file_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"width": width, "height": height, "x": x, "y": y, "maximized": maximized}))
