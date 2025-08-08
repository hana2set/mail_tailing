import sys
import logging

from user import User

from config import config
from toast import toast
from session_thread import SessionThread

from PyQt6.QtWidgets import (
    QSystemTrayIcon, QMenu, QDialog, QApplication, QPushButton
)
from PyQt6.QtGui import QIcon, QAction
from PyQt6.uic import loadUi

logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.DEBUG,
    handlers=[
        logging.FileHandler('log.txt'),
        logging.StreamHandler()
    ]
)

class LoginDialog(QDialog):

    def __init__(self):
        super().__init__()

        loadUi("ui/login.ui", self)

        self.logged_in = False
        self.thread:SessionThread
        self.setWindowIcon(QIcon("assets/icon.png"))

        user = User.get_default_user()
        self.id.setText(user.username)
        self.password.setText(user.password)

        self.login_button.clicked.connect(self.login_toggle)

    # def show(self):

        # # 위치: 오른쪽 하단
        # screen = QApplication.primaryScreen().availableGeometry()
        # login.end_pos = QPoint(screen.right() - login.width() - 20, screen.bottom() - login.height() - 20)
        # login.start_pos = QPoint(login.end_pos.x(), screen.bottom() + 100)
        #
        # login.move(login.start_pos)

        # 애니메이션
        # self.ui.anim = QPropertyAnimation(self.ui, b"geometry")
        # self.ui.anim.setDuration(200)
        # self.ui.anim.setStartValue(QRect(self.ui.start_pos, self.ui.size()))
        # self.ui.anim.setEndValue(QRect(self.ui.end_pos, self.ui.size()))
        # self.ui.anim.start()

        # self.show()

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
        self.thread = SessionThread(
            login_url=config.URL + config.END_POINT.LOGIN,
            logout_url=config.URL + config.END_POINT.LOGOUT,
            data_url=config.URL + config.END_POINT.MAIL_LIST + '?currentPage=1&viewRowCnt=' + '10' + '&sortField=RECEIVE_DT&sortType=DESC',
            username=user.username,
            password=user.password
        )

        self.thread.msg.connect(self.thread_state_change)
        self.thread_state_change()

        if self.thread.status == "active":
            self.status_label.setText("🟢")
            self.thread.start()

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
        show_action = QAction("Show Login")
        quit_action = QAction("Exit")

        show_action.triggered.connect(self.login_dialog.show)
        quit_action.triggered.connect(self.quit_app)

        tray_menu.addAction(show_action)
        tray_menu.addSeparator()
        tray_menu.addAction(quit_action)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self.handle_tray_icon_activated)
        # 트레이 아이콘 end

        self.login_dialog.login_toggle() # 계정정보 있으면 로그인 시도

        sys.exit(self.app.exec())

    def handle_tray_icon_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.login_dialog.show()

    def quit_app(self):
        self.tray_icon.hide()
        self.app.quit()

    # def login_state_change(self):
    #     if self.login_dialog.thread.status == "work":
    #         self.login_dialog.status_label.setText("🟢")
    #         self.tray_icon.setIcon(QIcon("assets/icon.png"))
    #         toast.success('프로그램 시작', '메일 감지가 시작됩니다..')
    #     else:
    #         self.login_dialog.status_label.setText("🔴")
    #         self.tray_icon.setIcon(QIcon("assets/fail.png"))
    #         toast.warn('프로그램 종료', '메일 감지가 중지되었습니다..')


if __name__ == "__main__":
    app = App()