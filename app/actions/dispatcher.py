from __future__ import annotations

import logging
import threading
from queue import Queue

from ..settings.manager import SettingsManager
from .client import AgentClient
import time
from .mapping import action_to_agent_payload, build_request_id
from ..data.models import Action

logger = logging.getLogger(__name__)


class ActionDispatcher:
    def __init__(self, settings: SettingsManager) -> None:
        self._settings = settings
        self._queue: Queue[dict] = Queue()
        self._client = AgentClient(settings)
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        self._health_ok = False
        self._health_thread = threading.Thread(target=self._health_loop, daemon=True)
        self._health_thread.start()

    def enqueue(self, action: dict) -> None:
        logger.info("Enqueue raw action: action=%s", action.get("action"))
        self._queue.put(action)

    def enqueue_action_record(
        self,
        action: Action,
        request_id: str | None = None,
        context: dict | None = None,
    ) -> None:
        payload = action_to_agent_payload(
            action,
            request_id=request_id or build_request_id(),
            context=context,
        )
        logger.info(
            "Enqueue action record: id=%s type=%s trigger=%s mapped_action=%s request_id=%s",
            action.id,
            action.action_type,
            action.trigger,
            payload.get("action"),
            payload.get("request_id"),
        )
        self._queue.put(payload)

    def _run(self) -> None:
        while True:
            action = self._queue.get()
            self._send_with_retry(action)

    def _send_with_retry(self, action: dict) -> None:
        backoffs = [0.0, 0.5, 1.0]
        for delay in backoffs:
            if delay:
                time.sleep(delay)
            if self._client.send(action):
                logger.info(
                    "Dispatched action: action=%s request_id=%s",
                    action.get("action"),
                    action.get("request_id"),
                )
                return
        logger.error(
            "Failed to dispatch action after retries: action=%s request_id=%s",
            action.get("action"),
            action.get("request_id"),
        )

    def _health_loop(self) -> None:
        while True:
            self._health_ok = self._client.health_check()
            time.sleep(2.0)

    def last_health_ok(self) -> bool:
        return self._health_ok
