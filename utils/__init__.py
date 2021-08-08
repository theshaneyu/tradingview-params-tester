import os
import pickle
from typing import Dict, TypedDict

from PIL import Image
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement

from constants import EXECUTION_TIME


def save_cookie(driver: WebDriver, path: str) -> None:
    with open(path, "wb") as filehandler:
        pickle.dump(driver.get_cookies(), filehandler)


def load_cookie(driver: WebDriver, path: str) -> None:
    with open(path, "rb") as cookiesfile:
        cookies = pickle.load(cookiesfile)
        for cookie in cookies:
            driver.add_cookie(cookie)


def save_screenshot_as_png(
    driver: WebDriver, element: WebElement, filename: str
) -> None:
    image_file_path = os.path.join('results', EXECUTION_TIME, 'charts', filename)

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
