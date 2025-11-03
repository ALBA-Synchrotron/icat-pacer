from __future__ import annotations

import copy
from contextlib import AbstractContextManager
from logging import Logger
from typing import TypeVar

from helpers.integrations.icat_utils import ICATClient

T = TypeVar("T")


class ICATRollbackContext(AbstractContextManager):
    _icat_client: ICATClient
    _rollbackable_objects: dict
    _logger: Logger

    def __init__(self, icat_client: ICATClient, logger: Logger) -> None:
        self._icat_client = icat_client
        self._rollbackable_objects = {}
        self._logger = logger

    def __setattr__(self, key: str, value: T) -> None:
        if key in ("_icat_client", "_rollbackable_objects", "_logger"):
            super().__setattr__(key, value)
        else:
            if key not in self._rollbackable_objects:
                self._logger.debug(
                    f"Object {key} added to ICAT rollback context {id(self)} via shallow copy")
                self._rollbackable_objects[key] = copy.copy(value)

    def __enter__(self) -> ICATRollbackContext:
        return self

    def __exit__(self, exc_type, exc_value, traceback, /):
        pass
