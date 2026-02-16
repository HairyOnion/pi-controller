from __future__ import annotations

import sqlite3
from pathlib import Path


def main() -> int:
    db_path = Path("C:/home/hairyonion/pi_controller/app.db")
    if not db_path.exists():
        print(f"DB not found: {db_path}")
        return 1

    conn = sqlite3.connect(str(db_path))
    try:
        cur = conn.cursor()
        cur.execute("PRAGMA table_info(controls);")
        columns = {row[1] for row in cur.fetchall()}
        if "button_svg_path" not in columns:
            cur.execute("ALTER TABLE controls ADD COLUMN button_svg_path TEXT;")
        if "slider_track_path" not in columns:
            cur.execute("ALTER TABLE controls ADD COLUMN slider_track_path TEXT;")
        if "slider_knob_path" not in columns:
            cur.execute("ALTER TABLE controls ADD COLUMN slider_knob_path TEXT;")
        cur.execute(
            """
            UPDATE controls
            SET button_svg_path = COALESCE(button_svg_path, 'resources/icons/button_n.svg')
            WHERE type IN ('button', 'toggle', 'setting_text', 'setting_dropdown')
              AND (button_svg_path IS NULL OR button_svg_path = '');
            """
        )
        cur.execute(
            """
            UPDATE controls
            SET slider_track_path = COALESCE(slider_track_path, 'resources/icons/fader_track.svg'),
                slider_knob_path = COALESCE(slider_knob_path, 'resources/icons/fader_knob.svg')
            WHERE type IN ('slider', 'slider_vertical', 'setting_slider')
              AND (slider_track_path IS NULL OR slider_track_path = ''
                   OR slider_knob_path IS NULL OR slider_knob_path = '');
            """
        )
        conn.commit()
    finally:
        conn.close()

    print("Updated SVG paths for Windows dev DB.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
