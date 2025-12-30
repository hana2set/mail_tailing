from pathlib import Path  # 추가
from PyQt6.QtWidgets import QDialog
from PyQt6.QtGui import QIcon
from PyQt6.uic import loadUi

from src.models.user import User
from src.ui.toast_manager import ToastManager
from src.services.mail_service import MailService  # 새로 만든 서비스

toast = ToastManager()
BASE_DIR = Path(__file__).resolve().parent


class LoginDialog(QDialog):

    def __init__(self, service: MailService):
        super().__init__()

        loadUi("src/ui/files/login.ui", self)

        self.service = service
        self.setWindowIcon(QIcon("assets/icon.png"))

        user = User.load()
        if user:
            self.id.setText(user.username)
            self.password.setText(user.password)

        self.login_button.clicked.connect(self.toggle_login)
        self.service.login_status_changed.connect(self.update_ui_state)

    def toggle_login(self):
        if self.service.is_logged_in():
            # 로그아웃
            self.service.logout()
        else:
            # 로그인
            username = self.id.text()
            password = self.password.text()

            if not username or not password:
                return

            try:
                self.service.login(username, password)
                self.close()
            except Exception as e:
                self.status_label.setText("🔴")
                toast.warn("로그인 실패", str(e))

            # self.logged_in = True
            # self.login_button.setText("로그아웃")

    def update_ui_state(self, is_logged_in):
        if is_logged_in:
            self.status_label.setText("🟢")
            self.login_button.setText("로그아웃")
        else:
            self.status_label.setText("🔴")
            self.login_button.setText("로그인")
