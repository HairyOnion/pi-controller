#!/usr/bin/env bash
set -euo pipefail

cat <<'EOF'
Touch calibration notes (manual steps):
1) Install tslib if not present.
2) Run ts_calibrate to generate calibration data.
3) Export required environment in /etc/pi-touch-controller.env:
   TSLIB_TSDEVICE=/dev/input/eventX
   TSLIB_CALIBFILE=/etc/pointercal
   QT_QPA_EGLFS_TSLIB=1
4) Restart the service.
EOF
