import logging

from selenium import webdriver
from selenium.webdriver.chrome.service import Service

from config import config
from session_manager import session_manager

driver = None


def init_driver():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--incognito")  # 시크릿 모드
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-gpu")  # GPU 가속 비활성화
    chrome_options.add_argument("--disable-extensions")  # 확장 프로그램 비활성화
    chrome_options.add_argument("--disable-dev-shm-usage")  # 공유 메모리 비활성
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_experimental_option("detach", True)
    chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])  # 콘솔로그 출력 안하게
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])  # 자동화 제어 메시지 제거

    return webdriver.Chrome(service=Service(), options=chrome_options)


def open_web_mail():
    global driver

    # chromedriver 서비스 종료되지 않는 현상 제거
    if driver is not None:
        driver.quit()

    driver = init_driver()

    # Chrome 옵션 설정
    driver.get(config.URL + config.END_POINT.INDEX)
    # request -> selenium
    cookie_name = "JSESSIONID"
    cookies = session_manager.session.cookies.get_dict()
    driver.delete_cookie(cookie_name)
    driver.add_cookie(
        {
            "name": cookie_name,
            "value": cookies[cookie_name],
            "domain": config.URL.split("://")[1],
        }
    )
    driver.get(config.URL + config.END_POINT.MAIL)
