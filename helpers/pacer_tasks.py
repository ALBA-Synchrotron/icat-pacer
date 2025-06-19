import logging


class PACERTasks:
    logger: logging.Logger = None

    def __init__(self, logger: logging.Logger = None):
        self.logger = logger