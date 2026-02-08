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
]
