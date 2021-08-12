import json
from datetime import datetime

from typing import Literal, List, TypedDict

from shared_types import Params


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


# seconds to sleep after each iteration
SEC_TO_SLEEP_PER_ITERATION = 1.5

EXECUTION_TIME = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')

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
