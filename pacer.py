import logging
import multiprocessing
import os
import sys

from kombu import Connection

from conf.definitions import EXCHANGES, QUEUES
from conf.kombu_config import BASE_DIR
from conf.logging import add_log_handler
from config.config import ConfigParser
from helpers.pacer_consumer import PACERConsumer
from helpers.serializers import register_custom_serializers
from helpers.utils import Singleton


class PACER:
    config: dict = {}
    broker_connection: Connection = None
    consumers: list = []
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
        logger = logging.getLogger()

        log_level: str = self.get_config_value("logging.level", "INFO")
        logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))

        print_format: str = self.get_config_value("logging.printFormat",
                                                  "%(asctime)s [%(levelname)s] %(name)s: %(message)s")

        if self.get_config_value("logging.file.enabled"):
            log_file: str = self.get_config_value("logging.file.path",
                                                  os.path.join(BASE_DIR, "..", "logs", "icat-pacer.log"))
            os.makedirs(os.path.dirname(log_file), exist_ok=True)

            add_log_handler(
                handler=logging.FileHandler(log_file),
                print_format=print_format,
                logger=logger)

        if self.get_config_value("logging.console.enabled"):
            add_log_handler(
                handler=logging.StreamHandler(sys.stdout),
                print_format=print_format,
                logger=logger)

    @classmethod
    def __declare_architecture(cls, connection: Connection) -> None:
        for exchange in EXCHANGES:
            exchange(connection).declare()
        for queue in QUEUES:
            queue(connection).declare()

    def __get_broker_url(self):
        protocol: str = self.config.get("broker.protocol")
        host: str = self.config.get("broker.host")
        port: int = self.config.get("broker.port")
        username: str = self.config.get("broker.username")
        password: str = self.config.get("broker.password")
        vhost: str = self.config.get("broker.vHost")

        url: str = f"{protocol}://"
        url = f"{url}{username}:{password}@" if username and password else url
        url = f"{url}{host}:{port}" if port else url
        url = f"{url}/{vhost}" if vhost else url

        return url

    def __open_broker_connection(self) -> None:
        if not isinstance(self.broker_connection, Connection):
            self.broker_connection = Connection(self.__get_broker_url())

    def __initial_setup(self) -> None:
        method: str = self.get_config_value("multiprocessStartMethod", "spawn")
        multiprocessing.set_start_method(method)
        self.__configure_logging()

    def init_workers(self) -> None:
        # Declare queues and exchanges (created if they do not exist yet)
        with self.broker_connection.channel() as channel:
            self.__class__.__declare_architecture(channel)

            # Register custom serializers
            register_custom_serializers()

            for consumer in self.config.get("consumers", []):
                module: str = consumer.get("module")
                workers: int = consumer.get("workers")
                enabled: bool = consumer.get("enabled")
                worker_module_name: str = consumer.get("moduleName")
                worker_class_name: str = consumer.get("className")

                pacer_consumer: PACERConsumer = PACERConsumer(module, workers, enabled, worker_module_name,
                                                              worker_class_name, self.broker_connection)
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
