"""
split root loopers to avoid out-of-memory
"""
import os
import sys
import json
import shutil
import logging
import subprocess
from pprint import pprint
from datetime import datetime

from merge_results import merge_results


assert len(sys.argv) == 3, 'must have exactly 2 system args, found {}'.format(
    len(sys.argv)
)


CONFIG_COPY_PATH = os.path.join('.tmp', 'config.copy.json')


def get_split_runner_logger() -> logging.Logger:
    # check logs folder
    if not os.path.exists(os.path.join('logs', 'split_runner')):
        os.makedirs(os.path.join('logs', 'split_runner'))

    formatter = logging.Formatter(
        fmt='%(asctime)s [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S'
    )

    file_handler = logging.FileHandler(
        os.path.join(
            'logs',
            'split_runner',
            '{}.log'.format(datetime.now().strftime('%Y-%m-%d-%H-%M-%S')),
        ),
        'a',
        'utf-8',
    )
    file_handler.setFormatter(formatter)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    logger = logging.getLogger('split_runner_logger')
    logger.setLevel(logging.INFO)
    logger.addHandler(stream_handler)
    logger.addHandler(file_handler)

    return logger


sr_logger = get_split_runner_logger()

# make a copy of the original config.json in .tmp
shutil.copy('config.json', CONFIG_COPY_PATH)

with open('config.json', 'r', encoding='utf8') as rf:
    config = json.load(rf)

# calcualte (total period / 2)
half_period_iterations = (
    config['period']['upper_limit'] - config['period']['lower_limit']
) / 2.0


# modify upper limit
config['period']['upper_limit'] = (
    config['period']['lower_limit'] + half_period_iterations
)
with open('config.json', 'w', encoding='utf8') as wf:
    json.dump(config, wf, indent=4)

sr_logger.info(
    'first stage period range: {} -> {}'.format(
        config['period']['lower_limit'], config['period']['upper_limit']
    )
)


# track the filename of the first half period iterations
first_iter_filename = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
# sys.exit()
subprocess.call(
    [
        os.path.join('venv', 'Scripts', 'python.exe'),
        'crawler.py',
        sys.argv[1],
        sys.argv[2],
    ]
)

# print('---------------')
# pprint(config)

# increase period's lower limit and upper limit
config['period']['lower_limit'] = config['period']['upper_limit'] + 1

config['period']['upper_limit'] = (
    config['period']['upper_limit'] + half_period_iterations
)

# revise config.json
with open('config.json', 'w', encoding='utf8') as wf:
    json.dump(config, wf, indent=4)

sr_logger.info(
    'second stage period range: {} -> {}'.format(
        config['period']['lower_limit'], config['period']['upper_limit']
    )
)

second_iter_filename = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
subprocess.call(
    [
        os.path.join('venv', 'Scripts', 'python.exe'),
        'crawler.py',
        sys.argv[1],
        sys.argv[2],
    ]
)


# pprint(config)

# restore config.json
shutil.copy(CONFIG_COPY_PATH, 'config.json')

# read the restored config.json
with open('config.json', 'r', encoding='utf8') as rf:
    config = json.load(rf)


sr_logger.info('finished the entire script 🎉')
sr_logger.info('ACCOUNT: {} | CONTRACT: {}'.format(sys.argv[1], sys.argv[2]))
sr_logger.info(
    'period range: {} -> {}'.format(
        config['period']['lower_limit'], config['period']['upper_limit']
    )
)
sr_logger.info('first iteration start time: {}'.format(first_iter_filename))
sr_logger.info('second iteration start time: {}'.format(second_iter_filename))

merge_results(first_iter_filename, second_iter_filename, sys.argv[2], sr_logger)
