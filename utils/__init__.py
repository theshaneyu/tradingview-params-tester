import os

from .browser_helpers import *
from .file_savers import *


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
    current_params: CurrentParams,
    profit: str,
    win_rate: str,
    current_iter: int,
    total_iter: int,
    total_hours: float,
) -> None:
    print(
        (
            'current pamameters: {} {:.2f} {} {} | profit: {} |'
            ' win_rate: {} | iterations ({}/{}) | estimatedly takes {:.2f} hours |'
            ' start time {}'.format(
                int(current_params['period']),
                float(current_params['amplification']),
                int(current_params['long_take_profit']),
                int(current_params['short_take_profit']),
                profit,
                win_rate,
                current_iter,
                total_iter,
                total_hours,
                EXECUTION_TIME,
            )
        )
    )
