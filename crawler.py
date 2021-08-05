import os
import time

import pickle
from utils import load_cookie, save_cookie

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


URL = "https://tw.tradingview.com/chart/Iyu69JVU/"
# URL = "https://www.tradingview.com/cryptocurrency-signals/"

# COOKIE_PATH = "/tmp/cookie"
COOKIE_PATH = os.path.join(".tmp", "cookie")


class Crawler:
    def __init__(self) -> None:
        self._check_driver_and_cookie_folders()

    def _check_driver_and_cookie_folders(self) -> None:
        # check chromedriver's existence
        files = os.listdir("chromedriver")
        if len(files) != 1:
            raise Exception("Chromedriver not found")
        self.chromedriver_path = os.path.join("chromedriver", files[0])

        # check cookies folder
        if not os.path.exists(".tmp"):
            os.makedirs(".tmp")

    def wait_and_click(browser, path):
        WebDriverWait(browser, 10).until(
            EC.element_to_be_clickable((By.XPATH, path))
        ).click()

    def main(self) -> None:
        options = webdriver.ChromeOptions()
        # options.add_argument("headless")
        # options.add_argument("window-size=1200,1100")

        browser = webdriver.Chrome(
            executable_path=self.chromedriver_path, chrome_options=options
        )

        browser.get(URL)

        if not os.path.exists(COOKIE_PATH):
            # no cookies are found yet
            _ = input()
            save_cookie(browser, COOKIE_PATH)

        load_cookie(browser, COOKIE_PATH)

        browser.get(URL)

        _ = input()

        # save_cookie(browser, COOKIE_PATH)

        # browser.maximize_window()
        # browser.implicitly_wait(60)
        # time.sleep(1000)

        # self.wait_and_click(browser, '//*[@id="js-screener-container"]/div[2]/div[7]/div[1]')
        # self.wait_and_click(
        #     browser,
        #     '//*[@id="js-screener-container"]/div[2]/div[7]/div[2]/div/div[1]/div[2]',
        # )
        # self.wait_and_click(browser, '//*[@id="js-screener-container"]/div[2]/div[13]')


if __name__ == "__main__":
    crawler = Crawler()
    crawler.main()
