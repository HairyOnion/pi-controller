#!/usr/bin/env bash
set -euo pipefail

RULE_SRC="systemd/90-backlight.rules"
RULE_DST="/etc/udev/rules.d/90-backlight.rules"
APP_USER="${PI_TC_USER:-hairyonion}"

if [[ ! -f "$RULE_SRC" ]]; then
  echo "Missing $RULE_SRC"
  exit 1
fi

sudo cp "$RULE_SRC" "$RULE_DST"
sudo udevadm control --reload-rules
sudo udevadm trigger

if id -u "$APP_USER" >/dev/null 2>&1; then
  sudo usermod -aG video "$APP_USER"
fi

echo "Backlight permissions installed. Reboot recommended."
