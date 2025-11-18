from __future__ import absolute_import, unicode_literals

import logging
from pathlib import Path

from icat.entity import Entity

from helpers.dataclasses.dataset import DatasetContext
from helpers.integrations.icat.extended_client import ICATClient
from helpers.static_settings import DATASET_NAME_PARAMETER, DATASET_FILE_COUNT_PARAMETER, DATASET_VOLUME_PARAMETER, \
    DATASET_ELAPSE_TIME_PARAMETER, INVESTIGATION_DATASET_COUNT_PARAMETER, \
    INVESTIGATION_ACQUISITION_DATASET_COUNT_PARAMETER, \
    RAW_DATASET_TYPE_NAME, \
    INVESTIGATION_SAMPLE_COUNT_PARAMETER, INVESTIGATION_VOLUME_PARAMETER, INVESTIGATION_ACQUISITION_VOLUME_PARAMETER, \
    PROCESSED_DATASET_TYPE_NAME, INVESTIGATION_PROCESSED_DATASET_COUNT_PARAMETER, \
    INVESTIGATION_ELAPSE_TIME_PARAMETER, INVESTIGATION_FILE_COUNT_PARAMETER, \
    INVESTIGATION_ACQUISITION_FILE_COUNT_PARAMETER, INVESTIGATION_PROCESSED_FILE_COUNT_PARAMETER
from helpers.utils.dataset import set_dataset_parameter, get_dataset_parameter
from helpers.utils.icat_rollback_proxy import ICATRollbackContext
from helpers.utils.investigation import set_investigation_parameter, get_investigation_parameter
from helpers.utils.parameters import get_parameter_type


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

                    param_value: str | int | float = parameter.value
                    param_type_name: str = parameter.name

                    new_dataset_param = get_dataset_parameter(icat_client, dataset_id, param_type_name)
                    new_dataset_param = set_dataset_parameter(new_dataset_param, param_value)

                    setattr(rb, f"new_dataset_param_{index}", new_dataset_param)

                self.logger.info(f"Created following parameters for dataset {dataset_ctx.parameters}")

            except Exception as e:
                rb.rollback_all(force_delete=True)

                error_msg: str = f"Error: {e}"
                self.logger.error(error_msg)
                raise Exception(error_msg)

    def update_dataset_statistics(self, icat_client: ICATClient, dataset_id: int, *_args, **_kwargs) -> None:

        if not dataset_id:
            raise Exception("Dataset ID not received")

        with ICATRollbackContext(icat_client, self.logger) as rb:
            try:
                rb.dataset = icat_client.search("Dataset", conditions={"id__eq": dataset_id}, flatten_single=True,
                                                includes=["datafiles"])
                if not rb.dataset:
                    raise Exception("Dataset not found")

                rb.dataset_name_param = get_dataset_parameter(icat_client, dataset_id, DATASET_NAME_PARAMETER)
                rb.dataset_name_param = set_dataset_parameter(rb.dataset_name_param._obj, rb.dataset.name)

                rb.file_count_param = get_dataset_parameter(icat_client, dataset_id, DATASET_FILE_COUNT_PARAMETER)
                rb.file_count_param = set_dataset_parameter(rb.file_count_param._obj, len(rb.dataset.datafiles))

                rb.volume_param = get_dataset_parameter(icat_client, dataset_id, DATASET_VOLUME_PARAMETER)
                rb.volume_param = set_dataset_parameter(rb.volume_param._obj,
                                                        sum(i.fileSize for i in rb.dataset.datafiles))

                if rb.dataset.startDate is not None:
                    if rb.dataset.endDate is not None:
                        elapsed_time: float = int((rb.dataset.endDate - rb.dataset.startDate).total_seconds())

                        rb.elapsed_time_param = get_dataset_parameter(icat_client, dataset_id,
                                                                      DATASET_ELAPSE_TIME_PARAMETER)
                        rb.elapsed_time_param = set_dataset_parameter(rb.elapsed_time_param._obj, elapsed_time)

            except Exception as e:
                rb.rollback_all(force_delete=True)

                error_msg: str = f"Error: {e}"
                self.logger.error(error_msg)
                raise Exception(error_msg)

    def update_investigation_statistics(self, icat_client: ICATClient, investigation_name: str, *_args,
                                        **_kwargs) -> None:
        # TODO: This query takes some time to resolve in test, check if there is a better way to do this after testing in prod
        investigation: Entity = icat_client.search("Investigation", conditions={"name__eq": investigation_name},
                                                   includes=["datasets", "datasets.type", "samples",
                                                             "datasets.parameters", "datasets.parameters.type"],
                                                   flatten_single=True)

        with ICATRollbackContext(icat_client, self.logger) as rb:
            try:
                # Total number of datasets
                rb.dataset_count_param = get_investigation_parameter(icat_client, investigation_name,
                                                                     INVESTIGATION_DATASET_COUNT_PARAMETER)
                rb.dataset_count_param = set_investigation_parameter(rb.dataset_count_param._obj,
                                                                     len(investigation.datasets))

                # Total number of raw datasets
                rb.acq_dataset_count_param = get_investigation_parameter(icat_client, investigation_name,
                                                                         INVESTIGATION_ACQUISITION_DATASET_COUNT_PARAMETER)
                rb.acq_dataset_count_param = set_investigation_parameter(rb.acq_dataset_count_param._obj,
                                                                         len([i for i in investigation.datasets if
                                                                              i.type.name == RAW_DATASET_TYPE_NAME]))

                # Total number of processed datasets
                rb.proc_dataset_count_param = get_investigation_parameter(icat_client, investigation_name,
                                                                          INVESTIGATION_PROCESSED_DATASET_COUNT_PARAMETER)
                rb.proc_dataset_count_param = set_investigation_parameter(rb.proc_dataset_count_param._obj,
                                                                          len([i for i in investigation.datasets if
                                                                               i.type.name == PROCESSED_DATASET_TYPE_NAME]))

                # Total number of samples
                rb.sample_count_param = get_investigation_parameter(icat_client, investigation_name,
                                                                    INVESTIGATION_SAMPLE_COUNT_PARAMETER)
                rb.sample_count_param = set_investigation_parameter(rb.sample_count_param._obj,
                                                                    len(investigation.samples))

                # Total volume of all datasets
                rb.inv_vol_param = get_investigation_parameter(icat_client, investigation_name,
                                                               INVESTIGATION_VOLUME_PARAMETER)

                dataset_vol_param_type: Entity = get_parameter_type(icat_client, DATASET_VOLUME_PARAMETER)

                vol_params: filter = filter(
                    lambda x: x.type == dataset_vol_param_type, (j for i in investigation.datasets for j in
                                                                 i.parameters))

                inv_vol: int = sum(int(p.stringValue) if p.stringValue else p.numericValue for p in vol_params)

                rb.inv_vol_param = set_investigation_parameter(rb.inv_vol_param._obj, inv_vol)

                # Total volume of all raw datasets
                rb.acq_vol_param = get_investigation_parameter(icat_client, investigation_name,
                                                               INVESTIGATION_ACQUISITION_VOLUME_PARAMETER)

                acq_vol_params: filter = filter(
                    lambda x: x.type == dataset_vol_param_type, (j for i in investigation.datasets for j in
                                                                 i.parameters if i.type.name == RAW_DATASET_TYPE_NAME))

                inv_acq_vol: int = sum(int(p.stringValue) if p.stringValue else p.numericValue for p in acq_vol_params)

                rb.acq_vol_param = set_investigation_parameter(rb.acq_vol_param._obj, inv_acq_vol)

                # Total elapsed time
                rb.inv_elapsed_time_param = get_investigation_parameter(icat_client, investigation_name,
                                                                        INVESTIGATION_ELAPSE_TIME_PARAMETER)

                elapsed_time_param_type: Entity = get_parameter_type(icat_client, DATASET_ELAPSE_TIME_PARAMETER)
                elapsed_time_params: filter = filter(
                    lambda x: x.type == elapsed_time_param_type, (j for i in investigation.datasets for j in
                                                                  i.parameters))

                elapsed_time: int = sum(
                    int(p.stringValue) if p.stringValue else p.numericValue for p in elapsed_time_params)

                rb.inv_elapsed_time_param = set_investigation_parameter(rb.inv_elapsed_time_param._obj, elapsed_time)

                # Total number of files
                rb.file_count_param = get_investigation_parameter(icat_client, investigation_name,
                                                                  INVESTIGATION_FILE_COUNT_PARAMETER)

                file_count_param_type: Entity = get_parameter_type(icat_client, DATASET_FILE_COUNT_PARAMETER)
                file_count_params: filter = filter(
                    lambda x: x.type == file_count_param_type, (j for i in investigation.datasets for j in
                                                                i.parameters))

                file_count: int = sum(
                    int(p.stringValue) if p.stringValue else p.numericValue for p in file_count_params)

                rb.file_count_param = set_investigation_parameter(rb.file_count_param._obj, file_count)

                # Total number of raw files
                rb.acq_file_count_param = get_investigation_parameter(icat_client, investigation_name,
                                                                      INVESTIGATION_ACQUISITION_FILE_COUNT_PARAMETER)
                acq_file_count_params: filter = filter(
                    lambda x: x.type == file_count_param_type, (j for i in investigation.datasets for j in
                                                                i.parameters if i.type.name == RAW_DATASET_TYPE_NAME))

                acq_file_count: int = sum(
                    int(p.stringValue) if p.stringValue else p.numericValue for p in acq_file_count_params)

                rb.acq_file_count_param = set_investigation_parameter(rb.acq_file_count_param._obj, acq_file_count)

                # Total number of processed files
                rb.proc_file_count_param = get_investigation_parameter(icat_client, investigation_name,
                                                                       INVESTIGATION_PROCESSED_FILE_COUNT_PARAMETER)
                proc_file_count_params: filter = filter(
                    lambda x: x.type == file_count_param_type, (j for i in investigation.datasets for j in
                                                                i.parameters if
                                                                i.type.name == PROCESSED_DATASET_TYPE_NAME))

                proc_file_count: int = sum(
                    int(p.stringValue) if p.stringValue else p.numericValue for p in proc_file_count_params)

                rb.proc_file_count_param = set_investigation_parameter(rb.proc_file_count_param._obj, proc_file_count)

            except Exception as e:
                rb.rollback_all(force_delete=True)

                error_msg: str = f"Error: {e}"
                self.logger.error(error_msg)
                raise Exception(error_msg)

    def update_sample_statistics(self, icat_client: ICATClient, investigation_name: str, *_args,
                                        **_kwargs) -> None:
        # TODO: This query takes some time to resolve in test, check if there is a better way to do this after testing in prod
        investigation: Entity = icat_client.search("Investigation", conditions={"name__eq": investigation_name},
                                                   includes=["datasets", "datasets.type", "samples",
                                                             "datasets.parameters", "datasets.parameters.type"],
                                                   flatten_single=True)

        with ICATRollbackContext(icat_client, self.logger) as rb:
            try:
                # Total number of datasets
                rb.dataset_count_param = get_investigation_parameter(icat_client, investigation_name,
                                                                     INVESTIGATION_DATASET_COUNT_PARAMETER)
                rb.dataset_count_param = set_investigation_parameter(rb.dataset_count_param._obj,
                                                                     len(investigation.datasets))



            except Exception as e:
                rb.rollback_all(force_delete=True)

                error_msg: str = f"Error: {e}"
                self.logger.error(error_msg)
                raise Exception(error_msg)
