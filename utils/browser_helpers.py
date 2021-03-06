import os
import pickle
from typing import Literal

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC

from constants import CONTRACT
from logger import logger


IS_MAC = os.name == 'posix'


def save_cookie(driver: WebDriver, path: str) -> None:
    with open(path, "wb") as filehandler:
        pickle.dump(driver.get_cookies(), filehandler)


def load_cookie(driver: WebDriver, path: str) -> None:
    with open(path, "rb") as cookiesfile:
        cookies = pickle.load(cookiesfile)
        for cookie in cookies:
            driver.add_cookie(cookie)


def wait_and_click(
    driver: WebDriver, path: str, by: Literal['xpath', 'css'] = 'xpath'
) -> None:
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable(
            (By.XPATH, path) if by == 'xpath' else (By.CSS_SELECTOR, path)
        )
    ).click()


def get_element_until_present(
    driver: WebDriver, path: str, by: Literal['xpath', 'css'] = 'xpath'
) -> WebElement:
    return WebDriverWait(driver, 20).until(
        EC.presence_of_element_located(
            (By.XPATH, path) if by == 'xpath' else (By.CSS_SELECTOR, path)
        )
    )


def check_if_visible(driver: WebDriver, xpath: str) -> None:
    logger.info(
        'waiting for "FDC_{}" indicator to be visible ...'.format(CONTRACT.upper())
    )
    WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, xpath)))
    logger.info('"FDC_{}" indicator is visible'.format(CONTRACT.upper()))


def fill_input(element_to_fill: WebElement, to_fill: str) -> None:
    if IS_MAC:
        while True:
            element_to_fill.send_keys(Keys.BACK_SPACE)

            if element_to_fill.get_attribute('value') == '':
                break
    else:
        element_to_fill.send_keys(Keys.CONTROL + "a")
        element_to_fill.send_keys(Keys.DELETE)

    element_to_fill.send_keys(to_fill)
