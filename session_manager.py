import logging
import json
import requests
from bs4 import BeautifulSoup

from user import User
from config import config


class SessionManager:
    login_url: str = config.URL + config.END_POINT.LOGIN
    logout_url: str = config.URL + config.END_POINT.LOGOUT
    data_url: str = config.URL + config.END_POINT.MAIL_LIST + '?currentPage=1&viewRowCnt=' + '10' + '&sortField=RECEIVE_DT&sortType=DESC'
    confirmedEmailIds = set()

    def __init__(self):
        self.session = None

    def login(self, username, password):
        self.session = requests.Session()

        # 로그인 로직...
        logging.debug("로그인 시도 중..")
        payload = {'userId': username, 'userPw': password}
        response = self.session.post(self.login_url, data=payload)
        soup = BeautifulSoup(response.text, 'html.parser')
        titles = soup.findAll('title')

        for title in titles:
            if "로그인" in str(title):
                raise Exception("로그인에 실패하였습니다.")

        User.set_default_user(User(username, password))

        return self.session

    def logout(self):
        self.session.get(self.logout_url)

    def get_new_email(self):
        response = json.loads(self.session.get(self.data_url).text)
        if bool(response["errorMap"]):
            raise Exception(response["errorMap"])

        new_mails = list(filter(lambda r: r["emailId"] not in self.confirmedEmailIds, response["data"]))

        for row in new_mails:
            self.confirmedEmailIds.add(row["emailId"])

        return new_mails

session_manager = SessionManager()
