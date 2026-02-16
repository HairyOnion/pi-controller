#!/usr/bin/env bash
set -euo pipefail

ENV_DST="/etc/pi-touch-controller.env"

tmp="$(mktemp)"
if [[ -f "$ENV_DST" ]]; then
  sudo cp "$ENV_DST" "$tmp"
  sudo sed -i '/^QT_IM_MODULE=/d;/^QT_VIRTUALKEYBOARD_STYLE=/d' "$tmp"
else
  cat >"$tmp" <<'EOF'
QT_QPA_PLATFORM=linuxfb
QT_QPA_FB=/dev/fb0
QT_QPA_EGLFS_HIDECURSOR=1
EOF
fi

cat >>"$tmp" <<'EOF'
QT_IM_MODULE=qtvirtualkeyboard
QT_VIRTUALKEYBOARD_STYLE=retro
EOF

sudo cp "$tmp" "$ENV_DST"
rm -f "$tmp"

echo "Wrote $ENV_DST. Restart the service to apply."
