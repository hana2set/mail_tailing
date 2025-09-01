# import requests
import logging

from PyQt6.QtCore import QThread, pyqtSignal, QTimer

# from bs4 import BeautifulSoup

from config import config
from session_manager import session_manager

# from user import User
from dataclasses import dataclass


@dataclass(frozen=True)
class ToastRequest:
    status: str
    title: str
    msg: str


class SessionThread(QThread):
    msg = pyqtSignal(object)  # 외부 메세지용 시그널

    def __init__(self, username, password):
        super().__init__()
        self._message = None
        self.status = "waiting"

        self.timer = QTimer()
        self.timer.timeout.connect(self.monitor)
        self.timer.moveToThread(self)

        try:
            self.session = session_manager
            self.session.login(username, password)
            self.status = "active"
            self.message = ToastRequest("ready", "프로그램 시작", "메일 감지가 시작됩니다..")
        except Exception as e:
            self.message = ToastRequest("error", "로그인 실패", f"{e}")

    @property
    def message(self):
        return self._message

    @message.setter
    def message(self, value):
        self._message = value
        self.msg.emit(value)

    def run(self):
        logging.debug("thread 시작..")
        # self.monitor()  #최초 1회 직접 실행
        self.session.get_new_email()  # 기존 메일 리스트 입력
        self.timer.start(config.SESSION_CONFIG.AUTO_REFRESH_INTERVAL_SEC)
        self.exec_()  # 타이머 실행 대기

    def stop(self, e):
        if e is not None:
            self.message = ToastRequest("error", "에러가 발생하여 모니터링이 종료됩니다.", f"에러: {e}")
        else:
            self.message = ToastRequest("stop", "프로그램 종료", "메일 감지가 중지되었습니다..")
        self.session.logout()
        self.timer.stop()
        self.quit()
        self.wait()  # 스레드 종료 대기

    def monitor(self):
        logging.info("메일 모니터링 중..")
        if self.status == "active":
            try:
                new_mails: list = self.session.get_new_email()
                if len(new_mails) > 0:
                    self.message = ToastRequest("work", f"신규 메일 {len(new_mails)} 건", f"제목: {new_mails[0]["emailTitle"]}")
            except Exception as e:
                # self.message = ToastRequest("error", "에러가 발생하여 모니터링이 종료됩니다.", f"에러: {e}")
                self.status = "error"
                self.stop(e)
