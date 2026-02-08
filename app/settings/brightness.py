from __future__ import annotations

from pathlib import Path


class BrightnessController:
    def __init__(self, backlight_path: Path) -> None:
        self._path = backlight_path
        self._max_path = backlight_path.parent / "max_brightness"

    def set_level_percent(self, percent: int) -> None:
        percent = max(0, min(100, percent))
        max_val = self._read_max()
        value = int((percent / 100.0) * max_val)
        self._path.write_text(str(value))

    def _read_max(self) -> int:
        try:
            return int(self._max_path.read_text().strip())
        except Exception:
            return 255


def find_backlight_brightness_path() -> Path | None:
    base = Path("/sys/class/backlight")
    if not base.exists():
        return None
    for child in base.iterdir():
        candidate = child / "brightness"
        if candidate.exists():
            return candidate
    return None
