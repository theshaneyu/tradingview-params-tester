import os
import sys
import base64
import logging
import traceback
from time import sleep

from typing import Dict, Literal

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC

from constants import EXECUTION_TIME
from utils import (
    append_params_csv,
    load_cookie,
    save_cookie,
    save_performance_summary_to_csv,
    save_screenshot_as_png,
)


URL = 'https://tw.tradingview.com/chart/Iyu69JVU/'
# URL = 'https://www.tradingview.com/cryptocurrency-signals/'

# COOKIE_PATH = '/tmp/cookie'
COOKIE_PATH = os.path.join('.tmp', 'cookie')

PARAMS_INDEX_MAPPING = {
    '2': 'period',
    '4': 'amplifier',
    '6': 'long_take_profit',
    '8': 'short_take_profit',
}


class Crawler:
    def __init__(self) -> None:
        self._create_files_and_folders()

    def _create_files_and_folders(self) -> None:
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
        if not os.path.exists(os.path.join('results', EXECUTION_TIME)):
            os.makedirs(os.path.join('results', EXECUTION_TIME))
            os.makedirs(os.path.join('results', EXECUTION_TIME, 'params'))
            os.makedirs(os.path.join('results', EXECUTION_TIME, 'charts'))
            os.makedirs(os.path.join('results', EXECUTION_TIME, 'performance'))
            os.makedirs(os.path.join('results', EXECUTION_TIME, 'transactions'))

        # add header to params csv
        with open(
            os.path.join(
                'results',
                EXECUTION_TIME,
                'params',
                '{}.csv'.format(EXECUTION_TIME),
            ),
            'w',
            encoding='utf8',
        ) as wf:
            wf.write(
                'Period,Amplification,LongTakeProfit,ShortTakeProfit,Profit,WinRate\n'
            )

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
            options.add_argument('window-size=1010,1390')

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
            #     sleep(1)
            #     print(i)

            # hover over the FDC_NQ area in order to show the gearwheel
            fdc_nq_xpath = (
                '/html/body/div[2]/div[1]/div[2]/div[1]/div/table'
                '/tr[1]/td[2]/div/div[1]/div[2]/div[2]/div[3]/div[1]'
            )
            self._check_if_visible(driver, fdc_nq_xpath)
            fdc_nq_element = driver.find_element_by_xpath(fdc_nq_xpath)
            # print(type(fdc_nq_element))
            ActionChains(driver).move_to_element(fdc_nq_element).perform()
            sleep(1)
            print('done hover')

            # click the gearwheel to enter params adjustment
            self._wait_and_click(
                driver,
                (
                    '/html/body/div[2]/div[1]/div[2]/div[1]/div/table/tr[1]/td[2]'
                    '/div/div[1]/div[2]/div[2]/div[3]/div[1]/div[2]/div/div[2]'
                ),
            )
            sleep(1)
            print('done clicking')

            # hover over the params' span to show the add button
            period_adjustment_element = driver.find_element_by_xpath(
                (
                    '//*[@id="overlap-manager-root"]/'
                    'div/div/div[1]/div/div[3]/div/div[2]/div/span'
                )
            )
            ActionChains(driver).move_to_element(period_adjustment_element).perform()
            sleep(0.5)

            # click the add button
            self._wait_and_click(
                driver,
                (
                    '//*[@id="overlap-manager-root"]/div/div/div[1]'
                    '/div/div[3]/div/div[2]/div/span/span[2]/div/button[1]'
                ),
            )
            sleep(1.5)

            # track the current params
            params: Dict[str, str] = {}

            for index in ['2', '4', '6', '8']:
                params[PARAMS_INDEX_MAPPING[index]] = driver.find_element_by_xpath(
                    (
                        '//*[@id="overlap-manager-root"]/div/div/div'
                        '[1]/div/div[3]/div/div[{}]/div/span/span[1]/input'.format(
                            index
                        )
                    )
                ).get_attribute('value')

            # click on `概要`
            self._wait_and_click(
                driver, '//*[@id="bottom-area"]/div[4]/div[1]/div[6]/ul/li[1]'
            )
            sleep(0.5)

            # save profit and win rate data
            profit = driver.find_element_by_xpath(
                '//*[@id="bottom-area"]/div[4]/div[3]/div/div/div[1]/div[1]/strong'
            ).text
            profit = profit.replace('$ ', '')
            win_rate = driver.find_element_by_xpath(
                '//*[@id="bottom-area"]/div[4]/div[3]/div/div/div[1]/div[3]/strong'
            ).text
            win_rate = str(float(win_rate.replace(' %', '')) / 100.0)
            append_params_csv(params, profit, win_rate)

            # format a params filename string
            params_filename = '{}_{}_{}_{}'.format(
                params['period'],
                params['amplifier'],
                str(params['long_take_profit']).replace('.', '-'),
                str(params['short_take_profit']).replace('.', '-'),
            )

            # save the entire backtest results div as PNG screenshot
            backtest_results_element = driver.find_element_by_css_selector(
                (
                    '#bottom-area > div.bottom-widgetbar-content.backtesting '
                    '> div.backtesting-content-wrapper'
                )
            )
            save_screenshot_as_png(driver, backtest_results_element, params_filename)
            print('done saving chart as PNG')

            # click on `績效摘要`
            self._wait_and_click(
                driver, '//*[@id="bottom-area"]/div[4]/div[1]/div[6]/ul/li[2]'
            )
            sleep(0.5)

            # save `績效摘要`
            performance_summary_element = driver.find_element_by_xpath(
                '//*[@id="bottom-area"]/div[4]/div[3]/div/div/div/table'
            )
            save_performance_summary_to_csv(
                performance_summary_element, params_filename
            )

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
