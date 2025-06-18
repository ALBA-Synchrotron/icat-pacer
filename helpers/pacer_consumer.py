from __future__ import absolute_import, unicode_literals

import importlib
from multiprocessing import Process
from typing import Any, override

from kombu import Connection, Queue
from kombu.mixins import ConsumerMixin

from conf.definitions import user_create_queue


class PACERConsumer(ConsumerMixin):
    module: str = None
    workers: int = 0
    enabled: bool = False
    processes: list = []
    worker_module = None
    worker_class = None
    connection: Connection = None
    queues: list[Queue] = []

    def __init__(self, module: str, workers: int, enabled: bool, worker_module_name: str, worker_class_name: str,
                 connection: Connection) -> None:
        self.module = module
        self.workers = workers
        self.enabled = enabled
        self.worker_module = importlib.import_module(worker_module_name)
        self.worker_class = getattr(self.worker_module, worker_class_name)
        self.connection = connection

    @override
    def get_consumers(self, Consumer, channel):
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
            #TODO:self.logger.error(f"Error setting up consumers: {e!r}")
            raise e

    def __get_callback_functions(self) -> list:
        callback_functions = [
            attr for attr in dir(self)
            if callable(getattr(self, attr)) and attr.startswith('callback_func_')
        ]
        return callback_functions

    def start(self) -> None:
        if self.enabled:
            for _ in range(self.workers):
                process: Process = Process(target=self.__class__._consumer_main,
                                           args=(self.connection, self.worker_class,))
                process.start()
                self.processes.append(process)

    def stop(self) -> None:
        if self.enabled:
            for process in self.processes:
                process.terminate()
                process.join()

    @classmethod
    def _consumer_main(cls, connection: Connection, worker_cls: Any) -> None:
        #logger = logging.getLogger(__name__)
        worker_cls(connection).run()

    @override
    def on_connection_error(self, exc, interval):
        pass
        #self.logger.info(f"Connection error: {exc!r}. Retrying in {interval} seconds...")

    @override
    def on_consume_ready(self, connection, channel, consumers, **kwargs):
        print("consumer ready >> ")
        #self.logger.info("Consumer is ready to consume messages!")

    @override
    def on_consume_end(self, connection, default_channel):
        pass
        #self.logger.info("Consumer ended.")

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