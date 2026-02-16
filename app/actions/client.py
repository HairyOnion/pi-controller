from __future__ import annotations

import logging
import requests

from ..settings.manager import SettingsManager


logger = logging.getLogger(__name__)


class AgentClient:
    def __init__(self, settings: SettingsManager) -> None:
        self._settings = settings

    def send(self, payload: dict) -> bool:
        target = self._settings.get_agent_target()
        url = f"http://{target.host}:{target.port}/command"
        headers = {"Authorization": f"Bearer {target.token}"}
        try:
            resp = requests.post(url, json=payload, headers=headers, timeout=2)
            ok = resp.status_code == 200
            if not ok:
                logger.warning("Agent command failed: status=%s url=%s", resp.status_code, url)
            return ok
        except requests.RequestException as exc:
            logger.warning("Agent command request error: %s url=%s", exc, url)
            return False

    def health_check(self) -> bool:
        target = self._settings.get_agent_target()
        url = f"http://{target.host}:{target.port}/health"
        try:
            resp = requests.get(url, timeout=1)
            ok = resp.status_code == 200
            if not ok:
                logger.warning("Agent health check failed: status=%s url=%s", resp.status_code, url)
            return ok
        except requests.RequestException as exc:
            logger.warning("Agent health check request error: %s url=%s", exc, url)
            return False
