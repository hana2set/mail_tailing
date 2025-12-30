import logging

from selenium import webdriver
from selenium.webdriver.chrome.service import Service

from src.config import config


def init_driver():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--incognito")  # 시크릿 모드
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-gpu")  # GPU 가속 비활성화
    # chrome_options.add_argument("--disable-extensions")  # 확장 프로그램 비활성화
    chrome_options.add_argument("--disable-dev-shm-usage")  # 공유 메모리 비활성
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_experimental_option("detach", True)
    chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])  # 콘솔로그 출력 안하게
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])  # 자동화 제어 메시지 제거

    return webdriver.Chrome(service=Service(), options=chrome_options)


class BrowserManager:
    def __init__(self):
        self.driver = None

    def open_web_mail(self, cookies: dict):
        """
        :param cookies: requests 세션에서 추출한 쿠키 딕셔너리
        """

        try:
            # chromedriver 서비스 종료되지 않는 현상 제거
            if self.driver is not None:
                try:
                    self.driver.quit()
                except Exception as e:
                    logging.error(e)
                    raise AssertionError("기존 브라우저 종료에 실패했습니다.")

            self.driver = init_driver()

            # Chrome 옵션 설정
            # request -> selenium
            self.driver.get(config.URL + config.END_POINT.INDEX)    # 로그인 화면 진입
            cookie_name = "JSESSIONID"
            self.driver.delete_cookie(cookie_name)
            self.driver.add_cookie(
                {
                    "name": cookie_name,
                    "value": cookies[cookie_name],
                    "domain": config.URL.split("://")[1],
                }
            )
            self.driver.get(config.URL + config.END_POINT.MAIL)     # 메일 화면 진입

        except Exception as e:
            logging.error(f"브라우저 열기 실패: {e}")
