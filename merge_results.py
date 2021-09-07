"""
to merge multiple result CSVs, simply put result folder names in the system args,
the result will be generated in `reuslts/merged`

usage example:
   python merge_results.py 2021-08-26-13-21-47 2021-08-27-11-09-33

generated csv:
    results/merged/2021-08-26-13-21-47+2021-08-27-11-09-33.csv
"""

import os
import sys
from logging import Logger

from typing import Tuple


if not os.path.exists(os.path.join('results', 'merged')):
    os.makedirs(os.path.join('results', 'merged'))


def _find_correct_foldername(
    first_half_folder: str, second_half_folder: str, contract: str, logger: Logger
) -> Tuple[str, str]:
    trimed_first = '-'.join(first_half_folder.split('-')[:5])
    trimed_second = '-'.join(second_half_folder.split('-')[:5])

    for foldername in os.listdir(os.path.join('results', contract)):
        if trimed_first in foldername:
            logger.info(
                'found "{}" matches the original first-half start time "{}"'.format(
                    os.path.join('results', contract, foldername), first_half_folder
                )
            )
            found_first = foldername
            continue

        if trimed_second in foldername:
            logger.info(
                'found "{}" matches the original second-half start time "{}"'.format(
                    os.path.join('results', contract, foldername), second_half_folder
                )
            )
            found_second = foldername

    if found_first is None or found_second is None:
        logger.error(
            (
                'can not find corresponding foldername '
                'under "{}" with trimmed foldername "{}"'
            ).format(
                os.path.join('results', contract),
                trimed_first if found_first is None else trimed_second,
            )
        )

        raise Exception('no similar fodlername found')

    return found_first, found_second


def merge_results(
    first_half_folder: str,
    second_half_folder: str,
    contract_folder: str,
    logger: Logger,
) -> None:
    correct_first_half_folder, correct_second_half_folder = _find_correct_foldername(
        first_half_folder, second_half_folder, contract_folder, logger
    )

    logger.info(
        'start merging: "{}" & "{}"'.format(
            os.path.join(
                'results',
                contract_folder,
                first_half_folder,
                'params',
                '{}.csv'.format(first_half_folder),
            ),
            os.path.join(
                'results',
                contract_folder,
                second_half_folder,
                'params',
                '{}.csv'.format(second_half_folder),
            ),
        )
    )

    folder_list = [correct_first_half_folder, correct_second_half_folder]

    result_list: list = []

    for foldername in folder_list:
        with open(
            os.path.join(
                'results',
                contract_folder,
                foldername,
                'params',
                '{}.csv'.format(foldername),
            ),
            'r',
            encoding='utf8',
        ) as rf:
            for line in rf:
                if 'Profit,WinRate' in line:
                    if folder_list.index(foldername) == 0:
                        result_list.append(line)
                    continue

                result_list.append(line)

    merged_filepath = os.path.join(
        'results', 'merged', '{}.csv'.format('+'.join(folder_list))
    )

    with open(
        merged_filepath,
        'w',
        encoding='utf8',
    ) as wf:
        for line in result_list:
            wf.write(line)

    logger.info('merged file generated at "{}"'.format(merged_filepath))


if __name__ == "__main__":
    import logging

    formatter = logging.Formatter(
        fmt='%(asctime)s [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S'
    )
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    test_logger = logging.getLogger('test')
    test_logger.setLevel(logging.INFO)
    test_logger.addHandler(stream_handler)

    merge_results(
        '2021-09-02-16-59-16',
        '2021-09-02-20-16-20',
        'ym',
        test_logger,
    )

    # _find_correct_foldername('2021-09-02-16-59-16', '2021-09-02-20-16-19', 'ym')
