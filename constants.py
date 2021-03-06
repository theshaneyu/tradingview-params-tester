import os
import sys
import json
from datetime import datetime
from typing import Literal, List, TypedDict

from dotenv import load_dotenv

from shared_types import Params


load_dotenv()

# types
Indexes = List[Literal['2', '4', '6', '8']]

ParamsConfig = TypedDict(
    'ParamsConfig',
    {
        'period': float,
        'amplification': float,
        'long_take_profit': float,
        'short_take_profit': float,
    },
)

IndexParamMapper = TypedDict(
    'IndexParamMapper',
    {
        '2': Literal['period'],
        '4': Literal['amplification'],
        '6': Literal['long_take_profit'],
        '8': Literal['short_take_profit'],
    },
)

ParamIndexMapper = TypedDict(
    'ParamIndexMapper',
    {
        'period': Literal['2'],
        'amplification': Literal['4'],
        'long_take_profit': Literal['6'],
        'short_take_profit': Literal['8'],
    },
)


# assertions
assert os.getenv('PYTHON_ENV') is not None, "no 'PYTHON_ENV' found in .env"
assert os.getenv('PYTHON_ENV') in (
    'dev',
    'prod',
), "PYTHON_ENV can only be 'dev' or 'prod', found '{}'".format(os.getenv('PYTHON_ENV'))

assert os.getenv('SEND_EMAIL') is not None, "no 'SEND_EMAIL' found in .env"
assert os.getenv('SEND_EMAIL') in (
    '0',
    '1',
), "SEND_EMAIL can only be '0' or '1', found '{}'".format(os.getenv('SEND_EMAIL'))

assert len(sys.argv) == 3, 'must have exactly two system arguments'


# constants
EXECUTION_TIME = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')

SEND_EMAIL = os.getenv('SEND_EMAIL') == '1'

SEC_TO_SLEEP_FOR_IDENTICAL_REPORT = 0.2

MAX_WAITING_SEC_FOR_IDENTICAL_REPORT = 3

SEC_TO_SLEEP_WHEN_STALE_ELEMENT_OCCUR = 0.2

LOG_PATH = os.path.join('logs', '{}.log'.format(EXECUTION_TIME))

PYTHON_ENV = os.getenv('PYTHON_ENV')

ACCOUNT = sys.argv[1]

CONTRACT = sys.argv[2]

__PROD__ = PYTHON_ENV == 'prod'

PARAMS: Params = ['period', 'amplification', 'long_take_profit', 'short_take_profit']

INDEXES: Indexes = ['2', '4', '6', '8']

INDEX_PARAM_MAPPER: IndexParamMapper = {
    '2': 'period',
    '4': 'amplification',
    '6': 'long_take_profit',
    '8': 'short_take_profit',
}

PARAM_INDEX_MAPPER: ParamIndexMapper = {
    'period': '2',
    'amplification': '4',
    'long_take_profit': '6',
    'short_take_profit': '8',
}

PARAMS_LOWER_LIMITS: ParamsConfig = {
    'period': 0.0,
    'amplification': 0.0,
    'long_take_profit': 0.0,
    'short_take_profit': 0.0,
}

PARAMS_UPPER_LIMITS: ParamsConfig = {
    'period': 0.0,
    'amplification': 0.0,
    'long_take_profit': 0.0,
    'short_take_profit': 0.0,
}

INCREASE_SIZE: ParamsConfig = {
    'period': 0.0,
    'amplification': 0.0,
    'long_take_profit': 0.0,
    'short_take_profit': 0.0,
}

with open('config.json', 'r', encoding='utf8') as rf:
    script_config = json.load(rf)

for param in PARAMS:
    PARAMS_LOWER_LIMITS[param] = script_config[param]['lower_limit']
    PARAMS_UPPER_LIMITS[param] = script_config[param]['upper_limit']
    INCREASE_SIZE[param] = script_config[param]['increase_size']
