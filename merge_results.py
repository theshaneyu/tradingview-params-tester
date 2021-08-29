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

folder_list = sys.argv[1:]

print('merging: {}'.format(' & '.join(folder_list)))

result_list: list = []

for folder in sys.argv[1:]:
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


if not os.path.exists(os.path.join('results', 'merged')):
    os.makedirs(os.path.join('results', 'merged'))

if not os.path.exists(os.path.join('results', 'merged', contract_folder)):
    os.makedirs(os.path.join('results', 'merged', contract_folder))

with open(
    os.path.join(
        'results', 'merged', contract_folder, '{}.csv'.format('+'.join(folder_list))
    ),
    'w',
    encoding='utf8',
) as wf:
    for line in result_list:
        wf.write(line)

print(
    'merged file generated at "{}"'.format(
        os.path.join(
            'results', 'merged', contract_folder, '{}.csv'.format('+'.join(folder_list))
        )
    )
)
