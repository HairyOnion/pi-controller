#!/usr/bin/env bash
set -euo pipefail

ENV_DST="/etc/pi-touch-controller.env"
QPA_PLATFORM="${PI_TC_QPA_PLATFORM:-linuxfb}"
FB_DEVICE="${PI_TC_FB_DEVICE:-/dev/fb0}"

sudo tee "$ENV_DST" >/dev/null <<EOF
QT_QPA_PLATFORM=$QPA_PLATFORM
QT_QPA_FB=$FB_DEVICE
QT_QPA_EGLFS_HIDECURSOR=1
QT_QPA_FB_HIDECURSOR=1
QT_ENABLE_HIGHDPI_SCALING=0
QT_AUTO_SCREEN_SCALE_FACTOR=0
QT_SCALE_FACTOR=1
QT_FONT_DPI=96
EOF

echo "Wrote $ENV_DST using $QPA_PLATFORM ($FB_DEVICE)."

# Hide Linux framebuffer console cursor/blink that can appear at screen edge.
if [[ -e /sys/class/graphics/fbcon/cursor_blink ]]; then
  echo 0 | sudo tee /sys/class/graphics/fbcon/cursor_blink >/dev/null || true
fi

if command -v setterm >/dev/null 2>&1 && [[ -e /dev/tty1 ]]; then
  sudo sh -c 'setterm -cursor off -blank 0 -powersave off >/dev/tty1' || true
fi

echo "Restart the service: sudo systemctl restart pi-touch-controller.service"
