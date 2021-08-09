import pickle
from typing import Literal


from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC


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


def check_if_visible(driver: WebDriver, xpath: str) -> None:
    print('Waiting to be visible ...')
    WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, xpath)))
    print('Visible')
