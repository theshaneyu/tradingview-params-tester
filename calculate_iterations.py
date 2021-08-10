import sys

from constants import (
    PARAMS_LOWER_LIMITS,
    PARAMS_UPPER_LIMITS,
    INCREASE_SIZE,
    PARAMS,
    SEC_TO_SLEEP_PER_ITER,
)


iterations = 1.0
param_iter = {}

for param in PARAMS:
    iterations = iterations * (
        (float(PARAMS_UPPER_LIMITS[param]) - PARAMS_LOWER_LIMITS[param])
        / INCREASE_SIZE[param]
    )
    param_iter[param] = (
        float(PARAMS_UPPER_LIMITS[param]) - PARAMS_LOWER_LIMITS[param]
    ) / INCREASE_SIZE[param]

total_hours = ((iterations * 2.0) / 60.0) / 60.0
total_days = total_hours / 24.0

for param in PARAMS:
    print(
        '{} ({} -> {} | move {} per iter): {} iterations'.format(
            param,
            int(PARAMS_LOWER_LIMITS[param]),
            int(PARAMS_UPPER_LIMITS[param]),
            int(INCREASE_SIZE[param]),
            int(param_iter[param]),
        )
    )

print('total iterations:', int(iterations))
print('{} sec / per iteration'.format(int(SEC_TO_SLEEP_PER_ITER)))
print('total time (hours):', total_hours)
print('total time (days):', total_days)
