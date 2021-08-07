import os
import pickle
from PIL import Image

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement


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
    location = element.location
    size = element.size

    driver.save_screenshot(filename)

    x = location['x']
    y = location['y']
    w = size['width']
    h = size['height']
    width = x + w
    height = y + h

    img = Image.open(filename)
    img = img.crop((int(x), int(y), int(width), int(height)))
    img.save(os.path.join('results', 'charts', filename))
