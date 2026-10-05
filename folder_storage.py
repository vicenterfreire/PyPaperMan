"""JSON persistence for the folder list and wallpaper-change interval."""

import json
from pathlib import Path


SETTINGS_FILE = Path(__file__).with_name("folders.json")
DEFAULT_INTERVAL = 300


def load_settings(
    file_path: Path = SETTINGS_FILE,
) -> tuple[list[str], int]:
    """Load settings, or return empty folders and the default interval if absent."""
    try:
        contents = file_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return [], DEFAULT_INTERVAL

    settings = json.loads(contents)
    if isinstance(settings, list):
        folders = settings
        interval = DEFAULT_INTERVAL
    elif isinstance(settings, dict):
        folders = settings.get("folders")
        interval = settings.get("interval", DEFAULT_INTERVAL)
    else:
        raise ValueError("The settings file must contain a JSON object.")

    if not isinstance(folders, list) or any(
        not isinstance(folder, str) for folder in folders
    ):
        raise ValueError("The saved folders must be a JSON array of strings.")
    if isinstance(interval, bool) or not isinstance(interval, int) or interval < 1:
        raise ValueError("The saved interval must be a positive integer.")

    return folders, interval


def save_settings(
    folders: list[str],
    interval: int,
    file_path: Path = SETTINGS_FILE,
) -> None:
    """Write folders and a positive interval to the settings JSON file."""
    if isinstance(interval, bool) or not isinstance(interval, int) or interval < 1:
        raise ValueError("The interval must be a positive integer.")

    file_path.write_text(
        json.dumps(
            {"folders": folders, "interval": interval},
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
