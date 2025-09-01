import sys
import logging

from user import User

from config import config
from toast import toast
from session_thread import SessionThread

from PyQt6.QtWidgets import QSystemTrayIcon, QMenu, QDialog, QApplication
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import QTimer, QTime, QDateTime
from PyQt6.uic import loadUi

from web_util import open_web_mail

logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.DEBUG, handlers=[logging.FileHandler("log.txt"), logging.StreamHandler()])


class LoginDialog(QDialog):

    def __init__(self):
        super().__init__()

        loadUi("ui/login.ui", self)

        self.logged_in = False
        self.thread: SessionThread
        self.setWindowIcon(QIcon("assets/icon.png"))

        user = User.get_default_user()
        self.id.setText(user.username)
        self.password.setText(user.password)

        self.login_button.clicked.connect(self.login_toggle)

    def login_toggle(self):
        if self.logged_in:
            # 로그아웃
            self.logout()
            self.logged_in = False
            self.login_button.setText("로그인")
        else:
            # 로그인
            username = self.id.text()
            password = self.password.text()

            if not username or not password:
                return

            user = User(username, password)

            self.run_monitor(user)

            self.logged_in = True
            self.login_button.setText("로그아웃")

    def logout(self):
        self.thread.stop()
        self.thread = None

    def run_monitor(self, user):

        try:
            self.thread = SessionThread(username=user.username, password=user.password)

            self.thread.msg.connect(self.thread_state_change)
            self.thread_state_change()

            if self.thread.status == "active":
                self.status_label.setText("🟢")
                self.thread.start()

        except Exception as e:
            logging.error(f"모니터링 시작 실패: {e}")
            self.status_label.setText("🔴")

    def thread_state_change(self):
        if self.thread.message.status == "ready":
            toast.success(self.thread.message.title, self.thread.message.msg)
        elif self.thread.message.status == "work":
            toast.mail_info(self.thread.message.title, self.thread.message.msg)
        else:
            self.status_label.setText("🔴")
            toast.warn(self.thread.message.title, self.thread.message.msg)


class App:
    def __init__(self):

        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)

        self.login_dialog = LoginDialog()

        # 트레이 아이콘
        self.tray_icon = QSystemTrayIcon(QIcon("assets/icon.png"))
        self.tray_icon.setToolTip("메일 모니터링")
        self.tray_icon.setVisible(True)

        tray_menu = QMenu()
        show_action = QAction("Login")
        web_action = QAction("Open Web")
        quit_action = QAction("Exit")

        show_action.triggered.connect(self.login_dialog.show)
        web_action.triggered.connect(self.open_mail)
        quit_action.triggered.connect(self.quit_app)

        tray_menu.addAction(show_action)
        tray_menu.addAction(web_action)
        tray_menu.addSeparator()
        tray_menu.addAction(quit_action)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self.handle_tray_icon_activated)
        # 트레이 아이콘 end

        self.login_dialog.login_toggle()  # 계정정보 있으면 로그인 시도

        self.quit_app_scheduler(config.SESSION_CONFIG.QUIT_APP_HOUR, config.SESSION_CONFIG.QUIT_APP_MINUTE)

        sys.exit(self.app.exec())

    def handle_tray_icon_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.login_dialog.show()

    def quit_app(self):
        if hasattr(self.login_dialog, "thread") and self.login_dialog.thread:
            self.login_dialog.thread.stop()
        self.tray_icon.hide()
        self.app.quit()

    def open_mail(self):
        open_web_mail()

    def quit_app_scheduler(self, hour, minute):
        now = QDateTime.currentDateTime()
        target = QDateTime(now.date(), QTime(hour, minute))

        # 이미 지났다면 다음날 18시로 설정
        if now > target:
            target = target.addDays(1)

        ms_until_target = now.msecsTo(target)
        QTimer.singleShot(ms_until_target, QApplication.quit)


if __name__ == "__main__":
    app = App()
