import logging

from PyQt6.QtCore import Qt
from pyqttoast import Toast as _Toast, ToastPreset

from config import config
from web_util import open_web_mail

_Toast.setMaximumOnScreen(5)


class Toast:
    def mail_info(self, title, message):
        _toast = _Toast()
        _toast.setTitle(title)
        _toast.setText(message)
        _toast.setDuration(config.SESSION_CONFIG.TOAST_MAIL_DURATION_SEC)
        _toast.mousePressEvent = lambda e, t=_toast: self.open_email(e, t)
        _toast.applyPreset(ToastPreset.INFORMATION)
        _toast.show()

        logging.info(title)
        logging.info(message)

    def success(self, title, message):
        _toast = _Toast()
        _toast.setTitle(title)
        _toast.setText(message)
        _toast.setDuration(config.SESSION_CONFIG.TOAST_SUCCESS_DURATION_SEC)
        _toast.applyPreset(ToastPreset.SUCCESS)
        _toast.show()

    def warn(self, title, message):
        _toast = _Toast()
        _toast.setDuration(config.SESSION_CONFIG.TOAST_WARN_DURATION_SEC)
        _toast.setTitle(title)
        _toast.setText(message)
        _toast.applyPreset(ToastPreset.WARNING)
        _toast.show()

        logging.warning(title)
        logging.warning(message)

    def open_email(self, e, _toast: _Toast):
        if e.button() == Qt.MouseButton.LeftButton:
            # 창 닫기
            _toast.close()

            # 웹메일 페이지 띄우기
            open_web_mail()


toast = Toast()
