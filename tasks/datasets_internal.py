from __future__ import absolute_import, unicode_literals

import logging
import os
from pathlib import Path

from icat.entity import Entity

import globals_var
from exceptions.dataset import DatasetValidationError, DatasetNotFound
from helpers.dataclasses.dataset import DatasetContext, DatasetDatafileContext
from helpers.integrations.icat.extended_client import ICATClient
from helpers.integrations.icat.icat_plus import ICATPlusClient
from helpers.static_settings import INPUT_DATASET_PARAMETER_NAME, INPUT_DATASET_IDS_PARAMETER_NAME, \
    OUTPUT_DATASET_IDS_PARAMETER_NAME, OUTPUT_DATASET_DATASETS_PARAMETER_NAME, OUTPUT_DATASET_NAMES_PARAMETER_NAME, \
    DATASET_PROCESSING_VERSION_PARAMETER_NAME, DATASET_PARAMETER_START_DATE_PARAMETER_NAME, \
    DATASET_PARAMETER_END_DATE_PARAMETER_NAME, DATASET_PARAMETER_RESOURCE_GALLERY_FILE_PATHS, \
    DATASET_PARAMETER_RESOURCE_GALLERY
from helpers.utils.dataset import set_dataset_parameter, get_dataset_parameter
from helpers.utils.icat_rollback_proxy import ICATRollbackContext


class DatasetsInternalTasks:

    def __init__(self, logger: logging.Logger = None):
        self.logger = logger

    def create_dataset_datafiles(self, icat_client: ICATClient, dataset_ctx: DatasetContext, dataset_id: int,
                                 is_duplicated: bool, *_args, **_kwargs) -> None:

        ingestion_settings: dict = globals_var.ingestion_settings.get("dataset", {})

        if not dataset_id:
            raise DatasetValidationError("Dataset ID not received")

        with ICATRollbackContext(icat_client, self.logger) as rb:
            try:
                rb.dataset = icat_client.search("Dataset", conditions={"id__eq": dataset_id}, flatten_single=True)
                if not rb.dataset:
                    raise DatasetNotFound("Dataset not found")

                if is_duplicated:
                    self.logger.info("Duplicated dataset found, removing existing files")
                    for datafile in rb.dataset.datafiles:
                        icat_client.delete(datafile)

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
                rb.rollback_all(force_delete=(not is_duplicated))

                error_msg: str = f"Error: {e}"
                self.logger.error(error_msg)
                raise e

    def __need_overwrite_dataset_metadata(self, icat_client: ICATClient, dataset: Entity,
                                          dataset_ctx: DatasetContext) -> bool:
        with ICATRollbackContext(icat_client, self.logger) as rb:
            try:
                rb.dataset = dataset
                rb.existing_proc_version_param = get_dataset_parameter(icat_client,
                                                                       DATASET_PROCESSING_VERSION_PARAMETER_NAME,
                                                                       entity=rb.dataset, create_if_missing=False)
                new_proc_version_param = next(
                    (x for x in dataset_ctx.parameters if x.name == DATASET_PROCESSING_VERSION_PARAMETER_NAME), None)

                if rb.existing_proc_version_param and new_proc_version_param:
                    # Overwrite dataset metadata with processing version
                    dataset_ctx.parameters.remove(new_proc_version_param)

                    new_processing_version = int(new_proc_version_param.value)
                    current_processing_version = int(
                        rb.existing_proc_version_param.numericValue if rb.existing_proc_version_param.type.valueType == "NUMERIC" else rb.existing_proc_version_param.stringValue)

                    if new_processing_version > current_processing_version:
                        self.logger.info(
                            f"Update metadata processed dataset id={rb.dataset.id}, new_version={new_processing_version} current_version={current_processing_version}")
                        rb.existing_proc_version_param = set_dataset_parameter(rb.existing_proc_version_param._obj,
                                                                               new_processing_version)
                        return True
                    else:
                        self.logger.info(
                            f"Dataset {rb.dataset.id} already processed with version {current_processing_version}, no update to metadata")
                        return False
                else:
                    # Overwrite dataset metadata dates
                    self.logger.info(
                        f"Update metadata processed dataset id={rb.dataset.id}, overwrite start and end dates")
                    rb.start_date_param = get_dataset_parameter(icat_client,
                                                                DATASET_PARAMETER_START_DATE_PARAMETER_NAME,
                                                                entity=rb.dataset, create_if_missing=False)
                    rb.end_date_param = get_dataset_parameter(icat_client,
                                                              DATASET_PARAMETER_END_DATE_PARAMETER_NAME,
                                                              entity=rb.dataset, create_if_missing=False)

                    new_start_date_param = next(
                        (x for x in dataset_ctx.parameters if x.name == DATASET_PARAMETER_START_DATE_PARAMETER_NAME),
                        None)
                    new_end_date_param = next(
                        (x for x in dataset_ctx.parameters if x.name == DATASET_PARAMETER_END_DATE_PARAMETER_NAME),
                        None)

                    if rb.start_date_param:
                        rb.start_date_param = set_dataset_parameter(rb.start_date_param._obj,
                                                                    new_start_date_param.stringValue)

                    if rb.end_date_param:
                        rb.end_date_param = set_dataset_parameter(rb.end_date_param._obj,
                                                                  new_end_date_param.stringValue)
                    return False

            except Exception as e:
                rb.rollback_all()

                error_msg: str = f"Error: {e}"
                self.logger.error(error_msg)
                raise e

    def create_dataset_parameters(self, icat_client: ICATClient, dataset_ctx: DatasetContext, dataset_id: int,
                                  is_duplicated: bool, *_args, **_kwargs) -> None:

        if not dataset_id:
            raise DatasetValidationError("Dataset ID not received")

        with ICATRollbackContext(icat_client, self.logger) as rb:
            try:
                rb.dataset = icat_client.search("Dataset", conditions={"id__eq": dataset_id}, flatten_single=True)
                if not rb.dataset:
                    raise DatasetNotFound("Dataset not found")

                if is_duplicated:
                    if not self.__need_overwrite_dataset_metadata(icat_client, rb.dataset._obj, dataset_ctx):
                        return

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
                rb.rollback_all(force_delete=(not is_duplicated))

                error_msg: str = f"Error: {e}"
                self.logger.error(error_msg)
                raise e

    def __link_output_dataset_to_input_dataset(self, icat_client: ICATClient, raw_dataset: Entity,
                                               processed_datasets: list[Entity]) -> None:
        with ICATRollbackContext(icat_client, self.logger) as rb:
            try:
                rb.output_dataset_ids_param = get_dataset_parameter(icat_client, OUTPUT_DATASET_IDS_PARAMETER_NAME,
                                                                    entity=raw_dataset)
                output_dataset_ids_value = f"{rb.output_dataset_ids_param._obj.stringValue or ''} {' '.join(str(i.id) for i in processed_datasets)}"
                rb.output_dataset_ids_param = set_dataset_parameter(rb.output_dataset_ids_param._obj,
                                                                    output_dataset_ids_value.strip())

                rb.output_dataset_param = get_dataset_parameter(icat_client, OUTPUT_DATASET_DATASETS_PARAMETER_NAME,
                                                                entity=raw_dataset)
                output_dataset_value = f"{rb.output_dataset_param._obj.stringValue or ''} {' '.join(i.location for i in processed_datasets)}"
                rb.output_dataset_param = set_dataset_parameter(rb.output_dataset_param._obj,
                                                                output_dataset_value.strip())

                rb.output_dataset_names_param = get_dataset_parameter(icat_client, OUTPUT_DATASET_NAMES_PARAMETER_NAME,
                                                                      entity=raw_dataset)
                output_dataset_names_value = f"{rb.output_dataset_names_param._obj.stringValue or ''} {' '.join(i.name for i in processed_datasets)}"
                rb.output_dataset_names_param = set_dataset_parameter(rb.output_dataset_names_param._obj,
                                                                      output_dataset_names_value.strip())

            except Exception as e:
                rb.rollback_all(force_delete=True)

                error_msg: str = f"Error: {e}"
                self.logger.error(error_msg)
                raise e

    def raw_dataset_linkage(self, icat_client: ICATClient, dataset_id: int, *_args,
                            **_kwargs) -> None:
        """
        Link a raw dataset to its input_datasets
        """
        if not dataset_id:
            raise DatasetValidationError("Dataset ID not received")

        with ICATRollbackContext(icat_client, self.logger) as rb:
            try:
                rb.dataset = icat_client.search("Dataset", conditions={"id__eq": dataset_id}, flatten_single=True)
                if not rb.dataset:
                    raise DatasetNotFound("Dataset not found")

                investigation = rb.dataset.investigation

                processed_datasets_params = icat_client.search("DatasetParameter", flatten_single=False, conditions={
                    "dataset.investigation.id__eq": investigation.id,
                    "type.name__eq": INPUT_DATASET_PARAMETER_NAME,
                    "stringValue__eq": rb.dataset.location
                })
                if not processed_datasets_params:
                    return

                processed_datasets = [i.dataset for i in processed_datasets_params]

                self.logger.info(
                    f"Found {len(processed_datasets)} datasets for which input dataset parameter is location of dataset={dataset_id}")

                for index, dataset in enumerate(processed_datasets):
                    processed_dataset_input_ids_param = get_dataset_parameter(icat_client,
                                                                              INPUT_DATASET_IDS_PARAMETER_NAME,
                                                                              entity=dataset)
                    setattr(rb, f"processed_dataset_input_ids_param_{index}", processed_dataset_input_ids_param)

                    processed_dataset_input_ids_param = set_dataset_parameter(processed_dataset_input_ids_param,
                                                                              str(rb.dataset.id))

                    setattr(rb, f"processed_dataset_input_ids_param_{index}", processed_dataset_input_ids_param)

                self.__link_output_dataset_to_input_dataset(icat_client, rb.dataset._obj, processed_datasets)

            except Exception as e:
                rb.rollback_all(force_delete=True)

                error_msg: str = f"Error: {e}"
                self.logger.error(error_msg)
                raise e

    def processed_dataset_linkage(self, icat_client: ICATClient, dataset_id: int, *_args,
                                  **_kwargs) -> None:
        """
        Link a processed dataset to its input_datasets
        """
        if not dataset_id:
            raise DatasetValidationError("Dataset ID not received")

        with ICATRollbackContext(icat_client, self.logger) as rb:
            try:
                rb.dataset = icat_client.search("Dataset", conditions={"id__eq": dataset_id}, flatten_single=True)
                if not rb.dataset:
                    raise DatasetNotFound("Dataset not found")

                input_dataset_param = get_dataset_parameter(icat_client, INPUT_DATASET_PARAMETER_NAME,
                                                            create_if_missing=False,
                                                            entity=rb.dataset._obj)

                if not input_dataset_param:
                    return

                input_dataset_locations = input_dataset_param.stringValue.split(",")

                raw_datasets = icat_client.search("Dataset", conditions={"location__in": input_dataset_locations},
                                                  flatten_single=False)
                if not raw_datasets:
                    self.logger.warning(f"No raw datasets found for dataset {dataset_id}")
                    return

                self.logger.info(
                    f"Informed {len(input_dataset_locations)} input datasets for dataset={dataset_id}, found {len(raw_datasets)} raw datasets in ICAT")

                rb.input_dataset_ids_param = get_dataset_parameter(icat_client, INPUT_DATASET_IDS_PARAMETER_NAME,
                                                                   entity=rb.dataset._obj)
                raw_datasets_ids = " ".join(str(i.id) for i in raw_datasets)
                rb.input_dataset_ids_param = set_dataset_parameter(rb.input_dataset_ids_param._obj, raw_datasets_ids)
                self.logger.info(f"Linked following raw datasets to dataset {dataset_id}: {raw_datasets_ids}")

                for raw_dataset in raw_datasets:
                    self.__link_output_dataset_to_input_dataset(icat_client, raw_dataset, [rb.dataset._obj])

            except Exception as e:
                rb.rollback_all(force_delete=True)

                error_msg: str = f"Error: {e}"
                self.logger.error(error_msg)
                raise e

    def create_dataset_gallery(self, client: ICATPlusClient, icat_client: ICATClient, dataset_ctx: DatasetContext,
                               dataset_id: int,
                               *_args, **_kwargs) -> None:
        ingestion_settings: dict = globals_var.ingestion_settings.get("dataset", {})

        if not dataset_id:
            raise DatasetValidationError("Dataset ID not received")

        with ICATRollbackContext(icat_client, self.logger) as rb:
            try:
                rb.dataset = icat_client.search("Dataset", conditions={"id__eq": dataset_id}, flatten_single=True)
                if not rb.dataset:
                    raise DatasetNotFound("Dataset not found")

                dataset_resources_gallery_file_paths_param = get_dataset_parameter(icat_client,
                                                                                   DATASET_PARAMETER_RESOURCE_GALLERY_FILE_PATHS,
                                                                                   create_if_missing=False,
                                                                                   entity=rb.dataset._obj)
                file_paths: list = []
                if dataset_resources_gallery_file_paths_param and dataset_resources_gallery_file_paths_param.stringValue:
                    file_paths: list[str] = dataset_resources_gallery_file_paths_param.stringValue.split(",")

                    self.logger.info(
                        f"Processing gallery for dataset {dataset_ctx.name}, given {len(file_paths)} files")

                else:
                    self.logger.info(
                        f"No ResourcesGalleryFilePaths parameter found for dataset {dataset_ctx.name}, checking default location")

                    location: Path = Path(dataset_ctx.location)

                    if location.exists() and location.is_dir():
                        location = location / ingestion_settings.get("galleryFolderName", "gallery")
                        if location.exists() and location.is_dir():

                            allowed_extensions: list = ingestion_settings.get("galleryAcceptedUploadTypes", [])
                            file_paths = [
                                f for f in location.rglob("*")
                                if f.is_file() and f.suffix in allowed_extensions
                            ]

                            if not file_paths:
                                self.logger.info(f"No files found in gallery folder for dataset {dataset_ctx.name}")
                                return
                        else:
                            self.logger.info("No gallery folder found in dataset location, skipping gallery upload")
                            return

                self.logger.info(
                    f"Processing gallery for dataset {dataset_ctx.name}, found {len(file_paths)} files.")
                if file_paths:
                    resource_ids: str = client.upload_gallery_files(file_paths, dataset_ctx)

                    if resource_ids:
                        rb.resources_gallery_file_paths_param = get_dataset_parameter(icat_client,
                                                                                      DATASET_PARAMETER_RESOURCE_GALLERY_FILE_PATHS,
                                                                                      entity=rb.dataset._obj)
                        rb.resources_gallery_file_paths_param = set_dataset_parameter(
                            rb.resources_gallery_file_paths_param._obj, ",".join(str(i) for i in file_paths))
                        self.logger.info(
                            f"Set dataset parameter {DATASET_PARAMETER_RESOURCE_GALLERY_FILE_PATHS} with resource IDs: {resource_ids}")

                        rb.resources_gallery_param = get_dataset_parameter(icat_client,
                                                                           DATASET_PARAMETER_RESOURCE_GALLERY,
                                                                           entity=rb.dataset._obj)
                        rb.resources_gallery_param = set_dataset_parameter(
                            rb.resources_gallery_param._obj, resource_ids)
                        self.logger.info(
                            f"Set dataset parameter {DATASET_PARAMETER_RESOURCE_GALLERY} with resource IDs: {resource_ids}")

            except Exception as e:
                rb.rollback_all(force_delete=True)
                error_msg: str = f"Error: {e}"
                self.logger.error(error_msg)
                raise e
