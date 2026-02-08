from __future__ import annotations

import requests

from ..settings.manager import SettingsManager


class AgentClient:
    def __init__(self, settings: SettingsManager) -> None:
        self._settings = settings

    def send(self, payload: dict) -> bool:
        target = self._settings.get_agent_target()
        url = f"http://{target.host}:{target.port}/command"
        headers = {"Authorization": f"Bearer {target.token}"}
        try:
            resp = requests.post(url, json=payload, headers=headers, timeout=2)
            return resp.status_code == 200
        except requests.RequestException:
            return False

    def health_check(self) -> bool:
        target = self._settings.get_agent_target()
        url = f"http://{target.host}:{target.port}/health"
        try:
            resp = requests.get(url, timeout=1)
            return resp.status_code == 200
        except requests.RequestException:
            return False
