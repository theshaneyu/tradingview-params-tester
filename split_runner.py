"""
split root loopers to avoid out-of-memory
"""
import os
import sys
import json
import shutil
import subprocess
from pprint import pprint


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
    json.dump(config, wf)

print(
    'first stage period range: {} -> {}'.format(
        config['period']['lower_limit'], config['period']['upper_limit']
    )
)

# assert len(sys.argv) == 3, 'must have exactly 2 system args, found {}'.format(
#     len(sys.argv)
# )

# subprocess.call(['python', 'crawler.py', sys.argv[1], sys.argv[2]])

# pprint(config)

# config['period']['upper_limit'] = (
#     config['period']['lower_limit'] + half_period_iterations
# )


# pprint
