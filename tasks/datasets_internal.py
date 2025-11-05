from __future__ import absolute_import, unicode_literals

import logging
from enum import Enum
from pathlib import Path

from icat.entity import Entity

from helpers.dataclasses.dataset import DatasetContext
from helpers.integrations.icat_utils import ICATClient
from helpers.utils.icat_rollback_proxy import ICATRollbackContext

PARAMETER_STRING_VALUE_MAX_LENGTH: int = 4000


class DatasetsInternalTasks:

    def __init__(self, logger: logging.Logger = None):
        self.logger = logger

    def create_dataset_datafiles(self, icat_client: ICATClient, dataset_ctx: DatasetContext, dataset_id: int, *_args,
                                 **_kwargs) -> None:

        if not dataset_id:
            raise Exception("Dataset ID not received")

        with ICATRollbackContext(icat_client, self.logger) as rb:
            try:
                rb.dataset = icat_client.search("Dataset", conditions={"id__eq": dataset_id}, flatten_single=True)
                if not rb.dataset:
                    raise Exception("Dataset not found")

                for index, datafile in enumerate(dataset_ctx.datafiles):
                    new_datafile: Entity = icat_client.new("Datafile")
                    setattr(rb, f"new_datafile_{index}", new_datafile.copy())

                    path: Path = Path(datafile.location)

                    new_datafile.location = datafile.location
                    new_datafile.dataset = rb.dataset._obj
                    new_datafile.name = path.name
                    new_datafile.fileSize = path.stat().st_size
                    new_datafile.create()

                    setattr(rb, f"new_datafile_{index}", new_datafile)
                    self.logger.info(f"Created datafile {dataset_ctx.location} with id {new_datafile.id}")

            except Exception as e:
                rb.rollback_all(force_delete=True)

                error_msg: str = f"Error: {e}"
                self.logger.error(error_msg)
                raise Exception(error_msg)

    def create_dataset_parameters(self, icat_client: ICATClient, dataset_ctx: DatasetContext, dataset_id: int, *_args,
                                  **_kwargs) -> None:

        if not dataset_id:
            raise Exception("Dataset ID not received")

        with ICATRollbackContext(icat_client, self.logger) as rb:
            try:
                rb.dataset = icat_client.search("Dataset", conditions={"id__eq": dataset_id}, flatten_single=True)
                if not rb.dataset:
                    raise Exception("Dataset not found")

                for index, parameter in enumerate(dataset_ctx.parameters):
                    new_dataset_param: Entity = icat_client.new("DatasetParameter")
                    setattr(rb, f"new_dataset_param_{index}", new_dataset_param.copy())

                    value: str | int | float = parameter.value
                    name: str = parameter.name

                    parameter_type: Entity = icat_client.search("ParameterType", conditions={"name__eq": name},
                                                                flatten_single=True)
                    if not parameter_type:
                        raise Exception(f"Parameter type {name} not found in ICAT.")

                    new_dataset_param.dataset = rb.dataset._obj
                    new_dataset_param.type = parameter_type

                    match parameter_type.valueType:
                        case "DATE_AND_TIME":
                            new_dataset_param.dateTimeValue = value
                        case "NUMERIC":
                            new_dataset_param.numericValue = value
                        case "STRING":
                            if len(str(value)) > PARAMETER_STRING_VALUE_MAX_LENGTH:
                                raise Exception(f"Parameter value for {name} is too long, exceeds max limit.")
                            new_dataset_param.stringValue = value
                    new_dataset_param.create()

                    setattr(rb, f"new_dataset_param_{index}", new_dataset_param)

                self.logger.info(f"Created following parameters for dataset {dataset_ctx.parameters}")

            except Exception as e:
                rb.rollback_all(force_delete=True)

                error_msg: str = f"Error: {e}"
                self.logger.error(error_msg)
                raise Exception(error_msg)
