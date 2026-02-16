from __future__ import annotations

import os
from pathlib import Path

from .data.db import Database
from .data.repository import Repository
from .settings.manager import SettingsManager
from .actions.dispatcher import ActionDispatcher
from .ui.app_window import AppWindow
from .utils.logging import setup_logging


def main() -> None:
    setup_logging()
    db_path = os.environ.get("PI_TC_DB", str(Path.home() / "pi_controller" / "app.db"))
    db = Database(db_path)
    db.migrate()
    Repository(db).insert_seed_data()

    settings = SettingsManager(db)
    dispatcher = ActionDispatcher(settings)

    window = AppWindow(db=db, settings=settings, dispatcher=dispatcher)
    window.run()


if __name__ == "__main__":
    main()
#
