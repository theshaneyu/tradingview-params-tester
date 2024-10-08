import os
import sys
import traceback
from time import sleep
from typing import Literal, Tuple, Set

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import (
    ElementNotInteractableException,
    StaleElementReferenceException,
    NoSuchElementException,
)

from constants import (
    PARAMS,
    ACCOUNT,
    INDEXES,
    CONTRACT,
    __PROD__,
    INCREASE_SIZE,
    EXECUTION_TIME,
    PARAM_INDEX_MAPPER,
    INDEX_PARAM_MAPPER,
    PARAMS_UPPER_LIMITS,
    PARAMS_LOWER_LIMITS,
    SEC_TO_SLEEP_FOR_IDENTICAL_REPORT,
    MAX_WAITING_SEC_FOR_IDENTICAL_REPORT,
    SEC_TO_SLEEP_WHEN_STALE_ELEMENT_OCCUR,
)
from utils import (
    limit_checker,
    fill_input,
    send_email,
    save_cookie,
    load_cookie,
    wait_and_click,
    get_driver_path,
    check_if_visible,
    append_params_csv,
    print_current_info,
    get_params_filename,
    save_screenshot_as_png,
    get_element_until_present,
    save_performance_brief_to_csv,
)
from logger import logger, logger_only_stdout
from shared_types import CurrentParams, Params
from calculate_iterations import get_estamated_interations_and_time


# types
Param = Literal['period', 'amplification', 'long_take_profit', 'short_take_profit']

# constants
URL = (
    'https://tw.tradingview.com/chart/Iyu69JVU/'
    if ACCOUNT == 'shane'
    else 'https://tw.tradingview.com/chart/6DUbI1y5/'
)

SAVE_EXTRA = False

COOKIE_PATH = os.path.join(
    'cookies', ACCOUNT if ACCOUNT is not None else 'shane', 'cookie'
)


class Crawler:
    def __init__(self) -> None:
        logger.info('ACCOUNT: {} | CONTRACT: {}'.format(ACCOUNT, CONTRACT))
        self.driver_path = get_driver_path()
        self._set_driver()
        self.estimated_total_iterations = get_estamated_interations_and_time(
            log_info=True
        )
        self.current_iteration = 1
        self.last_profit = ''
        self.last_win_rate = ''
        self.total_sec_been_waiting_for_report = 0.0
        self.profits_caught_after_reset: Set[str] = set()

    def _set_driver(self) -> None:
        options = webdriver.ChromeOptions()
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        # options.add_argument('headless')
        options.add_argument('window-size=700,1390')

        self.driver = webdriver.Chrome(
            executable_path=self.driver_path, options=options
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
        logger.info('done hover')

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
        logger.info('done clicking')

    def _reset_params(
        self,
        params_to_reset: Params,
        sec_to_sleep: float = 0,
        collect_garbage_profit: bool = False,
    ) -> CurrentParams:
        for param in params_to_reset:
            input_element: WebElement = self.driver.find_element_by_xpath(
                (
                    '//*[@id="overlap-manager-root"]/div/div/div[1]'
                    '/div/div[3]/div/div[{}]/div/span/span[1]/input'.format(
                        PARAM_INDEX_MAPPER[param]
                    )
                )
            )
            # fill in the float if it's `amplification`, otherwise fill in the int
            to_fill = str(
                (
                    PARAMS_LOWER_LIMITS[param]
                    if param == 'amplification'
                    else int(PARAMS_LOWER_LIMITS[param])
                )
            )
            fill_input(input_element, to_fill)
            sleep(0.5)
        if sec_to_sleep != 0:
            sleep(sec_to_sleep)
        logger.info('Parameter reset {}'.format(params_to_reset))

        if collect_garbage_profit:
            profit, _ = self._get_profit_and_win_rate()
            self.profits_caught_after_reset.add(profit)

        # get the current params from the browser
        current_params = self._get_current_params_from_browser()

        return current_params

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

    def _get_profit_and_win_rate(self) -> Tuple[str, str]:
        while True:
            try:
                profit: str = self.driver.find_element_by_css_selector(
                    (
                        'div.backtesting-content-wrapper > div > '
                        'div > div.report-data > div:nth-child(1) > strong'
                    )
                ).text
                profit = profit.replace('$ ', '')

                if profit in self.profits_caught_after_reset:
                    logger.info(
                        'skipping mis-captured profit from params reset: {}'.format(
                            profit
                        )
                    )
                    sleep(0.5)
                    continue

                self.profits_caught_after_reset.clear()

                win_rate: str = self.driver.find_element_by_css_selector(
                    (
                        'div.backtesting-content-wrapper > div > '
                        'div > div.report-data > div:nth-child(3) > strong'
                    )
                ).text
                win_rate = '{:.4f}'.format(float(win_rate.replace(' %', '')) / 100.0)

                # check if the report has been updated
                if profit == self.last_profit and win_rate == self.last_win_rate:
                    if (
                        'opacity-transition fade'
                    ) in self.driver.find_element_by_css_selector(
                        (
                            '#bottom-area > div.bottom-widgetbar-content.backtesting >'
                            ' div.backtesting-content-wrapper > div'
                        )
                    ).get_attribute(
                        'class'
                    ):
                        # the report area fades
                        logger.debug('identical report and faded report UI')
                        sleep(SEC_TO_SLEEP_FOR_IDENTICAL_REPORT)
                        continue

                    # found same report, but the report area doesn't fade
                    # wait for up to 5 seconds (this should rarely happen)
                    logger.debug('identical report but NOT faded')
                    sleep(SEC_TO_SLEEP_FOR_IDENTICAL_REPORT)
                    self.total_sec_been_waiting_for_report += (
                        SEC_TO_SLEEP_FOR_IDENTICAL_REPORT
                    )

                    if (
                        self.total_sec_been_waiting_for_report
                        <= MAX_WAITING_SEC_FOR_IDENTICAL_REPORT
                    ):
                        continue

                    self.total_sec_been_waiting_for_report = 0.0

                self.last_profit = profit
                self.last_win_rate = win_rate

                # check if `超過裝置上限` happened
                limit_checker.check('{},{}'.format(profit, win_rate))

                # print('{} -> {} | {}'.format(str(current_params), profit, win_rate))

                return profit, win_rate

            except StaleElementReferenceException:
                sleep(SEC_TO_SLEEP_WHEN_STALE_ELEMENT_OCCUR)
                logger_only_stdout.warning(
                    'stale element, element is not attached to the page document'
                )
                continue

            except NoSuchElementException:
                _ = input('please fix the UI and press any key to continue')

    def _save_profit_and_win_rate_to_csv(self, current_params: CurrentParams) -> str:
        profit, win_rate = self._get_profit_and_win_rate()
        return append_params_csv(current_params, profit, win_rate)

    def _screenshot_backtest_result(self, params_filename: str) -> None:
        backtest_results_element = self.driver.find_element_by_css_selector(
            (
                '#bottom-area > div.bottom-widgetbar-content.backtesting '
                '> div.backtesting-content-wrapper'
            )
        )
        save_screenshot_as_png(self.driver, backtest_results_element, params_filename)
        logger.info('done saving chart screenshot as PNG')

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

        try:
            fill_input(
                element_to_fill,
                str(increased_float)
                # only `amplification` needs to fill in `float`, otherwise `int`
                if param_to_increase == 'amplification' else str(int(increased_float)),
            )
        except ElementNotInteractableException:
            send_email(
                'error occur: "ElementNotInteractableException"', traceback.format_exc()
            )
            _ = input('please fix the error and press any key to continue 👀')

        # press ENTER after filling in the increased param
        if press_enter:
            element_to_fill.send_keys(Keys.RETURN)

    def _select_correct_contract(self) -> None:
        toolbar_watchlist_icon_xpath = (
            '/html/body/div[2]/div[5]/div/div[2]/div/div/div/div/div[1]/span'
        )
        # right-hand toolbar
        if 'isGrayed' not in get_element_until_present(
            self.driver, '/html/body/div[2]/div[5]/div/div[2]/div/div/div/div'
        ).get_attribute("class"):
            # right sidebar is close, then click the icon and open it
            self.driver.find_element_by_xpath(toolbar_watchlist_icon_xpath).click()
            sleep(0.5)

        # find the correct contract
        index = 2
        found = False
        while True:
            try:
                contract_element: WebElement = self.driver.find_element_by_xpath(
                    '/html/body/div[2]/div[5]/div/div[1]/div[1]/div[1]/div[1]/div[2]/div/div[2]/div/div[2]/div/div[{}]/div/div/div[2]/span/span[1]'.format(
                        index
                    )
                )
                if '{}1!'.format(CONTRACT.upper()) in contract_element.text:
                    # found the correct contract
                    found = True
                    break

                index += 1

            except NoSuchElementException:
                # reached the end of the contract list
                break

        if not found:
            self.driver.quit()
            raise Exception(
                'contract "{}1!" was not found in the right toolbar'.format(
                    CONTRACT.upper()
                )
            )

        contract_element.click()
        sleep(0.5)

        # click the toolbar watchlist icon again to close the toolbar
        self.driver.find_element_by_xpath(toolbar_watchlist_icon_xpath).click()
        sleep(0.2)

    def _check_contract(self) -> None:
        contract_text = 'E-迷你納斯達克' if CONTRACT == 'nq' else 'E-迷你道瓊'
        tried = False

        while True:
            title_text = get_element_until_present(
                self.driver,
                (
                    '/html/body/div[2]/div[1]/div[2]/div[1]/div/table/'
                    'tr[1]/td[2]/div/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]'
                ),
            ).text

            # logger.debug('title_element: ', title_text)
            if contract_text not in title_text:
                # input contract and page contract mismatch
                if tried:
                    logger.error(
                        'fail to select the correct contract in the right toolbar ⚠️'
                    )
                    input('please fix the UI and press any key to continue')

                logger.info('input contract and UI contract mismatch')
                logger.info('input: {}, but found: {}'.format(CONTRACT, title_text))
                logger.info('start trying to change contract in right-hand toolbar')
                self._select_correct_contract()
                tried = True
                continue

            logger.info('change contract to "{}" successfully'.format(title_text))
            break

        # make sure the right toolbar is closed
        if 'isGrayed' in get_element_until_present(
            self.driver, '/html/body/div[2]/div[5]/div/div[2]/div/div/div/div'
        ).get_attribute("class"):
            # right sidebar is not close, then click the icon to close it
            self.driver.find_element_by_xpath(
                ('/html/body/div[2]/div[5]/div/div[2]/div/div/div/div/div[1]/span')
            ).click()
            sleep(0.5)

    def handle_cookies(self) -> None:
        # load/save cookies
        if not os.path.exists(COOKIE_PATH):
            # no cookies are found yet
            logger.info('use the browser to log in, then exit and rerun the program')
            _ = input('press any key to exit')
            save_cookie(self.driver, COOKIE_PATH)
            self.driver.quit()
            sys.exit()
        else:
            load_cookie(self.driver, COOKIE_PATH)

    def _check_summary(self) -> None:
        tried = False
        # check if the report area is visible on the UI
        while True:
            if 'active' not in self.driver.find_element_by_xpath(
                '//*[@id="footer-chart-panel"]/div[1]/div[1]/div[4]'
            ).get_attribute('class'):
                # `策略測試器` button is not active
                if tried:
                    # had tried, but fail again
                    send_email('fail to toggle "策略測試器" 💔', traceback.format_exc())
                    input('fail to toggle "策略測試器" 💔')

                # `策略測試器` is not shown, then click the span to toggle it
                logger.info(
                    'report area is not shown on the UI, try to click the span to toggle it'
                )
                self.driver.find_element_by_xpath(
                    '//*[@id="footer-chart-panel"]/div[1]/div[1]/div[4]/div/span'
                ).click()
                tried = True
                sleep(0.5)

            break

        logger.info('report area is shown on the UI')

    def launch_browser_and_visit_url(self) -> None:
        self.driver.get(URL)
        self.handle_cookies()
        self.driver.get(URL)
        self._check_contract()
        self._check_summary()

    def _iteration_process(
        self,
        iteration_type: Literal['TAKE_PROFIT', 'AMPLIFICATION', 'PERIOD'],
        current_params: CurrentParams,
    ) -> CurrentParams:
        if iteration_type == 'TAKE_PROFIT':
            # increase the `long_take_profit` but NOT to hit ENTER
            self._increase_param('long_take_profit', current_params, press_enter=False)
            # increase the `short_take_profit` and hit ENTER
            self._increase_param('short_take_profit', current_params)

        elif iteration_type == 'AMPLIFICATION':
            # increase the `amplification` and press ENTER
            self._increase_param('amplification', current_params)

        elif iteration_type == 'PERIOD':
            # increase the `period` and press ENTER
            self._increase_param('period', current_params)

        # get the current params from the browser
        current_params = self._get_current_params_from_browser()

        # save profit and win rate data from the browser
        csv_line = self._save_profit_and_win_rate_to_csv(current_params)

        self.current_iteration += 1

        print_current_info(
            csv_line,
            self.current_iteration,
            self.estimated_total_iterations,
        )

        return current_params

    def main(self) -> None:
        try:
            self.launch_browser_and_visit_url()
            # _ = input('check the TradingView web UI, then press any key to start 🚀')

            # hover over the FDC_NQ area in order to show the gearwheel
            self._hover_fdc_nq(sec_to_sleep=1)

            # click the gearwheel to enter params adjustment
            self._click_gearwheel(sec_to_sleep=1)

            # reset all params
            current_params = self._reset_params(params_to_reset=PARAMS, sec_to_sleep=1)

            # save profit and win rate data from the browser
            csv_line = self._save_profit_and_win_rate_to_csv(current_params)

            print_current_info(
                csv_line,
                self.current_iteration,
                self.estimated_total_iterations,
            )

            while True:
                while True:
                    while True:
                        # beginning of long/short take profit's loop
                        current_params = self._iteration_process(
                            'TAKE_PROFIT', current_params
                        )

                        if (
                            float(current_params['long_take_profit'])
                            >= PARAMS_UPPER_LIMITS['long_take_profit']
                        ):
                            break

                    if (
                        float(current_params['amplification'])
                        >= PARAMS_UPPER_LIMITS['amplification']
                    ):
                        break
                    # after finishing the loop of long/short take profit
                    # 1. first reset the long/short take profit
                    current_params = self._reset_params(
                        ['long_take_profit', 'short_take_profit'],
                        0.5,
                        collect_garbage_profit=True,
                    )
                    # 2. increase the `amplification` and hit ENTER
                    # 3. get the current params from the browser
                    # 4. save profit and win_rate from the browser
                    current_params = self._iteration_process(
                        'AMPLIFICATION', current_params
                    )

                if float(current_params['period']) >= PARAMS_UPPER_LIMITS['period']:
                    break
                # after finishing the loop of amplification
                # 1. first reset the amplification and long/short take profit
                current_params = self._reset_params(
                    ['long_take_profit', 'short_take_profit', 'amplification'],
                    0.5,
                    collect_garbage_profit=True,
                )
                # 2. increase the `period` and press ENTER
                # 3. set the current params from the browser
                # 4. save profit and win_rate from the browser
                current_params = self._iteration_process('PERIOD', current_params)

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

            send_email(
                '爬蟲執行完畢',
                'finished period {} -> {}'.format(
                    PARAMS_LOWER_LIMITS['period'], PARAMS_UPPER_LIMITS['period']
                ),
            )
            # _ = input('\nPress any key to exit 🎉')
            self.driver.quit()

        except SystemExit:
            self.driver.quit()

        except KeyboardInterrupt:
            self.driver.quit()

        except Exception:
            if __PROD__:
                self.driver.save_screenshot(
                    filename=os.path.join('logs', '{}.png'.format(EXECUTION_TIME))
                )
            logger.exception(traceback.format_exc())
            # _ = input('error occur 💔')
            send_email('error occur 💔', traceback.format_exc())
            self.driver.quit()


if __name__ == '__main__':

    crawler = Crawler()
    crawler.main()
