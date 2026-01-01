import logging
import os
from datetime import datetime

from utils.common_utils import project_name, create_folders_if_not_exist

LOG_DIR = f"assets/{project_name}/log_files"
create_folders_if_not_exist([LOG_DIR])

formatter = logging.Formatter(
    '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)


def setup_custom_logger(name):
    log_file = os.path.join(LOG_DIR, f"app_{datetime.now().strftime('%Y%m%d')}.log")
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.DEBUG)

    custom_logger = logging.getLogger(name)
    custom_logger.setLevel(logging.DEBUG)

    if not custom_logger.handlers:
        custom_logger.addHandler(file_handler)
        custom_logger.addHandler(console_handler)

    return custom_logger


logger = setup_custom_logger(f"{project_name}_logger")
