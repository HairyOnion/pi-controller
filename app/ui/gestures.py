from __future__ import annotations

from PySide6 import QtCore, QtWidgets


class SwipeNavigator(QtCore.QObject):
    def __init__(self, target: QtWidgets.QWidget, on_prev, on_next, threshold: int = 80) -> None:
        super().__init__(target)
        self._target = target
        self._on_prev = on_prev
        self._on_next = on_next
        self._threshold = threshold
        self._start_pos: QtCore.QPoint | None = None
        target.installEventFilter(self)

    def eventFilter(self, watched, event):  # type: ignore[override]
        if event.type() == QtCore.QEvent.Type.MouseButtonPress:
            self._start_pos = event.position().toPoint()
            return False
        if event.type() == QtCore.QEvent.Type.MouseButtonRelease and self._start_pos:
            end_pos = event.position().toPoint()
            delta = end_pos - self._start_pos
            if abs(delta.x()) > self._threshold and abs(delta.x()) > abs(delta.y()):
                if delta.x() < 0:
                    self._on_next()
                else:
                    self._on_prev()
            self._start_pos = None
            return False
        return False
