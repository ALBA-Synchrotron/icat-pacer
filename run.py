from __future__ import absolute_import, unicode_literals

import logging
import multiprocessing
import os

from conf.definitions import EXCHANGES, QUEUES
from conf.logging import setup_logging
from connections.rabbitmq import get_rabbitmq_connection
from helpers.consumers import start_module_processes
from helpers.serializers import register_custom_serializers


def declare_architecture(c) -> None:
    for exchange in EXCHANGES:
        exchange(c).declare()
    for queue in QUEUES:
        queue(c).declare()


if __name__ == '__main__':
    multiprocessing.set_start_method("spawn")

    # Set up logging
    setup_logging()
    logger = logging.getLogger(__name__)

    with get_rabbitmq_connection() as conn:
        try:
            # Declare queues and exchanges (created if they do not exist yet)
            with conn.channel() as channel:
                declare_architecture(channel)

            # Register custom serializers
            register_custom_serializers()

            # Get all consumers
            os.environ['USERS_WORKERS_ENABLED'] = '1'
            os.environ['USERS_WORKERS'] = '4'

            processes = []
            loaded_modules = ['users', ]  # Add other modules as needed
            for module in loaded_modules:
                processes.extend(start_module_processes(conn, module) or [])
            terminate = False
        except KeyboardInterrupt:
            logger.error("Worker stopped by user.")
            terminate = True
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")
            terminate = True
        finally:
            if terminate and processes:
                logger.info("Stopping all workers...")
                for p in processes:
                    p.terminate()
