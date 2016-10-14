import os
from contextlib import contextmanager
import logging
import datetime
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions import staleness_of

from secret import LOGIN, PASSWORD, MAIN_URL

os.path.join(os.path.dirname(os.path.abspath(__file__)), '')


class LoginPageLocators:
    LOGIN_INPUT = (By.NAME, 'USER_LOGIN')
    PASS_INPUT = (By.NAME, 'USER_PASSWORD')
    LOGIN_BTN = (By.CLASS_NAME, 'login-btn')


class MainPageLocators:
    STATUS = (By.XPATH, '//*[@id="timeman-status"]')
    TIMER_CONT = (By.XPATH, '//*[@id="timeman-block"]')
    OPEN_DAY_BTN = (By.CLASS_NAME, 'tm-popup-button-handler')

    SEND_REPORT_BTN = (By.ID, 'tm-work-report-send')

    FIRST_CLOSE_BTN = (By.CLASS_NAME, 'webform-button-decline')
    REPORT_TEXTAREA = (By.CLASS_NAME, 'tm-report-popup-desc-textarea')
    CLOSE_DAY_BTNS = (By.CLASS_NAME, 'popup-window-button-decline')


class Bitrix(object):
    main_url = MAIN_URL

    def __init__(self, headless=True):
        if headless:
            self.browser = webdriver.PhantomJS(
                executable_path='/usr/local/lib/node_modules'
                                '/phantomjs/lib/phantom/bin/phantomjs')
            self.browser.set_window_size(1600, 1200)
        else:
            driver = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                  'chromedriver')
            self.browser = webdriver.Chrome(driver)

        self.log = logging.getLogger('bitrix')
        self.logged_in = False

    @contextmanager
    def wait_for_page_load(self, timeout=10):
        self.log.debug(
            "Waiting for page load at {}.".format(self.browser.current_url))
        old_page = self.browser.find_element_by_tag_name('html')
        yield
        WebDriverWait(self.browser, timeout).until(staleness_of(old_page))

    def login(self):
        self.browser.get(self.main_url)
        login_input = self.browser.find_element(*LoginPageLocators.LOGIN_INPUT)
        pass_input = self.browser.find_element(*LoginPageLocators.PASS_INPUT)
        login_btn = self.browser.find_element(*LoginPageLocators.LOGIN_BTN)

        login_input.clear()
        login_input.send_keys(LOGIN)

        pass_input.clear()
        pass_input.send_keys(PASSWORD)

        with self.wait_for_page_load():
            login_btn.click()

        try:
            assert 'optimism' in self.browser.title, "Wrong title"
        except AssertionError as e:
            self.log.warning(e)

        self.logged_in = True
        self.log.debug("Successfully logged in")

    def open_day(self):
        if not self.logged_in:
            self.login()

        status = self.browser.find_element(*MainPageLocators.STATUS)

        assert 'Начать' in status.get_attribute('innerHTML')

        timer_cont = self.browser.find_element(*MainPageLocators.TIMER_CONT)
        timer_cont.click()

        open_btn = self.browser.find_element(*MainPageLocators.OPEN_DAY_BTN)
        open_btn.click()

        self.browser.close()
        self.log.debug('Day opened')

    def _close_week(self):
        send_report_btn = self.browser.find_element(
            *MainPageLocators.SEND_REPORT_BTN)
        send_report_btn.click()
        self.log.debug('Weekly report sent')

    def close_day(self):
        if not self.logged_in:
            self.login()

        today = datetime.date.today()
        if today.weekday() == 4:  # 0 - Monday, 6 - Sunday
            self._close_week()

        status = self.browser.find_element(*MainPageLocators.STATUS)

        assert 'Работаю' in status.get_attribute('innerHTML')

        timer_cont = self.browser.find_element(*MainPageLocators.TIMER_CONT)
        timer_cont.click()

        first_close_btn = self.browser.find_element(
            *MainPageLocators.FIRST_CLOSE_BTN)
        first_close_btn.click()
        time.sleep(3)  # cause bitrix, that's why

        report_text_areas = self.browser.find_elements(
            *MainPageLocators.REPORT_TEXTAREA)
        for report in report_text_areas:  # minimum 3 same areas
            if report.is_displayed():
                report.send_keys('qwe')

        close_btns = self.browser.find_elements(
            *MainPageLocators.CLOSE_DAY_BTNS)
        for btn in close_btns:  # minimum 3 same btns
            if btn.is_displayed():
                btn.click()

        self.browser.close()
        self.log.debug('Day closed')
