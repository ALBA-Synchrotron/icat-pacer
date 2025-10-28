import importlib
import logging
import multiprocessing
import os
import sys
from logging.handlers import QueueListener
from time import sleep
from urllib.parse import quote

from amqp import Channel
from kombu import Connection, Exchange, Queue

from config.config import ConfigParser
from helpers.integrations.icat_utils import ICATClient
from helpers.logging import configure_pacer_logger
from helpers.utils.pacer_consumer import PACERConsumer
from helpers.utils.serializers import register_custom_serializers
from helpers.utils import Singleton, mask_amqp_password

MAIN_LOOP_WAIT_TIME: int = 15 * 60


class PACER:
    config: dict = {}
    broker_connection: Connection = None
    queues: list = []
    exchanges: list = []
    consumers: list = []
    log_queue: multiprocessing.Queue = None
    log_queue_listener: QueueListener = None
    logger: logging.Logger = None
    icat_client: ICATClient = None
    recipient_connections: dict = {}
    recipient_fw_rules: dict = {}
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

    @classmethod
    def __construct_broker_url(cls, protocol: str, host: str, port: int, username: str, password: str,
                               vhost: str) -> str:
        url: str = f"{protocol}://"
        url = f"{url}{username}:{password}@" if username and password else url
        url = f"{url}{host}:{port}" if port else f"{url}{host}"
        url = f"{url}/{vhost}" if vhost else url

        return url

    def __open_main_broker_connection(self) -> None:
        main_broker_protocol: str = self.get_config_value("brokers.main.protocol")
        main_broker_host: str = self.get_config_value("brokers.main.host")
        main_broker_port: int = self.get_config_value("brokers.main.port")
        main_broker_username: str = quote(self.get_config_value("brokers.main.username", fallback_value=""))
        main_broker_password: str = quote(self.get_config_value("brokers.main.password", fallback_value=""))
        main_broker_vhost: str = quote(self.get_config_value("brokers.main.vHost", fallback_value=""))

        main_broker_url: str = self.__construct_broker_url(main_broker_protocol, main_broker_host, main_broker_port,
                                                           main_broker_username, main_broker_password,
                                                           main_broker_vhost)
        self.broker_connection = Connection(main_broker_url)
        self.logger.debug(f"Main broker connection URL is: {mask_amqp_password(main_broker_url)}")
        self.logger.info("Main broker connection opened")

    def __open_recipient_broker_connections(self) -> None:
        recipients: list = self.get_config_value("brokers.recipients", [])
        for recipient in recipients:
            recipient_name: str = recipient.get("name")
            recipient_protocol: str = recipient.get("protocol")
            recipient_host: str = recipient.get("host")
            recipient_port: int = recipient.get("port")
            recipient_username: str = quote(recipient.get("username", ""))
            recipient_password: str = quote(recipient.get("password", ""))
            recipient_vhost: str = quote(recipient.get("vHost", ""))

            recipient_broker_url: str = self.__construct_broker_url(recipient_protocol, recipient_host, recipient_port,
                                                                    recipient_username, recipient_password,
                                                                    recipient_vhost)
            self.recipient_connections[recipient_name] = Connection(recipient_broker_url)
            self.logger.debug(f"Recipient broker connection URL for {recipient_name} is: "
                              f"{mask_amqp_password(recipient_broker_url)}")
            self.logger.info(f"Recipient broker connection opened for {recipient_name}")

            fw_rules: list = recipient.get("forwardingRules", [])
            for i in fw_rules:
                from_exchange: str = i.get("fromExchange")
                with_routing_key: bool = i.get("withRoutingKey")
                to_broker: str = i.get("toBroker")

                if (from_exchange, with_routing_key) not in self.recipient_fw_rules:
                    self.recipient_fw_rules[(from_exchange, with_routing_key)] = []
                self.recipient_fw_rules[(from_exchange, with_routing_key)].append(to_broker)

    def __open_broker_connections(self) -> None:
        if not isinstance(self.broker_connection, Connection):
            self.__open_main_broker_connection()
        else:
            self.logger.error("Main broker connection not opened: A connection is already open")

        if not any(isinstance(value, Connection) for value in self.recipient_connections.values()):
            self.__open_recipient_broker_connections()
        else:
            self.logger.error("Recipient broker connections not opened: Connections are already open")

    def __create_exchanges(self) -> None:
        self.logger.info("Creating broker exchanges...")
        for exchange in self.get_config_value("exchanges", []):
            exchange_name: str = exchange.get("name")
            exchange_type: str = exchange.get("type")
            self.logger.debug(f"Creating exchange: name={exchange_name} type={exchange_type}")
            self.exchanges.append(Exchange(name=exchange_name, type=exchange_type))
        self.logger.debug(f"Created {len(self.exchanges)} exchanges")

    def __create_queues(self) -> None:
        self.logger.info("Creating broker queues...")
        for queue in self.get_config_value("queues", []):
            queue_name: str = queue.get("name")
            exchange_name: str = queue.get("exchange")
            routing_key: str = queue.get("routingKey")
            self.logger.debug(f"Creating queue: name={queue_name} exchange={exchange_name} routing_key={routing_key}")
            self.queues.append(Queue(name=queue_name, exchange=exchange_name, routing_key=routing_key))
        self.logger.debug(f"Created {len(self.queues)} queues")

    def __open_icat_session(self) -> None:
        self.icat_client = ICATClient.open_icat_session(self.config)
        if self.icat_client:
            self.logger.info("ICAT session opened")
        else:
            self.logger.error("ICAT session not opened: Could not open ICAT session")

    def __initial_setup(self) -> None:
        method: str = self.get_config_value("multiprocessStartMethod", "spawn")
        multiprocessing.set_start_method(method)

        self.__configure_logging()
        self.logger.info("Logging configured for PACER main process")

        self.logger.info("Registering custom serializers")
        custom_serializers: list = self.get_config_value("customSerializers", [])
        register_custom_serializers(custom_serializers)

        self.__open_broker_connections()
        self.__create_exchanges()
        self.__create_queues()

        with self.broker_connection.channel() as channel:
            self.__declare_architecture(channel)

        self.__open_icat_session()

    def __get_queues_by_name(self, names: str or list) -> list:
        if isinstance(names, str):
            names = [names]
        return list(filter(lambda q: q.name in names, self.queues))

    def init_workers(self) -> None:
        self.logger.info("Initializing workers...")

        for consumer in self.get_config_value("consumers", []):
            module: str = consumer.get("module")
            workers: int = consumer.get("workers")
            enabled: bool = consumer.get("enabled")
            worker_module_name: str = consumer.get("module")
            worker_class_name: str = consumer.get("className")
            consumer_queues: list = self.__get_queues_by_name(consumer.get("queues"))
            integrations: list = consumer.get("integrations", [])

            worker_module = importlib.import_module(worker_module_name)
            worker_class = getattr(worker_module, worker_class_name)

            pacer_consumer: PACERConsumer = worker_class(module, workers, enabled, self.broker_connection,
                                                         self.recipient_connections,
                                                         consumer_queues, self.recipient_fw_rules, self.log_queue,
                                                         self.config, integrations,
                                                         self.icat_client.session_id)
            self.consumers.append(pacer_consumer)

    def main_background_loop(self) -> None:
        try:
            while True:
                sleep(MAIN_LOOP_WAIT_TIME)
                self.icat_client.auto_refresh_session()
        except KeyboardInterrupt:
            self.stop_consumers()
            sys.exit(0)

    def start_consumers(self) -> None:
        for consumer in self.consumers:
            consumer.start()

    def stop_consumers(self) -> None:
        for consumer in self.consumers:
            consumer.stop()
