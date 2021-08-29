import os
import logging

from constants import LOG_PATH, __PROD__


formatter = logging.Formatter(
    fmt='%(asctime)s [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S'
)

# check logs folder
if not os.path.exists('logs'):
    os.makedirs('logs')

file_handler = logging.FileHandler(LOG_PATH, 'a', 'utf-8')
file_handler.setFormatter(formatter)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)


def setup_logger(
    logger_name: str, log_to_file: bool, level: int = logging.INFO
) -> logging.Logger:
    """To setup as many loggers as you want"""

    logger = logging.getLogger(logger_name)
    logger.setLevel(level)
    logger.addHandler(stream_handler)

    if log_to_file and __PROD__:
        logger.addHandler(file_handler)

    return logger
