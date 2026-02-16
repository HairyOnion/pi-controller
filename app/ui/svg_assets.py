from __future__ import annotations

import hashlib
import os
from pathlib import Path
import sys

from PySide6 import QtCore, QtGui, QtSvg


class SvgRasterCache:
    def __init__(self, cache_dir: Path | None = None) -> None:
        self._renderers: dict[Path, QtSvg.QSvgRenderer] = {}
        self._pixmaps: dict[tuple[str, int, int, int], QtGui.QPixmap] = {}
        self._cache_dir = cache_dir or self._default_cache_dir()
        try:
            self._cache_dir.mkdir(parents=True, exist_ok=True)
        except Exception:
            self._cache_dir = None

    def render(self, path: Path, size: QtCore.QSize, dpr: float) -> QtGui.QPixmap:
        if size.isEmpty() or not path.exists():
            return QtGui.QPixmap()
        dpr_key = int(round(dpr * 100))
        key = (str(path), size.width(), size.height(), dpr_key)
        cached = self._pixmaps.get(key)
        if cached is not None:
            return cached
        disk_path = self._cache_path(path, size, dpr_key)
        if disk_path and disk_path.exists():
            pm = QtGui.QPixmap(str(disk_path))
            if not pm.isNull():
                pm.setDevicePixelRatio(dpr)
                self._pixmaps[key] = pm
                return pm
        renderer = self._renderers.get(path)
        if renderer is None:
            renderer = QtSvg.QSvgRenderer(str(path))
            self._renderers[path] = renderer
        width = max(1, int(size.width() * dpr))
        height = max(1, int(size.height() * dpr))
        image = QtGui.QImage(width, height, QtGui.QImage.Format.Format_ARGB32_Premultiplied)
        image.fill(QtCore.Qt.GlobalColor.transparent)
        painter = QtGui.QPainter(image)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing, True)
        painter.setRenderHint(QtGui.QPainter.RenderHint.SmoothPixmapTransform, True)
        renderer.render(painter, QtCore.QRectF(0, 0, width, height))
        painter.end()
        if disk_path:
            try:
                image.save(str(disk_path), "PNG")
            except Exception:
                pass
        pm = QtGui.QPixmap.fromImage(image)
        pm.setDevicePixelRatio(dpr)
        self._pixmaps[key] = pm
        return pm

    def _cache_path(self, path: Path, size: QtCore.QSize, dpr_key: int) -> Path | None:
        if not self._cache_dir:
            return None
        digest = hashlib.md5(str(path).encode("utf-8")).hexdigest()  # nosec - non-cryptographic cache key
        filename = f"{path.stem}-{digest}-{size.width()}x{size.height()}@{dpr_key}.png"
        return self._cache_dir / filename

    def _default_cache_dir(self) -> Path:
        if sys.platform.startswith("win"):
            base = os.getenv("LOCALAPPDATA")
            if base:
                return Path(base) / "pi_controller" / "svg_cache"
            return Path.home() / "AppData" / "Local" / "pi_controller" / "svg_cache"
        base = os.getenv("XDG_CACHE_HOME")
        if base:
            return Path(base) / "pi_controller" / "svg_cache"
        return Path.home() / ".cache" / "pi_controller" / "svg_cache"
