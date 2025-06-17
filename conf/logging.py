import logging
import sys
import os
from logging import StreamHandler
from typing import Optional

from conf.kombu_config import BASE_DIR


def add_log_handler(handler: StreamHandler, print_format: str, logger: logging.Logger) -> None:
    handler.setFormatter(logging.Formatter(print_format))
    logger.addHandler(handler)


def setup_logging() -> logging.Logger:
    pass
