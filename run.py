from __future__ import absolute_import, unicode_literals

import os
from multiprocessing import Process

from conf.definitions import EXCHANGES, QUEUES
from connections.rabbitmq import get_rabbitmq_connection
from consumers.users import UsersWorker
from helpers.consumers import start_module_processes
from helpers.serializers import register_custom_serializers


def declare_architecture(c) -> None:
    for exchange in EXCHANGES:
        exchange(c).declare()
    for queue in QUEUES:
        queue(c).declare()


if __name__ == '__main__':
    with get_rabbitmq_connection() as conn:
        try:
            # Declare queues and exchanges (created if they do not exist yet)
            with conn.channel() as channel:
                declare_architecture(channel)

            # Register custom serializers
            register_custom_serializers()

            # Get all consumers
            # TODO: Use ENV var to determine which consumers to start and how many
            os.environ["USERS_WORKERS_ENABLED"] = '1'
            os.environ["USERS_WORKERS"] = '4'

            processes = []
            loaded_modules = ['users', ]  # Add other modules as needed
            for module in loaded_modules:
                processes.extend(start_module_processes(conn, module) or [])  # this already starts processes
            terminate = False
        except KeyboardInterrupt:
            print("Worker stopped by user.")
            terminate = True
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            terminate = True
        finally:
            if terminate and processes:
                print("Stopping all workers...")
                for p in processes:
                    p.terminate()
