from __future__ import absolute_import, unicode_literals

import logging
from typing import override

from kombu.mixins import ConsumerMixin

from conf.definitions import user_create_queue
from tasks.users import UserTasks


class UsersWorker(ConsumerMixin):
    def __init__(self, connection):
        self.logger = logging.getLogger(__name__)

        self.user_tasks = UserTasks()

        self.connection = connection

    @override
    def get_consumers(self, Consumer, channel):
        try:
            return [
                Consumer(
                    queues=[user_create_queue, ],
                    # on_message=self.create_user, -> use this if you want to use a single callback
                    # callbacks=[c1, c2], -> use this instead of on_message if you want to use multiple callbacks
                    # on_message=self.run_tasks,
                    callbacks=[self.create_user_visa, self.create_user_icat],
                    accept=['text/plain'],
                    prefetch_count=1  # how many unacknowledged messages to fetch at once
                ),
                #  add here more user queue consumers
            ]
        except Exception as e:
            self.logger.error(f"Error setting up consumers: {e!r}")
            raise e

    @override
    def on_connection_error(self, exc, interval):
        self.logger.info(f"Connection error: {exc!r}. Retrying in {interval} seconds...")

    @override
    def on_consume_ready(self, connection, channel, consumers, **kwargs):
        self.logger.info("Consumer is ready to consume messages!")

    @override
    def on_consume_end(self, connection, default_channel):
        self.logger.info("Consumer ended.")

    """
        IMPORTANT NOTE:
            According to Kombu documentation, callbacks are executed in the order they are defined.
            Therefore, message.ack() can be handled in the last callback, but you can handle them per-callback with
            message.acknowledged or in a wrapper function like run_tasks using on_message=func instead of 
            callbacks=[func1,func2].
    """

    def run_tasks(self, body, message):
        """Call tasks here"""
        raise NotImplementedError('run_tasks method is not implemented. Use callback methods instead.')

    def create_user_visa(self, body, message):
        self.logger.info(f"Processing message from {message.delivery_info['routing_key']}: {message.payload!r}")
        return self.user_tasks.create_user_visa(body, message)

    def create_user_icat(self, body, message):
        self.logger.info(f"Processing message from {message.delivery_info['routing_key']}: {message.payload!r}")
        return self.user_tasks.create_user_icat(body, message)
