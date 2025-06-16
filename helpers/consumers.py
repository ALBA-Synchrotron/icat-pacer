from __future__ import absolute_import, unicode_literals

import importlib
import logging
import os
from multiprocessing import Process
from typing import Any

from conf.logging import setup_logging
from helpers.utils import string_to_classname

logger = logging.getLogger(__name__)


def worker(conn, worker_cls: Any):
    setup_logging()
    worker_cls(conn).run()


def start_module_processes(conn, module_name: str) -> list[Process]:
    """
    module_name: str - the name of the module to start processes for, e.g. 'users' or 'dataset_parameter'
    """

    logger.info(
        f'{module_name.upper()}_WORKERS_ENABLED -- {os.environ.get(f"{module_name.upper()}_WORKERS_ENABLED", "NOT SET")}')
    workers_enabled = int(os.environ.get(f'{module_name.upper()}_WORKERS_ENABLED', 0))
    worker_num = int(
        os.environ[f'{module_name.upper()}_WORKERS']) if f'{module_name.upper()}_WORKERS' in os.environ else 1
    if not workers_enabled:
        logger.info(f"{module_name} workers are not enabled, skipping process start")
        return []

    logger.info(f'Starting module {module_name} with {worker_num} workers.')
    processes = []
    for n in list(range(1, worker_num + 1)):
        # Import the worker dynamically based on the module name
        worker_class_name = f'{string_to_classname(module_name)}Worker'
        worker_module_name = f'app.consumers.{module_name}'
        worker_module = importlib.import_module(worker_module_name)
        worker_class = getattr(worker_module, worker_class_name)

        logger.info(f"Starting {worker_class_name} {n} of {worker_num}")
        process = Process(target=worker, args=(conn, worker_class,))
        process.start()
        logger.info(f"{worker_class_name} {n} of {worker_num} started")
        processes.append(process)
    return processes
