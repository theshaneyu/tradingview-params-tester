import sys

from crawler import PARAMS_LOWER_LIMITS, PARAMS_UPPER_LIMITS, ITERATION_SIZE


ITER_TIME = 2.0

iterations = 1.0
param_iter = {}

for param in ('period', 'amplification', 'long_take_profit', 'short_take_profit'):
    iterations = iterations * (
        (float(PARAMS_UPPER_LIMITS[param]) - PARAMS_LOWER_LIMITS[param])
        / ITERATION_SIZE[param]
    )
    param_iter[param] = (
        float(PARAMS_UPPER_LIMITS[param]) - PARAMS_LOWER_LIMITS[param]
    ) / ITERATION_SIZE[param]

total_hours = ((iterations * 2.0) / 60.0) / 60.0
total_days = total_hours / 24.0

for param in ('period', 'amplification', 'long_take_profit', 'short_take_profit'):
    print(
        '{} ({} -> {} | move {} per iter): {} iterations'.format(
            param,
            int(PARAMS_LOWER_LIMITS[param]),
            int(PARAMS_UPPER_LIMITS[param]),
            int(ITERATION_SIZE[param]),
            int(param_iter[param]),
        )
    )

print('total iterations:', int(iterations))
print('{} sec / per iteration'.format(int(ITER_TIME)))
print('total time (hours):', total_hours)
print('total time (days):', total_days)
