# Pi Touch Controller Handoff

Date: 2026-02-15

## Current State
- Service/runtime working on Pi (`pi-touch-controller.service`).
- Display backend baseline is `linuxfb` via `/etc/pi-touch-controller.env`.
- UI layout issues at `800x480` are resolved.
- Agent communication path is working when Windows agent is reachable on LAN.

## Stable Baseline (Reinstall / Recovery)
1. Run `./scripts/install_all.sh`
2. Run `./scripts/configure_display_linuxfb.sh`
3. Restart service: `sudo systemctl restart pi-touch-controller.service`
4. Verify: `sudo systemctl status pi-touch-controller.service --no-pager`

## Important Runtime Notes
- Settings text fields use an internal touch keyboard dialog (default path).
- Qt Virtual Keyboard is optional and may cause split/blank rendering on some `linuxfb` systems.
- Brightness is clamped to `20-100`; `./scripts/recover_brightness.sh` restores to `50%`.
- Main vertical faders now send live updates while dragging (4/sec) plus final update on release.

## Agent Connectivity Requirements
- Windows agent must bind to LAN (`0.0.0.0:8765`), not localhost-only.
- Windows Firewall must allow inbound TCP `8765`.
- On Pi, configure `Agent Host/Port/Token` in `System -> Settings -> Agent`.

## If Communication Breaks Again
- On Pi:
  - `sudo journalctl -u pi-touch-controller.service -f --no-pager`
  - Look for `app.actions.client` timeouts/status failures.
- Verify stored settings:
  - `agent_host`, `agent_port`, `agent_token` in `/home/hairyonion/pi_controller/app.db`.
