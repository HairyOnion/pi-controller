# Operator Card - Pi Touch Controller

1. Power on the Pi and wait for the UI to appear.
2. Open **Settings** on the Pi.
3. Enter **Agent Host**, **Agent Port**, **Agent Token**.
4. Adjust **Brightness** if needed.
5. Use swipe left/right or on-screen buttons to navigate.
6. Optional (Windows dev): set **Resolution** in Settings to resize the app window.
7. If "Agent Offline" appears, check the Windows agent and network.

Service control (if needed):
- Start: `sudo systemctl start pi-touch-controller.service`
- Stop: `sudo systemctl stop pi-touch-controller.service`
- Restart: `sudo systemctl restart pi-touch-controller.service`
- Status: `sudo systemctl status pi-touch-controller.service`
