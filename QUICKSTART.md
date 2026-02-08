# Quick Start (Pi Touch Controller)

## Pi Install
1. Install:
```bash
cd /home/pi/pi_touch_controller
./scripts/install_all.sh
```

2. Reboot:
```bash
sudo reboot
```

3. Set Windows agent settings on the Pi:
- Open the Settings screen.
- Fill in Agent Host, Agent Port, Agent Token.

4. Verify service:
```bash
sudo systemctl status pi-touch-controller.service
```

5. If needed, restart:
```bash
sudo systemctl restart pi-touch-controller.service
```

## Windows Dev (Windowed)
1. Install dependencies:
```bash
python -m pip install -e .
```

2. Seed the demo DB:
```bash
python -m app.data.seed
```

3. Run the app:
```bash
python -m app.main
```

Notes:
- The Resolution dropdown in Settings resizes the window (Windows dev only).
