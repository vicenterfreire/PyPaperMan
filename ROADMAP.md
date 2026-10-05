# Next steps

This roadmap records follow-up work suggested by the current implementation.
It is not a claim that these features already exist. Priorities are ordered to
address reliability and verification before optional product expansion.

## 1. Handle wallpaper API failures

- Check the return value from `SystemParametersInfoW` and surface failures to
  the user instead of assuming the wallpaper changed.
- Handle inaccessible folders and directories with no supported images.
- Avoid showing a notification on every timer tick for a persistent failure;
  report the issue clearly without flooding the user.
- Add tests for image filtering/selection and isolate the Windows API behind a
  testable boundary.

## 2. Add application-level tests

- Test folder add/remove and interval validation without opening modal dialogs.
- Test starting/stopping the timer and changing the active folder.
- Test tray close/reopen/quit behavior, including when a tray is unavailable.
- Use Qt's offscreen platform for headless widget tests where feasible, and
  keep OS wallpaper effects mocked.

## 3. Improve settings durability

- Save settings atomically (write a temporary file and replace the old file) to
  reduce risk of a truncated JSON file if the app exits during a write.
- Consider placing user settings in the OS-standard per-user application data
  directory instead of next to the source/executable.
- If the settings format changes, add an explicit schema version and
  migration tests.

## 4. Persist carousel selection/state

- Decide whether the active folder should survive restarts.
- Decide whether the carousel should resume automatically after app restart or
  Windows login; keep the default opt-in if automatic wallpaper changes are
  not expected.
- If implemented, persist and validate the state with backward-compatible
  settings migrations.

## 5. Add optional Windows startup integration

- Define opt-in startup behavior (for example, a Settings toggle) separately
  from the existing system-tray behavior.
- Provide a clear way to disable startup and test install/uninstall cleanup.
- Do not turn the app into a Windows service without a separate requirement:
  wallpaper changes are tied to the logged-in user's desktop session.

## 6. Prepare a distributable Windows build

- Choose and document a packaging tool (for example, PyInstaller) and build
  configuration.
- Verify the bundled Qt plugins, tray icon, settings location, and wallpaper
  behavior on a clean Windows environment.
- Add versioning and a repeatable release/build procedure.

## 7. Product polish

- Make the active folder persistently distinguishable in the list; current
  status text is temporary and is overwritten by carousel start/stop state.
- Consider image preview, scheduling controls, and configurable supported
  formats only after the core failure handling and tests are in place.
