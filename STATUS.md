# Pi Touch Controller - Current Status

Snapshot date: 2026-02-17

## Implemented Features
- [x] Full-screen, frameless Qt window.
- [x] Systemd service file provided for boot-time launch.
- [x] SQLite migrations and seeded starter data.
- [x] Fully database-driven screens and controls.
- [x] Screen navigation via DB-defined actions.
- [x] Control types: button, toggle, slider, setting_text, setting_slider.
- [x] Control state persistence via `control_state` table.
- [x] Settings persistence and validation.
- [x] Theme settings applied from database.
- [x] Background color and image support per screen.
- [x] Agent dispatcher queue, retries, and health checks.
- [x] HTTP/JSON command dispatch to Windows agent with bearer token.
- [x] Agent offline overlay when health checks fail.
- [x] Brightness control via settings and backlight helper.
- [x] Swipe navigation between screens.
- [x] SVG button backgrounds and slider track/knob assets (per-control paths).
- [x] SVG raster caching with optional on-disk PNG cache.
- [x] In-app touch keyboard dialog for settings text fields (linuxfb-safe default).
- [x] Slider touch hitbox improvements for easier finger interaction.
- [x] Continuous slider value dispatch while dragging (throttled to 4 Hz) with final release dispatch.
- [x] Brightness safety floor (`20%`) and recovery helper (`scripts/recover_brightness.sh`).
- [x] Seeded Voicemeeter-ready controls/actions:
  - Four-screen seeded layout (`Main`, `System`, `Settings - Agent`, `Settings - Theme`).
  - Main row of profile buttons: `Casual`, `Gaming`, `Audio Restart`, `S Headphones`, `S Gaming`, `S Casual`.
  - `run_app` actions for `Casual.ps1` and `Gaming.ps1`.
  - `voicemeeter_command` action for `restart`.
  - `voicemeeter_apply` mute profiles for buses `0..2`.
  - Vertical gain faders `Web`, `Games`, `Comms`, `Vol` with range `-60..12` dB.
  - `voicemeeter_apply` targets for `strip-5`, `strip-6`, `strip-7` and `voicemeeter_group_bus_gain` for grouped bus volume.
  - System controls include `Settings`, `Restart Pi`, and `Shutdown Pi`.
  - Settings tabs include top-row `Agent`/`Theme` navigation and a top-right `Home` button back to Main.

## Dev Mode (Windows)
1. From `C:\Users\HairyOnion\Documents\codex\pi_controller`, install dependencies:
   `python -m pip install -e .`
2. Run the app:
   `python -m app.main`

Notes:
- The app creates its SQLite DB at `/home/hairyonion/pi_controller/app.db`, which maps to `C:\home\hairyonion\pi_controller\app.db` on Windows.
- To reset and reseed manually: `python -m app.data.seed`.
- To update existing Windows dev DB rows with SVG paths: `python scripts/update_svg_paths_windows.py`.

## Known Limitations (Polish Only)
- No UI for editing screen layouts; changes require database edits.
- Basic styling only; no animations or advanced layout transitions.
- No visible loading indicators for slow network responses.
- Voicemeeter action execution depends on Windows IntegrateAgent implementing those action names.

## Active Blockers (2026-02-17)
- None currently.

## Resolved Today (2026-02-17)
- `800x480` UI clipping/scaling regressions on Pi were fixed.
- Framebuffer cursor artifact and boot shell text bleed-through were fixed via service pre-start console handling.
- Service startup loop from missing `PySide6` on Pi was identified and resolved.
- `touch_deploy` automation now supports incremental deploy with dependency sync and service restart.
- Windows agent communication restored by using LAN host and validating agent reachability from Pi.
- Qt Virtual Keyboard dependence removed from default Pi path to avoid `linuxfb` split/blank rendering.
