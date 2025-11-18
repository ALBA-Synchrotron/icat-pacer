from icat.entity import Entity

from helpers.integrations.icat.extended_client import ICATClient
from helpers.static_settings import PARAMETER_STRING_VALUE_MAX_LENGTH
from helpers.utils.parameters import get_parameter_type
from helpers.utils.strings import to_camel_case

ENTITIES_WITH_PARAMETERS: list = ["Dataset", "Sample", "Investigation", "DataCollection", "Datafile"]


def get_entity_parameter(icat_client: ICATClient, entity_name: str, parameter_name: str, conditions: dict = {},
                         create_if_missing: bool = True) -> Entity | None:
    if entity_name not in ENTITIES_WITH_PARAMETERS:
        raise Exception(f"{entity_name} does not support parameters.")

    entity: Entity | None = icat_client.search(entity_name, conditions=conditions,
                                               includes=["parameters", "parameters.type"],
                                               flatten_single=True)

    if not entity:
        raise Exception(f"{entity_name} with filters {conditions} not found in ICAT.")

    entity_param: Entity | None = None
    for i in entity.parameters:
        if i.type.name == parameter_name:
            entity_param = i
            break

    if not entity_param and create_if_missing:
        entity_param = icat_client.new(f"{entity_name}Parameter")
        type: Entity = get_parameter_type(icat_client, parameter_name)

        entity_param.type = type
        setattr(entity_param, to_camel_case(entity_name), entity)

    return entity_param


def set_entity_parameter(entity_parameter: Entity, parameter_value: str | int | float) -> Entity:
    if len(str(parameter_value)) > PARAMETER_STRING_VALUE_MAX_LENGTH:
        raise Exception(f"Parameter value for {entity_parameter.type.name} is too long, exceeds max limit.")

    # For some reason the good ol' ingester saves all parameters values as strings. So we'll do the same for now here.

    match entity_parameter.type.valueType:
        case "DATE_AND_TIME":
            entity_parameter.dateTimeValue = parameter_value
            entity_parameter.stringValue = parameter_value
        case "NUMERIC":
            entity_parameter.numericValue = parameter_value
            entity_parameter.stringValue = parameter_value
        case "STRING":
            entity_parameter.stringValue = parameter_value

    if entity_parameter.id:
        entity_parameter.update()
    else:
        entity_parameter.create()

    return entity_parameter
