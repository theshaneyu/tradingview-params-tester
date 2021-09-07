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


if not os.path.exists(os.path.join('results', 'merged')):
    os.makedirs(os.path.join('results', 'merged'))


def merge_results(
    first_half_folder: str, second_half_folder: str, logger: Logger
) -> None:
    folder_list = [first_half_folder, second_half_folder]

    logger.info('merging: {}'.format(' & '.join(folder_list)))

    result_list: list = []

    for folder in folder_list:
        if os.path.exists(os.path.join('results', 'ym', folder)):
            contract_folder = 'ym'
        else:
            contract_folder = 'nq'

        with open(
            os.path.join(
                'results', contract_folder, folder, 'params', '{}.csv'.format(folder)
            ),
            'r',
            encoding='utf8',
        ) as rf:
            for line in rf:
                if 'Profit,WinRate' in line:
                    if folder_list.index(folder) == 0:
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
