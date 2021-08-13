import os

from .file_savers import *
from .browser_helpers import *
from .logger import *


create_files_and_folders()

logger = setup_logger('file_and_stdout_logger', True)
logger_only_stdout = setup_logger('stdout_logger', False)


def get_chromedriver_path() -> str:
    # check chromedriver's existence
    files = os.listdir('chromedriver')
    if len(files) != 1:
        raise Exception('Chromedriver not found')

    return os.path.join('chromedriver', files[0])


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
    total_hours: float,
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
            ' win_rate: {} | iterations ({}/{}) | estimatedly takes {:.2f} hours |'
            ' start time {}'.format(
                period,
                amplification,
                long_take_profit,
                short_take_profit,
                profit,
                win_rate,
                current_iter,
                total_iter,
                total_hours,
                EXECUTION_TIME,
            )
        )
    )
