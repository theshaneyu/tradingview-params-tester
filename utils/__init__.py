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


def print_current_params(
    current_params: CurrentParams, profit: str, win_rate: str
) -> None:
    print(
        'current pamameters: {}  {}  {}  {} | profit: {} | win_rate: {}'.format(
            current_params['period'],
            current_params['amplification'],
            current_params['long_take_profit'],
            current_params['short_take_profit'],
            profit,
            win_rate,
        )
    )
