#!/usr/bin/env bash
set -euo pipefail

APP_DIR="${APP_DIR:-$HOME/pi_controller}"
VENV_PY="${VENV_PY:-$APP_DIR/.venv/bin/python}"
DB_PATH="${DB_PATH:-$APP_DIR/app.db}"
SERVICE_NAME="${SERVICE_NAME:-pi-touch-controller.service}"

echo "Recovering brightness to 50%..."

if compgen -G "/sys/class/backlight/*/max_brightness" >/dev/null; then
  for max_file in /sys/class/backlight/*/max_brightness; do
    brightness_file="${max_file%/max_brightness}/brightness"
    if [[ -f "$brightness_file" ]]; then
      max_val="$(cat "$max_file")"
      target="$((max_val / 2))"
      echo "$target" | sudo tee "$brightness_file" >/dev/null
      echo "Set $brightness_file to $target (50% of $max_val)"
    fi
  done
else
  echo "No backlight sysfs path found under /sys/class/backlight"
fi

if [[ ! -x "$VENV_PY" ]]; then
  echo "Python runtime not found at $VENV_PY"
  exit 1
fi

echo "Updating DB brightness setting to 50 and applying migrations..."
"$VENV_PY" - <<PY
from app.data.db import Database
from app.data.repository import Repository

db = Database("$DB_PATH")
db.migrate()
Repository(db).set_setting("brightness", "50")
print("Brightness setting saved: 50")
PY

echo "Restarting service: $SERVICE_NAME"
sudo systemctl restart "$SERVICE_NAME"
sudo systemctl status "$SERVICE_NAME" --no-pager | sed -n '1,12p'

echo "Done."
