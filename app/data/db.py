from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Iterator

from .schema import MIGRATIONS


class Database:
    def __init__(self, path: str) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        return conn

    def migrate(self) -> None:
        with self.connect() as conn:
            conn.execute("CREATE TABLE IF NOT EXISTS schema_version (version INTEGER NOT NULL)")
            row = conn.execute("SELECT version FROM schema_version ORDER BY version DESC LIMIT 1").fetchone()
            current = int(row[0]) if row else 0
            for version, sql in MIGRATIONS:
                if version > current:
                    if version == 5:
                        self._ensure_control_svg_columns(conn)
                    elif sql.strip():
                        conn.executescript(sql)
                    conn.execute("INSERT INTO schema_version (version) VALUES (?)", (version,))
            conn.commit()

    def _ensure_control_svg_columns(self, conn: sqlite3.Connection) -> None:
        rows = conn.execute("PRAGMA table_info(controls);").fetchall()
        columns = {row[1] for row in rows}
        if "button_svg_path" not in columns:
            conn.execute("ALTER TABLE controls ADD COLUMN button_svg_path TEXT;")
        if "slider_track_path" not in columns:
            conn.execute("ALTER TABLE controls ADD COLUMN slider_track_path TEXT;")
        if "slider_knob_path" not in columns:
            conn.execute("ALTER TABLE controls ADD COLUMN slider_knob_path TEXT;")

    def reset(self) -> None:
        with self.connect() as conn:
            conn.executescript("""
            DROP TABLE IF EXISTS actions;
            DROP TABLE IF EXISTS control_state;
            DROP TABLE IF EXISTS controls;
            DROP TABLE IF EXISTS screens;
            DROP TABLE IF EXISTS settings;
            DROP TABLE IF EXISTS schema_version;
            """)
            conn.commit()
