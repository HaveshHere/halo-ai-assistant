import json
import os
from pathlib import Path


DEFAULT_MODEL = "qwen3"
DEFAULT_OLLAMA_TIMEOUT = 300
HALO_VERSION = "0.1.0"
UI_PREFERENCES = {
    "theme": ("Dark", "Light"),
    "accent": ("Halo Green", "Blue", "Purple"),
    "response_style": ("Concise", "Balanced", "Detailed"),
    "default_page": ("Dashboard", "Tasks", "Briefing"),
    "show_completed": (True, False),
}
UI_DEFAULTS = {
    "theme": "Dark",
    "accent": "Halo Green",
    "response_style": "Balanced",
    "default_page": "Dashboard",
    "show_completed": True,
}


def preferences_path():
    return Path(os.getenv("APPDATA", Path.home())) / "Halo" / "preferences.json"


def validate_ui_preferences(preferences):
    valid = {}
    for key, default in UI_DEFAULTS.items():
        value = preferences.get(key)
        valid[key] = value if type(value) is type(default) and value in UI_PREFERENCES[key] else default
    return valid


def load_ui_preferences():
    try:
        saved = json.loads(preferences_path().read_text(encoding="utf-8"))
    except (OSError, ValueError):
        saved = {}
    if not isinstance(saved, dict):
        saved = {}
    return validate_ui_preferences(saved)


def save_ui_preferences(preferences):
    path = preferences_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    valid = validate_ui_preferences(preferences)
    path.write_text(json.dumps(valid, indent=2), encoding="utf-8")
    return valid


def get_recommended_model():
    return os.getenv("AI_MODEL", DEFAULT_MODEL)


def get_ai_provider():
    return os.getenv("AI_PROVIDER", "ollama")


def get_ollama_base_url():
    return os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")


def get_ollama_timeout():
    try:
        timeout = float(os.getenv("OLLAMA_TIMEOUT", str(DEFAULT_OLLAMA_TIMEOUT)))
    except ValueError:
        return DEFAULT_OLLAMA_TIMEOUT

    return timeout if timeout > 0 else DEFAULT_OLLAMA_TIMEOUT
