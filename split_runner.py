"""
split root loopers to avoid out-of-memory
"""
import os
import sys
import json
import shutil
import subprocess
from pprint import pprint
from datetime import datetime


# from logger import logger


CONFIG_COPY_PATH = os.path.join('.tmp', 'config.copy.json')

# make a copy of the original config.json
shutil.copy('config.json', CONFIG_COPY_PATH)

with open('config.json', 'r', encoding='utf8') as rf:
    config = json.load(rf)

# pprint(original_config)

# half period iterations
half_period_iterations = (
    config['period']['upper_limit'] - config['period']['lower_limit']
) / 2.0


config['period']['upper_limit'] = (
    config['period']['lower_limit'] + half_period_iterations
)

with open('config.json', 'w', encoding='utf8') as wf:
    json.dump(config, wf, indent=4)

print(
    'first stage period range: {} -> {}'.format(
        config['period']['lower_limit'], config['period']['upper_limit']
    )
)

assert len(sys.argv) == 3, 'must have exactly 2 system args, found {}'.format(
    len(sys.argv)
)

first_iter_filename = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
# subprocess.call(['pwd'])
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

print(
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

print('first_iter_filename: {}'.format(first_iter_filename))
print('second_iter_filename: {}'.format(second_iter_filename))
