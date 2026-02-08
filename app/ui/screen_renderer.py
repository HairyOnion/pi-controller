from __future__ import annotations

import json
from pathlib import Path

from PySide6 import QtCore, QtGui, QtWidgets
import sys

from ..actions.dispatcher import ActionDispatcher
from ..data.db import Database
from ..data.repository import Repository
from ..data.models import Action, Control, Screen
from ..settings.manager import SettingsManager
from ..settings.brightness import BrightnessController, find_backlight_brightness_path
from .gestures import SwipeNavigator


class ScreenRenderer:
    def __init__(self, db: Database, dispatcher: ActionDispatcher) -> None:
        self._db = db
        self._dispatcher = dispatcher
        self._repo = Repository(db)
        self._stack = QtWidgets.QStackedWidget()
        self._screen_index: dict[int, int] = {}
        self._brightness = self._init_brightness()
        self._settings = SettingsManager(db)
        self._bg_helpers: list[BackgroundImageBinder] = []
        self._theme_spacing = self._get_int_setting("theme_spacing", 12)
        self._theme_button_radius = self._get_int_setting("theme_button_radius", 8)
        self._apply_theme()
        self._toast_handler = None

    def build_root(self) -> QtWidgets.QWidget:
        SwipeNavigator(self._stack, self.go_prev, self.go_next)
        return self._stack

    def load_initial_screen(self) -> None:
        self._rebuild_screens()
        if self._stack.count() == 0:
            self._stack.addWidget(self._empty_state("No screens configured in database."))
            return
        self._stack.setCurrentIndex(0)
        if self._brightness:
            self._brightness.set_level_percent(self._settings.get_brightness())

    def _empty_state(self, message: str) -> QtWidgets.QWidget:
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(widget)
        layout.addWidget(QtWidgets.QLabel(message))
        return widget

    def _rebuild_screens(self) -> None:
        while self._stack.count() > 0:
            widget = self._stack.widget(0)
            self._stack.removeWidget(widget)
            widget.deleteLater()
        self._screen_index.clear()
        screens = self._repo.list_screens()
        for idx, screen in enumerate(screens):
            self._stack.addWidget(self._build_screen(screen))
            self._screen_index[screen.id] = idx

    def _build_screen(self, screen: Screen) -> QtWidgets.QWidget:
        widget = QtWidgets.QWidget()
        grid = QtWidgets.QGridLayout(widget)
        grid.setSpacing(self._theme_spacing)
        grid.setContentsMargins(16, 16, 16, 16)

        self._apply_screen_style(widget, screen)

        controls = self._repo.list_controls_for_screen(screen.id)
        max_row = 0
        max_col = 0
        for control in controls:
            ctrl_widget = self._build_control(control)
            row = control.row or 0
            col = control.col or 0
            rowspan = control.rowspan or 1
            colspan = control.colspan or 1
            grid.addWidget(ctrl_widget, row, col, rowspan, colspan)
            max_row = max(max_row, row)
            max_col = max(max_col, col)

        for r in range(max_row + 1):
            grid.setRowStretch(r, 1)
        for c in range(max_col + 1):
            grid.setColumnStretch(c, 1)
        if max_row >= 1:
            grid.setRowStretch(0, 1)
            grid.setRowStretch(1, 4)

        return widget

    def _build_control(self, control: Control) -> QtWidgets.QWidget:
        if control.type == "button":
            btn = QtWidgets.QPushButton(control.label or "Button")
            self._apply_control_style(btn, control)
            self._apply_control_icon(btn, control)
            btn.clicked.connect(lambda _=False, c=control: self._fire_actions(c, "press"))
            return btn

        if control.type == "toggle":
            btn = QtWidgets.QPushButton(control.label or "Toggle")
            btn.setCheckable(True)
            self._apply_initial_state_toggle(btn, control)
            self._apply_control_style(btn, control)
            self._apply_control_icon(btn, control)
            btn.toggled.connect(lambda checked, c=control: self._on_toggle(c, checked))
            return btn

        if control.type == "slider":
            slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
            if control.min_value is not None:
                slider.setMinimum(int(control.min_value))
            if control.max_value is not None:
                slider.setMaximum(int(control.max_value))
            if control.step:
                slider.setSingleStep(int(control.step))
                slider.setPageStep(int(control.step))
            self._apply_initial_state_slider(slider, control)
            self._apply_control_style(slider, control)
            if control.is_continuous:
                slider.valueChanged.connect(lambda _value, c=control: self._fire_actions(c, "value_change"))
            slider.sliderReleased.connect(lambda c=control, s=slider: self._on_slider_release(c, s))
            value_label = QtWidgets.QLabel(str(slider.value()))
            value_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignVCenter)
            self._apply_control_style(value_label, control)
            slider.valueChanged.connect(lambda v, lbl=value_label: lbl.setText(str(v)))
            wrapper = QtWidgets.QWidget()
            layout = QtWidgets.QVBoxLayout(wrapper)
            layout.setSpacing(self._theme_spacing)
            layout.addWidget(value_label)
            layout.addWidget(slider)
            return wrapper

        if control.type == "slider_vertical":
            wrapper = QtWidgets.QWidget()
            layout = QtWidgets.QVBoxLayout(wrapper)
            layout.setSpacing(self._theme_spacing)
            label = QtWidgets.QLabel(control.label or "Slider")
            label.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter | QtCore.Qt.AlignmentFlag.AlignVCenter)
            slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Vertical)
            label.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed)
            slider.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding)
            slider.setMinimumWidth(120)
            self._apply_control_style(label, control)
            self._apply_control_style(slider, control)
            slider.setStyleSheet(
                "\n".join(
                    [
                        "QSlider::groove:vertical {"
                        " width: 14px; background: #1f2937; border: 1px solid #111827; border-radius: 7px; }",
                        "QSlider::sub-page:vertical { background: #1f2937; border-radius: 7px; }",
                        "QSlider::add-page:vertical { background: #1f2937; border-radius: 7px; }",
                        "QSlider::handle:vertical {"
                        " height: 32px; width: 28px; margin: -8px 0;"
                        " background: #4b5563; border: 1px solid #111827; border-radius: 6px; }",
                    ]
                )
            )
            if control.min_value is not None:
                slider.setMinimum(int(control.min_value))
            if control.max_value is not None:
                slider.setMaximum(int(control.max_value))
            if control.step:
                slider.setSingleStep(int(control.step))
                slider.setPageStep(int(control.step))
            self._apply_initial_state_slider(slider, control)
            if control.is_continuous:
                slider.valueChanged.connect(lambda _value, c=control: self._fire_actions(c, "value_change"))
            slider.sliderReleased.connect(lambda c=control, s=slider: self._on_slider_release(c, s))
            layout.addWidget(label)
            layout.addWidget(slider, 1)
            return wrapper

        if control.type == "setting_text":
            wrapper = QtWidgets.QWidget()
            layout = QtWidgets.QHBoxLayout(wrapper)
            layout.setSpacing(self._theme_spacing)
            label = QtWidgets.QLabel(control.label or "Setting")
            label.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter | QtCore.Qt.AlignmentFlag.AlignVCenter)
            edit = QtWidgets.QLineEdit()
            edit.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password if control.setting_key == "agent_token" else QtWidgets.QLineEdit.EchoMode.Normal)
            self._apply_control_style(label, control)
            self._apply_control_style(edit, control)
            value = self._settings.get_value(control.setting_key)
            if value is not None:
                edit.setText(value)
            if control.placeholder_text:
                edit.setPlaceholderText(control.placeholder_text)
            error_label = QtWidgets.QLabel("")
            error_label.setStyleSheet("QLabel { color: #ef4444; font-size: 14px; }")
            error_label.hide()
            edit.editingFinished.connect(
                lambda c=control, e=edit, err=error_label: self._save_setting_text(c, e, err)
            )
            layout.addWidget(label)
            layout.addWidget(edit)
            layout.addWidget(error_label)
            return wrapper

        if control.type == "setting_dropdown":
            wrapper = QtWidgets.QWidget()
            layout = QtWidgets.QHBoxLayout(wrapper)
            layout.setSpacing(self._theme_spacing)
            label = QtWidgets.QLabel(control.label or "Setting")
            label.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter | QtCore.Qt.AlignmentFlag.AlignVCenter)
            combo = QtWidgets.QComboBox()
            self._apply_control_style(label, control)
            self._apply_control_style(combo, control)
            options = self._get_dropdown_options(control)
            for option in options:
                combo.addItem(option)
            current = self._settings.get_value(control.setting_key) if control.setting_key else None
            if current and current in options:
                combo.setCurrentText(current)
            elif control.default_value and control.default_value in options:
                combo.setCurrentText(control.default_value)
            error_label = QtWidgets.QLabel("")
            error_label.setStyleSheet("QLabel { color: #ef4444; font-size: 14px; }")
            error_label.hide()
            combo.currentTextChanged.connect(
                lambda text, c=control, err=error_label: self._save_setting_dropdown(c, text, err)
            )
            layout.addWidget(label)
            layout.addWidget(combo)
            layout.addWidget(error_label)
            return wrapper

        if control.type == "setting_slider":
            wrapper = QtWidgets.QWidget()
            layout = QtWidgets.QVBoxLayout(wrapper)
            layout.setSpacing(self._theme_spacing)
            label = QtWidgets.QLabel(control.label or "Setting")
            label.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter | QtCore.Qt.AlignmentFlag.AlignVCenter)
            slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
            self._apply_control_style(label, control)
            self._apply_control_style(slider, control)
            if control.min_value is not None:
                slider.setMinimum(int(control.min_value))
            if control.max_value is not None:
                slider.setMaximum(int(control.max_value))
            if control.step:
                slider.setSingleStep(int(control.step))
            value = self._settings.get_value(control.setting_key)
            if value is not None:
                slider.setValue(int(float(value)))
            error_label = QtWidgets.QLabel("")
            error_label.setStyleSheet("QLabel { color: #ef4444; font-size: 14px; }")
            error_label.hide()
            slider.sliderReleased.connect(lambda c=control, s=slider, err=error_label: self._save_setting_slider(c, s, err))
            value_label = QtWidgets.QLabel(str(slider.value()))
            value_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignVCenter)
            self._apply_control_style(value_label, control)
            slider.valueChanged.connect(lambda v, lbl=value_label: lbl.setText(str(v)))
            layout.addWidget(label)
            layout.addWidget(value_label)
            layout.addWidget(slider)
            layout.addWidget(error_label)
            return wrapper

        return QtWidgets.QLabel(f"Unknown control type: {control.type}")

    def _apply_initial_state_toggle(self, btn: QtWidgets.QPushButton, control: Control) -> None:
        if not control.persist_state:
            if control.default_value:
                btn.setChecked(control.default_value.lower() in {"1", "true", "on", "yes"})
            return
        state = self._repo.get_control_state(control.id)
        if state and state.value is not None:
            btn.setChecked(state.value.lower() in {"1", "true", "on", "yes"})

    def _apply_initial_state_slider(self, slider: QtWidgets.QSlider, control: Control) -> None:
        if not control.persist_state:
            if control.default_value is not None:
                slider.setValue(int(float(control.default_value)))
            return
        state = self._repo.get_control_state(control.id)
        if state and state.value is not None:
            slider.setValue(int(float(state.value)))

    def _on_toggle(self, control: Control, checked: bool) -> None:
        if control.persist_state:
            self._repo.set_control_state(control.id, "1" if checked else "0")
        trigger = "toggle_on" if checked else "toggle_off"
        self._fire_actions(control, trigger, context={"state": checked})

    def _on_slider_release(self, control: Control, slider: QtWidgets.QSlider) -> None:
        if control.persist_state:
            self._repo.set_control_state(control.id, str(slider.value()))
        self._fire_actions(control, "value_release", context={"value": slider.value()})

    def _fire_actions(self, control: Control, trigger: str, context: dict | None = None) -> None:
        actions = self._repo.list_actions_for_control(control.id)
        for action in actions:
            if action.trigger == trigger:
                if action.action_type == "navigate_screen":
                    self._handle_navigation_action(action)
                elif action.action_type == "show_resolution":
                    self._handle_show_resolution()
                else:
                    self._dispatcher.enqueue_action_record(action, context=context)

    def _handle_navigation_action(self, action: Action) -> None:
        try:
            data = json.loads(action.payload_json)
            target_id = int(data.get("screen_id"))
        except Exception:
            return
        idx = self._screen_index.get(target_id)
        if idx is not None:
            self._stack.setCurrentIndex(idx)

    def _handle_show_resolution(self) -> None:
        screen = QtWidgets.QApplication.primaryScreen()
        if not screen:
            self._toast("Resolution unavailable")
            return
        size = screen.size()
        self._toast(f"Resolution: {size.width()}x{size.height()}")

    def _apply_screen_style(self, widget: QtWidgets.QWidget, screen: Screen) -> None:
        styles = []
        if screen.bg_color:
            styles.append(f"background-color: {screen.bg_color};")
        if screen.bg_image_path:
            pass
        if styles:
            widget.setStyleSheet(f"QWidget {{ {' '.join(styles)} }}")
        widget.setAutoFillBackground(True)
        if screen.bg_image_path:
            self._bg_helpers.append(
                BackgroundImageBinder(
                    widget,
                    self._resolve_asset_path(screen.bg_image_path),
                    screen.bg_image_mode or "stretch",
                )
            )

    def _apply_control_style(self, widget: QtWidgets.QWidget, control: Control) -> None:
        styles = []
        if control.style_bg:
            styles.append(f"background-color: {control.style_bg};")
        if control.style_fg:
            styles.append(f"color: {control.style_fg};")
        if isinstance(widget, QtWidgets.QPushButton):
            styles.append("border: 2px solid transparent;")
            styles.append("padding: 6px;")
            styles.append("font-size: 18px;")
            styles.append(f"border-radius: {self._theme_button_radius}px;")
            styles.append("font-weight: 600;")
            styles.append("qproperty-iconSize: 32px 32px;")
            styles.append("background-clip: padding;")
            base = " ".join(styles)
            if widget.isCheckable():
                widget.setStyleSheet(
                    f"QPushButton {{ {base} }} QPushButton:checked {{ border-color: #f59e0b; }}"
                )
            else:
                widget.setStyleSheet(f"QPushButton {{ {base} }}")
        elif styles:
            widget.setStyleSheet(f"{widget.__class__.__name__} {{ {' '.join(styles)} }}")
        if control.width_hint:
            widget.setMinimumWidth(int(control.width_hint) * 120)
        if control.height_hint:
            widget.setMinimumHeight(int(control.height_hint) * 80)
        widget.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding)

    def _apply_control_icon(self, widget: QtWidgets.QPushButton, control: Control) -> None:
        if not control.icon_path:
            return
        path = self._resolve_asset_path(control.icon_path)
        if not path.exists():
            return
        icon = QtGui.QIcon(str(path))
        widget.setIcon(icon)
        widget.setIconSize(QtCore.QSize(48, 48))

    def _resolve_asset_path(self, value: str) -> Path:
        path = Path(value)
        if path.is_absolute():
            return path
        base = Path(__file__).resolve().parents[2]
        return (base / path).resolve()

    def _get_int_setting(self, key: str, default: int) -> int:
        value = self._settings.get_value(key)
        try:
            return int(value) if value is not None else default
        except ValueError:
            return default

    def _apply_theme(self) -> None:
        font_family = self._settings.get_value("theme_font_family") or "DejaVu Sans"
        font_size = self._get_int_setting("theme_font_size", 18)
        text_color = self._settings.get_value("theme_text_color") or "#e2e8f0"
        accent_color = self._settings.get_value("theme_accent_color") or "#38bdf8"
        groove = self._settings.get_value("theme_slider_groove") or "#334155"
        handle = self._settings.get_value("theme_slider_handle") or "#f59e0b"
        app = QtWidgets.QApplication.instance()
        if app:
            app.setFont(QtGui.QFont(font_family, font_size))
            app.setStyleSheet(
                "\n".join(
                    [
                        f"QWidget {{ color: {text_color}; }}",
                        "QLabel { font-weight: 500; }",
                        f"QSlider::groove:horizontal {{ height: 8px; background: {groove}; border-radius: 4px; }}",
                        f"QSlider::handle:horizontal {{ width: 20px; background: {handle}; margin: -6px 0; border-radius: 10px; }}",
                        f"QSlider::sub-page:horizontal {{ background: {accent_color}; border-radius: 4px; }}",
                    ]
                )
            )

    def _refresh_theme(self) -> None:
        current = self._stack.currentIndex()
        self._apply_theme()
        self._rebuild_screens()
        if self._stack.count() > 0:
            self._stack.setCurrentIndex(min(current, self._stack.count() - 1))

    def _init_brightness(self) -> BrightnessController | None:
        path = find_backlight_brightness_path()
        if not path:
            return None
        return BrightnessController(path)

    def _save_setting_text(self, control: Control, edit: QtWidgets.QLineEdit, error_label: QtWidgets.QLabel | None = None) -> None:
        if not control.setting_key:
            return
        ok, normalized, err = self._settings.validate_and_set(control.setting_key, edit.text())
        if ok:
            edit.setText(normalized)
            if control.setting_key.startswith("theme_"):
                self._refresh_theme()
            if error_label:
                error_label.setText("")
                error_label.hide()
            self._toast(self._success_message(control.setting_key))
        else:
            self._mark_invalid(edit)
            if err:
                self._toast(err)
            if error_label and err:
                error_label.setText(err)
                error_label.show()

    def _save_setting_dropdown(
        self,
        control: Control,
        value: str,
        error_label: QtWidgets.QLabel | None = None,
    ) -> None:
        if not control.setting_key:
            return
        ok, normalized, err = self._settings.validate_and_set(control.setting_key, value)
        if ok:
            if error_label:
                error_label.setText("")
                error_label.hide()
            self._toast(self._success_message(control.setting_key))
            if control.setting_key == "resolution":
                self._apply_resolution(normalized)
        else:
            if err:
                self._toast(err)
            if error_label and err:
                error_label.setText(err)
                error_label.show()

    def _save_setting_slider(
        self,
        control: Control,
        slider: QtWidgets.QSlider,
        error_label: QtWidgets.QLabel | None = None,
    ) -> None:
        if not control.setting_key:
            return
        value = slider.value()
        ok, normalized, err = self._settings.validate_and_set(control.setting_key, str(value))
        if ok:
            if str(value) != normalized:
                slider.setValue(int(normalized))
            if error_label:
                error_label.setText("")
                error_label.hide()
            self._toast(self._success_message(control.setting_key))
        if control.setting_key == "brightness" and self._brightness:
            self._brightness.set_level_percent(value)
        if control.setting_key.startswith("theme_"):
            self._refresh_theme()
        if not ok and err:
            self._toast(err)
            if error_label:
                error_label.setText(err)
                error_label.show()

    def _mark_invalid(self, widget: QtWidgets.QWidget) -> None:
        prev = widget.styleSheet()
        widget.setStyleSheet(prev + " border: 2px solid #ef4444;")
        QtCore.QTimer.singleShot(1200, lambda: widget.setStyleSheet(prev))

    def _toast(self, message: str) -> None:
        if self._toast_handler:
            self._toast_handler(message)

    def set_toast_handler(self, handler) -> None:
        self._toast_handler = handler

    def _success_message(self, key: str | None) -> str:
        if not key:
            return "Saved"
        if key == "resolution":
            return "Resolution updated"
        if key == "brightness":
            return "Brightness updated"
        if key in {"agent_host", "agent_port", "agent_token"}:
            return "Agent settings saved"
        if key.startswith("theme_"):
            return "Theme updated"
        return "Saved"

    def go_prev(self) -> None:
        if self._stack.count() == 0:
            return
        idx = (self._stack.currentIndex() - 1) % self._stack.count()
        self._stack.setCurrentIndex(idx)

    def go_next(self) -> None:
        if self._stack.count() == 0:
            return
        idx = (self._stack.currentIndex() + 1) % self._stack.count()
        self._stack.setCurrentIndex(idx)

    def _get_dropdown_options(self, control: Control) -> list[str]:
        if control.setting_key == "resolution":
            return ["800x480", "1024x600", "1280x720", "1920x1080"]
        return []

    def _apply_resolution(self, value: str) -> None:
        if not sys.platform.startswith("win"):
            return
        try:
            width_str, height_str = value.lower().split("x", 1)
            width = int(width_str)
            height = int(height_str)
        except ValueError:
            return
        window = QtWidgets.QApplication.activeWindow()
        if not window:
            widgets = QtWidgets.QApplication.topLevelWidgets()
            window = widgets[0] if widgets else None
        if not window:
            return
        screen = window.screen() or QtWidgets.QApplication.primaryScreen()
        if not screen:
            window.resize(width, height)
            return
        available = screen.availableGeometry()
        width = min(width, available.width())
        height = min(height, available.height())
        window.resize(width, height)
        x = available.x() + (available.width() - width) // 2
        y = available.y() + (available.height() - height) // 2
        window.move(x, y)


class BackgroundImageBinder(QtCore.QObject):
    def __init__(self, target: QtWidgets.QWidget, image_path: Path, mode: str) -> None:
        super().__init__(target)
        self._target = target
        self._path = image_path
        self._mode = mode
        self._pixmap = QtGui.QPixmap(str(image_path))
        self._label = QtWidgets.QLabel(target)
        self._label.setAttribute(QtCore.Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self._label.lower()
        self._update(target.size())
        target.installEventFilter(self)

    def eventFilter(self, watched, event):  # type: ignore[override]
        if watched is self._target and event.type() == QtCore.QEvent.Type.Resize:
            self._update(event.size())
        return False

    def _update(self, size: QtCore.QSize) -> None:
        if self._pixmap.isNull():
            self._label.hide()
            return
        mode = (self._mode or "stretch").lower()
        if mode == "fit":
            pm = self._pixmap.scaled(size, QtCore.Qt.AspectRatioMode.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
            self._label.setPixmap(pm)
            self._label.resize(size)
            self._label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            self._label.show()
            return
        if mode == "cover":
            pm = self._pixmap.scaled(
                size, QtCore.Qt.AspectRatioMode.KeepAspectRatioByExpanding, QtCore.Qt.SmoothTransformation
            )
            self._label.setPixmap(pm)
            self._label.resize(size)
            self._label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            self._label.show()
            return
        if mode == "tile":
            tiled = QtGui.QPixmap(size)
            tiled.fill(QtCore.Qt.GlobalColor.transparent)
            painter = QtGui.QPainter(tiled)
            painter.drawTiledPixmap(tiled.rect(), self._pixmap)
            painter.end()
            self._label.setPixmap(tiled)
            self._label.resize(size)
            self._label.show()
            return
        if mode == "center":
            self._label.setPixmap(self._pixmap)
            self._label.resize(size)
            self._label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            self._label.show()
            return
        pm = self._pixmap.scaled(size, QtCore.Qt.AspectRatioMode.IgnoreAspectRatio, QtCore.Qt.SmoothTransformation)
        self._label.setPixmap(pm)
        self._label.resize(size)
        self._label.show()
