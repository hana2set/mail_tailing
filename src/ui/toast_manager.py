import logging

from PyQt6.QtCore import QObject, pyqtSignal, Qt
from PyQt6.QtWidgets import QAbstractButton
from pyqttoast import Toast, ToastPreset

from src.config import config

Toast.setMaximumOnScreen(5)


class _ClickableToast(Toast):
    clicked = pyqtSignal()  # 클릭 이벤트 신호 정의

    def __init__(self, parent):
        super().__init__(parent)

    # 마우스 클릭 이벤트 오버라이딩
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()  # 액션 추가용 신호 발송
            self._trigger_close_button()
        super().mousePressEvent(event)  # 기존 동작 수행

    def _trigger_close_button(self):
        """
        Toast 내부에 있는 닫기 버튼을 찾아서 강제로 클릭.
        """
        buttons = self.findChildren(QAbstractButton)

        found_close_btn = False
        for btn in buttons:
            if btn.isVisible():
                btn.animateClick()  # 사용자가 클릭한 것과 동일한 효과
                found_close_btn = True
                break

        # X 버튼 못찾으면 강제 종료 (기존 애니메이션 X)
        if not found_close_btn:
            self.close()


class ToastManager(QObject):
    def __init__(self, parent_widget=None):
        super().__init__()
        self.parent_widget = parent_widget

    def mail_info(self, title, message, callback=None):
        toast = _ClickableToast(self.parent_widget)
        toast.setTitle(title)
        toast.setText(message)
        toast.setDuration(config.SESSION_CONFIG.TOAST_MAIL_DURATION_SEC)
        toast.applyPreset(ToastPreset.INFORMATION)

        if callback:
            toast.clicked.connect(callback)
        toast.show()

        logging.info(title)
        logging.info(message)

    def success(self, title, message, callback=None):
        toast = _ClickableToast(self.parent_widget)
        toast.setTitle(title)
        toast.setText(message)
        toast.setDuration(config.SESSION_CONFIG.TOAST_SUCCESS_DURATION_SEC)
        toast.applyPreset(ToastPreset.SUCCESS)

        if callback:
            toast.clicked.connect(callback)
        toast.show()

    def warn(self, title, message):
        toast = Toast(self.parent_widget)
        toast.setDuration(config.SESSION_CONFIG.TOAST_WARN_DURATION_SEC)
        toast.setTitle(title)
        toast.setText(message)
        toast.applyPreset(ToastPreset.WARNING)
        toast.show()

        logging.warning(title)
        logging.warning(message)
