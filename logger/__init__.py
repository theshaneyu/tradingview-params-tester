from .setup_logger import setup_logger


logger = setup_logger('file_and_stPdout_logger', True)
logger_only_stdout = setup_logger('stdout_logger', False)
