import logging
import os

import sys
from logging.handlers import RotatingFileHandler

from helpers.elastic import CustomElasticHandler

BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_LOGGING_FORMAT: str = "%(asctime)s [%(levelname)s] %(name)s -- %(message)s"


def configure_handler_format_and_level(handler: logging.StreamHandler, log_level: str,
                                       print_format: str or None) -> None:
    if print_format:
        handler.setFormatter(logging.Formatter(print_format))
    handler.setLevel(log_level)


def configure_worker_logger(handler: logging.StreamHandler or logging.Handler, config: dict,
                            logger: logging.Logger) -> None:
    log_level: str = config.get("logging").get("logLevel", "INFO")

    configure_handler_format_and_level(handler, log_level, None)
    handler.setLevel(log_level)
    logger.setLevel(log_level)
    logger.addHandler(handler)


def configure_pacer_logger(config: dict, logger: logging.Logger) -> list:
    logging_config: dict = config.get("logging")

    log_level: str = logging_config.get("logLevel", "INFO")
    print_format: str = logging_config.get("printFormat", DEFAULT_LOGGING_FORMAT)

    handlers: list = []

    file_logging_config: dict = logging_config.get("file")

    if file_logging_config.get("enabled", False):
        log_file: str = file_logging_config.get("path", os.path.join(BASE_DIR, "logs", "icat-pacer.log"))
        os.makedirs(os.path.dirname(log_file), exist_ok=True)

        if file_logging_config.get("rotate", False):
            max_bytes: int = file_logging_config.get("maxMBytes", 100 * 1024)
            backup_count: int = file_logging_config.get("backupCount", 5)
            handlers.append(RotatingFileHandler(log_file, maxBytes=max_bytes, backupCount=backup_count))
        else:
            handlers.append(logging.FileHandler(log_file))

    elastic_logging_config: dict = logging_config.get("elastic")
    if elastic_logging_config.get("enabled", False):
        server_url: str = elastic_logging_config.get("serverUrl", "")
        index: str = elastic_logging_config.get("indexName")
        service_name: str = elastic_logging_config.get("serviceName", "icat-pacer")
        service_environment: str = elastic_logging_config.get("serviceEnvironment", "local")
        logging.getLogger('elastic_transport.transport').setLevel(logging.ERROR)

        handlers.append(CustomElasticHandler(host=server_url, index=index, service_name=service_name,
                                             service_environment=service_environment))

    if logging_config.get("console").get("enabled", False):
        handlers.append(logging.StreamHandler(sys.stdout))

    logger.setLevel(log_level)

    for handler in handlers:
        configure_handler_format_and_level(handler, log_level, print_format)
        logger.addHandler(handler)

    return handlers
