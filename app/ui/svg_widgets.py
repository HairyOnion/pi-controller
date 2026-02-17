from __future__ import annotations

from pathlib import Path

from PySide6 import QtCore, QtGui, QtWidgets

from .svg_assets import SvgRasterCache


class SvgBackgroundButton(QtWidgets.QPushButton):
    uses_svg_background = True

    def __init__(self, label: str, svg_path: Path | None, cache: SvgRasterCache, parent=None) -> None:
        super().__init__(label, parent)
        self._svg_path = svg_path
        self._cache = cache
        self.setFlat(True)
        self.setAutoFillBackground(False)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setStyleSheet("QPushButton { background: transparent; border: none; }")

    def set_svg_background(self, path: Path | None) -> None:
        self._svg_path = path
        self.update()

    def paintEvent(self, event):  # type: ignore[override]
        if self._svg_path and self._svg_path.exists():
            pm = self._cache.render(self._svg_path, self.size(), self.devicePixelRatioF())
            if not pm.isNull():
                painter = QtGui.QPainter(self)
                painter.setRenderHint(QtGui.QPainter.RenderHint.SmoothPixmapTransform, True)
                painter.drawPixmap(0, 0, pm)
                painter.end()
        super().paintEvent(event)


class SvgSlider(QtWidgets.QSlider):
    uses_svg_track = True

    def __init__(
        self,
        orientation: QtCore.Qt.Orientation,
        track_path: Path | None,
        knob_path: Path | None,
        cache: SvgRasterCache,
        parent=None,
    ) -> None:
        super().__init__(orientation, parent)
        self._track_path = track_path
        self._knob_path = knob_path
        self._cache = cache
        self._drag_active = False
        self.setStyleSheet("QSlider { background: transparent; }")

    def set_svg_assets(self, track_path: Path | None, knob_path: Path | None) -> None:
        self._track_path = track_path
        self._knob_path = knob_path
        self.update()

    def paintEvent(self, event):  # type: ignore[override]
        if not (self._track_path and self._track_path.exists() and self._knob_path and self._knob_path.exists()):
            return super().paintEvent(event)
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing, True)
        painter.setRenderHint(QtGui.QPainter.RenderHint.SmoothPixmapTransform, True)
        track_rect = self._track_rect()
        knob_rect = self._knob_rect(track_rect)
        track_pm = self._cache.render(self._track_path, track_rect.size(), self.devicePixelRatioF())
        if not track_pm.isNull():
            painter.drawPixmap(track_rect.topLeft(), track_pm)
        knob_pm = self._cache.render(self._knob_path, knob_rect.size(), self.devicePixelRatioF())
        if not knob_pm.isNull():
            painter.drawPixmap(knob_rect.topLeft(), knob_pm)
        painter.end()

    def _track_rect(self) -> QtCore.QRect:
        rect = self.rect()
        pad = max(6, int(min(rect.width(), rect.height()) * 0.08))
        if self.orientation() == QtCore.Qt.Orientation.Horizontal:
            thickness = max(6, int(rect.height() * 0.28))
            y = rect.top() + (rect.height() - thickness) // 2
            return QtCore.QRect(rect.left() + pad, y, rect.width() - 2 * pad, thickness)
        thickness = max(6, int(rect.width() * 0.28))
        x = rect.left() + (rect.width() - thickness) // 2
        return QtCore.QRect(x, rect.top() + pad, thickness, rect.height() - 2 * pad)

    def _knob_rect(self, track_rect: QtCore.QRect) -> QtCore.QRect:
        thickness = track_rect.height() if self.orientation() == QtCore.Qt.Orientation.Horizontal else track_rect.width()
        knob_size = max(12, int(thickness * 1.6))
        ratio = 0.0
        span = self.maximum() - self.minimum()
        if span > 0:
            ratio = (self.value() - self.minimum()) / span
        if self.orientation() == QtCore.Qt.Orientation.Horizontal:
            x = int(track_rect.left() + ratio * track_rect.width() - knob_size / 2)
            y = int(track_rect.center().y() - knob_size / 2)
        else:
            y = int(track_rect.bottom() - ratio * track_rect.height() - knob_size / 2)
            x = int(track_rect.center().x() - knob_size / 2)
        rect = QtCore.QRect(x, y, knob_size, knob_size)
        return rect.intersected(self.rect())

    def _knob_hit_rect(self, track_rect: QtCore.QRect) -> QtCore.QRect:
        knob = self._knob_rect(track_rect)
        # Expand touch area to improve finger capture around the knob.
        pad = max(10, knob.width() // 2)
        return knob.adjusted(-pad, -pad, pad, pad).intersected(self.rect())

    def _track_hit_rect(self, track_rect: QtCore.QRect) -> QtCore.QRect:
        pad = 14
        return track_rect.adjusted(-pad, -pad, pad, pad).intersected(self.rect())

    def _set_value_from_pos(self, pos: QtCore.QPoint) -> None:
        track_rect = self._track_rect()
        span = max(1, self.maximum() - self.minimum())
        if self.orientation() == QtCore.Qt.Orientation.Horizontal:
            x = min(max(pos.x(), track_rect.left()), track_rect.right())
            ratio = (x - track_rect.left()) / max(1, track_rect.width())
        else:
            y = min(max(pos.y(), track_rect.top()), track_rect.bottom())
            ratio = (track_rect.bottom() - y) / max(1, track_rect.height())
        value = self.minimum() + int(round(ratio * span))
        self.setValue(min(self.maximum(), max(self.minimum(), value)))

    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:  # type: ignore[override]
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            track = self._track_rect()
            if self._knob_hit_rect(track).contains(event.position().toPoint()) or self._track_hit_rect(track).contains(
                event.position().toPoint()
            ):
                self._drag_active = True
                self.setSliderDown(True)
                self._set_value_from_pos(event.position().toPoint())
                event.accept()
                return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:  # type: ignore[override]
        if self._drag_active:
            self._set_value_from_pos(event.position().toPoint())
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QtGui.QMouseEvent) -> None:  # type: ignore[override]
        if self._drag_active and event.button() == QtCore.Qt.MouseButton.LeftButton:
            self._set_value_from_pos(event.position().toPoint())
            self._drag_active = False
            self.setSliderDown(False)
            self.sliderReleased.emit()
            event.accept()
            return
        super().mouseReleaseEvent(event)
