import sys

from typing import List, Literal

from constants import (
    PARAMS_LOWER_LIMITS,
    PARAMS_UPPER_LIMITS,
    INCREASE_SIZE,
    PARAMS,
    SEC_TO_SLEEP_PER_ITERATION,
)


REMOVED_PARAMS: List[Literal['period', 'amplification', 'long_take_profit']] = [
    'period',
    'amplification',
    'long_take_profit',
]


iterations = 1.0
param_iter = {}

for param in REMOVED_PARAMS:
    iterations_of_this_param = (
        float(PARAMS_UPPER_LIMITS[param]) - float(PARAMS_LOWER_LIMITS[param])
    ) / float(INCREASE_SIZE[param])

    iterations = iterations * iterations_of_this_param
    param_iter[param] = iterations_of_this_param

total_hours = ((iterations * SEC_TO_SLEEP_PER_ITERATION) / 60.0) / 60.0
total_days = total_hours / 24.0

for param in REMOVED_PARAMS:
    print(
        '{} ({} -> {} | move {} per iter): {} iterations'.format(
            param,
            float(PARAMS_LOWER_LIMITS[param])
            if param == 'amplification'
            else int(PARAMS_LOWER_LIMITS[param]),
            float(PARAMS_UPPER_LIMITS[param])
            if param == 'amplification'
            else int(PARAMS_UPPER_LIMITS[param]),
            float(INCREASE_SIZE[param])
            if param == 'amplification'
            else int(INCREASE_SIZE[param]),
            float(param_iter[param])
            if param == 'amplification'
            else int(param_iter[param]),
        )
    )

print('total iterations:', int(iterations))
print('{} sec / per iteration'.format(float(SEC_TO_SLEEP_PER_ITERATION)))
print('total time (hours):', total_hours)
print('total time (days):', total_days)
