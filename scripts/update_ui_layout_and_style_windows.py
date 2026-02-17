from __future__ import annotations

import argparse
import os
import sqlite3
from pathlib import Path


def default_db_path() -> Path:
    env = os.environ.get("PI_TC_DB")
    if env:
        return Path(env)
    return Path.home() / "pi_controller" / "app.db"


def apply_updates(db_path: Path) -> None:
    if not db_path.exists():
        raise FileNotFoundError(f"Database not found: {db_path}")

    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()
        cur.execute(
            """
            UPDATE controls
            SET style_fg = '#000000',
                updated_at = datetime('now')
            WHERE screen_id = 1
              AND id IN (4, 5, 6);
            """
        )
        green_updated = cur.rowcount

        cur.execute(
            """
            UPDATE controls
            SET row = 0,
                col = 0,
                rowspan = 1,
                colspan = 2,
                width_hint = 2,
                height_hint = 1,
                updated_at = datetime('now')
            WHERE id = 19 AND screen_id = 2;
            """
        )
        settings_updated = cur.rowcount

        cur.execute(
            """
            UPDATE controls
            SET row = 0,
                col = 2,
                rowspan = 1,
                colspan = 2,
                width_hint = 2,
                height_hint = 1,
                updated_at = datetime('now')
            WHERE id = 20 AND screen_id = 2;
            """
        )
        restart_updated = cur.rowcount

        cur.execute(
            """
            UPDATE controls
            SET row = 0,
                col = 4,
                rowspan = 1,
                colspan = 2,
                width_hint = 2,
                height_hint = 1,
                updated_at = datetime('now')
            WHERE id = 21 AND screen_id = 2;
            """
        )
        shutdown_updated = cur.rowcount
        conn.commit()

    print(f"Updated DB: {db_path}")
    print(f"Green button text rows updated: {green_updated}")
    print(f"System Settings button updated: {settings_updated}")
    print(f"System Restart button updated: {restart_updated}")
    print(f"System Shutdown button updated: {shutdown_updated}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Apply UI style/layout updates to Pi Touch Controller DB.")
    parser.add_argument("--db", type=Path, default=default_db_path(), help="Path to app.db")
    args = parser.parse_args()
    apply_updates(args.db)


if __name__ == "__main__":
    main()
