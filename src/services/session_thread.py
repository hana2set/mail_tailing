import logging
from PyQt6.QtCore import QThread, pyqtSignal, QTimer
from src.config import config
from dataclasses import dataclass


@dataclass(frozen=True)
class ToastRequest:
    status: str
    title: str
    msg: str


class SessionThread(QThread):
    msg_signal = pyqtSignal(object)  # 외부 메세지용 시그널

    def __init__(self, session_manager):
        super().__init__()
        self.session_manager = session_manager
        self.timer = None

    def run(self):
        logging.debug("thread 시작..")

        # 테스트: 최초 1회 직접 실행
        # self.monitor()

        try:
            self.session_manager.get_new_email()  # 기존 메일 리스트 입력
        except Exception as e:
            self._send_toast("error", "초기화 실패", str(e))
            return

        self.timer = QTimer()
        self.timer.timeout.connect(self.monitor)
        self.timer.start(config.SESSION_CONFIG.AUTO_REFRESH_INTERVAL_SEC)

        self._send_toast("ready", "프로그램 시작", "메일 감지가 시작됩니다..")

        self.exec()
        # self.exec_()  # 타이머 실행 대기

    def stop(self):
        self._send_toast("stop", "종료", "모니터링이 중지되었습니다.")
        if self.timer:
            self.timer.stop()
        self.session_manager.logout()
        self.quit()
        self.wait()  # 스레드 종료 대기

    def monitor(self):
        logging.info("메일 확인 중..")

        try:
            new_mails: list = self.session_manager.get_new_email()
            if new_mails:
                title = new_mails[0].get("emailTitle", "제목 없음")
                self._send_toast("work", f"신규 메일 {len(new_mails)} 건", f"제목: {title}")
        except Exception as e:
            self._send_toast("error", "오류 발생", str(e))
            self.stop()

    def _send_toast(self, status, title, message):
        req = ToastRequest(status, title, message)
        self.msg_signal.emit(req)
