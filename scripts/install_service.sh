#!/usr/bin/env bash
set -e
sudo cp systemd/pi-touch-controller.service /etc/systemd/system/pi-touch-controller.service
sudo systemctl daemon-reload
sudo systemctl enable pi-touch-controller.service
sudo systemctl start pi-touch-controller.service
