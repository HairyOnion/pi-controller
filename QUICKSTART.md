# Quick Start (Pi Touch Controller)

## Pi Install
1. Install:
```bash
cd /home/hairyonion/pi_controller
./scripts/install_all.sh
```

2. Configure display backend (Pi OS Lite):
```bash
./scripts/configure_display_linuxfb.sh
sudo systemctl restart pi-touch-controller.service
```

3. Reboot:
```bash
sudo reboot
```

4. Set Windows agent settings on the Pi:
- Open `System` -> `Settings` -> `Agent`.
- Fill in Agent Host, Agent Port, Agent Token.
- For `setting_text` fields, tap the field to open the in-app touch keyboard.

5. On Windows, ensure agent is reachable from LAN:
- Bind agent to `0.0.0.0:8765` (not `127.0.0.1` only).
- Allow inbound TCP `8765` in Windows Firewall.

6. Verify service:
```bash
sudo systemctl status pi-touch-controller.service
```

7. If needed, restart:
```bash
sudo systemctl restart pi-touch-controller.service
```

## Fresh Install Validation Checklist
After install/reboot, verify in this order:

1. Service is running:
```bash
sudo systemctl status pi-touch-controller.service --no-pager
```

2. UI renders correctly at `800x480`:
- Main, System, Settings-Agent, Settings-Theme screens fill the display.
- No clipped right/bottom regions.

3. Agent connectivity:
- Windows agent is running on `0.0.0.0:8765`.
- Windows firewall allows inbound TCP `8765`.
- Pi can reach health endpoint:
```bash
curl -m 3 http://<windows-agent-ip>:8765/health
```

4. Settings save path:
- In `System -> Settings -> Agent`, edit `Agent Host` using touch keyboard dialog and save.
- Confirm value persists after returning to the screen.

5. Action dispatch:
- Press one profile button (for example `Casual`).
- Confirm Windows agent receives `/command`.

6. Fader behavior:
- Drag a vertical fader and confirm smooth movement.
- Confirm live updates while dragging (~4/sec) and final value on release.

## Windows Dev (Windowed)
1. Install dependencies:
```bash
python -m pip install -e .
```

2. Seed the demo DB:
```bash
python -m app.data.seed
```

3. Update existing Windows dev DB rows with SVG paths (if needed):
```bash
python scripts/update_svg_paths_windows.py
```

4. Run the app:
```bash
python -m app.main
```

Notes:
- The Resolution dropdown in `Settings - Agent` resizes the window (Windows dev only).
- Main faders send live updates while dragging (throttled to 4/sec) plus a final send on release.
