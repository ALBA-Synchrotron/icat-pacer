import logging
import sys
import os
from typing import Optional

from conf.kombu_config import BASE_DIR


def setup_logging(log_file: Optional[str] = None, level: int = logging.INFO):
    logger = logging.getLogger()
    if log_file is None:
        log_file = os.path.join(BASE_DIR, '..', 'logs', 'icat-pacer.log')
    logger.setLevel(level)

    if logger.handlers:
        return

    # Create log directory if missing (just for local development)
    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    print_format = '%(asctime)s [%(levelname)s] %(name)s: %(message)s'

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter(print_format))
    logger.addHandler(console_handler)

    # File handler
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(logging.Formatter(print_format))
        logger.addHandler(file_handler)
