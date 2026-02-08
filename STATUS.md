# Pi Touch Controller - Current Status

Snapshot date: 2026-02-07

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

## Dev Mode (Windows)
1. From `C:\Users\HairyOnion\Documents\codex\pi_touch_controller`, install dependencies:
   `python -m pip install -e .`
2. Run the app:
   `python -m app.main`

Notes:
- The app creates its SQLite DB at `/home/pi/pi_touch_controller/app.db`, which maps to `C:\home\pi\pi_touch_controller\app.db` on Windows.
- To reset and reseed manually: `python -m app.data.seed`.

## Known Limitations (Polish Only)
- No UI for editing screen layouts; changes require database edits.
- Basic styling only; no animations or advanced layout transitions.
- No visible loading indicators for slow network responses.
