from PyQt6.QtCore import QObject, pyqtSignal
from session_thread import SessionThread
import logging

class MonitorService(QObject):
    # UI로 보낼 신호들 정의
    state_changed = pyqtSignal(bool)  # 로그인 상태 변경 (True/False)
    mail_received = pyqtSignal(str, str)  # 제목, 내용
    error_occurred = pyqtSignal(str)  # 에러 메시지

    def __init__(self):
        super().__init__()
        self.thread = None

    def start_monitoring(self, username, password):
        self.stop_monitoring()  # 기존 스레드 정리

        try:
            self.thread = SessionThread(username=username, password=password)
            self.thread.msg_signal.connect(self._handle_thread_msg)
            self.thread.start()

            # 성공했다고 가정하고 상태 알림 (실제 성공 여부는 스레드 내부 로직에 따라 다를 수 있음)
            self.state_changed.emit(True)
            logging.info(f"Service: {username} 모니터링 시작")

        except Exception as e:
            self.error_occurred.emit(str(e))

    def stop_monitoring(self):
        if self.thread:
            self.thread.stop()
            self.thread = None
        self.state_changed.emit(False)

    def _handle_thread_msg(self):
        # 스레드에서 온 메시지를 가공해서 적절한 신호로 변환
        if not self.thread:
            return

        msg = self.thread.message
        if msg.status == "work":
            self.mail_received.emit(msg.title, msg.msg_signal)
        elif msg.status == "fail":
            self.error_occurred.emit(msg.msg_signal)
            self.state_changed.emit(False)
        # 필요한 경우 "ready" 상태 처리 등 추가
