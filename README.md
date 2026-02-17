# Raspberry Pi Touch Controller

Data-driven touchscreen controller for a Windows automation agent. The UI is fully generated from a local SQLite database and is intended to run as a kiosk on Raspberry Pi.

## Highlights
- Full-screen kiosk mode on Pi (systemd, no desktop).
- Windowed dev mode on Windows for UI testing.
- SQLite-driven screens, controls, styling, and actions.
- Control types include buttons, toggles, sliders, vertical sliders, and settings inputs.
- Settings are split across tab-like screens for Agent and Theme settings, with a Home button to return to Main.
- Local UI-only actions such as `navigate_screen` and `show_resolution`.
- Per-control SVG styling for button backgrounds and slider track/knob assets.
- Seeded four-screen Voicemeeter profile: Main controls, System actions, Agent settings tab, and Theme settings tab.
- Vertical faders support easier touch hitboxes and continuous live updates while dragging (throttled to 4 updates/sec).
- Settings text fields use an in-app touch keyboard dialog (works reliably on `linuxfb`).

## Notes
- UI is generated from SQLite at runtime.
- Systemd service is provided in `systemd/pi-touch-controller.service`.
- Behavior must follow `PI_CONTROLLER_SPEC.md`.
- Windows dev DB helper: `python scripts/update_svg_paths_windows.py`.

## Windows-to-Pi Deploy
- Use `scripts\touch_deploy.bat` for incremental deploy from Windows.
- The deploy script tracks last deploy time in `scripts/.touch_deploy_state.json`.
- First run deploys git working-tree changes by default; use `-ForceAll` for full bootstrap.
- Deploy runs `python3 -m pip install -e .` on Pi by default, then restarts `pi-touch-controller.service`.
- Use `-SkipPipInstall` only when you intentionally want copy/restart without dependency sync.

## System Setup (Pi)
Backlight permissions:
- Run `scripts/install_backlight_permissions.sh` to allow non-root brightness control.

Display backend (recommended on Pi OS Lite):
- Run `scripts/configure_display_linuxfb.sh` and restart the service.

Keyboard input:
- By default, settings text fields open an internal touch keyboard dialog.
- Qt Virtual Keyboard is optional (`scripts/enable_virtual_keyboard.sh`) but can cause split/blank rendering on some `linuxfb` setups.

Touch calibration:
- See `scripts/touch_calibration_notes.sh` for tslib-based calibration steps.

One-step install:
- Run `scripts/install_all.sh` to install the service, env file, and backlight permissions.
- `install_all.sh` also installs power-command permissions for Restart/Shutdown buttons.

DB update helper (Windows):
- `python scripts/update_ui_layout_and_style_windows.py` applies the latest System-screen layout and green-button text updates to existing DBs.

## Windows Agent Reachability
- The Windows agent must listen on LAN, not only localhost.
- If using uvicorn/FastAPI, start with host `0.0.0.0` on port `8765`.
- Allow inbound TCP `8765` in Windows Firewall.
