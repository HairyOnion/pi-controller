from __future__ import annotations

from .data.db import Database
from .data.repository import Repository
from .settings.manager import SettingsManager
from .actions.dispatcher import ActionDispatcher
from .ui.app_window import AppWindow


def main() -> None:
    db = Database("/home/pi/pi_touch_controller/app.db")
    db.migrate()
    Repository(db).insert_seed_data()

    settings = SettingsManager(db)
    dispatcher = ActionDispatcher(settings)

    window = AppWindow(db=db, settings=settings, dispatcher=dispatcher)
    window.run()


if __name__ == "__main__":
    main()
#