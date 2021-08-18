import sys
from typing import List, Literal, Tuple

from logger import logger
from constants import (
    INCREASE_SIZE,
    PARAMS_LOWER_LIMITS,
    PARAMS_UPPER_LIMITS,
    SEC_TO_SLEEP_AFTER_INCREASING_PARAM,
)


REMOVED_PARAMS: List[Literal['period', 'amplification', 'long_take_profit']] = [
    'period',
    'amplification',
    'long_take_profit',
]


def get_estamated_interations_and_time(log_info: bool = False) -> Tuple[int, float]:
    """calculate estimated iterations and time to take based on
       the script config

    Args:
        print_info (bool, optional): whether to print out the estimnated number
                                     defaults to False.

    Returns:
        Tuple[float, float]: estimated iterations and time
    """
    iterations = 1.0
    param_iter = {}

    for param in REMOVED_PARAMS:
        iterations_of_this_param = (
            float(PARAMS_UPPER_LIMITS[param]) - float(PARAMS_LOWER_LIMITS[param])
        ) / float(INCREASE_SIZE[param])

        iterations = iterations * iterations_of_this_param
        param_iter[param] = iterations_of_this_param

    total_hours = ((iterations * SEC_TO_SLEEP_AFTER_INCREASING_PARAM) / 60.0) / 60.0
    total_days = total_hours / 24.0

    if log_info:
        for param in REMOVED_PARAMS:
            logger.info(
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

        logger.info('total iterations: {}'.format(int(iterations)))
        logger.info('{} sec / per iteration'.format(float(SEC_TO_SLEEP_AFTER_INCREASING_PARAM)))
        logger.info('total time (hours): {}'.format(total_hours))
        logger.info('total time (days): {}'.format(total_days))

    return int(iterations), total_hours


if __name__ == '__main__':
    get_estamated_interations_and_time(log_info=True)
