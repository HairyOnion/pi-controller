#!/usr/bin/env bash
set -euo pipefail

ENV_DST="/etc/pi-touch-controller.env"

sudo tee "$ENV_DST" >/dev/null <<'EOF'
QT_QPA_PLATFORM=eglfs
QT_QPA_EGLFS_HIDECURSOR=1
QT_IM_MODULE=qtvirtualkeyboard
QT_VIRTUALKEYBOARD_STYLE=retro
EOF

echo "Wrote $ENV_DST. Restart the service to apply."
