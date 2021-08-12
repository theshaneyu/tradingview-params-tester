import os
import sys
import traceback
from time import sleep

from typing import Literal

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.action_chains import ActionChains

from constants import (
    INCREASE_SIZE,
    INDEXES,
    PARAMS,
    PARAMS_UPPER_LIMITS,
    PARAMS_LOWER_LIMITS,
    PARAM_INDEX_MAPPER,
    INDEX_PARAM_MAPPER,
    SEC_TO_SLEEP_PER_ITERATION,
    LOG_PATH,
    __PROD__,
)
from utils import (
    fill_input,
    save_cookie,
    load_cookie,
    wait_and_click,
    check_if_visible,
    append_params_csv,
    get_params_filename,
    print_current_info,
    get_chromedriver_path,
    save_screenshot_as_png,
    create_files_and_folders,
    save_performance_brief_to_csv,
)
from shared_types import CurrentParams, Params
from calculate_iterations import get_estamated_interations_and_time


# types
Param = Literal['period', 'amplification', 'long_take_profit', 'short_take_profit']

# constants
URL = 'https://tw.tradingview.com/chart/Iyu69JVU/'

SAVE_EXTRA = False

COOKIE_PATH = os.path.join('.tmp', 'cookie')


class Crawler:
    def __init__(self) -> None:
        create_files_and_folders()
        self.chromedriver_path = get_chromedriver_path()
        self._set_driver()
        (
            self.estimated_total_iterations,
            self.estimated_time,
        ) = get_estamated_interations_and_time()
        self.current_iteration = 0

    def _set_driver(self) -> None:
        options = webdriver.ChromeOptions()
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        # options.add_argument('headless')
        options.add_argument('window-size=700,1390')

        self.driver = webdriver.Chrome(
            executable_path=self.chromedriver_path, options=options
        )

    def _hover_fdc_nq(self, sec_to_sleep: float = 0) -> None:
        fdc_nq_xpath = (
            '/html/body/div[2]/div[1]/div[2]/div[1]/div/'
            'table/tr[1]/td[2]/div/div[1]/div[2]/div[2]/div[2]/div[1]'
        )
        check_if_visible(self.driver, fdc_nq_xpath)
        fdc_nq_element = self.driver.find_element_by_xpath(fdc_nq_xpath)
        ActionChains(self.driver).move_to_element(fdc_nq_element).perform()
        if sec_to_sleep != 0:
            sleep(sec_to_sleep)
        logging.info('done hover')

    def _click_gearwheel(self, sec_to_sleep: float = 0) -> None:
        wait_and_click(
            self.driver,
            (
                '/html/body/div[2]/div[1]/div[2]/div[1]/div/table/tr[1]/'
                'td[2]/div/div[1]/div[2]/div[2]/div[2]/div[1]/div[2]/div/div[2]'
            ),
        )
        if sec_to_sleep != 0:
            sleep(sec_to_sleep)
        logging.info('done clicking')

    def _reset_params(
        self,
        params_to_reset: Params,
        sec_to_sleep: float = 0,
    ) -> None:
        for param in params_to_reset:
            input_element: WebElement = self.driver.find_element_by_xpath(
                (
                    '//*[@id="overlap-manager-root"]/div/div/div[1]'
                    '/div/div[3]/div/div[{}]/div/span/span[1]/input'.format(
                        PARAM_INDEX_MAPPER[param]
                    )
                )
            )
            input_element.send_keys(Keys.CONTROL + "a")
            input_element.send_keys(Keys.DELETE)

            # fill in the float is it's `amplification`, otherwise fill in the int
            to_fill = (
                PARAMS_LOWER_LIMITS[param]
                if param == 'amplification'
                else int(PARAMS_LOWER_LIMITS[param])
            )
            input_element.send_keys(str(to_fill))
            sleep(0.5)
        if sec_to_sleep != 0:
            sleep(sec_to_sleep)
        logging.info('Parameter reset {}'.format(params_to_reset))

    def _hover_params_input(self, sec_to_sleep: float = 0) -> None:
        period_adjustment_element = self.driver.find_element_by_xpath(
            (
                '//*[@id="overlap-manager-root"]/'
                'div/div/div[1]/div/div[3]/div/div[2]/div/span'
            )
        )
        ActionChains(self.driver).move_to_element(period_adjustment_element).perform()
        if sec_to_sleep != 0:
            sleep(sec_to_sleep)

    def _click_params_increase(self, sec_to_sleep: float = 0) -> None:
        wait_and_click(
            self.driver,
            (
                '//*[@id="overlap-manager-root"]/div/div/div[1]'
                '/div/div[3]/div/div[2]/div/span/span[2]/div/button[1]'
            ),
        )
        if sec_to_sleep != 0:
            sleep(sec_to_sleep)

    def _get_current_params_from_browser(self) -> CurrentParams:
        params: CurrentParams = {
            'period': '',
            'amplification': '',
            'long_take_profit': '',
            'short_take_profit': '',
        }

        for index in INDEXES:
            params[INDEX_PARAM_MAPPER[index]] = self.driver.find_element_by_xpath(
                (
                    '//*[@id="overlap-manager-root"]/div/div/div'
                    '[1]/div/div[3]/div/div[{}]/div/span/span[1]/input'.format(index)
                )
            ).get_attribute('value')

        return params

    def _click_summary(self, sec_to_sleep: float = 0) -> None:
        wait_and_click(
            self.driver, '//*[@id="bottom-area"]/div[4]/div[1]/div[6]/ul/li[1]'
        )
        if sec_to_sleep != 0:
            sleep(sec_to_sleep)

    def _save_profit_and_win_rate_to_csv(self, current_params: CurrentParams) -> str:
        profit: str = self.driver.find_element_by_xpath(
            '//*[@id="bottom-area"]/div[4]/div[3]/div/div/div[1]/div[1]/strong'
        ).text
        profit = profit.replace('$ ', '')
        win_rate: str = self.driver.find_element_by_xpath(
            '//*[@id="bottom-area"]/div[4]/div[3]/div/div/div[1]/div[3]/strong'
        ).text
        win_rate = '{:.4f}'.format(float(win_rate.replace(' %', '')) / 100.0)

        return append_params_csv(current_params, profit, win_rate)

    def _screenshot_backtest_result(self, params_filename: str) -> None:
        backtest_results_element = self.driver.find_element_by_css_selector(
            (
                '#bottom-area > div.bottom-widgetbar-content.backtesting '
                '> div.backtesting-content-wrapper'
            )
        )
        save_screenshot_as_png(self.driver, backtest_results_element, params_filename)
        logging.info('done saving chart screenshot as PNG')

    def _click_performance_brief(self, sec_to_sleep: float = 0) -> None:
        wait_and_click(
            self.driver, '//*[@id="bottom-area"]/div[4]/div[1]/div[6]/ul/li[2]'
        )
        if sec_to_sleep != 0:
            sleep(sec_to_sleep)

    def _save_performance_brief(self, current_params_filename: str) -> None:
        performance_summary_element = self.driver.find_element_by_xpath(
            '//*[@id="bottom-area"]/div[4]/div[3]/div/div/div/table'
        )
        save_performance_brief_to_csv(
            performance_summary_element, current_params_filename
        )

    def _increase_param(
        self,
        param_to_increase: Param,
        current_params: CurrentParams,
        press_enter: bool = True,
    ) -> None:
        """use browser to increase the specific param on the params adjustment panel
           and return the increased param in float

        Args:
            param_to_increase (Param): the specific param to increase
            current_params (CurrentParams): the params dict before increasement

        Returns:
            float: the increased specidifc param
        """
        element_to_fill: WebElement = self.driver.find_element_by_xpath(
            (
                '//*[@id="overlap-manager-root"]/div/div/div[1]'
                '/div/div[3]/div/div[{}]/div/span/span[1]/input'.format(
                    PARAM_INDEX_MAPPER[param_to_increase]
                )
            )
        )

        increased_float = (
            float(current_params[param_to_increase]) + INCREASE_SIZE[param_to_increase]
        )

        fill_input(
            element_to_fill,
            str(increased_float)
            # only `amplification` needs to fill in `float`, otherwise `int`
            if param_to_increase == 'amplification' else str(int(increased_float)),
        )

        # press ENTER after filling in the increased param
        if press_enter:
            element_to_fill.send_keys(Keys.RETURN)

    def main(self) -> None:
        try:
            self.driver.get(URL)

            # load/save cookies
            if not os.path.exists(COOKIE_PATH):
                # no cookies are found yet
                logging.info(
                    'use the browser to log in, then exit and rerun the program'
                )
                _ = input('press any key to exit')
                save_cookie(self.driver, COOKIE_PATH)
                self.driver.quit()
                sys.exit()
            else:
                load_cookie(self.driver, COOKIE_PATH)

            self.driver.get(URL)

            # hover over the FDC_NQ area in order to show the gearwheel
            self._hover_fdc_nq(sec_to_sleep=1)

            # click the gearwheel to enter params adjustment
            self._click_gearwheel(sec_to_sleep=1)

            # reset all params
            self._reset_params(params_to_reset=PARAMS, sec_to_sleep=1)

            # track the current params
            # period, amplification, long_take_profit, short_take_profit
            current_params = self._get_current_params_from_browser()

            while float(current_params['period']) < PARAMS_UPPER_LIMITS['period']:
                # # the loop of period
                # increased_period = self._increase_param('period', current_params)
                # current_params['period'] = str(increased_period)
                # sleep(SEC_TO_SLEEP_PER_ITERATION)

                while (
                    float(current_params['amplification'])
                    < PARAMS_UPPER_LIMITS['amplification']
                ):
                    while (
                        float(current_params['long_take_profit'])
                        < PARAMS_UPPER_LIMITS['long_take_profit']
                    ):
                        # the loop of long/short take profit
                        # increase the `long_take_profit` but NOT to hit ENTER
                        self._increase_param(
                            'long_take_profit', current_params, press_enter=False
                        )
                        # increase the `short_take_profit` and hit ENTER
                        self._increase_param('short_take_profit', current_params)
                        # set the current params from the browser
                        current_params = self._get_current_params_from_browser()
                        # save profit and win rate data from the browser
                        csv_line = self._save_profit_and_win_rate_to_csv(current_params)
                        self.current_iteration += 1
                        print_current_info(
                            csv_line,
                            self.current_iteration,
                            self.estimated_total_iterations,
                            self.estimated_time,
                        )
                        sleep(SEC_TO_SLEEP_PER_ITERATION)

                    # after finishing the loop of long/short take profit
                    # 1. first reset the long/short take profit
                    self._reset_params(['long_take_profit', 'short_take_profit'], 1)
                    # 2. increase the `amplification` and press ENTER
                    self._increase_param('amplification', current_params)
                    # 3. set the current params from the browser
                    current_params = self._get_current_params_from_browser()
                    # 4. save profit and win_rate from the browser
                    csv_line = self._save_profit_and_win_rate_to_csv(current_params)
                    self.current_iteration += 1
                    print_current_info(
                        csv_line,
                        self.current_iteration,
                        self.estimated_total_iterations,
                        self.estimated_time,
                    )
                    sleep(SEC_TO_SLEEP_PER_ITERATION)

                # after finishing the loop of amplification
                # 1. first reset the amplification and long/short take profit
                self._reset_params(['long_take_profit', 'short_take_profit'], 1)
                self._reset_params(['amplification'], 1)
                # 2. increase the `period` and press ENTER
                self._increase_param('period', current_params)
                # 3. set the current params from the browser
                current_params = self._get_current_params_from_browser()
                # 4. save profit and win_rate from the browser
                csv_line = self._save_profit_and_win_rate_to_csv(current_params)
                self.current_iteration += 1
                print_current_info(
                    csv_line,
                    self.current_iteration,
                    self.estimated_total_iterations,
                    self.estimated_time,
                )
                sleep(SEC_TO_SLEEP_PER_ITERATION)

            # # track the current params
            # current_params = self._get_current_params()

            # # hover over the params' span to show the increase button
            # self._hover_params_input(sec_to_sleep=0.5)

            # # click the increase button
            # self._click_params_increase(sec_to_sleep=1.5)

            # # click on `概要` bullton
            # self._click_summary(sec_to_sleep=0.5)

            if SAVE_EXTRA:
                # format a params filename string
                current_params_filename = get_params_filename(current_params)

                # screenshot the backtest result chart and data and save as PNG
                self._screenshot_backtest_result(current_params_filename)

                # click on `績效摘要` button
                self._click_performance_brief(sec_to_sleep=0.5)

                # save `績效摘要` table as csv
                self._save_performance_brief(current_params_filename)

            _ = input('\nPress any key to exit 🎉')
            self.driver.quit()

        except SystemExit:
            self.driver.quit()

        except KeyboardInterrupt:
            self.driver.quit()

        except Exception:
            logging.exception(traceback.format_exc())
            self.driver.quit()


if __name__ == '__main__':
    import logging

    # initailize logger
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[
            logging.FileHandler(LOG_PATH, 'a', 'utf-8'),
            logging.StreamHandler(),
        ]
        if __PROD__
        else [
            logging.StreamHandler(),
        ],
    )

    crawler = Crawler()
    crawler.main()
