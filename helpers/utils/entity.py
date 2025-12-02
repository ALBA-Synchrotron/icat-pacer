from functools import partial

from icat.entity import Entity

from globals_var import ingestion_settings
from helpers.integrations.icat.extended_client import ICATClient
from helpers.static_settings import PARAMETER_STRING_VALUE_MAX_LENGTH
from helpers.utils.parameters import get_parameter_type
from helpers.utils.strings import to_camel_case
import globals_var

ENTITIES_WITH_PARAMETERS: list = ["Dataset", "Sample", "Investigation", "DataCollection", "Datafile"]


def get_entity_parameter(icat_client: ICATClient, parameter_name: str, conditions: dict = {},
                         create_if_missing: bool = True, entity_name: str = "",
                         entity: Entity | None = None) -> Entity | None:
    if (entity_name and entity_name not in ENTITIES_WITH_PARAMETERS) or (
            entity and entity.BeanName not in ENTITIES_WITH_PARAMETERS):
        raise Exception(f"{entity_name or Entity.BeanName} does not support parameters.")

    if not entity:
        entity = icat_client.search(entity_name, conditions=conditions,
                                    flatten_single=True)

    entity_param_main_fk_name: str = to_camel_case(entity_name or entity.BeanName)

    if not entity:
        raise Exception(f"{entity_param_main_fk_name} with filters {conditions} not found in ICAT.")

    entity_param: Entity | None = next(
        (p for p in entity.parameters if p.type.name == parameter_name),
        None
    )

    if entity_param and not hasattr(entity_param, entity_param_main_fk_name):
        raise Exception(f"{entity_param_main_fk_name}Parameter does not have foreign key {entity_param_main_fk_name}.")

    if not entity_param and create_if_missing:
        entity_param = icat_client.new(f"{entity_param_main_fk_name}Parameter")
        type: Entity = get_parameter_type(icat_client, parameter_name)

        entity_param.type = type
        setattr(entity_param, entity_param_main_fk_name, entity)

    return entity_param


def set_entity_parameter(entity_parameter: Entity, parameter_value: str | int | float) -> Entity:
    if len(str(parameter_value)) > PARAMETER_STRING_VALUE_MAX_LENGTH:
        raise Exception(f"Parameter value for {entity_parameter.type.name} is too long, exceeds max limit.")


    store_value_also_as_text: bool = globals_var.ingestion_settings.get("parameters", {}).get(
        "storeParametersValuesAlsoAsString",
        False)

    match entity_parameter.type.valueType:
        case "DATE_AND_TIME":
            if store_value_also_as_text:
                entity_parameter.stringValue = parameter_value
            entity_parameter.dateTimeValue = parameter_value
        case "NUMERIC":
            if store_value_also_as_text:
                entity_parameter.stringValue = parameter_value
            entity_parameter.numericValue = parameter_value
        case "STRING":
            entity_parameter.stringValue = parameter_value

    if entity_parameter.id:
        entity_parameter.update()
    else:
        entity_parameter.create()

    return entity_parameter
