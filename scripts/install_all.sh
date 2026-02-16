#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
APP_USER="${PI_TC_USER:-hairyonion}"
APP_HOME="/home/$APP_USER"
DB_PATH="${PI_TC_DB:-$APP_HOME/pi_controller/app.db}"

echo "Installing Python dependencies..."
python3 -m pip install -e "$ROOT_DIR"

echo "Seeding database at $DB_PATH..."
PI_TC_DB="$DB_PATH" python3 -m app.data.seed

echo "Installing systemd service..."
sudo cp "$ROOT_DIR/systemd/pi-touch-controller.service" /etc/systemd/system/pi-touch-controller.service

if [[ -f /etc/pi-touch-controller.env ]]; then
  echo "Using existing /etc/pi-touch-controller.env"
else
  echo "Installing default /etc/pi-touch-controller.env"
  sudo cp "$ROOT_DIR/systemd/pi-touch-controller.env.example" /etc/pi-touch-controller.env
fi

echo "Installing backlight permissions..."
sudo cp "$ROOT_DIR/systemd/90-backlight.rules" /etc/udev/rules.d/90-backlight.rules
sudo udevadm control --reload-rules
sudo udevadm trigger

if id -u "$APP_USER" >/dev/null 2>&1; then
  sudo usermod -aG video "$APP_USER"
fi

echo "Enabling service..."
sudo systemctl daemon-reload
sudo systemctl enable pi-touch-controller.service
sudo systemctl restart pi-touch-controller.service

echo "Done. Reboot recommended for backlight permissions to apply."
