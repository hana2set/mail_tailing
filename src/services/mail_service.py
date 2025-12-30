import logging
from PyQt6.QtCore import QObject, pyqtSignal

from src.services.session_manager import SessionManager
from src.services.session_thread import SessionThread
from src.utils.web_util import BrowserManager
from src.models.user import User


class MailService(QObject):
    # UI에 상태를 알리기 위한 시그널들
    login_status_changed = pyqtSignal(bool)  # True: 성공, False: 실패/로그아웃
    thread_msg_received = pyqtSignal(object)  # ToastRequest 전달

    def __init__(self):
        super().__init__()
        self.session_manager = SessionManager()
        self.browser_manager = BrowserManager()
        self.thread = None
        self.current_user = None

    def login(self, username, password):
        try:
            self.session_manager.login(username, password)
            self.current_user = User(username, password)
            self.current_user.save()

            self._start_thread()
            self.login_status_changed.emit(True)

        except Exception as e:
            logging.error(f"로그인 실패: {e}")
            # 여기서 UI에 실패 알림을 보내거나 예외를 다시 던짐
            raise e

    def logout(self):
        if self.thread:
            self.thread.stop()
            self.thread = None

        self.session_manager.logout()
        self.current_user = None
        self.login_status_changed.emit(False)

    def open_browser(self):
        cookies = self.session_manager.get_cookies_dict()
        if not cookies:
            logging.warning("로그인 상태가 아닙니다.")
            return
        self.browser_manager.open_web_mail(cookies)

    def is_logged_in(self):
        return self.session_manager.session is not None

    def _start_thread(self):
        if self.thread is not None:
            self.thread.stop()

        self.thread = SessionThread(self.session_manager)
        self.thread.msg_signal.connect(self.thread_msg_received)
        self.thread.start()
