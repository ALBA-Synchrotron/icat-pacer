from __future__ import absolute_import, unicode_literals

import logging


class DatasetsInternalTasks:

    def __init__(self, logger: logging.Logger = None):
        self.logger = logger

    # TODO: Tasks here need to rollback with rollback_creation param to True; also need to take into account that an
    #       object might have been rollbacked in another function before it reached the next function.
    #       TLDR: Dataset might not exist for some funcs executed here
