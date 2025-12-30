import logging
import json
import requests
from bs4 import BeautifulSoup

from src.models.user import User
from src.config import config


class SessionManager:

    def __init__(self):
        self.session = None
        self.confirmed_email_ids = set()

        self.login_url = config.URL + config.END_POINT.LOGIN
        self.logout_url = config.URL + config.END_POINT.LOGOUT
        self.data_url = (
            f"{config.URL}{config.END_POINT.MAIL_LIST}"
            "?currentPage=1&viewRowCnt=10&sortField=RECEIVE_DT&sortType=DESC"
        )

    def login(self, username, password) -> requests.Session:
        logging.debug("로그인 시도 중..")

        session = requests.Session()
        payload = {"userId": username, "userPw": password}
        try:
            response = session.post(self.login_url, data=payload)
            soup = BeautifulSoup(response.text, "html.parser")
            titles = soup.findAll("title")

            if any("로그인" in str(title) for title in titles):
                raise Exception("로그인에 실패하였습니다.")

            User(username, password).save()

            self.session = session
            return self.session

        except requests.RequestException as e:
            logging.error(f"네트워크 오류: {e}")
            raise ConnectionError("서버에 접속할 수 없습니다.")

    def logout(self):
        if self.session:
            try:
                self.session.get(self.logout_url)
            except Exception:
                pass
            self.session = None

    def get_new_email(self) -> list:
        if not self.session:
            raise PermissionError("로그인이 필요합니다.")

        response = json.loads(self.session.get(self.data_url).text)
        if bool(response["errorMap"]):
            raise Exception(response["errorMap"])

        new_mails = [m for m in response["data"] if m["emailId"] not in self.confirmed_email_ids]

        for mail in new_mails:
            self.confirmed_email_ids.add(mail["emailId"])

        return new_mails

    def get_cookies_dict(self):
        if self.session:
            return self.session.cookies.get_dict()
        return {}
