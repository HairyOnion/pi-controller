# Raspberry Pi Touch Controller — User Guide

This guide covers installation on a Raspberry Pi and general day‑to‑day use of the touchscreen controller. It assumes the Windows IntegrateAgent is already installed and running on the LAN.

## Requirements
- Raspberry Pi 4 with a 5" touchscreen
- Raspberry Pi OS Lite (64-bit preferred)
- Python 3.11+
- Local network access to the Windows agent

## Install (Recommended: one-step)
From the project root:
```bash
cd /home/hairyonion/pi_controller
./scripts/install_all.sh
```
This will:
- Install Python dependencies
- Seed the local SQLite database
- Install the systemd service
- Install backlight permissions (udev rule)

Reboot after installation to ensure backlight permissions are applied.

## Install (Manual)
1) Install dependencies:
```bash
cd /home/hairyonion/pi_controller
python3 -m pip install -e .
```

2) Seed database:
```bash
python3 -m app.data.seed
```

3) Install systemd service:
```bash
sudo cp systemd/pi-touch-controller.service /etc/systemd/system/pi-touch-controller.service
```

4) Configure display backend (Pi OS Lite):
```bash
chmod +x ./scripts/configure_display_linuxfb.sh
./scripts/configure_display_linuxfb.sh
```

5) Enable and start service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable pi-touch-controller.service
sudo systemctl start pi-touch-controller.service
```

6) Install backlight permissions:
```bash
chmod +x ./scripts/install_backlight_permissions.sh
./scripts/install_backlight_permissions.sh
```

7) Install power button permissions (one-time):
```bash
chmod +x ./scripts/install_power_permissions.sh
./scripts/install_power_permissions.sh
```

## Keyboard Input
- Settings text fields use an internal touch keyboard dialog.
- Tap a text field (Agent Host/Port/Token, Theme text fields), enter value, then press `Save`.
- This is the default because it is stable on `linuxfb`.

### Optional: Qt Virtual Keyboard
If you explicitly want Qt Virtual Keyboard:
```bash
chmod +x ./scripts/enable_virtual_keyboard.sh
./scripts/enable_virtual_keyboard.sh
sudo systemctl restart pi-touch-controller.service
```
Note: on some `linuxfb` systems this can cause partial black/blank screen regions while keyboard is open.

## Optional: Touch Calibration
See:
```bash
chmod +x ./scripts/touch_calibration_notes.sh
./scripts/touch_calibration_notes.sh
```

## Configure the Windows Agent Target
Open `System` -> `Settings` -> `Agent` and enter:
- Agent Host (IP or hostname)
- Agent Port
- Agent Token (must match `AGENT_TOKEN` on Windows)

These settings are saved when you press `Save` in the touch keyboard dialog.

## Brightness Control
The Agent settings screen includes a brightness slider. It applies immediately and persists across reboots.
- Brightness minimum is clamped to `20%` to prevent unreadable screens.
- Recovery helper: `./scripts/recover_brightness.sh` restores hardware and stored brightness to `50%`.

## General Use
- The UI is generated entirely from the local SQLite database.
- Screens are navigated via buttons (if configured) or swipe left/right.
- Buttons and sliders trigger HTTP requests to the Windows agent.
- If the Windows agent is unreachable, an “Agent Offline” banner appears.

## Voicemeeter Profile (Seeded Demo)
- The seeded DB includes four screens: `Main`, `System`, `Settings - Agent`, and `Settings - Theme`.
- Main screen row 1 includes six buttons:
  - `Casual` -> `run_app` to launch `Casual.ps1` via PowerShell.
  - `Gaming` -> `run_app` to launch `Gaming.ps1` via PowerShell.
  - `Audio Restart` -> `voicemeeter_command` with `command: restart`.
  - `S Headphones` -> `voicemeeter_apply` mute profile (`bus-0=true`, `bus-1=false`, `bus-2=true`).
  - `S Gaming` -> `voicemeeter_apply` mute profile (`bus-0=false`, `bus-1=true`, `bus-2=true`).
  - `S Casual` -> `voicemeeter_apply` mute profile (`bus-0=true`, `bus-1=true`, `bus-2=false`).
- Main screen row 2 includes four vertical faders (range `-60` to `12` dB):
  - `Web` -> `voicemeeter_apply` for `strip-5.gain`
  - `Games` -> `voicemeeter_apply` for `strip-6.gain`
  - `Comms` -> `voicemeeter_apply` for `strip-7.gain`
  - `Vol` -> `voicemeeter_group_bus_gain` with `gain`
  - Faders send live updates while dragging (throttled to `4/sec`) and a final update on release.
- System screen includes:
  - `Settings` button (opens settings tabs)
  - `Restart Pi` button (local reboot command)
  - `Shutdown Pi` button (local poweroff command)
- Settings tabs:
  - `Settings - Agent`: Agent Host, Agent Port, Agent Token, Brightness, Resolution
  - `Settings - Theme`: theme fields
  - `Home` button at top-right on both tabs returns to the Main screen
- These action names require matching support in the Windows IntegrateAgent service.

## Start/Stop/Status
Check service status:
```bash
sudo systemctl status pi-touch-controller.service
```

Restart the service:
```bash
sudo systemctl restart pi-touch-controller.service
```

## Windows-to-Pi Deploy (Incremental)
From Windows, run:
```bat
scripts\touch_deploy.bat
```

PowerShell options:
```powershell
.\scripts\touch_deploy.ps1
.\scripts\touch_deploy.ps1 -ForceAll
.\scripts\touch_deploy.ps1 -NoServiceRestart
.\scripts\touch_deploy.ps1 -SkipPipInstall
```

Notes:
- Tracks last deploy timestamp in `scripts/.touch_deploy_state.json`.
- First run defaults to git working-tree changes only.
- Installs Python dependencies on Pi by default (`python3 -m pip install -e .`).
- Restarts `pi-touch-controller.service` automatically by default.
- Reboot is only attempted for reboot-required file changes and only with `-AllowReboot`.

Apply UI DB tweaks from Windows (for existing DB):
```powershell
python .\scripts\update_ui_layout_and_style_windows.py
```

## Database Location
Default DB path:
```
/home/hairyonion/pi_controller/app.db
```
Override for seeding:
```bash
PI_TC_DB=/path/to/app.db python3 -m app.data.seed
```

## Common Troubleshooting
- **Agent Offline banner / commands not reaching Windows**:
  - verify Windows agent is running and reachable; confirm host/port/token.
  - ensure Windows agent binds to LAN (`0.0.0.0:8765`), not localhost-only (`127.0.0.1`).
  - allow inbound TCP `8765` in Windows Firewall.
- **Brightness not changing**: ensure udev rule was installed and you rebooted.
- **Touch input inaccurate**: run calibration steps from `scripts/touch_calibration_notes.sh`.
- **Display backend errors (`eglfs_kms`, `no screens available`)**: rerun:
  - `chmod +x ./scripts/configure_display_linuxfb.sh`
  - `./scripts/configure_display_linuxfb.sh`
  - `sudo systemctl restart pi-touch-controller.service`
- **Framebuffer cursor artifact / shell prompt visible under UI after reboot**:
  - `sudo cp systemd/pi-touch-controller.service /etc/systemd/system/pi-touch-controller.service`
  - `sudo systemctl daemon-reload`
  - `sudo systemctl restart pi-touch-controller.service`
  - optional: rerun `./scripts/configure_display_linuxfb.sh`
- **Service restart loop / blank screen with cursor only**:
  - verify dependencies: `python3 -c "import PySide6; print('PySide6 OK')"`
  - if missing, install: `python3 -m pip install -e .`
  - restart service: `sudo systemctl restart pi-touch-controller.service`
  - inspect logs: `sudo journalctl -u pi-touch-controller.service -n 120 --no-pager`
- **Restart/Shutdown buttons do nothing**:
  - install sudoers permissions: `./scripts/install_power_permissions.sh`
  - restart service: `sudo systemctl restart pi-touch-controller.service`

## Notes
- The Pi app does not expose any remote server. It only sends outbound HTTP requests.
- Screen layout, styling, and actions are fully data-driven via SQLite.
