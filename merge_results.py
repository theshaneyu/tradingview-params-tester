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
    with open(
        os.path.join('results', folder, 'params', '{}.csv'.format(folder)),
        'r',
        encoding='utf8',
    ) as rf:
        for line in rf:
            if 'Profit,WinRate' in line:
                if folder_list.index(folder) == 0:
                    result_list.append(line)
                continue

            result_list.append(line)


with open(
    os.path.join('results', 'merged', '{}.csv'.format('+'.join(folder_list))),
    'w',
    encoding='utf8',
) as wf:
    for line in result_list:
        wf.write(line)
