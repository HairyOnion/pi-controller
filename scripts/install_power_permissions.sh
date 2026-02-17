#!/usr/bin/env bash
set -euo pipefail

APP_USER="${PI_TC_USER:-hairyonion}"
SUDOERS_FILE="/etc/sudoers.d/90-pi-touch-power"

sudo tee "$SUDOERS_FILE" >/dev/null <<EOF
$APP_USER ALL=(root) NOPASSWD: /usr/bin/systemctl reboot
$APP_USER ALL=(root) NOPASSWD: /usr/bin/systemctl poweroff
$APP_USER ALL=(root) NOPASSWD: /sbin/shutdown -r now
$APP_USER ALL=(root) NOPASSWD: /sbin/shutdown -h now
$APP_USER ALL=(root) NOPASSWD: /usr/sbin/shutdown -r now
$APP_USER ALL=(root) NOPASSWD: /usr/sbin/shutdown -h now
$APP_USER ALL=(root) NOPASSWD: /sbin/reboot
$APP_USER ALL=(root) NOPASSWD: /sbin/poweroff
$APP_USER ALL=(root) NOPASSWD: /usr/sbin/reboot
$APP_USER ALL=(root) NOPASSWD: /usr/sbin/poweroff
EOF

sudo chmod 0440 "$SUDOERS_FILE"
sudo visudo -cf "$SUDOERS_FILE"
echo "Installed power permissions for $APP_USER in $SUDOERS_FILE"
