# Raspberry Pi Touch Controller

Data-driven touchscreen controller for a Windows automation agent. The UI is fully generated from a local SQLite database and is intended to run as a kiosk on Raspberry Pi.

## Highlights
- Full-screen kiosk mode on Pi (systemd, no desktop).
- Windowed dev mode on Windows for UI testing.
- SQLite-driven screens, controls, styling, and actions.
- Control types include buttons, toggles, sliders, vertical sliders, and settings inputs.
- Settings screen includes agent target, brightness, and a Windows-only resolution dropdown.
- Local UI-only actions such as `navigate_screen` and `show_resolution`.

## Notes
- UI is generated from SQLite at runtime.
- Systemd service is provided in `systemd/pi-touch-controller.service`.
- Behavior must follow `PI_CONTROLLER_SPEC.md`.

## System Setup (Pi)
Backlight permissions:
- Run `scripts/install_backlight_permissions.sh` to allow non-root brightness control.

On-screen keyboard (Qt Virtual Keyboard):
- Run `scripts/enable_virtual_keyboard.sh` to write `/etc/pi-touch-controller.env`.
- Restart the systemd service to apply.

Touch calibration:
- See `scripts/touch_calibration_notes.sh` for tslib-based calibration steps.

One-step install:
- Run `scripts/install_all.sh` to install the service, env file, and backlight permissions.
