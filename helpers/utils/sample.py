from icat.entity import Entity

from helpers.integrations.icat.extended_client import ICATClient
from helpers.utils.entity import get_entity_parameter, set_entity_parameter


def get_sample_parameter(icat_client: ICATClient, parameter_name: str,
                          create_if_missing: bool = True, dataset_id: int = 0,
                          entity: Entity | None = None) -> Entity | None:
    return get_entity_parameter(icat_client, parameter_name,
                                conditions={"id__eq": dataset_id} if dataset_id else {},
                                create_if_missing=create_if_missing,
                                entity_name="Sample" if not entity else "", entity=entity)


def set_sample_parameter(dataset_parameter: Entity,
                          parameter_value: str | int | float) -> Entity:
    return set_entity_parameter(dataset_parameter, parameter_value)
