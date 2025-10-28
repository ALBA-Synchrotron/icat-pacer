import copy
import inspect
from functools import wraps
from typing import TypeVar, Generic, List, Dict, Tuple, Any, Callable

from helpers.integrations.icat_utils import ICATClient

T = TypeVar("T")
R = TypeVar("R")


class ICATRollbackProxy(Generic[T]):
    _target: T
    _initial_state: Dict[str, Any]

    def __init__(self, obj) -> None:
        super().__setattr__("_target", obj)
        super().__setattr__("_initial_state", copy.deepcopy(obj.__dict__))

    def rollback(self, icat_client: ICATClient, rollback_creation: bool = False) -> None:
        target = super().__getattribute__("_target")
        target.__dict__.clear()
        target.__dict__.update(copy.deepcopy(self._initial_state))

        if not hasattr(target, "id") or rollback_creation:
            icat_client.delete(target)
        else:
            target.save()

    def __getattr__(self, name: str) -> Any:
        target = super().__getattribute__("_target")
        return getattr(target, name)

    def __repr__(self) -> str:
        return f"<RollbackProxy for {repr(self._target)}>"


def rollbackable(func: Callable[..., R]) -> Callable[..., R]:
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> R:
        frame = inspect.currentframe()
        rollback_proxies: List[ICATRollbackProxy[Any]] = []

        try:
            result = func(*args, **kwargs)
            caller_locals = frame.f_back.f_locals
            rb_objects = {
                name: obj for name, obj in caller_locals.items()
                if name.startswith("rb_") and hasattr(obj, "__dict__")
            }

            for name, obj in rb_objects.items():
                proxy = ICATRollbackProxy(obj)
                caller_locals[name] = proxy
                rollback_proxies.append(proxy)

            return result

        finally:
            del frame

    return wrapper
