# Pi Touch Controller - Design Contract

This document is the authoritative design contract for the Raspberry Pi Touch Controller application. It defines what the product is, how it behaves, and what must not change without updating this contract.

## Purpose
- Provide an appliance-style, single-purpose touchscreen controller for a Windows-based automation agent.
- Prioritize reliability, fast boot, and zero-maintenance operation for operators.
- Present a full-screen, kiosk-style UI that never exposes the underlying OS or desktop.

## Target Platform
- Raspberry Pi 4 with 5" (or similar) touchscreen.
- Raspberry Pi OS Lite (no desktop environment).
- Python 3.11+ runtime.

## Kiosk Behavior
- Must start at boot via systemd and run as a foreground, full-screen application.
- Must not require a desktop session or window manager.
- Must be frameless and full-screen; users should never see window chrome.
- If the app crashes, systemd must restart it (service configuration responsibility).

## Windows Dev Mode (Non-Pi)
- On Windows, the app may run windowed for development and QA.
- Windowed mode must be centered and resizable without clipping content.
- Any resolution selection in Settings is a window-size simulation only and must not change OS display settings.

## Architecture
- UI layer: Qt-based window, screen renderer, status overlay, and gesture handling.
- Data layer: SQLite database with migrations and a repository for queries.
- Dispatcher layer: queues and sends actions to the Windows agent, with retry and health checks.
- Settings layer: validates and persists operator settings and theme values.

## Data-Driven UI (No Hard-Coded Screens)
- All screens and controls are defined in SQLite tables.
- UI layout and behavior must be generated from the database at runtime.
- The only acceptable hard-coded UI is an empty-state message when no screens exist.
- Adding or removing screens, controls, styling, or actions must be done via data, not code.

## Control Types
- `button`: fires actions on `press`.
- `toggle`: fires actions on `toggle_on` and `toggle_off`.
- `slider`: fires actions on `value_change` (continuous) and `value_release` (discrete).
- `slider_vertical`: vertical slider with the same triggers as `slider`.
- `setting_text`: text input bound to a settings key.
- `setting_slider`: slider input bound to a settings key.
- `setting_dropdown`: dropdown input bound to a settings key.

## State and Persistence
- Control state persistence is optional and controlled by `persist_state`.
- Persisted control values are stored in `control_state` and restored on load.
- Non-persisted controls use `default_value` when provided.
- Settings are stored in `settings` and must be validated before saving.

## Styling and Theming (Database-Driven)
- Screen styling is defined by `bg_color`, `bg_image_path`, and `bg_image_mode`.
- Control styling is defined by `style_bg`, `style_fg`, `icon_path`, and size hints.
- Global theme values are defined in `settings` (font family, font size, colors, spacing, button radius, slider groove/handle, accent).
- Styling must not be hard-coded in the UI beyond generic widget defaults.

## Settings Screen (Required)
The settings screen must include the following operator-editable settings:
- Agent Host (`agent_host`)
- Agent Port (`agent_port`)
- Agent Token (`agent_token`)
- Brightness (`brightness`)
- Resolution (`resolution`) for Windows dev mode only (window resize simulation).

Additional theme settings may be exposed, but these five are mandatory.

## Windows Agent Communication
- Communication is HTTP/JSON over the local network.
- Commands are sent to `POST /command` with a JSON body and a `Bearer` token.
- Health checks are performed via `GET /health`.
- Action payloads are defined in the database as JSON and must include `action` and `payload`.
- Context interpolation is supported via `${value}` and `${state}` in payload JSON.
- `value_key` may be used to map slider values into a specific payload field.
- Local UI-only actions (e.g., `navigate_screen`, `show_resolution`) are handled on-device and never sent to the agent.

## Non-Goals / Out of Scope
- No local server or inbound API on the Pi.
- No on-device UI editor or configuration wizard beyond settings controls.
- No dependency on a desktop environment or window manager.
- No business logic for automation; the Windows agent owns automation logic.
- No multi-user authentication or role-based access control.
- No OS-level resolution changes from the Pi app.

## Rules for Future Changes
- This document is authoritative. If behavior changes, update this spec first.
- UI must remain fully data-driven. Do not hard-code screens or controls in code.
- Any new control type must define its triggers, persistence, and DB schema usage here.
- Any new agent protocol behavior must be documented here before implementation.
- Changes that affect operators must be documented in `STATUS.md` after implementation.
