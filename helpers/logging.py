import logging
import os
import sys

BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_LOGGING_FORMAT: str = "%(asctime)s [%(levelname)s] %(name)s -- %(message)s"

def configure_handler_format_and_level(handler: logging.StreamHandler, log_level: str, print_format: str or None) -> None:
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
    log_level: str = config.get("logging").get("logLevel", "INFO")
    print_format: str = config.get("logging").get("printFormat", DEFAULT_LOGGING_FORMAT)

    handlers: list = []

    if config.get("logging").get("file").get("enabled", False):
        log_file: str = config.get("logging").get("file").get("path",
                                                              os.path.join(BASE_DIR, "..", "logs", "icat-pacer.log"))
        os.makedirs(os.path.dirname(log_file), exist_ok=True)

        handlers.append(logging.FileHandler(log_file))

    if config.get("logging").get("console").get("enabled", False):
        handlers.append(logging.StreamHandler(sys.stdout))

    logger.setLevel(log_level)

    for handler in handlers:
        configure_handler_format_and_level(handler, log_level, print_format)
        logger.addHandler(handler)

    return handlers
