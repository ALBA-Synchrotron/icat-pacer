from logging import Logger

from icat.entity import Entity

from exceptions.instrument import InstrumentNotFound
from exceptions.investigation import InvestigationNotFound, InvestigationInstrumentMismatch, MultipleInvestigationsFound
from helpers.models.dataset import DatasetContext
from helpers.integrations.icat.extended_client import ICATClient
from helpers.static_settings import PROCESSED_DATASET_TYPE_NAME
from helpers.utils.datetime import try_parse_datetime
from helpers.utils.entity import get_entity_parameter, set_entity_parameter


def get_dataset_parameter(icat_client: ICATClient, parameter_name: str,
                          create_if_missing: bool = True, dataset_id: int = 0,
                          entity: Entity | None = None) -> Entity | None:
    return get_entity_parameter(icat_client, parameter_name,
                                entity_id=dataset_id or entity.id,
                                create_if_missing=create_if_missing,
                                entity_name="Dataset", entity=entity)


def set_dataset_parameter(dataset_parameter: Entity,
                          parameter_value: str | int | float) -> Entity:
    return set_entity_parameter(dataset_parameter, parameter_value)


def get_duplicated_processed_dataset_in_investigation(icat_client: ICATClient, dataset_name: str, dataset_type: str,
                                                      investigation_id: str) -> Entity | None:

    if dataset_type != PROCESSED_DATASET_TYPE_NAME:
        return None

    result = icat_client.search("Dataset", conditions={"name__like": dataset_name,
                                                       "type.name__eq": PROCESSED_DATASET_TYPE_NAME,
                                                       "sample.name__eq": sample_name,
                                                       "investigation.id__eq": investigation_id},
                                flatten_single=True)

    if isinstance(result, list):
        raise Exception(f"Multiple processed datasets found for {dataset_name} in investigation {investigation_id}")

    return result


def get_dataset_investigation(icat_client: ICATClient, logger: Logger, dataset_ctx: DatasetContext) -> Entity:
    investigation: Entity | None = None
    instrument: Entity = icat_client.search("Instrument",
                                            conditions={"name__eq": dataset_ctx.instrument},
                                            flatten_single=True)

    if not instrument:
        error_msg: str = f"Could not create dataset {dataset_ctx.name}, instrument {dataset_ctx.instrument} not found"
        logger.error(error_msg)
        raise InstrumentNotFound(error_msg)

    if dataset_ctx.investigation_id:
        investigation = icat_client.search("Investigation", conditions={"id__eq": dataset_ctx.investigation_id},
                                           flatten_single=True)
    else:
        investigation = icat_client.search("Investigation", conditions={"name__eq": dataset_ctx.investigation},
                                           flatten_single=True)

    if isinstance(investigation, list):
        logger.info(f"Multiple investigations found for {dataset_ctx.investigation}, refining search with dates")
        investigation = icat_client.search("Investigation", conditions={"name__eq": dataset_ctx.investigation,
                                                                        "startDate__lte": str(try_parse_datetime(
                                                                            dataset_ctx.start_date)),
                                                                        "endDate__gte": str(try_parse_datetime(
                                                                            dataset_ctx.end_date))},
                                           flatten_single=True
                                           )

        if isinstance(investigation, list):
            error_msg: str = f"Multiple colliding sessions found for investigation {dataset_ctx.investigation}, aborting ingestion"
            logger.error(error_msg)
            raise MultipleInvestigationsFound(error_msg)

    if not investigation:
        error_msg: str = f"Investigation {dataset_ctx.investigation if dataset_ctx.investigation else f'w/ id={dataset_ctx.investigation_id}'} not found"
        logger.error(error_msg)
        raise InvestigationNotFound(error_msg)

    if not dataset_ctx.investigation_id:
        if dataset_ctx.instrument.lower() not in [i.instrument.name.lower() for i in investigation.investigationInstruments]:
            error_msg: str = f"Dataset's {dataset_ctx.name} investigation ({investigation.name}/{investigation.visitId}) not associated with instrument {dataset_ctx.instrument}"
            logger.error(error_msg)
            raise InvestigationInstrumentMismatch(error_msg)

    logger.info(f"Investigation {investigation.name} with visitId {investigation.visitId} found")

    return investigation
