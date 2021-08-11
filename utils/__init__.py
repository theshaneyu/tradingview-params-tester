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
