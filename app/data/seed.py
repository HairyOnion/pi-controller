from __future__ import annotations

import os

from .db import Database
from .repository import Repository


def main() -> None:
    db_path = os.environ.get("PI_TC_DB", "/home/pi/pi_touch_controller/app.db")
    db = Database(db_path)
    db.reset()
    db.migrate()
    repo = Repository(db)
    repo.insert_seed_data()
    print(f"Seeded database at {db_path}")


if __name__ == "__main__":
    main()
