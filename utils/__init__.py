import os
import pickle
from typing import Dict, Literal

import pandas as pd
from PIL import Image
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC

from constants import EXECUTION_TIME


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



def save_screenshot_as_png(
    driver: WebDriver, element: WebElement, params_filename: str
) -> None:
    image_file_path = os.path.join(
        'results', EXECUTION_TIME, 'charts', '{}.png'.format(params_filename)
    )

    location = element.location
    size = element.size

    driver.save_screenshot(image_file_path)

    x = location['x']
    y = location['y']
    w = size['width']
    h = size['height']
    width = x + w
    height = y + h

    img = Image.open(image_file_path)
    img = img.crop((int(x), int(y), int(width), int(height)))
    img.save(image_file_path)


def append_params_csv(params: Dict[str, str], profit: str, win_rate: str) -> None:
    with open(
        os.path.join(
            'results', EXECUTION_TIME, 'params', '{}.csv'.format(EXECUTION_TIME)
        ),
        'a',
        encoding='utf8',
    ) as af:
        af.write(
            '{},{},{},{},{},{}'.format(
                params['period'],
                params['amplifier'],
                params['long_take_profit'],
                params['short_take_profit'],
                profit,
                win_rate,
            )
        )


def save_performance_summary_to_csv(
    table_element: WebElement, params_filename: str
) -> None:
    tbl = table_element.get_attribute('outerHTML')
    df = pd.read_html(tbl)[0]
    print(df)
    df.to_csv(
        os.path.join(
            'results', EXECUTION_TIME, 'performance', '{}.csv'.format(params_filename)
        ),
        encoding='utf_8_sig',
    )
