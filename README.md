# Wallpaper Carousel

A small Windows desktop app that rotates the desktop wallpaper from a selected
folder. The PySide6 window lets you manage folders, select the active folder,
configure a rotation interval, and start or stop the carousel. When a system
tray is available, closing the window hides it there without stopping a running
carousel.

## Requirements

- Windows (wallpaper changes call the Windows `user32` API).
- Python 3.10 or newer.
- PySide6, declared in `requirements.txt`.

## Setup and run

From PowerShell in the project directory:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python main.py
```

If Python's `py` launcher is not installed, create the virtual environment with
`python -m venv .venv` instead.

## Use

1. Add one or more folders containing `.jpg`, `.jpeg`, `.png`, or `.bmp` files.
2. Select a folder and choose **Set active**.
3. Enter a positive whole-number interval in seconds. The value is saved when
   the field loses focus or when the carousel starts.
4. Choose **Start carousel**. The app changes the wallpaper immediately, then
   repeats at the configured interval.
5. Choose **Stop** to stop the timer. Closing the window hides it in the system
   tray if the OS reports a tray as available. Use the tray menu to reopen or
   quit the app.

The tray menu provides **Open Wallpaper Carousel** and **Quit**. Running in the
tray does not currently configure automatic launch when Windows starts.

## Settings format

`folders.json` is read and written beside `folder_storage.py` (in the project
directory when run from source). Its current format is:

```json
{
  "folders": [
    "C:/path/to/wallpapers"
  ],
  "interval": 300
}
```

Folder additions/removals and interval changes save settings. The interval
defaults to 300 seconds when no settings file exists. Existing files containing
only a JSON array of folder paths remain readable; those use the default
interval until settings are next saved. Invalid JSON or invalid values are
reported in the UI.

The active folder and whether the carousel is running are in-memory state; they
are not restored after a restart.

## Architecture

```text
main.py
  └── app.py
        ├── folder_storage.py
        └── wallpaper.py

tests/
  └── test_folder_storage.py
```

- **`main.py`** — creates `QApplication`, constructs the main window, and starts
  Qt's event loop.
- **`app.py`** — `WallpaperApp`, the `QMainWindow` UI, user interactions,
  `QTimer` lifecycle, tray icon/menu, and UI-level error reporting. The timer
  drives wallpaper changes without a separate worker thread.
- **`folder_storage.py`** — reads/writes validated folder and interval settings
  in JSON. Accepts an optional `Path` so persistence can be tested using
  temporary files.
- **`wallpaper.py`** — finds supported image files, chooses one at random, and
  calls `SystemParametersInfoW` through `ctypes`.
- **`tests/test_folder_storage.py`** — standard-library `unittest` coverage for
  defaults, round-tripping, old-format compatibility, and interval validation.

## Development and tests

```powershell
python -m unittest discover -s tests -v
```

The current tests cover settings storage, not live Qt interaction or actual
wallpaper changes. See [ROADMAP.md](./ROADMAP.md) for recommended follow-up work
and [AGENTS.md](./AGENTS.md) for instructions intended for coding agents.
