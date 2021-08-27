import os

from constants import ACCOUNT
from logger import logger_only_stdout

from .file_savers import *
from .email_sender import *
from .browser_helpers import *
from .device_limit_checker import DeviceLimitChecker


limit_checker = DeviceLimitChecker()


def get_driver_path() -> str:
    # check driver's existence
    files = os.listdir('drivers')
    if len(files) != 1:
        raise Exception('driver not found')

    return os.path.join('drivers', files[0])


def get_params_filename(params: CurrentParams) -> str:
    return '{}_{}_{}_{}'.format(
        params['period'],
        params['amplification'],
        str(params['long_take_profit']).replace('.', '-'),
        str(params['short_take_profit']).replace('.', '-'),
    )


def print_current_info(
    csv_line: str,
    current_iter: int,
    total_iter: int,
) -> None:
    csv_item_list = csv_line.split(',')

    if len(csv_item_list) != 6:
        raise Exception('too many items in a csv line')

    (
        period,
        amplification,
        long_take_profit,
        short_take_profit,
        profit,
        win_rate,
    ) = csv_item_list

    logger_only_stdout.info(
        (
            'current pamameters: {} {} {} {} | profit: {} |'
            ' win_rate: {} | iterations ({}/{}) | start time {} | user: {}'.format(
                period,
                amplification,
                long_take_profit,
                short_take_profit,
                profit,
                win_rate,
                current_iter,
                total_iter,
                EXECUTION_TIME,
                ACCOUNT,
            )
        )
    )
