# Agent development guide

This document is the working handoff for agents making changes to Wallpaper
Carousel. Treat the current Python source as the behavior reference; do not
claim a feature is present just because it appears in the roadmap.

## Start here

1. Read `README.md` for the supported setup, user workflow, architecture, and
   current limitations.
2. Inspect the relevant source and tests before editing. Keep changes within
   the module that owns the behavior unless a feature needs coordinated changes.
3. Confirm the active Python interpreter has project dependencies installed.
   Install project dependencies with `python -m pip install -r requirements.txt`
   only when setting up the environment or a missing dependency blocks
   validation.
4. Run the focused test(s), then the complete suite with:

   ```powershell
   python -m unittest discover -s tests -v
   ```

5. Report validation accurately. A storage unit test or offscreen UI smoke test
   does not prove that Windows changed the wallpaper or that the tray works in
   every desktop environment.

## Module ownership

- `main.py`: application startup and Qt event loop only.
- `app.py`: PySide6 presentation, interaction flow, transient state, tray
  integration, and user-facing error messages.
- `folder_storage.py`: JSON schema, validation, defaults, and file IO. Keep
  storage independent of Qt so it remains easy to test.
- `wallpaper.py`: image selection and the OS wallpaper call. Keep platform
  integration out of widgets.
- `tests/`: standard-library `unittest` tests. Add focused regression tests
  alongside behavior changes.

## State and side-effect boundaries

- Persisted state: configured folder paths and the positive interval.
- Transient state: active folder and whether the current process is rotating.
- Configuration file: `folders.json`, located beside `folder_storage.py`.
- GUI framework: PySide6; Qt's event loop and `QTimer` currently manage the
  lifecycle. Do not introduce a second GUI framework.
- Platform boundary: `wallpaper.py` uses Windows `user32` through `ctypes`.
- Tray close behavior: close hides the window when a tray is available; it does
  not terminate the application. When a tray is unavailable, close stops the
  timer and accepts the close event.
- Persistence compatibility: `folder_storage.py` still reads the legacy JSON
  array of folders, assigning the default interval.

## Change guidelines

- Keep UI concerns out of `folder_storage.py` and OS wallpaper calls out of
  `app.py`.
- Preserve existing settings compatibility unless a migration is intentional,
  documented, and tested.
- Validate user-provided values and show failures explicitly; do not silently
  ignore failed persistence or OS operations.
- Keep settings tests independent of the real `folders.json` by using a
  temporary path.
- When adding a user-facing feature, update `README.md`, relevant tests, and
  `ROADMAP.md` (remove or revise completed items).
- Avoid recording local machine paths or personal folder names in committed
  docs, tests, or example configuration.
- Do not add startup behavior, background services, or new dependencies unless
  they are required by the requested feature and their lifecycle/UX is defined.

## Current verification boundaries

The committed automated tests validate JSON persistence. There is no
automated test suite for the full interactive window, tray activation, Windows
wallpaper API, packaging, or launch-at-login. Validate those at the appropriate
level when changing those surfaces and state any untested platform behavior.
