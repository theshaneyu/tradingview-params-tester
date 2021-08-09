import os
import sys
import logging
import traceback
from time import sleep

from typing import Dict

from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains

from utils import (
    append_params_csv,
    get_chromedriver_path,
    load_cookie,
    save_cookie,
    save_performance_summary_to_csv,
    save_screenshot_as_png,
    wait_and_click,
    check_if_visible,
    create_files_and_folders,
)


URL = 'https://tw.tradingview.com/chart/Iyu69JVU/'

COOKIE_PATH = os.path.join('.tmp', 'cookie')

PARAMS_INDEX_MAPPING = {
    '2': 'period',
    '4': 'amplifier',
    '6': 'long_take_profit',
    '8': 'short_take_profit',
}


class Crawler:
    def __init__(self) -> None:
        self.chromedriver_path = get_chromedriver_path()
        create_files_and_folders()

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
            check_if_visible(driver, fdc_nq_xpath)
            fdc_nq_element = driver.find_element_by_xpath(fdc_nq_xpath)
            # print(type(fdc_nq_element))
            ActionChains(driver).move_to_element(fdc_nq_element).perform()
            sleep(1)
            print('done hover')

            # click the gearwheel to enter params adjustment
            wait_and_click(
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
            wait_and_click(
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
            wait_and_click(
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
            wait_and_click(
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
