import sys
import logging

from ui.login_dialog import LoginDialog

from config import config
from src.ui.toast_manager import ToastManager

from PyQt6.QtWidgets import QSystemTrayIcon, QMenu, QApplication
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import QTimer, QTime, QDateTime, QObject
from src.services.mail_service import MailService  # 새로 만든 서비스

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.DEBUG,
    handlers=[logging.FileHandler("../log.txt"), logging.StreamHandler()],
)

toast = ToastManager()


class App(QObject):
    def __init__(self):
        super().__init__()
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)

        # 1. 서비스 생성
        self.mail_service = MailService()
        self.mail_service.thread_msg_received.connect(self.handle_thread_message)

        # 2. UI 생성
        self.login_dialog = LoginDialog(self.mail_service)

        # 3. 트레이 아이콘
        self.setup_tray()

    def setup_tray(self):
        self.tray_icon = QSystemTrayIcon(QIcon("assets/icon.png"))
        self.tray_icon.setToolTip("메일 모니터링")

        menu = QMenu()
        show_action = QAction("Login", menu)
        web_action = QAction("Open Web", menu)
        quit_action = QAction("Exit", menu)

        menu.addAction(show_action)
        menu.addAction(web_action)
        menu.addSeparator()
        menu.addAction(quit_action)

        # 이벤트
        show_action.triggered.connect(self.login_dialog.show)
        web_action.triggered.connect(self.mail_service.open_browser)
        quit_action.triggered.connect(self.quit_app)

        self.tray_icon.setContextMenu(menu)
        self.tray_icon.activated.connect(self.handle_tray_click)

    def run(self):
        # 기본 화면
        self.tray_icon.show()
        self.login_dialog.toggle_login()  # 계정정보 있으면 로그인 시도

        if not self.mail_service.is_logged_in():
            self.login_dialog.show()

        # 스케쥴러
        quit_app_scheduler(config.SESSION_CONFIG.QUIT_APP_HOUR, config.SESSION_CONFIG.QUIT_APP_MINUTE)

        logging.info("Application started")
        return self.app.exec()

    def handle_tray_click(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.login_dialog.show()

    def handle_thread_message(self, msg):
        if msg.status == "ready":
            toast.success(msg.title, msg.msg, None)
        elif msg.status == "work":
            # 클릭 시 웹 메일 열기 콜백 연결
            toast.mail_info(msg.title, msg.msg, callback=self.mail_service.open_browser)
        else:
            toast.warn(msg.title, msg.msg)

    def quit_app(self):
        self.mail_service.logout()  # 스레드 정리 포함됨
        self.tray_icon.hide()
        self.app.quit()


def quit_app_scheduler(hour, minute):
    now = QDateTime.currentDateTime()
    target = QDateTime(now.date(), QTime(hour, minute))

    # 이미 지났다면 다음날 18시로 설정
    if now > target:
        target = target.addDays(1)

    ms_until_target = now.msecsTo(target)
    QTimer.singleShot(ms_until_target, QApplication.quit)


if __name__ == "__main__":
    try:
        app_instance = App()
        exit_code = app_instance.run()
        sys.exit(exit_code)

    except Exception:
        logging.exception("치명적 오류 발생")
