from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Screen:
    id: int
    name: str
    order_index: int
    bg_color: Optional[str]
    bg_image_path: Optional[str]
    bg_image_mode: Optional[str]


@dataclass(frozen=True)
class Control:
    id: int
    screen_id: int
    type: str
    label: Optional[str]
    row: Optional[int]
    col: Optional[int]
    rowspan: Optional[int]
    colspan: Optional[int]
    min_value: Optional[float]
    max_value: Optional[float]
    step: Optional[float]
    is_continuous: Optional[bool]
    default_value: Optional[str]
    persist_state: Optional[bool]
    style_bg: Optional[str]
    style_fg: Optional[str]
    icon_path: Optional[str]
    width_hint: Optional[int]
    height_hint: Optional[int]
    setting_key: Optional[str]
    placeholder_text: Optional[str]


@dataclass(frozen=True)
class Action:
    id: int
    control_id: int
    trigger: str
    action_type: str
    payload_json: str
    value_key: Optional[str]


@dataclass(frozen=True)
class ControlState:
    control_id: int
    value: Optional[str]


@dataclass(frozen=True)
class Setting:
    key: str
    value: Optional[str]
