from __future__ import absolute_import, unicode_literals

import glob
import logging
import os
from pathlib import Path

from icat.entity import Entity

import globals_var
from helpers.dataclasses.dataset import DatasetContext, DatasetDatafileContext
from helpers.integrations.icat.extended_client import ICATClient
from helpers.utils.dataset import set_dataset_parameter, get_dataset_parameter
from helpers.utils.icat_rollback_proxy import ICATRollbackContext


class DatasetsInternalTasks:

    def __init__(self, logger: logging.Logger = None):
        self.logger = logger

    def create_dataset_datafiles(self, icat_client: ICATClient, dataset_ctx: DatasetContext, dataset_id: int, *_args,
                                 **_kwargs) -> None:


        ingestion_settings: dict = globals_var.ingestion_settings.get("dataset", {})

        if not dataset_id:
            raise Exception("Dataset ID not received")

        with ICATRollbackContext(icat_client, self.logger) as rb:
            try:
                rb.dataset = icat_client.search("Dataset", conditions={"id__eq": dataset_id}, flatten_single=True)
                if not rb.dataset:
                    raise Exception("Dataset not found")

                if not dataset_ctx.datafiles and ingestion_settings.get("automaticDatasetLocationIndex", False):
                    dataset_file_limit: int = ingestion_settings.get("maxDatafilesPerDataset", 30000)

                    for root, dirs, files in os.walk(dataset_ctx.location):
                        for file in files:
                            dataset_ctx.datafiles.append(DatasetDatafileContext(os.path.join(root, file)))

                            if file.startswith("."):
                                continue

                            if len(dataset_ctx.datafiles) >= dataset_file_limit:
                                break

                        if len(dataset_ctx.datafiles) >= dataset_file_limit:
                            break

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

                    param_value: str | int | float = parameter.value
                    param_type_name: str = parameter.name

                    new_dataset_param = get_dataset_parameter(icat_client, param_type_name, entity=rb.dataset._obj)
                    new_dataset_param = set_dataset_parameter(new_dataset_param, param_value)

                    setattr(rb, f"new_dataset_param_{index}", new_dataset_param)

                self.logger.info(f"Created following parameters for dataset {dataset_ctx.parameters}")

            except Exception as e:
                rb.rollback_all(force_delete=True)

                error_msg: str = f"Error: {e}"
                self.logger.error(error_msg)
                raise Exception(error_msg)
