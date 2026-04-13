import logging


class BaseTasks:

    def __init__(self, logger: logging.Logger = None):
        self.logger = logger
