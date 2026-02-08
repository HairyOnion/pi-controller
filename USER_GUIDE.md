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
cd /home/pi/pi_touch_controller
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
cd /home/pi/pi_touch_controller
python3 -m pip install -e .
```

2) Seed database:
```bash
python3 -m app.data.seed
```

3) Install systemd service:
```bash
sudo cp systemd/pi-touch-controller.service /etc/systemd/system/pi-touch-controller.service
sudo systemctl daemon-reload
sudo systemctl enable pi-touch-controller.service
sudo systemctl start pi-touch-controller.service
```

4) Install backlight permissions:
```bash
./scripts/install_backlight_permissions.sh
```

## Optional: On‑Screen Keyboard
Enable Qt virtual keyboard:
```bash
./scripts/enable_virtual_keyboard.sh
sudo systemctl restart pi-touch-controller.service
```

## Optional: Touch Calibration
See:
```bash
./scripts/touch_calibration_notes.sh
```

## Configure the Windows Agent Target
Open the Settings screen on the Pi and enter:
- Agent Host (IP or hostname)
- Agent Port
- Agent Token (must match `AGENT_TOKEN` on Windows)

These settings are saved automatically when you finish editing a field.

## Brightness Control
The Settings screen includes a brightness slider. It applies immediately and persists across reboots.

## General Use
- The UI is generated entirely from the local SQLite database.
- Screens are navigated via buttons (if configured) or swipe left/right.
- Buttons and sliders trigger HTTP requests to the Windows agent.
- If the Windows agent is unreachable, an “Agent Offline” banner appears.

## Start/Stop/Status
Check service status:
```bash
sudo systemctl status pi-touch-controller.service
```

Restart the service:
```bash
sudo systemctl restart pi-touch-controller.service
```

## Database Location
Default DB path:
```
/home/pi/pi_touch_controller/app.db
```
Override for seeding:
```bash
PI_TC_DB=/path/to/app.db python3 -m app.data.seed
```

## Common Troubleshooting
- **Agent Offline banner**: verify Windows agent is running and reachable; confirm host/port/token.
- **Brightness not changing**: ensure udev rule was installed and you rebooted.
- **Touch input inaccurate**: run calibration steps from `scripts/touch_calibration_notes.sh`.

## Notes
- The Pi app does not expose any remote server. It only sends outbound HTTP requests.
- Screen layout, styling, and actions are fully data-driven via SQLite.
