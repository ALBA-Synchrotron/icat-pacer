from __future__ import annotations

import copy
from contextlib import AbstractContextManager
from logging import Logger
from typing import TypeVar

from elasticsearch.esql.functions import starts_with
from icat.entity import Entity

from helpers.integrations.icat_utils import ICATClient

T = TypeVar("T")


class _TrackedObjectProxy:

    def __init__(self, obj: T, context: 'ICATRollbackContext', key: str) -> None:
        object.__setattr__(self, '_obj', obj)
        object.__setattr__(self, '_context', context)
        object.__setattr__(self, '_key', key)

    def __getattr__(self, name: str):
        obj = object.__getattribute__(self, '_obj')
        attr = getattr(obj, name)

        if callable(attr) and name in ('create', 'update'):
            context = object.__getattribute__(self, '_context')
            _key = object.__getattribute__(self, '_key')

            def tracked_method(*args, **kwargs) -> T | None:
                result = attr(*args, **kwargs)
                setattr(context, _key, obj)
                return result

            return tracked_method

        return attr

    def __setattr__(self, key: str, value: T):
        obj = object.__getattribute__(self, '_obj')
        context = object.__getattribute__(self, '_context')
        _key = object.__getattribute__(self, '_key')

        setattr(obj, key, value)
        setattr(context, _key, obj)

    def __repr__(self) -> str:
        return f"TrackedObjectProxy({self._obj})"


class ICATRollbackContext(AbstractContextManager):
    _icat_client: ICATClient
    _rollbackable_objects: dict
    _logger: Logger
    _keep_history: bool

    def __init__(self, icat_client: ICATClient, logger: Logger, keep_history: bool = False) -> None:
        self._icat_client = icat_client
        self._rollbackable_objects = {}
        self._logger = logger
        self._keep_history = keep_history

    def __setattr__(self, key: str, value: T) -> None:
        if key in self.__annotations__:
            object.__setattr__(self, key, value)
        else:
            if value.__module__ != "icat.entities":
                raise ValueError(f"Object with {key} is not an ICAT entity")

            if key not in self._rollbackable_objects:
                self._rollbackable_objects[key] = [value]
                self._logger.debug(f"Object with {key} added to ICAT rollback context {id(self)}")
            elif self._keep_history:
                self._rollbackable_objects[key].append(value)
                self._logger.debug(
                    f"Object with {key} added to ICAT rollback context history {id(self)}")
            else:
                if len(self._rollbackable_objects[key]) < 2:
                    self._rollbackable_objects[key].append(value)
                else:
                    self._rollbackable_objects[key][-1] = value
                self._logger.debug(f"Live object with {key} replaced running copy {id(self)}")

    def __getattr__(self, key: str) -> T:
        if key in self.__annotations__:
            object.__getattribute__(self, key)
        else:
            if key in self._rollbackable_objects:
                return _TrackedObjectProxy(self._rollbackable_objects[key][-1].copy(), self, key)
        raise AttributeError(f"Object with {key} doesn't exist")

    def __icat_entity_rollback(self, previous_entity: Entity, latest_entity: Entity, force_delete: bool) -> None:
        if (previous_entity.id is None and latest_entity.id is not None) or force_delete:
            self._icat_client.delete(latest_entity)
        elif previous_entity.id is not None and latest_entity.id is not None:
            latest_entity.update()

    def rollback(self, key: str, force_delete: bool = False) -> T:
        if key in self._rollbackable_objects:
            previous_obj: T = self._rollbackable_objects[key][-2] if len(self._rollbackable_objects[key]) >= 2 else \
                self._rollbackable_objects[key][0]

            latest_obj: T = self._rollbackable_objects[key].pop(-1)

            if previous_obj.__module__ == "icat.entities" and latest_obj.__module__ == "icat.entities":
                self.__icat_entity_rollback(previous_obj, latest_obj, force_delete)
            return latest_obj
        raise AttributeError(f"Object with {key} doesn't exist")

    def rollback_all(self, force_delete: bool = False) -> None:
        self._logger.info(f"Rolling back all objects")
        for obj_key in self._rollbackable_objects.keys():
            _ = self.rollback(obj_key, force_delete=force_delete)

    def __enter__(self) -> ICATRollbackContext:
        return self

    def __exit__(self, exc_type, exc_value, traceback, /):
        pass
