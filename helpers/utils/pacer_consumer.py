from __future__ import absolute_import, unicode_literals

import datetime
import logging
from contextlib import suppress
from multiprocessing.managers import convert_to_error

from icat import ICATSessionError

import globals_var
import multiprocessing
from logging.handlers import QueueHandler
from multiprocessing import Process
from typing import override

from kombu import Connection, Queue, Message
from kombu.mixins import ConsumerMixin
from kombu.transport.virtual import Channel
from psycopg_pool import ConnectionPool

from helpers.contexts.dashboard import get_configured_dashboard_callback, create_message_context
from helpers.integrations.icat.extended_client import ICATClient
from helpers.integrations.datacite import get_datacite_client, DataciteClient
from helpers.integrations.icat.icat_plus import ICATPlusClient, get_icat_plus_client
from helpers.integrations.panosc import PaNOSCClient, get_panosc_client
from helpers.integrations.visa_utils import get_pg_connection_pool
from helpers.logging.general import configure_worker_logger
from helpers.utils.utils import running_in_pytest, camel_case_to_snake_case

from producers.forwarder import MessageForwarder
from producers.generic import GenericProducer


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
    icat_session_id: multiprocessing.Value = None
    visa_pg_pool: ConnectionPool = None
    integrations: list = []
    recipients_connections: dict = {}
    recipient_fw_rules: dict = {}
    dashboard_message_type: str = "unknown"
    datacite_client: DataciteClient = None
    panosc_client: PaNOSCClient = None
    icat_plus_client: ICATPlusClient = None
    reject_msg_at_first_callback_error: bool = False
    max_msg_retries: int

    def __init__(self, module: str, workers: int, enabled: bool, connection: Connection, recipient_connections: dict,
                 queues: list,
                 fw_rules: dict, log_queue: multiprocessing.Queue, config: dict, integrations: list,
                 icat_session_id: multiprocessing.Value,
                 dashboard_message_type: str) -> None:
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
        self.dashboard_message_type = dashboard_message_type
        self.icat_session_id = icat_session_id

        self.max_msg_retries = self.pacer_config.get("ingestionSettings", {}).get("messageProcessingRetries", 10)

        handler: QueueHandler = QueueHandler(log_queue)
        self.logger = logging.getLogger(__name__)
        configure_worker_logger(handler, config, self.logger)
        self.logger.info(f"Consumer {self.module} initialized.")

    def __callback_router(self, body, message: Message) -> None:
        errors: dict = {}
        shared_obj_identifiers: dict = {}
        processed_timestamp: str = datetime.datetime.now().isoformat()
        retries: int = message.headers.get("x-retries", 0)
        log_dashboard_retries: bool = (retries == 0 or retries == self.max_msg_retries)

        for func in self.__get_callback_functions(log_dashboard_retries):
            if errors and self.reject_msg_at_first_callback_error and func != self.__dashboard_message_logging_callback:
                continue
            try:
                self.logger.info(f"Calling callback function: {func.__name__}")
                func(body, message, errors=errors, received_at=processed_timestamp,
                     shared_obj_identifiers=shared_obj_identifiers)

            except Exception as e:
                if running_in_pytest():
                    raise e
                self.logger.error(f"Error processing callback router: {e!r}")
                errors[func.__name__] = f"{type(e).__name__}: {str(e)}"
        if errors:
            requeue: bool = any(
                isinstance(i, ICATSessionError) or "Service Temporarily Unavailable" in text for i, text in
                errors.items()) and retries <= self.max_msg_retries
            self.logger.error(f"Message rejected ({'not ' if not requeue else ''}requeued) due to errors: {errors}")

            if requeue:
                GenericProducer.send_message(self.connection, exchange_name="dead-letters-exchange",
                                             routing_key="dead.letters",
                                             headers={"x-retries": retries + 1, "x-delay": 60 * (retries + 1),
                                                      "original-routing-key": message.delivery_info["routing_key"],
                                                      "original-exchange": message.delivery_info["exchange"],
                                                      "x-processing-ts": datetime.datetime.now().isoformat()}, ctx=body)
            message.reject()
        else:
            message.ack()

    def __dashboard_message_logging_handler(self, message: Message, errors: dict = {}, received_at: str = "",
                                            shared_identifiers: dict = {}) -> None:
        obj_identifiers: dict = self.get_message_object_identifiers(message, shared_identifiers)
        msg_context = create_message_context(message, self.dashboard_message_type, error_message=errors,
                                             obj_identifiers=obj_identifiers, received_at=received_at)
        self.__configured_dashboard_logging_call(msg_context)

    def __dashboard_message_logging_callback(self, _body, message: Message, *_args, **kwargs) -> None:
        self.__dashboard_message_logging_handler(message, kwargs.get("errors", {}), kwargs.get("received_at", ''),
                                                 kwargs.get("shared_obj_identifiers", {}))

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

    def __get_callback_functions(self, log_dashboard: bool = False) -> list:
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
        if not log_dashboard:
            with suppress(ValueError):
                callback_functions.remove(self.__dashboard_message_logging_callback)
        return callback_functions

    def start(self) -> None:
        if self.enabled:
            self.logger.info("Starting worker processes")
            for _ in range(self.workers):
                process: Process = Process(target=self._consumer_main, args=(self.log_queue, self.icat_session_id))
                process.start()
                self.logger.debug(
                    f"Spawned {self.module} process: pid={process.pid}")
                self.processes.append(process)

    def stop(self) -> None:
        if self.enabled:
            self.logger.info("Stopping worker processes")
            for process in self.processes:
                self.logger.debug(f"Terminating process: pid={process.pid}")
                process.terminate()
                process.join()
                self.logger.debug(f"Process terminated: pid={process.pid}")

    def _consumer_main(self, log_queue: multiprocessing.Queue, shared_session_id) -> None:
        import os
        handler: QueueHandler = QueueHandler(log_queue)
        self.logger = logging.getLogger(camel_case_to_snake_case(self.__class__.__name__))
        configure_worker_logger(handler, self.pacer_config, self.logger)

        globals_var.ingestion_settings = self.pacer_config.get("ingestionSettings", {})

        if "messageForwarding" in self.integrations:
            self.callback_func_broker_forwarder_callback = self.__broker_forwarder_callback
        if "dashboard" in self.integrations:
            self.__configured_dashboard_logging_call = get_configured_dashboard_callback(self)
            self.callback_func_dashboard_message_logging = self.__dashboard_message_logging_callback
        if "icat" in self.integrations:
            self.icat_client = ICATClient.open_icat_session(self.pacer_config)
            self.icat_client.sessionId = shared_session_id
        if "visa" in self.integrations:
            self.visa_pg_pool = get_pg_connection_pool(self.pacer_config)
        if "datacite" in self.integrations:
            self.datacite_client = get_datacite_client(self.pacer_config, self.logger)
        if "panosc" in self.integrations:
            self.panosc_client = get_panosc_client(self.pacer_config, self.logger)
        if "icatPlus" in self.integrations:
            self.icat_plus_client = get_icat_plus_client(self.pacer_config, self.logger)

        if hasattr(self, "tasks"):
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
        raise NotImplementedError('run_tasks method is not implemented. Use callback methods instead.')

    def receive(self, *args, **kwargs):
        """Intercept message receipt and add arrival timestamp."""
        message = kwargs.get('message') or args[1]
        if message:
            # Add received timestamp (UTC ISO 8601)
            message.headers = message.headers or {}
            message.headers['received_at'] = datetime.now(datetime.timezone.utc).isoformat()
        return super().receive(*args, **kwargs)
