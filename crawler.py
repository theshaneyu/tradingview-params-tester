import os
import sys
import time
import base64
import logging
import traceback

from typing import Dict, Literal

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC

from constant import PARAMS_INDEX_MAPPING
from utils import load_cookie, save_cookie, save_screenshot_as_png


URL = 'https://tw.tradingview.com/chart/Iyu69JVU/'
# URL = 'https://www.tradingview.com/cryptocurrency-signals/'

# COOKIE_PATH = '/tmp/cookie'
COOKIE_PATH = os.path.join('.tmp', 'cookie')


class Crawler:
    def __init__(self) -> None:
        self._check_driver_and_cookie_folders()

    def _check_driver_and_cookie_folders(self) -> None:
        # check chromedriver's existence
        files = os.listdir('chromedriver')
        if len(files) != 1:
            raise Exception('Chromedriver not found')
        self.chromedriver_path = os.path.join('chromedriver', files[0])

        # check cookies folder
        if not os.path.exists('.tmp'):
            os.makedirs('.tmp')

        # check results folder
        if not os.path.exists('results'):
            os.makedirs('results')
            os.makedirs(os.path.join('results', 'charts'))
            os.makedirs(os.path.join('results', 'performance'))
            os.makedirs(os.path.join('results', 'transactions'))

    def _wait_and_click(
        self, driver: WebDriver, path: str, by: Literal['xpath', 'css'] = 'xpath'
    ) -> None:
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, path) if by == 'xpath' else (By.CSS_SELECTOR, path)
            )
        ).click()

    def _check_if_visible(self, driver: WebDriver, xpath: str) -> None:
        print('開始等')
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, xpath))
        )
        print('已出現')

        return

    def _save_chart_as_png(
        self, driver: WebDriver, canvas_element: WebElement, filename: str
    ) -> None:
        """
        docstring
        """
        # get the canvas as a PNG base64 string
        canvas_base64 = driver.execute_script(
            "return arguments[0].toDataURL('image/png').substring(21);", canvas_element
        )
        # decode
        canvas_png = base64.b64decode(canvas_base64)
        # save to a file
        with open(filename, 'wb') as wf:
            wf.write(canvas_png)

    def main(self) -> None:
        try:
            options = webdriver.ChromeOptions()
            options.add_experimental_option('excludeSwitches', ['enable-logging'])
            # options.add_argument('headless')
            options.add_argument('window-size=1100,1390')

            driver = webdriver.Chrome(
                executable_path=self.chromedriver_path, options=options
            )

            driver.get(URL)

            if not os.path.exists(COOKIE_PATH):
                # no cookies are found yet
                _ = input()
                save_cookie(driver, COOKIE_PATH)

            load_cookie(driver, COOKIE_PATH)

            driver.get(URL)

            # for i in range(3):
            #     time.sleep(1)
            #     print(i)

            # hover over the FDC_NQ area in order to show the gearwheel
            fdc_nq_xpath = '/html/body/div[2]/div[1]/div[2]/div[1]/div/table/tr[1]/td[2]/div/div[1]/div[2]/div[2]/div[3]/div[1]'
            self._check_if_visible(driver, fdc_nq_xpath)
            fdc_nq_element = driver.find_element_by_xpath(fdc_nq_xpath)
            # print(type(fdc_nq_element))
            ActionChains(driver).move_to_element(fdc_nq_element).perform()
            time.sleep(1)
            print('done hover')

            # click the gearwheel to enter params adjustment
            self._wait_and_click(
                driver,
                '/html/body/div[2]/div[1]/div[2]/div[1]/div/table/tr[1]/td[2]/div/div[1]/div[2]/div[2]/div[3]/div[1]/div[2]/div/div[2]',
            )
            time.sleep(1)
            print('done clicking')

            # hover over the params' span to show the add button
            period_adjustment_element = driver.find_element_by_xpath(
                '//*[@id="overlap-manager-root"]/div/div/div[1]/div/div[3]/div/div[2]/div/span'
            )
            ActionChains(driver).move_to_element(period_adjustment_element).perform()
            time.sleep(1)

            # click the add button
            self._wait_and_click(
                driver,
                '//*[@id="overlap-manager-root"]/div/div/div[1]/div/div[3]/div/div[2]/div/span/span[2]/div/button[1]',
            )
            time.sleep(1)

            # track the current params
            params: Dict[str, str] = {}
            for index in ['2', '4', '6', '8']:
                params[PARAMS_INDEX_MAPPING[index]] = driver.find_element_by_xpath(
                    '//*[@id="overlap-manager-root"]/div/div/div[1]/div/div[3]/div/div[{}]/div/span/span[1]/input'.format(
                        index
                    )
                ).get_attribute('value')

            # period = driver.find_element_by_xpath(
            #     '//*[@id="overlap-manager-root"]/div/div/div[1]/div/div[3]/div/div[2]/div/span/span[1]/input'
            # ).get_attribute('value')
            # period = driver.find_element_by_xpath(
            #     '//*[@id="overlap-manager-root"]/div/div/div[1]/div/div[3]/div/div[4]/div/span/span[1]/input'
            # ).get_attribute('value')
            # period = driver.find_element_by_xpath(
            #     '//*[@id="overlap-manager-root"]/div/div/div[1]/div/div[3]/div/div[6]/div/span/span[1]/input'
            # ).get_attribute('value')
            # period = driver.find_element_by_xpath(
            #     '//*[@id="overlap-manager-root"]/div/div/div[1]/div/div[3]/div/div[8]/div/span/span[1]/input'
            # ).get_attribute('value')

            # sys.exit()

            # click on `摘要`
            self._wait_and_click(
                driver, 'div.backtesting-select-wrapper > ul > :first-child', by='css'
            )

            # save the entire backtest results div as PNG screenshot
            backtest_results_element = driver.find_element_by_css_selector(
                '#bottom-area > div.bottom-widgetbar-content.backtesting > div.backtesting-content-wrapper'
            )
            save_screenshot_as_png(
                driver,
                backtest_results_element,
                '{}_{}_{}_{}.png'.format(
                    params['period'],
                    params['amplifier'],
                    params['long_take_profit'].replace('.', '-'),
                    params['short_take_profit'].replace('.', '-'),
                ),
            )
            print('done saving chart as PNG')

            _ = input('\nPress any key to exit 🎉')
            # sys.exit()

        except SystemExit:
            sys.exit()

        except Exception:
            logging.exception(traceback.format_exc())
            traceback.print_exc()
            sys.exit()


if __name__ == '__main__':
    crawler = Crawler()
    crawler.main()
