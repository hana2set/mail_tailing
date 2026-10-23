import json

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QCheckBox,
    QDialogButtonBox,
    QDialog,
    QFormLayout,
    QGroupBox,
    QLineEdit,
    QMessageBox,
)
from PyQt6.uic import loadUi

from src.config import CONFIG_PATH, save_config_data
from src.utils.paths import BASE_DIR, PROJECT_ROOT


SECTION_LABELS = {
    "END_POINT": "접속 경로",
    "SESSION_CONFIG": "세션 및 알림",
}

SETTING_LABELS = {
    "URL": "서버 주소",
    "LOGIN": "로그인 경로",
    "LOGOUT": "로그아웃 경로",
    "MAIL": "메일 페이지 경로",
    "INDEX": "메인 페이지 경로",
    "MAIL_LIST": "메일 목록 경로",
    "MAX_RETRY_COUNT": "최대 재시도 횟수 (회)",
    "RETRY_DELAY": "재시도 대기 시간 (ms)",
    "AUTO_REFRESH_INTERVAL_SEC": "메일 확인 간격 (ms)",
    "TOAST_MAIL_DURATION_SEC": "새 메일 알림 표시 시간 (ms)",
    "TOAST_SUCCESS_DURATION_SEC": "성공 알림 표시 시간 (ms)",
    "TOAST_WARN_DURATION_SEC": "경고 알림 표시 시간 (ms)",
    "QUIT_APP_HOUR": "자동 종료 시각 (시)",
    "QUIT_APP_MINUTE": "자동 종료 시각 (분)",
}


class SettingsDialog(QDialog):
    """Edit scalar values in data/config.json in a separate settings window."""

    def __init__(self, parent=None):
        super().__init__(parent)
        loadUi(BASE_DIR / "ui" / "files" / "settings.ui", self)
        self.setWindowIcon(QIcon(str(PROJECT_ROOT / "assets" / "icon.png")))
        self._widgets = {}
        self._original = self._read_config()
        self.button_box.button(QDialogButtonBox.StandardButton.Save).setText("저장")
        self.button_box.button(QDialogButtonBox.StandardButton.Cancel).setText("취소")

        for section_name, section_data in self._original.items():
            if isinstance(section_data, dict):
                group = QGroupBox(
                    SECTION_LABELS.get(section_name, section_name), self.settings_content
                )
                form = QFormLayout(group)
                for key, value in section_data.items():
                    self._add_field(form, f"{section_name}.{key}", value)
                self.settings_layout.addWidget(group)
            else:
                if not hasattr(self, "_root_form"):
                    top_group = QGroupBox("기본 설정", self.settings_content)
                    self._root_form = QFormLayout(top_group)
                    self.settings_layout.addWidget(top_group)
                self._add_field(self._root_form, section_name, section_data)

        self.settings_layout.addStretch(1)
        self.button_box.accepted.connect(self.save)
        self.button_box.rejected.connect(self.reject)

    @staticmethod
    def _read_config():
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)

    def _add_field(self, form, path, value):
        if isinstance(value, bool):
            widget = QCheckBox()
            widget.setChecked(value)
        else:
            display_value = f"{value:,}" if isinstance(value, (int, float)) else str(value)
            widget = QLineEdit(display_value)
            widget.setAlignment(Qt.AlignmentFlag.AlignLeft)
            if isinstance(value, (int, float)) and not isinstance(value, bool):
                widget.editingFinished.connect(
                    lambda field=widget, number_type=type(value): self._format_number(
                        field, number_type
                    )
                )
        self._widgets[path] = (widget, value)
        key = path.split(".")[-1]
        form.addRow(SETTING_LABELS.get(key, key), widget)

    def _collect_config(self):
        data = json.loads(json.dumps(self._original))
        for path, (widget, original) in self._widgets.items():
            value = widget.isChecked() if isinstance(widget, QCheckBox) else widget.text().strip()
            if isinstance(original, bool):
                parsed = value
            elif isinstance(original, int):
                parsed = int(value.replace(",", ""))
            elif isinstance(original, float):
                parsed = float(value.replace(",", ""))
            else:
                parsed = value

            parts = path.split(".")
            target = data
            for part in parts[:-1]:
                target = target[part]
            target[parts[-1]] = parsed
        return data

    @staticmethod
    def _format_number(widget, number_type):
        try:
            value = number_type(widget.text().replace(",", "").strip())
            widget.setText(f"{value:,}")
        except ValueError:
            pass

    def save(self):
        try:
            data = self._collect_config()
            save_config_data(data)
        except (ValueError, TypeError, OSError) as exc:
            QMessageBox.warning(self, "설정 저장 실패", f"입력값을 확인해 주세요.\n{exc}")
            return
        self.accept()
