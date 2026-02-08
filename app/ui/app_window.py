from __future__ import annotations

import sys

from PySide6 import QtCore, QtWidgets
from PySide6.QtCore import Qt

from .screen_renderer import ScreenRenderer
from .status_overlay import StatusOverlay
from ..data.db import Database
from ..settings.manager import SettingsManager
from ..actions.dispatcher import ActionDispatcher


class AppWindow:
    def __init__(self, db: Database, settings: SettingsManager, dispatcher: ActionDispatcher) -> None:
        self._db = db
        self._settings = settings
        self._dispatcher = dispatcher

        self._app = QtWidgets.QApplication([])
        self._window = QtWidgets.QMainWindow()
        self._window.setWindowTitle("Pi Touch Controller")
        if sys.platform.startswith("win"):
            self._window.setWindowFlag(Qt.FramelessWindowHint, False)
            self._configure_windowed_mode()
        else:
            self._window.setWindowFlag(Qt.FramelessWindowHint, True)
            self._window.showFullScreen()

        self._renderer = ScreenRenderer(db=self._db, dispatcher=self._dispatcher)
        self._overlay = StatusOverlay(self._window)
        self._renderer.set_toast_handler(self._overlay.show_toast)

        root = self._renderer.build_root()
        if sys.platform.startswith("win"):
            root.setSizePolicy(QtWidgets.QSizePolicy.Policy.Ignored, QtWidgets.QSizePolicy.Policy.Ignored)
            root.setMinimumSize(0, 0)
            self._window.setMinimumSize(320, 240)
        self._window.setCentralWidget(root)
        self._renderer.load_initial_screen()

        self._health_timer = QtCore.QTimer()
        self._health_timer.setInterval(1000)
        self._health_timer.timeout.connect(self._update_health_status)
        self._health_timer.start()

    def run(self) -> None:
        self._window.show()
        self._app.exec()

    def _configure_windowed_mode(self) -> None:
        screen = QtWidgets.QApplication.primaryScreen()
        if not screen:
            self._window.resize(1024, 600)
            return
        available = screen.availableGeometry()
        width = 1024
        height = 600
        value = self._settings.get_value("resolution")
        if value and "x" in value.lower():
            try:
                width_str, height_str = value.lower().split("x", 1)
                width = int(width_str)
                height = int(height_str)
            except ValueError:
                width = 1024
                height = 600
        width = min(width, available.width())
        height = min(height, available.height())
        self._window.resize(width, height)
        x = available.x() + (available.width() - width) // 2
        y = available.y() + (available.height() - height) // 2
        self._window.move(x, y)

    def _update_health_status(self) -> None:
        if self._dispatcher.last_health_ok():
            self._overlay.clear()
        else:
            self._overlay.set_error("Agent Offline")
