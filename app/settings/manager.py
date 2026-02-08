from __future__ import annotations

from dataclasses import dataclass

from ..data.db import Database
from ..data.repository import Repository


@dataclass
class AgentTarget:
    host: str
    port: int
    token: str


class SettingsManager:
    def __init__(self, db: Database) -> None:
        self._db = db
        self._repo = Repository(db)

    def get_agent_target(self) -> AgentTarget:
        host = self._repo.get_setting("agent_host")
        port = self._repo.get_setting("agent_port")
        token = self._repo.get_setting("agent_token")
        return AgentTarget(
            host=host.value if host and host.value else "127.0.0.1",
            port=int(port.value) if port and port.value else 8765,
            token=token.value if token and token.value else "",
        )

    def get_brightness(self) -> int:
        value = self._repo.get_setting("brightness")
        return int(value.value) if value and value.value else 80

    def set_setting(self, key: str, value: str) -> None:
        self._repo.set_setting(key, value)

    def get_value(self, key: str) -> str | None:
        setting = self._repo.get_setting(key)
        return setting.value if setting else None

    def set_value(self, key: str, value: str) -> None:
        self._repo.set_setting(key, value)

    def validate_and_set(self, key: str, value: str) -> tuple[bool, str, str | None]:
        normalized = value.strip()
        if key == "resolution":
            allowed = {"800x480", "1024x600", "1280x720", "1920x1080"}
            if normalized not in allowed:
                return False, value, "Resolution must be one of: 800x480, 1024x600, 1280x720, 1920x1080"
            self._repo.set_setting(key, normalized)
            return True, normalized, None
        if key == "agent_host":
            if not normalized:
                return False, value, "Host cannot be empty"
            self._repo.set_setting(key, normalized)
            return True, normalized, None
        if key == "agent_port":
            try:
                port = int(normalized)
                if port < 1 or port > 65535:
                    raise ValueError()
            except ValueError:
                return False, value, "Port must be 1-65535"
            self._repo.set_setting(key, str(port))
            return True, str(port), None
        if key == "agent_token":
            self._repo.set_setting(key, normalized)
            return True, normalized, None
        if key == "brightness":
            try:
                v = int(normalized)
                if v < 0 or v > 100:
                    raise ValueError()
            except ValueError:
                return False, value, "Brightness must be 0-100"
            self._repo.set_setting(key, str(v))
            return True, str(v), None
        if key == "theme_font_size":
            try:
                v = int(normalized)
                if v < 8 or v > 64:
                    raise ValueError()
            except ValueError:
                return False, value, "Font size must be 8-64"
            self._repo.set_setting(key, str(v))
            return True, str(v), None
        if key == "theme_spacing":
            try:
                v = int(normalized)
                if v < 4 or v > 40:
                    raise ValueError()
            except ValueError:
                return False, value, "Spacing must be 4-40"
            self._repo.set_setting(key, str(v))
            return True, str(v), None
        if key == "theme_button_radius":
            try:
                v = int(normalized)
                if v < 0 or v > 32:
                    raise ValueError()
            except ValueError:
                return False, value, "Radius must be 0-32"
            self._repo.set_setting(key, str(v))
            return True, str(v), None
        if key in {"theme_text_color", "theme_accent_color", "theme_slider_groove", "theme_slider_handle"}:
            if not self._is_hex_color(normalized):
                return False, value, "Color must be hex like #RRGGBB"
            self._repo.set_setting(key, normalized)
            return True, normalized, None
        if key == "theme_font_family":
            if not normalized:
                return False, value, "Font family cannot be empty"
            self._repo.set_setting(key, normalized)
            return True, normalized, None
        self._repo.set_setting(key, normalized)
        return True, normalized, None

    def _is_hex_color(self, value: str) -> bool:
        if len(value) != 7 or not value.startswith("#"):
            return False
        try:
            int(value[1:], 16)
            return True
        except ValueError:
            return False
