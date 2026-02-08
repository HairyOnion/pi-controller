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
                       persist_state, style_bg, style_fg, icon_path, width_hint, height_hint
                       , setting_key, placeholder_text
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
                (2, 'Apps', 2, '#1b1b1b', NULL, NULL, datetime('now'), datetime('now')),
                (3, 'Settings', 3, '#0f172a', NULL, NULL, datetime('now'), datetime('now'));

            INSERT INTO controls (
                id, screen_id, type, label, row, col, rowspan, colspan,
                min_value, max_value, step, is_continuous, default_value, persist_state,
                style_bg, style_fg, icon_path, width_hint, height_hint, setting_key, placeholder_text,
                created_at, updated_at
            ) VALUES
                (1, 1, 'button', 'Open Notepad', 0, 0, 1, 1, NULL, NULL, NULL, NULL, NULL, 0,
                 '#2d6cdf', '#ffffff', 'resources/icons/app.svg', 1, 1, NULL, NULL, datetime('now'), datetime('now')),
                (2, 1, 'toggle', 'Caps Lock', 0, 1, 1, 1, NULL, NULL, NULL, NULL, 'off', 1,
                 '#444444', '#ffffff', 'resources/icons/toggle.svg', 1, 1, NULL, NULL, datetime('now'), datetime('now')),
                (3, 2, 'slider', 'Volume', 0, 0, 1, 2, 0, 10, 1, 0, '5', 1,
                 '#333333', '#ffffff', NULL, 2, 1, NULL, NULL, datetime('now'), datetime('now')),
                (4, 1, 'button', 'Settings', 0, 2, 1, 1, NULL, NULL, NULL, NULL, NULL, 0,
                 '#0ea5e9', '#ffffff', 'resources/icons/gear.svg', 1, 1, NULL, NULL, datetime('now'), datetime('now')),
                (17, 1, 'button', 'Info', 0, 3, 1, 1, NULL, NULL, NULL, NULL, NULL, 0,
                 '#334155', '#ffffff', 'resources/icons/info.svg', 1, 1, NULL, NULL, datetime('now'), datetime('now')),
                (16, 1, 'slider_vertical', 'Game', 1, 1, 1, 1, 0, 100, 5, 0, '50', 0,
                 '#333333', '#ffffff', NULL, 1, 1, NULL, NULL, datetime('now'), datetime('now')),
                (19, 1, 'slider_vertical', 'Media', 1, 0, 1, 1, 0, 100, 5, 0, '50', 0,
                 '#333333', '#ffffff', NULL, 1, 1, NULL, NULL, datetime('now'), datetime('now')),
                (20, 1, 'slider_vertical', 'Chat', 1, 2, 1, 1, 0, 100, 5, 0, '50', 0,
                 '#333333', '#ffffff', NULL, 1, 1, NULL, NULL, datetime('now'), datetime('now')),
                (21, 1, 'slider_vertical', 'Main', 1, 3, 1, 1, 0, 100, 5, 0, '50', 0,
                 '#333333', '#ffffff', NULL, 1, 1, NULL, NULL, datetime('now'), datetime('now')),
                (5, 3, 'setting_text', 'Agent Host', 0, 0, 1, 2, NULL, NULL, NULL, NULL, NULL, 0,
                 '#1e293b', '#ffffff', NULL, 2, 1, 'agent_host', '127.0.0.1', datetime('now'), datetime('now')),
                (6, 3, 'setting_text', 'Agent Port', 1, 0, 1, 2, NULL, NULL, NULL, NULL, NULL, 0,
                 '#1e293b', '#ffffff', NULL, 2, 1, 'agent_port', '8765', datetime('now'), datetime('now')),
                (7, 3, 'setting_text', 'Agent Token', 2, 0, 1, 2, NULL, NULL, NULL, NULL, NULL, 0,
                 '#1e293b', '#ffffff', NULL, 2, 1, 'agent_token', '', datetime('now'), datetime('now')),
                (8, 3, 'setting_slider', 'Brightness', 3, 0, 1, 2, 0, 100, 1, 1, '80', 1,
                 '#334155', '#ffffff', NULL, 2, 1, 'brightness', NULL, datetime('now'), datetime('now')),
                (9, 3, 'button', 'Back', 4, 0, 1, 2, NULL, NULL, NULL, NULL, NULL, 0,
                 '#64748b', '#ffffff', NULL, 2, 1, NULL, NULL, datetime('now'), datetime('now'));

            INSERT INTO controls (
                id, screen_id, type, label, row, col, rowspan, colspan,
                min_value, max_value, step, is_continuous, default_value, persist_state,
                style_bg, style_fg, icon_path, width_hint, height_hint, setting_key, placeholder_text,
                created_at, updated_at
            ) VALUES
                (10, 3, 'setting_text', 'Theme Font', 5, 0, 1, 2, NULL, NULL, NULL, NULL, NULL, 0,
                 '#1e293b', '#ffffff', NULL, 2, 1, 'theme_font_family', 'DejaVu Sans', datetime('now'), datetime('now')),
                (11, 3, 'setting_text', 'Theme Font Size', 6, 0, 1, 2, NULL, NULL, NULL, NULL, NULL, 0,
                 '#1e293b', '#ffffff', NULL, 2, 1, 'theme_font_size', '18', datetime('now'), datetime('now')),
                (12, 3, 'setting_text', 'Theme Text Color', 7, 0, 1, 2, NULL, NULL, NULL, NULL, NULL, 0,
                 '#1e293b', '#ffffff', NULL, 2, 1, 'theme_text_color', '#e2e8f0', datetime('now'), datetime('now')),
                (13, 3, 'setting_text', 'Theme Accent', 8, 0, 1, 2, NULL, NULL, NULL, NULL, NULL, 0,
                 '#1e293b', '#ffffff', NULL, 2, 1, 'theme_accent_color', '#38bdf8', datetime('now'), datetime('now')),
                (14, 3, 'setting_text', 'Slider Groove', 9, 0, 1, 2, NULL, NULL, NULL, NULL, NULL, 0,
                 '#1e293b', '#ffffff', NULL, 2, 1, 'theme_slider_groove', '#334155', datetime('now'), datetime('now')),
                (15, 3, 'setting_text', 'Slider Handle', 10, 0, 1, 2, NULL, NULL, NULL, NULL, NULL, 0,
                 '#1e293b', '#ffffff', NULL, 2, 1, 'theme_slider_handle', '#f59e0b', datetime('now'), datetime('now')),
                (18, 3, 'setting_dropdown', 'Resolution', 11, 0, 1, 2, NULL, NULL, NULL, NULL, '1024x600', 0,
                 '#1e293b', '#ffffff', NULL, 2, 1, 'resolution', NULL, datetime('now'), datetime('now'));

            INSERT INTO actions (id, control_id, trigger, action_type, payload_json, value_key, created_at, updated_at)
            VALUES
                (1, 1, 'press', 'run_app', '{"action":"run_app","payload":{"app":"notepad"}}', NULL, datetime('now'), datetime('now')),
                (2, 2, 'toggle_on', 'key_press', '{"action":"key_press","payload":{"keys":["ctrl","shift","s"]}}', NULL, datetime('now'), datetime('now')),
                (3, 2, 'toggle_off', 'key_press', '{"action":"key_press","payload":{"keys":["ctrl","s"]}}', NULL, datetime('now'), datetime('now')),
                (4, 3, 'value_release', 'run_app', '{"action":"run_app","payload":{"app":"your_app","args":["--volume","${value}"]}}', 'value', datetime('now'), datetime('now')),
                (5, 4, 'press', 'navigate_screen', '{"screen_id":3}', NULL, datetime('now'), datetime('now')),
                (7, 17, 'press', 'show_resolution', '{"action":"show_resolution","payload":{}}', NULL, datetime('now'), datetime('now')),
                (6, 9, 'press', 'navigate_screen', '{"screen_id":1}', NULL, datetime('now'), datetime('now'));

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
