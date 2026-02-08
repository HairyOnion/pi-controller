from __future__ import annotations

from PySide6 import QtWidgets


class SettingsScreen(QtWidgets.QWidget):
    def __init__(self) -> None:
        super().__init__()
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(QtWidgets.QLabel("Settings screen (DB-driven in full implementation)"))
