from __future__ import annotations

from PySide6 import QtCore, QtWidgets


class StatusOverlay:
    def __init__(self, parent: QtWidgets.QWidget) -> None:
        self._label = QtWidgets.QLabel(parent)
        self._label.setText("")
        self._label.setStyleSheet(
            "QLabel { background-color: #991b1b; color: white; padding: 8px; font-size: 18px; }"
        )
        self._label.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop | QtCore.Qt.AlignmentFlag.AlignHCenter)
        self._label.setFixedHeight(40)
        self._label.hide()

        self._toast = QtWidgets.QLabel(parent)
        self._toast.setText("")
        self._toast.setStyleSheet(
            "QLabel { background-color: #0f172a; color: #e2e8f0; padding: 8px; font-size: 16px; border: 1px solid #334155; }"
        )
        self._toast.setAlignment(QtCore.Qt.AlignmentFlag.AlignBottom | QtCore.Qt.AlignmentFlag.AlignHCenter)
        self._toast.setFixedHeight(36)
        self._toast.hide()

    def set_error(self, text: str) -> None:
        self._label.setText(text)
        self._label.show()

    def clear(self) -> None:
        self._label.setText("")
        self._label.hide()

    def show_toast(self, text: str, ms: int = 1500) -> None:
        self._toast.setText(text)
        self._toast.show()
        QtCore.QTimer.singleShot(ms, self._toast.hide)
