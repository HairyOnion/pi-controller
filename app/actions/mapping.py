from __future__ import annotations

import json
import uuid
from typing import Any, Dict

from ..data.models import Action


def build_request_id() -> str:
    return str(uuid.uuid4())


def _apply_context(obj: Any, context: Dict[str, Any]) -> Any:
    if isinstance(obj, dict):
        return {k: _apply_context(v, context) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_apply_context(v, context) for v in obj]
    if isinstance(obj, str):
        if obj == "${value}" and "value" in context:
            return context["value"]
        if obj == "${state}" and "state" in context:
            return context["state"]
    return obj


def action_to_agent_payload(
    action: Action,
    request_id: str | None = None,
    context: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    try:
        data = json.loads(action.payload_json)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid action payload_json: {exc}") from exc

    if "action" not in data or "payload" not in data:
        raise ValueError("Action payload_json must include 'action' and 'payload'")

    payload = data["payload"]
    if context:
        payload = _apply_context(payload, context)
        if action.value_key and isinstance(payload, dict) and "value" in context:
            payload[action.value_key] = context["value"]

    return {
        "request_id": request_id or build_request_id(),
        "action": data["action"],
        "payload": payload,
    }
