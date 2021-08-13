import os
import pandas as pd
from PIL import Image
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement

from constants import EXECUTION_TIME
from shared_types import CurrentParams


def create_files_and_folders() -> None:
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

    # check logs folder
    if not os.path.exists('logs'):
        os.makedirs('logs')

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
        wf.write('Period,Amplification,LongTakeProfit,ShortTakeProfit,Profit,WinRate\n')


create_files_and_folders()


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


def append_params_csv(params: CurrentParams, profit: str, win_rate: str) -> str:
    csv_line = '{},{:.2f},{},{},{},{}'.format(
        int(params['period']),
        float(params['amplification']),
        int(params['long_take_profit']),
        int(params['short_take_profit']),
        profit,
        win_rate,
    )
    with open(
        os.path.join(
            'results', EXECUTION_TIME, 'params', '{}.csv'.format(EXECUTION_TIME)
        ),
        'a',
        encoding='utf8',
    ) as af:
        af.write(csv_line + '\n')

    return csv_line


def save_performance_brief_to_csv(
    table_element: WebElement, params_filename: str
) -> None:
    tbl = table_element.get_attribute('outerHTML')
    df = pd.read_html(tbl)[0]
    # logger.info(df)
    df.to_csv(
        os.path.join(
            'results', EXECUTION_TIME, 'performance', '{}.csv'.format(params_filename)
        ),
        encoding='utf_8_sig',
    )
