from icat.entity import Entity

from helpers.integrations.icat.extended_client import ICATClient
from helpers.utils.entity import get_entity_parameter, set_entity_parameter


def get_dataset_parameter(icat_client: ICATClient, dataset_id: int, parameter_name: str,
                          create_if_missing: bool = True) -> Entity | None:
    return get_entity_parameter(icat_client, "Dataset", parameter_name,
                                conditions={"id__eq": dataset_id}, create_if_missing=create_if_missing)


def set_dataset_parameter(dataset_parameter: Entity,
                          parameter_value: str | int | float) -> Entity:
    return set_entity_parameter(dataset_parameter, parameter_value)
