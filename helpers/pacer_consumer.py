from __future__ import absolute_import, unicode_literals

import logging
import multiprocessing
from logging.handlers import QueueHandler
from multiprocessing import Process
from typing import override

from kombu import Connection, Queue, Message
from kombu.mixins import ConsumerMixin
from kombu.transport.virtual import Channel

from helpers.icat_utils import ICATClient
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
    icat_client: ICATClient = None
    icat_session_id: str = None

    def __init__(self, module: str, workers: int, enabled: bool, connection: Connection, queues: list,
                 log_queue: multiprocessing.Queue, config: dict, icat_session_id: str) -> None:
        self.module = module
        self.workers = workers
        self.enabled = enabled
        self.connection = connection
        self.queues = queues
        self.log_queue = log_queue
        self.pacer_config = config
        self.icat_session_id = icat_session_id

        handler: QueueHandler = QueueHandler(log_queue)
        self.logger = logging.getLogger()
        configure_worker_logger(handler, config, self.logger)
        self.logger.info(f"Consumer {self.module} initialized.")

    def __callback_router(self, body, message: Message) -> None:
        errors: list = []
        for func in self.__get_callback_functions():
            try:
                self.logger.info(f"Calling callback function: {func.__name__}")
                func(body, message)

            except Exception as e:
                self.logger.error(f"Error processing callback router: {e!r}")
                errors.append((func.__name__, e))
        if errors:
            self.logger.error(f"Message rejected due to errors: {errors}")
            message.reject(requeue=True)
        else:
            message.ack()

    @override
    def get_consumers(self, Consumer, channel) -> list:
        try:
            return [
                Consumer(
                    queues=self.queues,
                    callbacks=[self.__callback_router],
                    accept=['text/plain'],
                    prefetch_count=1
                ),
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
            self.logger.info("Starting worker processes")
            for _ in range(self.workers):
                process: Process = Process(target=self._consumer_main, args=(self.log_queue,))
                process.start()
                self.logger.debug(
                    f"Spawned {self.module} process {len(self.processes) + 1}/{self.workers}: pid={process.pid}")
                self.processes.append(process)

    def stop(self) -> None:
        if self.enabled:
            self.logger.info("Stopping worker processes")
            for process in self.processes:
                self.logger.debug(f"Terminating process: pid={process.pid}")
                process.terminate()
                process.join()
                self.logger.debug(f"Process terminated: pid={process.pid}")

    def _consumer_main(self, log_queue: multiprocessing.Queue) -> None:
        import os
        handler: QueueHandler = QueueHandler(log_queue)
        self.logger = logging.getLogger()
        configure_worker_logger(handler, self.pacer_config, self.logger)
        self.icat_client = ICATClient.open_icat_session(self.pacer_config, self.icat_session_id)
        self.logger.info(f"Consumer {self.module} started in own process with pid={os.getpid()}")
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

    def run_tasks(self, body: str, message: str) -> None:
        """Call tasks here"""
        raise NotImplementedError('run_tasks method is not implemented. Use callback methods instead.')
