from __future__ import annotations

from typing import Optional

from .db import Database
from .models import Action, Control, ControlState, Screen, Setting


class Repository:
    def __init__(self, db: Database) -> None:
        self._db = db

    def list_screens(self) -> list[Screen]:
        with self._db.connect() as conn:
            rows = conn.execute(
                "SELECT id, name, order_index, bg_color, bg_image_path, bg_image_mode FROM screens ORDER BY order_index ASC"
            ).fetchall()
        return [Screen(**dict(row)) for row in rows]

    def list_controls_for_screen(self, screen_id: int) -> list[Control]:
        with self._db.connect() as conn:
            rows = conn.execute(
                """
                SELECT id, screen_id, type, label, row, col, rowspan, colspan,
                       min_value, max_value, step, is_continuous, default_value,
                       persist_state, style_bg, style_fg, icon_path, width_hint, height_hint,
                       setting_key, placeholder_text,
                       button_svg_path, slider_track_path, slider_knob_path
                FROM controls
                WHERE screen_id = ?
                ORDER BY row ASC, col ASC
                """,
                (screen_id,),
            ).fetchall()
        return [Control(**dict(row)) for row in rows]

    def list_actions_for_control(self, control_id: int) -> list[Action]:
        with self._db.connect() as conn:
            rows = conn.execute(
                """
                SELECT id, control_id, trigger, action_type, payload_json, value_key
                FROM actions
                WHERE control_id = ?
                """,
                (control_id,),
            ).fetchall()
        return [Action(**dict(row)) for row in rows]

    def get_control_state(self, control_id: int) -> Optional[ControlState]:
        with self._db.connect() as conn:
            row = conn.execute(
                "SELECT control_id, value FROM control_state WHERE control_id = ?",
                (control_id,),
            ).fetchone()
        return ControlState(**dict(row)) if row else None

    def set_control_state(self, control_id: int, value: str) -> None:
        with self._db.connect() as conn:
            conn.execute(
                """
                INSERT INTO control_state (control_id, value, updated_at)
                VALUES (?, ?, datetime('now'))
                ON CONFLICT(control_id) DO UPDATE SET
                    value = excluded.value,
                    updated_at = excluded.updated_at
                """,
                (control_id, value),
            )
            conn.commit()

    def get_setting(self, key: str) -> Optional[Setting]:
        with self._db.connect() as conn:
            row = conn.execute("SELECT key, value FROM settings WHERE key = ?", (key,)).fetchone()
        return Setting(**dict(row)) if row else None

    def set_setting(self, key: str, value: str) -> None:
        with self._db.connect() as conn:
            conn.execute(
                """
                INSERT INTO settings (key, value, updated_at)
                VALUES (?, ?, datetime('now'))
                ON CONFLICT(key) DO UPDATE SET
                    value = excluded.value,
                    updated_at = excluded.updated_at
                """,
                (key, value),
            )
            conn.commit()

    def insert_seed_data(self) -> None:
        with self._db.connect() as conn:
            existing = conn.execute("SELECT COUNT(*) AS c FROM screens").fetchone()
            if existing and existing["c"] > 0:
                return

            conn.executescript("""
            INSERT INTO screens (id, name, order_index, bg_color, bg_image_path, bg_image_mode, created_at, updated_at)
            VALUES
                (1, 'Main', 1, '#101820', 'resources/icons/bg_grid.svg', 'stretch', datetime('now'), datetime('now')),
                (2, 'System', 2, '#0f172a', NULL, NULL, datetime('now'), datetime('now')),
                (3, 'Settings - Agent', 3, '#0f172a', NULL, NULL, datetime('now'), datetime('now')),
                (4, 'Settings - Theme', 4, '#0f172a', NULL, NULL, datetime('now'), datetime('now'));

            INSERT INTO controls (
                id, screen_id, type, label, row, col, rowspan, colspan,
                min_value, max_value, step, is_continuous, default_value, persist_state,
                style_bg, style_fg, icon_path, width_hint, height_hint, setting_key, placeholder_text,
                button_svg_path, slider_track_path, slider_knob_path,
                created_at, updated_at
            ) VALUES
                (1, 1, 'button', 'Casual', 0, 0, 1, 1, NULL, NULL, NULL, NULL, NULL, 0,
                 '#0ea5e9', '#ffffff', NULL, 1, 1, NULL, NULL,
                 'resources/icons/button_blue.svg', NULL, NULL, datetime('now'), datetime('now')),
                (2, 1, 'button', 'Gaming', 0, 1, 1, 1, NULL, NULL, NULL, NULL, NULL, 0,
                 '#2563eb', '#ffffff', NULL, 1, 1, NULL, NULL,
                 'resources/icons/button_blue.svg', NULL, NULL, datetime('now'), datetime('now')),
                (3, 1, 'button', 'Audio Restart', 0, 2, 1, 1, NULL, NULL, NULL, NULL, NULL, 0,
                 '#dc2626', '#ffffff', NULL, 1, 1, NULL, NULL,
                 'resources/icons/button_red.svg', NULL, NULL, datetime('now'), datetime('now')),
                (4, 1, 'button', 'S Headphones', 0, 3, 1, 1, NULL, NULL, NULL, NULL, NULL, 0,
                 '#16a34a', '#ffffff', NULL, 1, 1, NULL, NULL,
                 'resources/icons/button_green.svg', NULL, NULL, datetime('now'), datetime('now')),
                (5, 1, 'button', 'S Gaming', 0, 4, 1, 1, NULL, NULL, NULL, NULL, NULL, 0,
                 '#16a34a', '#ffffff', NULL, 1, 1, NULL, NULL,
                 'resources/icons/button_green.svg', NULL, NULL, datetime('now'), datetime('now')),
                (6, 1, 'button', 'S Casual', 0, 5, 1, 1, NULL, NULL, NULL, NULL, NULL, 0,
                 '#16a34a', '#ffffff', NULL, 1, 1, NULL, NULL,
                 'resources/icons/button_green.svg', NULL, NULL, datetime('now'), datetime('now')),
                (7, 1, 'slider_vertical', 'Web', 1, 0, 1, 1, -60, 12, 1, 1, '0', 1,
                 '#333333', '#ffffff', NULL, 1, 1, NULL, NULL,
                 NULL, 'resources/icons/fader_track.svg', 'resources/icons/fader_knob.svg',
                 datetime('now'), datetime('now')),
                (8, 1, 'slider_vertical', 'Games', 1, 1, 1, 1, -60, 12, 1, 1, '0', 1,
                 '#333333', '#ffffff', NULL, 1, 1, NULL, NULL,
                 NULL, 'resources/icons/fader_track.svg', 'resources/icons/fader_knob.svg',
                 datetime('now'), datetime('now')),
                (9, 1, 'slider_vertical', 'Comms', 1, 2, 1, 1, -60, 12, 1, 1, '0', 1,
                 '#333333', '#ffffff', NULL, 1, 1, NULL, NULL,
                 NULL, 'resources/icons/fader_track.svg', 'resources/icons/fader_knob.svg',
                 datetime('now'), datetime('now')),
                (10, 1, 'slider_vertical', 'Vol', 1, 3, 1, 1, -60, 12, 1, 1, '0', 1,
                 '#333333', '#ffffff', NULL, 1, 1, NULL, NULL,
                 NULL, 'resources/icons/fader_track.svg', 'resources/icons/fader_knob.svg',
                 datetime('now'), datetime('now')),
                (19, 2, 'button', 'Settings', 0, 0, 1, 2, NULL, NULL, NULL, NULL, NULL, 0,
                 '#334155', '#ffffff', NULL, 2, 1, NULL, NULL,
                 'resources/icons/button_n.svg', NULL, NULL, datetime('now'), datetime('now')),
                (20, 2, 'button', 'Restart Pi', 0, 2, 1, 2, NULL, NULL, NULL, NULL, NULL, 0,
                 '#dc2626', '#ffffff', NULL, 2, 1, NULL, NULL,
                 'resources/icons/button_red.svg', NULL, NULL, datetime('now'), datetime('now')),
                (21, 2, 'button', 'Shutdown Pi', 1, 0, 1, 4, NULL, NULL, NULL, NULL, NULL, 0,
                 '#7f1d1d', '#ffffff', NULL, 4, 1, NULL, NULL,
                 'resources/icons/button_red.svg', NULL, NULL, datetime('now'), datetime('now')),
                (30, 3, 'button', 'Agent', 0, 0, 1, 1, NULL, NULL, NULL, NULL, NULL, 0,
                 '#334155', '#ffffff', NULL, 1, 1, NULL, NULL,
                 'resources/icons/button_n.svg', NULL, NULL, datetime('now'), datetime('now')),
                (31, 3, 'button', 'Theme', 0, 1, 1, 1, NULL, NULL, NULL, NULL, NULL, 0,
                 '#334155', '#ffffff', NULL, 1, 1, NULL, NULL,
                 'resources/icons/button_n.svg', NULL, NULL, datetime('now'), datetime('now')),
                (32, 3, 'button', 'Home', 0, 3, 1, 1, NULL, NULL, NULL, NULL, NULL, 0,
                 '#0ea5e9', '#ffffff', NULL, 1, 1, NULL, NULL,
                 'resources/icons/button_blue.svg', NULL, NULL, datetime('now'), datetime('now')),
                (33, 3, 'setting_text', 'Agent Host', 1, 0, 1, 4, NULL, NULL, NULL, NULL, NULL, 0,
                 '#1e293b', '#ffffff', NULL, 4, 1, 'agent_host', '127.0.0.1',
                 'resources/icons/button_n.svg', NULL, NULL, datetime('now'), datetime('now')),
                (34, 3, 'setting_text', 'Agent Port', 2, 0, 1, 4, NULL, NULL, NULL, NULL, NULL, 0,
                 '#1e293b', '#ffffff', NULL, 4, 1, 'agent_port', '8765',
                 'resources/icons/button_n.svg', NULL, NULL, datetime('now'), datetime('now')),
                (35, 3, 'setting_text', 'Agent Token', 3, 0, 1, 4, NULL, NULL, NULL, NULL, NULL, 0,
                 '#1e293b', '#ffffff', NULL, 4, 1, 'agent_token', '',
                 'resources/icons/button_n.svg', NULL, NULL, datetime('now'), datetime('now')),
                (36, 3, 'setting_slider', 'Brightness', 4, 0, 1, 4, 20, 100, 1, 1, '80', 1,
                 '#334155', '#ffffff', NULL, 4, 1, 'brightness', NULL,
                 NULL, 'resources/icons/fader_track.svg', 'resources/icons/fader_knob.svg',
                 datetime('now'), datetime('now')),
                (37, 3, 'setting_dropdown', 'Resolution', 5, 0, 1, 4, NULL, NULL, NULL, NULL, '1024x600', 0,
                 '#1e293b', '#ffffff', NULL, 4, 1, 'resolution', NULL,
                 'resources/icons/button_n.svg', NULL, NULL, datetime('now'), datetime('now'));

            INSERT INTO controls (
                id, screen_id, type, label, row, col, rowspan, colspan,
                min_value, max_value, step, is_continuous, default_value, persist_state,
                style_bg, style_fg, icon_path, width_hint, height_hint, setting_key, placeholder_text,
                button_svg_path, slider_track_path, slider_knob_path,
                created_at, updated_at
            ) VALUES
                (40, 4, 'button', 'Agent', 0, 0, 1, 1, NULL, NULL, NULL, NULL, NULL, 0,
                 '#334155', '#ffffff', NULL, 1, 1, NULL, NULL,
                 'resources/icons/button_n.svg', NULL, NULL, datetime('now'), datetime('now')),
                (41, 4, 'button', 'Theme', 0, 1, 1, 1, NULL, NULL, NULL, NULL, NULL, 0,
                 '#334155', '#ffffff', NULL, 1, 1, NULL, NULL,
                 'resources/icons/button_n.svg', NULL, NULL, datetime('now'), datetime('now')),
                (42, 4, 'button', 'Home', 0, 3, 1, 1, NULL, NULL, NULL, NULL, NULL, 0,
                 '#0ea5e9', '#ffffff', NULL, 1, 1, NULL, NULL,
                 'resources/icons/button_blue.svg', NULL, NULL, datetime('now'), datetime('now')),
                (43, 4, 'setting_text', 'Theme Font', 1, 0, 1, 4, NULL, NULL, NULL, NULL, NULL, 0,
                 '#1e293b', '#ffffff', NULL, 4, 1, 'theme_font_family', 'DejaVu Sans',
                 'resources/icons/button_n.svg', NULL, NULL, datetime('now'), datetime('now')),
                (44, 4, 'setting_text', 'Theme Font Size', 2, 0, 1, 4, NULL, NULL, NULL, NULL, NULL, 0,
                 '#1e293b', '#ffffff', NULL, 4, 1, 'theme_font_size', '18',
                 'resources/icons/button_n.svg', NULL, NULL, datetime('now'), datetime('now')),
                (45, 4, 'setting_text', 'Theme Text Color', 3, 0, 1, 4, NULL, NULL, NULL, NULL, NULL, 0,
                 '#1e293b', '#ffffff', NULL, 4, 1, 'theme_text_color', '#e2e8f0',
                 'resources/icons/button_n.svg', NULL, NULL, datetime('now'), datetime('now')),
                (46, 4, 'setting_text', 'Theme Accent', 4, 0, 1, 4, NULL, NULL, NULL, NULL, NULL, 0,
                 '#1e293b', '#ffffff', NULL, 4, 1, 'theme_accent_color', '#38bdf8',
                 'resources/icons/button_n.svg', NULL, NULL, datetime('now'), datetime('now')),
                (47, 4, 'setting_text', 'Slider Groove', 5, 0, 1, 4, NULL, NULL, NULL, NULL, NULL, 0,
                 '#1e293b', '#ffffff', NULL, 4, 1, 'theme_slider_groove', '#334155',
                 'resources/icons/button_n.svg', NULL, NULL, datetime('now'), datetime('now')),
                (48, 4, 'setting_text', 'Slider Handle', 6, 0, 1, 4, NULL, NULL, NULL, NULL, NULL, 0,
                 '#1e293b', '#ffffff', NULL, 4, 1, 'theme_slider_handle', '#f59e0b',
                 'resources/icons/button_n.svg', NULL, NULL, datetime('now'), datetime('now'));

            INSERT INTO actions (id, control_id, trigger, action_type, payload_json, value_key, created_at, updated_at)
            VALUES
                (1, 1, 'press', 'run_app', '{"action":"run_app","payload":{"app":"C:\\\\Windows\\\\System32\\\\WindowsPowerShell\\\\v1.0\\\\powershell.exe","args":["-ExecutionPolicy","Bypass","-File","C:\\\\AppScripts\\\\PowerShell\\\\Monitor\\\\Casual.ps1"]}}', NULL, datetime('now'), datetime('now')),
                (2, 2, 'press', 'run_app', '{"action":"run_app","payload":{"app":"C:\\\\Windows\\\\System32\\\\WindowsPowerShell\\\\v1.0\\\\powershell.exe","args":["-ExecutionPolicy","Bypass","-File","C:\\\\AppScripts\\\\PowerShell\\\\Monitor\\\\Gaming.ps1"]}}', NULL, datetime('now'), datetime('now')),
                (3, 3, 'press', 'voicemeeter_command', '{"action":"voicemeeter_command","payload":{"command":"restart"}}', NULL, datetime('now'), datetime('now')),
                (4, 4, 'press', 'voicemeeter_apply', '{"action":"voicemeeter_apply","payload":{"settings":{"bus-0":{"mute":true},"bus-1":{"mute":false},"bus-2":{"mute":true}}}}', NULL, datetime('now'), datetime('now')),
                (5, 5, 'press', 'voicemeeter_apply', '{"action":"voicemeeter_apply","payload":{"settings":{"bus-0":{"mute":false},"bus-1":{"mute":true},"bus-2":{"mute":true}}}}', NULL, datetime('now'), datetime('now')),
                (6, 6, 'press', 'voicemeeter_apply', '{"action":"voicemeeter_apply","payload":{"settings":{"bus-0":{"mute":true},"bus-1":{"mute":true},"bus-2":{"mute":false}}}}', NULL, datetime('now'), datetime('now')),
                (7, 7, 'value_release', 'voicemeeter_apply', '{"action":"voicemeeter_apply","payload":{"settings":{"strip-5":{"gain":"${value}"}}}}', NULL, datetime('now'), datetime('now')),
                (8, 8, 'value_release', 'voicemeeter_apply', '{"action":"voicemeeter_apply","payload":{"settings":{"strip-6":{"gain":"${value}"}}}}', NULL, datetime('now'), datetime('now')),
                (9, 9, 'value_release', 'voicemeeter_apply', '{"action":"voicemeeter_apply","payload":{"settings":{"strip-7":{"gain":"${value}"}}}}', NULL, datetime('now'), datetime('now')),
                (10, 10, 'value_release', 'voicemeeter_group_bus_gain', '{"action":"voicemeeter_group_bus_gain","payload":{"gain":"${value}"}}', NULL, datetime('now'), datetime('now')),
                (11, 19, 'press', 'navigate_screen', '{"screen_id":3}', NULL, datetime('now'), datetime('now')),
                (12, 20, 'press', 'restart_pi', '{"mode":"restart"}', NULL, datetime('now'), datetime('now')),
                (13, 21, 'press', 'shutdown_pi', '{"mode":"shutdown"}', NULL, datetime('now'), datetime('now')),
                (14, 30, 'press', 'navigate_screen', '{"screen_id":3}', NULL, datetime('now'), datetime('now')),
                (15, 31, 'press', 'navigate_screen', '{"screen_id":4}', NULL, datetime('now'), datetime('now')),
                (16, 32, 'press', 'navigate_screen', '{"screen_id":1}', NULL, datetime('now'), datetime('now')),
                (17, 40, 'press', 'navigate_screen', '{"screen_id":3}', NULL, datetime('now'), datetime('now')),
                (18, 41, 'press', 'navigate_screen', '{"screen_id":4}', NULL, datetime('now'), datetime('now')),
                (19, 42, 'press', 'navigate_screen', '{"screen_id":1}', NULL, datetime('now'), datetime('now')),
                (20, 7, 'value_change', 'voicemeeter_apply', '{"action":"voicemeeter_apply","payload":{"settings":{"strip-5":{"gain":"${value}"}}}}', NULL, datetime('now'), datetime('now')),
                (21, 8, 'value_change', 'voicemeeter_apply', '{"action":"voicemeeter_apply","payload":{"settings":{"strip-6":{"gain":"${value}"}}}}', NULL, datetime('now'), datetime('now')),
                (22, 9, 'value_change', 'voicemeeter_apply', '{"action":"voicemeeter_apply","payload":{"settings":{"strip-7":{"gain":"${value}"}}}}', NULL, datetime('now'), datetime('now')),
                (23, 10, 'value_change', 'voicemeeter_group_bus_gain', '{"action":"voicemeeter_group_bus_gain","payload":{"gain":"${value}"}}', NULL, datetime('now'), datetime('now'));

            INSERT INTO settings (key, value, updated_at)
            VALUES
                ('agent_host', '127.0.0.1', datetime('now')),
                ('agent_port', '8765', datetime('now')),
                ('agent_token', '', datetime('now')),
                ('brightness', '80', datetime('now')),
                ('resolution', '1024x600', datetime('now')),
                ('theme_font_family', 'DejaVu Sans', datetime('now')),
                ('theme_font_size', '18', datetime('now')),
                ('theme_spacing', '12', datetime('now')),
                ('theme_button_radius', '8', datetime('now')),
                ('theme_text_color', '#e2e8f0', datetime('now')),
                ('theme_accent_color', '#38bdf8', datetime('now')),
                ('theme_slider_groove', '#334155', datetime('now')),
                ('theme_slider_handle', '#f59e0b', datetime('now'));
            """)
            conn.commit()
