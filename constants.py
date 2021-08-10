import json
from datetime import datetime

from typing import Dict


# seconds to sleep after each iteration
SEC_TO_SLEEP_PER_ITER = 2.0

PARAMS = ['period', 'amplification', 'long_take_profit', 'short_take_profit']

EXECUTION_TIME = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')

INDEX_PARAMS_MAPPING = {
    '2': 'period',
    '4': 'amplification',
    '6': 'long_take_profit',
    '8': 'short_take_profit',
}

PARAMS_INDEX_MAPPING = {
    'period': '2',
    'amplification': '4',
    'long_take_profit': '6',
    'short_take_profit': '8',
}

"""
example:
{
    'period': 4.0,
    'amplification': 2.0,
    'long_take_profit': 100.0,
    'short_take_profit': 100.0
}
"""
PARAMS_LOWER_LIMITS: Dict[str, float] = {}

PARAMS_UPPER_LIMITS: Dict[str, float] = {}

INCREASE_SIZE: Dict[str, float] = {}

with open('config.json', 'r', encoding='utf8') as rf:
    script_config = json.load(rf)

for param in PARAMS:
    PARAMS_LOWER_LIMITS[param] = script_config[param]['lower_limit']
    PARAMS_UPPER_LIMITS[param] = script_config[param]['upper_limit']
    INCREASE_SIZE[param] = script_config[param]['increase_size']
