"""Configuration loading for contribution focus charts."""

import json
from pathlib import Path

DEFAULT_THEME = {
    "light_text": "#24292f",
    "light_muted": "#57606a",
    "light_empty": "#d0d7de",
    "dark_text": "#f0f6fc",
    "dark_muted": "#8b949e",
    "dark_empty": "#30363d",
}

DEFAULT_COLORS = {"Other": "#8B949E"}


def load_config(config_path: Path) -> dict:
    raw = {}
    if config_path.exists():
        raw = json.loads(config_path.read_text(encoding="utf-8-sig"))

    theme = DEFAULT_THEME.copy()
    theme.update(raw.get("theme", {}))
    colors = DEFAULT_COLORS.copy()
    colors.update(raw.get("colors", {}))

    excluded = {
        str(repository).strip().casefold()
        for repository in raw.get("excluded_repositories", [])
        if str(repository).strip()
    }
    return {
        "owner": str(raw.get("owner", "")).strip(),
        "excluded_repositories": excluded,
        "theme": theme,
        "colors": colors,
    }
