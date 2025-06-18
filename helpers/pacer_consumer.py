from __future__ import absolute_import, unicode_literals

import logging
import multiprocessing
from logging.handlers import QueueHandler
from multiprocessing import Process
from typing import Any, override

from kombu import Connection, Queue
from kombu.mixins import ConsumerMixin
from kombu.transport.virtual import Channel

from helpers.logging import configure_worker_logger


class PACERConsumer(ConsumerMixin):
    module: str = None
    workers: int = 0
    enabled: bool = False
    processes: list = []
    connection: Connection = None
    queues: list[Queue] = []
    logger: logging.Logger = None
    log_queue: multiprocessing.Queue = None
    pacer_config: dict = None

    def __init__(self, module: str, workers: int, enabled: bool, connection: Connection, queues: list,
                 log_queue: multiprocessing.Queue, config: dict) -> None:
        self.module = module
        self.workers = workers
        self.enabled = enabled
        self.connection = connection
        self.queues = queues
        self.log_queue = log_queue
        self.pacer_config = config

        handler: QueueHandler = QueueHandler(log_queue)
        self.logger = logging.getLogger()
        configure_worker_logger(handler, config, self.logger)

        self.logger.debug("ASDASDADASDASDASDAWSDASDDADASDASD")

    @override
    def get_consumers(self, Consumer, channel) -> list:
        try:
            return [
                Consumer(
                    queues=self.queues,
                    # on_message=self.create_user, -> use this if you want to use a single callback
                    # callbacks=[c1, c2], -> use this instead of on_message if you want to use multiple callbacks
                    # on_message=self.run_tasks,
                    callbacks=self.__get_callback_functions(),
                    accept=['text/plain'],
                    prefetch_count=1  # how many unacknowledged messages to fetch at once
                ),
                #  add here more user queue consumers
            ]
        except Exception as e:
            self.logger.error(f"Error setting up consumers: {e!r}")
            raise e

    def __get_callback_functions(self) -> list:
        callback_functions = [
            getattr(self, attr) for attr in dir(self)
            if callable(getattr(self, attr)) and attr.startswith('callback_func_')
        ]
        return callback_functions

    def start(self) -> None:
        if self.enabled:
            for _ in range(self.workers):
                process: Process = Process(target=self._consumer_main, args=(self.log_queue, self.pacer_config,))
                process.start()
                self.processes.append(process)

    def stop(self) -> None:
        if self.enabled:
            for process in self.processes:
                process.terminate()
                process.join()

    def _consumer_main(self, log_queue: multiprocessing.Queue, config: dict) -> None:
        handler: QueueHandler = QueueHandler(log_queue)
        self.logger = logging.getLogger()
        configure_worker_logger(handler, config, self.logger)
        self.run()

    @override
    def on_connection_error(self, exc, interval) -> None:
        self.logger.info(f"Connection error: {exc!r}. Retrying in {interval} seconds...")

    @override
    def on_consume_ready(self, connection: Connection, channel: Channel, consumers, **kwargs) -> None:
        self.logger.info("Consumer is ready to consume messages!")

    @override
    def on_consume_end(self, connection: Connection, default_channel: Channel) -> None:
        self.logger.info("Consumer ended.")

    """
        IMPORTANT NOTE:
            According to Kombu documentation, callbacks are executed in the order they are defined.
            Therefore, message.ack() can be handled in the last callback, but you can handle them per-callback with
            message.acknowledged or in a wrapper function like run_tasks using on_message=func instead of 
            callbacks=[func1,func2].
    """

    def run_tasks(self, body: str, message: str) -> None:
        """Call tasks here"""
        raise NotImplementedError('run_tasks method is not implemented. Use callback methods instead.')
