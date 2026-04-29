import json
import os
from typing import Dict, List

SETTINGS_FILE = "settings.json"
LEADERBOARD_FILE = "leaderboard.json"

DEFAULT_SETTINGS = {
    "sound": True,
    "difficulty": "normal",
}

DEFAULT_LEADERBOARD = []


def load_json(filename: str, default):
    if not os.path.exists(filename):
        return default

    try:
        with open(filename, "r", encoding="utf-8") as file:
            return json.load(file)
    except (json.JSONDecodeError, OSError):
        return default


def save_json(filename: str, data) -> None:
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)


def load_settings() -> Dict:
    settings = load_json(SETTINGS_FILE, DEFAULT_SETTINGS.copy())
    for key, value in DEFAULT_SETTINGS.items():
        settings.setdefault(key, value)
    return settings


def save_settings(settings: Dict) -> None:
    save_json(SETTINGS_FILE, settings)


def load_leaderboard() -> List[Dict]:
    return load_json(LEADERBOARD_FILE, DEFAULT_LEADERBOARD.copy())


def save_score(name: str, score: int, distance: int, coins: int) -> None:
    leaderboard = load_leaderboard()
    leaderboard.append({
        "name": name[:12] if name else "Player",
        "score": int(score),
        "distance": int(distance),
        "coins": int(coins),
    })

    leaderboard.sort(key=lambda item: item["score"], reverse=True)
    save_json(LEADERBOARD_FILE, leaderboard[:10])
