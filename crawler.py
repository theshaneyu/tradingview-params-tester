import os
import logging
import traceback
from time import sleep

from typing import Dict

from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains

from utils import (
    save_cookie,
    load_cookie,
    wait_and_click,
    check_if_visible,
    append_params_csv,
    get_params_filename,
    get_chromedriver_path,
    save_screenshot_as_png,
    create_files_and_folders,
    save_performance_brief_to_csv,
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
        create_files_and_folders()
        self.chromedriver_path = get_chromedriver_path()
        self._set_driver()

    def _set_driver(self) -> None:
        options = webdriver.ChromeOptions()
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        # options.add_argument('headless')
        options.add_argument('window-size=1010,1390')

        self.driver = webdriver.Chrome(
            executable_path=self.chromedriver_path, options=options
        )

    def _hover_fdc_nq(self) -> None:
        fdc_nq_xpath = (
            '/html/body/div[2]/div[1]/div[2]/div[1]/div/table'
            '/tr[1]/td[2]/div/div[1]/div[2]/div[2]/div[3]/div[1]'
        )
        check_if_visible(self.driver, fdc_nq_xpath)
        fdc_nq_element = self.driver.find_element_by_xpath(fdc_nq_xpath)
        ActionChains(self.driver).move_to_element(fdc_nq_element).perform()
        sleep(1)
        print('done hover')

    def _click_gearwheel(self) -> None:
        wait_and_click(
            self.driver,
            (
                '/html/body/div[2]/div[1]/div[2]/div[1]/div/table/tr[1]/td[2]'
                '/div/div[1]/div[2]/div[2]/div[3]/div[1]/div[2]/div/div[2]'
            ),
        )
        sleep(1)
        print('done clicking')

    def _hover_params_input(self) -> None:
        period_adjustment_element = self.driver.find_element_by_xpath(
            (
                '//*[@id="overlap-manager-root"]/'
                'div/div/div[1]/div/div[3]/div/div[2]/div/span'
            )
        )
        ActionChains(self.driver).move_to_element(period_adjustment_element).perform()
        sleep(0.5)

    def _click_params_increase(self) -> None:
        wait_and_click(
            self.driver,
            (
                '//*[@id="overlap-manager-root"]/div/div/div[1]'
                '/div/div[3]/div/div[2]/div/span/span[2]/div/button[1]'
            ),
        )
        sleep(1.5)

    def _get_current_params(self) -> Dict[str, str]:
        params: Dict[str, str] = {}

        for index in ['2', '4', '6', '8']:
            params[PARAMS_INDEX_MAPPING[index]] = self.driver.find_element_by_xpath(
                (
                    '//*[@id="overlap-manager-root"]/div/div/div'
                    '[1]/div/div[3]/div/div[{}]/div/span/span[1]/input'.format(index)
                )
            ).get_attribute('value')

        return params

    def _click_summary(self) -> None:
        wait_and_click(
            self.driver, '//*[@id="bottom-area"]/div[4]/div[1]/div[6]/ul/li[1]'
        )
        sleep(0.5)

    def _save_profit_and_win_rate_to_csv(self, current_params: Dict[str, str]) -> None:
        profit = self.driver.find_element_by_xpath(
            '//*[@id="bottom-area"]/div[4]/div[3]/div/div/div[1]/div[1]/strong'
        ).text
        profit = profit.replace('$ ', '')
        win_rate = self.driver.find_element_by_xpath(
            '//*[@id="bottom-area"]/div[4]/div[3]/div/div/div[1]/div[3]/strong'
        ).text
        win_rate = str(float(win_rate.replace(' %', '')) / 100.0)
        append_params_csv(current_params, profit, win_rate)

    def _screenshot_backtest_result(self, params_filename: str) -> None:
        backtest_results_element = self.driver.find_element_by_css_selector(
            (
                '#bottom-area > div.bottom-widgetbar-content.backtesting '
                '> div.backtesting-content-wrapper'
            )
        )
        save_screenshot_as_png(self.driver, backtest_results_element, params_filename)
        print('done saving chart screenshot as PNG')

    def _click_performance_brief(self) -> None:
        wait_and_click(
            self.driver, '//*[@id="bottom-area"]/div[4]/div[1]/div[6]/ul/li[2]'
        )
        sleep(0.5)

    def _save_performance_brief(self, current_params_filename: str) -> None:
        performance_summary_element = self.driver.find_element_by_xpath(
            '//*[@id="bottom-area"]/div[4]/div[3]/div/div/div/table'
        )
        save_performance_brief_to_csv(
            performance_summary_element, current_params_filename
        )

    def main(self) -> None:
        try:
            self.driver.get(URL)

            # load/save cookies
            if not os.path.exists(COOKIE_PATH):
                # no cookies are found yet
                _ = input()
                save_cookie(self.driver, COOKIE_PATH)
            else:
                load_cookie(self.driver, COOKIE_PATH)

            self.driver.get(URL)

            # hover over the FDC_NQ area in order to show the gearwheel
            self._hover_fdc_nq()

            # click the gearwheel to enter params adjustment
            self._click_gearwheel()

            # hover over the params' span to show the increase button
            self._hover_params_input()

            # click the increase button
            self._click_params_increase()

            # track the current params
            current_params = self._get_current_params()

            # click on `概要` bullton
            self._click_summary()

            # save profit and win rate data
            self._save_profit_and_win_rate_to_csv(current_params)

            # format a params filename string
            current_params_filename = get_params_filename(current_params)

            # screenshot the backtest result chart and data and save as PNG
            self._screenshot_backtest_result(current_params_filename)

            # click on `績效摘要` button
            self._click_performance_brief()

            # save `績效摘要` table as csv
            self._save_performance_brief(current_params_filename)

            _ = input('\nPress any key to exit 🎉')
            self.driver.quit()

        except SystemExit:
            self.driver.quit()

        except Exception:
            logging.exception(traceback.format_exc())
            self.driver.quit()


if __name__ == '__main__':
    crawler = Crawler()
    crawler.main()
