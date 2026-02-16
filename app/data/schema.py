from __future__ import annotations

MIGRATIONS = [
    (1, """
    CREATE TABLE IF NOT EXISTS screens (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        order_index INTEGER NOT NULL,
        bg_color TEXT,
        bg_image_path TEXT,
        created_at TEXT,
        updated_at TEXT
    );

    CREATE TABLE IF NOT EXISTS controls (
        id INTEGER PRIMARY KEY,
        screen_id INTEGER NOT NULL,
        type TEXT NOT NULL,
        label TEXT,
        row INTEGER,
        col INTEGER,
        rowspan INTEGER,
        colspan INTEGER,
        min_value REAL,
        max_value REAL,
        step REAL,
        is_continuous INTEGER,
        default_value TEXT,
        persist_state INTEGER,
        style_bg TEXT,
        style_fg TEXT,
        icon_path TEXT,
        width_hint INTEGER,
        height_hint INTEGER,
        created_at TEXT,
        updated_at TEXT,
        FOREIGN KEY(screen_id) REFERENCES screens(id)
    );

    CREATE TABLE IF NOT EXISTS actions (
        id INTEGER PRIMARY KEY,
        control_id INTEGER NOT NULL,
        trigger TEXT NOT NULL,
        action_type TEXT NOT NULL,
        payload_json TEXT NOT NULL,
        created_at TEXT,
        updated_at TEXT,
        FOREIGN KEY(control_id) REFERENCES controls(id)
    );

    CREATE TABLE IF NOT EXISTS control_state (
        control_id INTEGER PRIMARY KEY,
        value TEXT,
        updated_at TEXT,
        FOREIGN KEY(control_id) REFERENCES controls(id)
    );

    CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT,
        updated_at TEXT
    );
    """),
    (2, """
    ALTER TABLE controls ADD COLUMN setting_key TEXT;
    ALTER TABLE controls ADD COLUMN placeholder_text TEXT;
    """),
    (3, """
    ALTER TABLE actions ADD COLUMN value_key TEXT;
    """),
    (4, """
    ALTER TABLE screens ADD COLUMN bg_image_mode TEXT;
    """),
    (5, """
    ALTER TABLE controls ADD COLUMN button_svg_path TEXT;
    ALTER TABLE controls ADD COLUMN slider_track_path TEXT;
    ALTER TABLE controls ADD COLUMN slider_knob_path TEXT;
    """),
    (6, """
    UPDATE controls
    SET button_svg_path = COALESCE(button_svg_path, 'resources/icons/button_n.svg')
    WHERE type IN ('button', 'toggle', 'setting_text', 'setting_dropdown')
      AND (button_svg_path IS NULL OR button_svg_path = '');

    UPDATE controls
    SET slider_track_path = COALESCE(slider_track_path, 'resources/icons/fader_track.svg'),
        slider_knob_path = COALESCE(slider_knob_path, 'resources/icons/fader_knob.svg')
    WHERE type IN ('slider', 'slider_vertical', 'setting_slider')
      AND (slider_track_path IS NULL OR slider_track_path = ''
           OR slider_knob_path IS NULL OR slider_knob_path = '');
    """),
    (7, """
    DELETE FROM actions;
    DELETE FROM control_state;
    DELETE FROM controls;
    DELETE FROM screens;

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
         'resources/icons/button_n.svg', NULL, NULL, datetime('now'), datetime('now')),
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
    """),
    (8, """
    UPDATE controls
    SET label = 'Audio Restart'
    WHERE id = 3 AND screen_id = 1 AND type = 'button';

    UPDATE actions
    SET payload_json = '{"action":"voicemeeter_command","payload":{"command":"restart"}}'
    WHERE id = 3
      AND control_id = 3
      AND trigger = 'press'
      AND action_type = 'voicemeeter_command';
    """),
    (9, """
    UPDATE controls
    SET min_value = 20
    WHERE type = 'setting_slider'
      AND setting_key = 'brightness'
      AND (min_value IS NULL OR min_value < 20);

    UPDATE settings
    SET value = '50', updated_at = datetime('now')
    WHERE key = 'brightness'
      AND (
        CAST(COALESCE(value, '0') AS INTEGER) < 20
        OR CAST(COALESCE(value, '0') AS INTEGER) > 100
      );
    """),
    (10, """
    UPDATE controls
    SET is_continuous = 1
    WHERE id IN (7, 8, 9, 10)
      AND screen_id = 1
      AND type = 'slider_vertical';

    INSERT INTO actions (control_id, trigger, action_type, payload_json, value_key, created_at, updated_at)
    SELECT 7, 'value_change', 'voicemeeter_apply', '{"action":"voicemeeter_apply","payload":{"settings":{"strip-5":{"gain":"${value}"}}}}', NULL, datetime('now'), datetime('now')
    WHERE NOT EXISTS (
      SELECT 1 FROM actions WHERE control_id = 7 AND trigger = 'value_change' AND action_type = 'voicemeeter_apply'
    );

    INSERT INTO actions (control_id, trigger, action_type, payload_json, value_key, created_at, updated_at)
    SELECT 8, 'value_change', 'voicemeeter_apply', '{"action":"voicemeeter_apply","payload":{"settings":{"strip-6":{"gain":"${value}"}}}}', NULL, datetime('now'), datetime('now')
    WHERE NOT EXISTS (
      SELECT 1 FROM actions WHERE control_id = 8 AND trigger = 'value_change' AND action_type = 'voicemeeter_apply'
    );

    INSERT INTO actions (control_id, trigger, action_type, payload_json, value_key, created_at, updated_at)
    SELECT 9, 'value_change', 'voicemeeter_apply', '{"action":"voicemeeter_apply","payload":{"settings":{"strip-7":{"gain":"${value}"}}}}', NULL, datetime('now'), datetime('now')
    WHERE NOT EXISTS (
      SELECT 1 FROM actions WHERE control_id = 9 AND trigger = 'value_change' AND action_type = 'voicemeeter_apply'
    );

    INSERT INTO actions (control_id, trigger, action_type, payload_json, value_key, created_at, updated_at)
    SELECT 10, 'value_change', 'voicemeeter_group_bus_gain', '{"action":"voicemeeter_group_bus_gain","payload":{"gain":"${value}"}}', NULL, datetime('now'), datetime('now')
    WHERE NOT EXISTS (
      SELECT 1 FROM actions WHERE control_id = 10 AND trigger = 'value_change' AND action_type = 'voicemeeter_group_bus_gain'
    );
    """),
]
