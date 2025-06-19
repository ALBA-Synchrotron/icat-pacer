import importlib
import logging
import multiprocessing
import os
import sys
import time
from logging.handlers import QueueListener

from amqp import Channel
from kombu import Connection, Exchange, Queue

from config.config import ConfigParser
from helpers.logging import configure_pacer_logger
from helpers.pacer_consumer import PACERConsumer
from helpers.serializers import register_custom_serializers
from helpers.utils import Singleton, mask_amqp_password


class PACER:
    config: dict = {}
    broker_connection: Connection = None
    queues: list = []
    exchanges: list = []
    consumers: list = []
    log_queue: multiprocessing.Queue = None
    log_queue_listener: QueueListener = None
    logger: logging.Logger = None
    __metaclass__ = Singleton

    def __init__(self) -> None:
        config_location: str or None = os.environ.get("PACER_CONFIG_LOCATION", "config.yaml")
        self.config = ConfigParser.load_config(config_location)
        self.__initial_setup()

    def get_config_value(self, key: str, fallback_value: any = None, config: dict = None) -> any:
        if not config:
            config = self.config
        try:
            if not isinstance(self.config, dict):
                raise ValueError("The provided config must be a dictionary.")

            if not key:
                raise ValueError("The key must be a non-empty string.")

            keys: list[str] = key.split(".", 1)
            current_key: str = keys[0]

            if len(keys) == 1:
                return config.get(current_key, fallback_value)
            return self.get_config_value(keys[1], fallback_value, config.get(current_key, {}))

        except (AttributeError, ValueError, TypeError) as e:
            return fallback_value

    def __configure_logging(self) -> None:
        if self.log_queue is None:
            self.log_queue = multiprocessing.Queue()

            self.logger = logging.getLogger(__name__)
            handlers: list = configure_pacer_logger(self.config, self.logger)

            self.log_queue_listener = QueueListener(self.log_queue, *handlers)
            self.log_queue_listener.start()



    def __declare_architecture(self, channel: Channel) -> None:
        self.logger.info("Declaring broker exchanges...")
        for exchange in self.exchanges:
            exchange(channel).declare()
            self.logger.debug(f"Exchange declared: name={exchange.name} ")
        self.logger.info("Declaring broker queues...")
        for queue in self.queues:
            queue(channel).declare()
            self.logger.debug(f"Queue declared: name={queue.name} ")

    def __get_broker_url(self):
        protocol: str = self.get_config_value("broker.protocol")
        host: str = self.get_config_value("broker.host")
        port: int = self.get_config_value("broker.port")
        username: str = self.get_config_value("broker.username")
        password: str = self.get_config_value("broker.password")
        vhost: str = self.get_config_value("broker.vHost")

        url: str = f"{protocol}://"
        url = f"{url}{username}:{password}@" if username and password else url
        url = f"{url}{host}:{port}" if port else f"{url}{host}"
        url = f"{url}/{vhost}" if vhost else url

        return url

    def __open_broker_connection(self) -> None:
        if not isinstance(self.broker_connection, Connection):
            self.broker_connection = Connection(self.__get_broker_url())
            self.logger.debug(f"Broker connection URL is: {mask_amqp_password(self.__get_broker_url())}")
            self.logger.info("Broker connection opened")
        else:
            self.logger.error("Broker connection not opened: A connection is already open")

    def __create_exchanges(self):
        self.logger.info("Creating broker exchanges...")
        for exchange in self.get_config_value("exchanges", []):
            exchange_name: str = exchange.get("name")
            exchange_type: str = exchange.get("type")
            self.logger.debug(f"Creating exchange: name={exchange_name} type={exchange_type}")
            self.exchanges.append(Exchange(name=exchange_name, type=exchange_type))
        self.logger.debug(f"Created {len(self.exchanges)} exchanges")

    def __create_queues(self):
        self.logger.info("Creating broker queues...")
        for queue in self.get_config_value("queues", []):
            queue_name: str = queue.get("name")
            exchange_name: str = queue.get("exchange")
            routing_key: str = queue.get("routingKey")
            self.logger.debug(f"Creating queue: name={queue_name} exchange={exchange_name} routing_key={routing_key}")
            self.queues.append(Queue(name=queue_name, exchange=exchange_name, routing_key=routing_key))
        self.logger.debug(f"Created {len(self.queues)} queues")

    def __initial_setup(self) -> None:
        method: str = self.get_config_value("multiprocessStartMethod", "spawn")
        multiprocessing.set_start_method(method)

        self.__configure_logging()
        self.logger.info("Logging configured for PACER main process")

        self.logger.info("Registering custom serializers")
        custom_serializers: list = self.get_config_value("customSerializers", [])
        register_custom_serializers(custom_serializers)

        self.__open_broker_connection()
        self.__create_exchanges()
        self.__create_queues()

    def __get_queues_by_name(self, names: str or list) -> list:
        if isinstance(names, str):
            names = [names]
        return list(filter(lambda q: q.name in names, self.queues))

    def init_workers(self) -> None:
        self.logger.info("Initializing workers...")
        with self.broker_connection.channel() as channel:
            self.__declare_architecture(channel)

            for consumer in self.get_config_value("consumers", []):
                module: str = consumer.get("module")
                workers: int = consumer.get("workers")
                enabled: bool = consumer.get("enabled")
                worker_module_name: str = consumer.get("module")
                worker_class_name: str = consumer.get("className")
                consumer_queues: list = self.__get_queues_by_name(consumer.get("queues"))

                worker_module = importlib.import_module(worker_module_name)
                worker_class = getattr(worker_module, worker_class_name)

                pacer_consumer: PACERConsumer = worker_class(module, workers, enabled, self.broker_connection,
                                                             consumer_queues, self.log_queue, self.config)
                self.consumers.append(pacer_consumer)

    def main_background_loop(self):
        try:
            while True:
                pass
        except KeyboardInterrupt:
            self.stop_consumers()
            sys.exit(0)

    def start_consumers(self) -> None:
        for consumer in self.consumers:
            consumer.start()

    def stop_consumers(self) -> None:
        for consumer in self.consumers:
            consumer.stop()
