from __future__ import absolute_import, unicode_literals

import logging
import multiprocessing
from logging.handlers import QueueHandler
from multiprocessing import Process
from typing import override

from kombu import Connection, Queue, Message
from kombu.mixins import ConsumerMixin
from kombu.transport.virtual import Channel
from psycopg_pool import ConnectionPool

from helpers.contexts.dashboard import get_configured_dashboard_callback, create_message_context
from helpers.integrations.icat_utils import ICATClient
from helpers.integrations.datacite import get_datacite_client, DataciteClient
from helpers.integrations.panosc import PaNOSCClient, get_panosc_client
from helpers.integrations.visa_utils import get_pg_connection_pool
from helpers.logging.general import configure_worker_logger
from producers.forwarder import MessageForwarder


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
    visa_pg_pool: ConnectionPool = None
    integrations: list = []
    recipients_connections: dict = {}
    recipient_fw_rules: dict = {}
    dashboard_message_type: str = "unknown"
    datacite_client: DataciteClient = None
    panosc_client: PaNOSCClient = None

    def __init__(self, module: str, workers: int, enabled: bool, connection: Connection, recipient_connections: dict,
                 queues: list,
                 fw_rules: dict, log_queue: multiprocessing.Queue, config: dict, integrations: list,
                 icat_session_id: str, dashboard_message_type: str) -> None:
        self.module = module
        self.workers = workers
        self.enabled = enabled
        self.connection = connection
        self.recipients_connections = recipient_connections
        self.queues = queues
        self.recipient_fw_rules = fw_rules
        self.log_queue = log_queue
        self.pacer_config = config
        self.integrations = integrations
        self.icat_session_id = icat_session_id
        self.dashboard_message_type = dashboard_message_type

        handler: QueueHandler = QueueHandler(log_queue)
        self.logger = logging.getLogger()
        configure_worker_logger(handler, config, self.logger)
        self.logger.info(f"Consumer {self.module} initialized.")

    def __callback_router(self, body, message: Message) -> None:
        errors: list = []
        for func in self.__get_callback_functions():
            try:
                self.logger.info(f"Calling callback function: {func.__name__}")
                func(body, message, errors=errors)

            except Exception as e:
                self.logger.error(f"Error processing callback router: {e!r}")
                errors.append((func.__name__, e))
        if errors:
            self.logger.error(f"Message rejected due to errors: {errors}")
            message.reject(requeue=False)
        else:
            message.ack()

    def __dashboard_message_logging_handler(self, message: Message, errors: list = ()) -> None:
        obj_identifiers: dict = self.get_message_object_identifiers(message)
        error_msg: str = "" if not errors else str(errors)
        msg_context = create_message_context(message, self.dashboard_message_type, error_message=error_msg,
                                             obj_identifiers=obj_identifiers)
        self.__configured_dashboard_logging_call(msg_context)

    def __dashboard_message_logging_callback(self, _body, message: Message, *_args, **kwargs) -> None:
        self.__dashboard_message_logging_handler(message, kwargs.get("errors", []))

    def __broker_forwarder_callback(self, _body, message: Message, *_args, **_kwargs) -> None:
        msg_exchange_name: str = message.delivery_info.get("exchange", "")
        routing_key: str = message.delivery_info.get("routing_key", "")
        if msg_exchange_name and routing_key and (msg_exchange_name, routing_key) in self.recipient_fw_rules.keys():
            broker_recipients: list = self.recipient_fw_rules.get((msg_exchange_name, routing_key), [])
            for i in broker_recipients:
                self.logger.info(
                    f"Forwarding message from exchange {msg_exchange_name} with routing_key {routing_key} to broker: {i}")
                broker_conn: Connection | None = self.recipients_connections.get(i, None)
                if broker_conn:
                    try:
                        MessageForwarder.forward_message(broker_conn, message)
                    except Exception as e:
                        self.logger.error(f"Error forwarding message to broker {i}: {e!r}")

    @override
    def get_consumers(self, Consumer, channel) -> list:
        try:
            consumers: list = [
                Consumer(
                    queues=self.queues,
                    callbacks=[self.__callback_router],
                    accept=["text/plain", "application/json", "application/xml", ],
                    prefetch_count=1
                )
            ]
            return consumers
        except Exception as e:
            self.logger.error(f"Error setting up consumers: {e!r}")
            raise e

    def __get_callback_functions(self) -> list:
        callback_functions = [
            getattr(self, attr) for attr in dir(self)
            if callable(getattr(self, attr)) and attr.startswith('callback_func_')
        ]
        callback_functions.sort(
            key=lambda f: (
                1 if f.__name__ == "__dashboard_message_logging_callback" else 0,
                f.__name__
            )
        )
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

        if "messageForwarding" in self.integrations:
            self.callback_func_broker_forwarder_callback = self.__broker_forwarder_callback
        if "dashboard" in self.integrations:
            self.__configured_dashboard_logging_call = get_configured_dashboard_callback(self)
            self.callback_func_dashboard_message_logging = self.__dashboard_message_logging_callback
        if "icat" in self.integrations:
            self.icat_client = ICATClient.open_icat_session(self.pacer_config, session_id=self.icat_session_id)
        if "visa" in self.integrations:
            self.visa_pg_pool = get_pg_connection_pool(self.pacer_config)
        if "datacite" in self.integrations:
            self.datacite_client = get_datacite_client(self.pacer_config, self.logger)
        if "panosc" in self.integrations:
            self.panosc_client = get_panosc_client(self.pacer_config, self.logger)

        self.tasks.logger = self.logger
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
