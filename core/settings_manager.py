"""Default shortcuts and settings management for AutoHotkey Manager."""
import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_DIR = os.path.join(BASE_DIR, "config")
SETTINGS_PATH = os.path.join(CONFIG_DIR, "settings.json")

DEFAULT_SHORTCUTS = {
    "run": "Ctrl+R",
    "stop": "Ctrl+T",
    "restart": "Ctrl+Shift+R",
    "save": "Ctrl+S",
    "edit_focus": "Ctrl+E",
    "new_category": "Ctrl+Shift+N",
    "new_file": "Ctrl+N",
    "import_file": "Ctrl+I",
    "delete_selected": "Delete",
    "rename_selected": "F2",
    "toggle_left_panel": "Ctrl+B",
    "toggle_toolbar": "Ctrl+Shift+T",
    "open_settings": "Ctrl+,",
    "quit": "Ctrl+Q",
}

DEFAULT_SETTINGS = {
    "shortcuts": dict(DEFAULT_SHORTCUTS),
    "toolbar_visible": True,
    "left_panel_visible": True,
    "left_panel_width": 280,
    "window_geometry": None,
}


def _ensure_dir():
    os.makedirs(CONFIG_DIR, exist_ok=True)


def load_settings() -> dict:
    _ensure_dir()
    if not os.path.exists(SETTINGS_PATH):
        save_settings(DEFAULT_SETTINGS)
        return dict(DEFAULT_SETTINGS)
    try:
        with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, IOError):
        data = dict(DEFAULT_SETTINGS)
        save_settings(data)
        return data
    # merge defaults for missing keys
    merged = dict(DEFAULT_SETTINGS)
    merged.update(data or {})
    if "shortcuts" not in merged or not isinstance(merged["shortcuts"], dict):
        merged["shortcuts"] = dict(DEFAULT_SHORTCUTS)
    else:
        sc = dict(DEFAULT_SHORTCUTS)
        sc.update(merged["shortcuts"])
        merged["shortcuts"] = sc
    return merged


def save_settings(data: dict) -> None:
    _ensure_dir()
    with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def reset_shortcuts() -> dict:
    s = load_settings()
    s["shortcuts"] = dict(DEFAULT_SHORTCUTS)
    save_settings(s)
    return s