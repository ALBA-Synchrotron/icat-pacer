import logging
import multiprocessing
import os
import sys

from kombu import Connection

from conf.definitions import EXCHANGES, QUEUES
from conf.kombu_config import BASE_DIR
from conf.logging import add_log_handler
from config.config import ConfigParser
from helpers.consumers import start_module_processes
from helpers.serializers import register_custom_serializers


class PACER:
    config: dict = {}
    broker_connection: Connection = None
    processes: list = []

    def __init__(self) -> None:
        config_location: str or None = os.environ.get("PACER_CONFIG_LOCATION", "config.yaml")
        self.config = ConfigParser.load_config(config_location)

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

    def __validate_config(self) -> None:
        required_keys = ["broker.url", "logging.level", "logging.file.enabled", "logging.console.enabled"]
        missing_keys = [key for key in required_keys if self.get_config_value(key, None) is None]
        if missing_keys:
            raise ValueError(f"The following required configuration keys are missing: {', '.join(missing_keys)}")

    def configure_logging(self) -> None:
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

    def __open_broker_connection(self) -> None:
        if not isinstance(self.broker_connection, Connection):
            self.broker_connection = Connection(
                self.get_config_value("broker.url", None))

    def initial_setup(self) -> None:
        method: str = self.get_config_value("multiprocessStartMethod", "spawn")
        multiprocessing.set_start_method(method)

    def start(self) -> None:

        try:
            # Declare queues and exchanges (created if they do not exist yet)
            with self.broker_connection.channel() as channel:
                self.__class__.__declare_architecture(channel)

            # Register custom serializers
            register_custom_serializers()

            # Get all consumers
            os.environ['USERS_WORKERS_ENABLED'] = '1'
            os.environ['USERS_WORKERS'] = '4'

            loaded_modules = ['users', ]  # Add other modules as needed
            for consumer in self.config.get("consumers", []):
                self.processes.extend(start_module_processes(self.broker_connection, module) or [])
            terminate = False
        except KeyboardInterrupt:
            logger.error("Worker stopped by user.")
            terminate = True
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")
            terminate = True
        finally:
            if terminate and processes:
                logger.info("Stopping all workers...")
                for p in processes:
                    p.terminate()
