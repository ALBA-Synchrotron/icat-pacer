from functools import lru_cache

from icat.entity import Entity

from helpers.integrations.icat.extended_client import ICATClient
from helpers.static_settings import LRU_CACHE_MAX


@lru_cache(maxsize=LRU_CACHE_MAX)
def get_parameter_type(icat_client: ICATClient, parameter_name: str) -> Entity:
    ret: Entity | None = icat_client.search("ParameterType", conditions={"name__eq": parameter_name},
                                            flatten_single=True)
    if not ret:
        raise Exception(f"Parameter type {parameter_name} not found in ICAT.")
    return ret
