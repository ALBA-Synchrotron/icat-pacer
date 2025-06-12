from __future__ import absolute_import, unicode_literals

from conf.definitions import EXCHANGES, QUEUES
from connections.rabbitmq import get_rabbitmq_connection
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
        except KeyboardInterrupt:
            print("Worker stopped by user.")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            raise e
