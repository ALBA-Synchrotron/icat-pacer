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
    INVESTIGATION_ACQUISITION_FILE_COUNT_PARAMETER, INVESTIGATION_PROCESSED_FILE_COUNT_PARAMETER, \
    SAMPLE_DATASET_COUNT_PARAMETER, SAMPLE_ACQUISITION_DATASET_COUNT_PARAMETER, \
    SAMPLE_PROCESSED_DATASET_COUNT_PARAMETER, SAMPLE_FILE_COUNT_PARAMETER, SAMPLE_ACQUISITION_FILE_COUNT_PARAMETER, \
    SAMPLE_PROCESSED_FILE_COUNT_PARAMETER, INVESTIGATION_PROCESSED_VOLUME_PARAMETER, SAMPLE_VOLUME_PARAMETER, \
    SAMPLE_ACQUISITION_VOLUME_PARAMETER, SAMPLE_PROCESSED_VOLUME_PARAMETER
from helpers.utils.dataset import set_dataset_parameter, get_dataset_parameter
from helpers.utils.icat_rollback_proxy import ICATRollbackContext
from helpers.utils.investigation import set_investigation_parameter, get_investigation_parameter
from helpers.utils.parameters import get_parameter_type
from helpers.utils.sample import get_sample_parameter, set_sample_parameter


class InternalStatisticsTasks:

    def __init__(self, logger: logging.Logger = None):
        self.logger = logger

    def update_dataset_statistics(self, icat_client: ICATClient, dataset_id: int, *_args, **_kwargs) -> None:

        if not dataset_id:
            raise Exception("Dataset ID not received")

        with ICATRollbackContext(icat_client, self.logger) as rb:
            try:
                rb.dataset = icat_client.search("Dataset", conditions={"id__eq": dataset_id}, flatten_single=True)
                if not rb.dataset:
                    raise Exception("Dataset not found")

                # Dataset name
                rb.dataset_name_param = get_dataset_parameter(icat_client, DATASET_NAME_PARAMETER,
                                                              entity=rb.dataset._obj)
                rb.dataset_name_param = set_dataset_parameter(rb.dataset_name_param._obj, rb.dataset.name)
                self.logger.debug("Updated dataset statistic: Dataset name")

                # Dataset file count
                rb.file_count_param = get_dataset_parameter(icat_client, DATASET_FILE_COUNT_PARAMETER,
                                                            entity=rb.dataset._obj)
                rb.file_count_param = set_dataset_parameter(rb.file_count_param._obj, rb.dataset.count("datafiles"))
                self.logger.debug("Updated dataset statistic: Dataset file count")

                # Dataset file volume
                rb.volume_param = get_dataset_parameter(icat_client, DATASET_VOLUME_PARAMETER, entity=rb.dataset._obj)
                rb.volume_param = set_dataset_parameter(rb.volume_param._obj,
                                                        sum(i.fileSize for i in rb.dataset.datafiles))
                self.logger.debug("Updated dataset statistic: Dataset file volume")

                if rb.dataset.startDate is not None:
                    if rb.dataset.endDate is not None:
                        elapsed_time: float = int((rb.dataset.endDate - rb.dataset.startDate).total_seconds())

                        rb.elapsed_time_param = get_dataset_parameter(icat_client,
                                                                      DATASET_ELAPSE_TIME_PARAMETER,
                                                                      entity=rb.dataset._obj)
                        rb.elapsed_time_param = set_dataset_parameter(rb.elapsed_time_param._obj, elapsed_time)

                self.logger.info(f"Updated dataset statistics for dataset={dataset_id}")
            except Exception as e:
                rb.rollback_all(force_delete=True)

                error_msg: str = f"Error: {e}"
                self.logger.error(error_msg)
                raise Exception(error_msg)

    def update_investigation_statistics(self, icat_client: ICATClient, investigation_name: str, dataset_id: int, *_args,
                                        **_kwargs) -> None:
        investigation: Entity = icat_client.search("Investigation", conditions={"name__eq": investigation_name},
                                                   flatten_single=True)

        if not dataset_id:
            raise Exception("Dataset ID not received")

        with ICATRollbackContext(icat_client, self.logger) as rb:
            rb.dataset = icat_client.search("Dataset", conditions={"id__eq": dataset_id}, flatten_single=True)
            if not rb.dataset:
                raise Exception("Dataset not found")

            try:
                # Total number of datasets
                rb.dataset_count_param = get_investigation_parameter(icat_client,
                                                                     INVESTIGATION_DATASET_COUNT_PARAMETER,
                                                                     entity=investigation)
                rb.dataset_count_param = set_investigation_parameter(rb.dataset_count_param._obj,
                                                                     len(investigation.datasets))
                self.logger.debug("Updated investigation statistic: Total number of datasets")

                # Total number of raw datasets
                rb.acq_dataset_count_param = get_investigation_parameter(icat_client,
                                                                         INVESTIGATION_ACQUISITION_DATASET_COUNT_PARAMETER,
                                                                         entity=investigation)
                rb.acq_dataset_count_param = set_investigation_parameter(rb.acq_dataset_count_param._obj,
                                                                         sum(1 for i in investigation.datasets if
                                                                             i.type.name == RAW_DATASET_TYPE_NAME)
                                                                         )
                self.logger.debug("Updated investigation statistic: Total number of raw datasets")

                # Total number of processed datasets
                rb.proc_dataset_count_param = get_investigation_parameter(icat_client,
                                                                          INVESTIGATION_PROCESSED_DATASET_COUNT_PARAMETER,
                                                                          entity=investigation)
                rb.proc_dataset_count_param = set_investigation_parameter(rb.proc_dataset_count_param._obj,
                                                                          sum(1 for i in investigation.datasets if
                                                                              i.type.name == PROCESSED_DATASET_TYPE_NAME))
                self.logger.debug("Updated investigation statistic: Total number of processed datasets")

                # Total number of samples
                rb.sample_count_param = get_investigation_parameter(icat_client,
                                                                    INVESTIGATION_SAMPLE_COUNT_PARAMETER,
                                                                    entity=investigation)
                rb.sample_count_param = set_investigation_parameter(rb.sample_count_param._obj,
                                                                    investigation.count("samples"))
                self.logger.debug("Updated investigation statistic: Total number of samples")

                # Total volume of all datasets
                rb.inv_vol_param = get_investigation_parameter(icat_client,
                                                               INVESTIGATION_VOLUME_PARAMETER,
                                                               entity=investigation)

                dataset_vol_param_type: Entity = get_parameter_type(icat_client, DATASET_VOLUME_PARAMETER)

                vol_params: filter = filter(
                    lambda x: x.type == dataset_vol_param_type, (j for i in investigation.datasets for j in
                                                                 i.parameters))

                inv_vol: int = sum(int(p.stringValue) if p.stringValue else p.numericValue for p in vol_params)

                rb.inv_vol_param = set_investigation_parameter(rb.inv_vol_param._obj, inv_vol)
                self.logger.debug("Updated investigation statistic: Total volume of all datasets")

                # Total volume of all raw datasets
                rb.acq_vol_param = get_investigation_parameter(icat_client,
                                                               INVESTIGATION_ACQUISITION_VOLUME_PARAMETER,
                                                               entity=investigation)

                acq_vol_params: filter = filter(
                    lambda x: x.type == dataset_vol_param_type, (j for i in investigation.datasets for j in
                                                                 i.parameters if i.type.name == RAW_DATASET_TYPE_NAME))

                inv_acq_vol: int = sum(int(p.stringValue) if p.stringValue else p.numericValue for p in acq_vol_params)

                rb.acq_vol_param = set_investigation_parameter(rb.acq_vol_param._obj, inv_acq_vol)
                self.logger.debug("Updated investigation statistic: Total volume of all raw datasets")

                # Total volume of all processed datasets
                rb.proc_vol_param = get_investigation_parameter(icat_client,
                                                                INVESTIGATION_PROCESSED_VOLUME_PARAMETER,
                                                                entity=investigation)

                proc_vol_params: filter = filter(
                    lambda x: x.type == dataset_vol_param_type, (j for i in investigation.datasets for j in
                                                                 i.parameters if
                                                                 i.type.name == PROCESSED_DATASET_TYPE_NAME))

                inv_proc_vol: int = sum(
                    int(p.stringValue) if p.stringValue else p.numericValue for p in proc_vol_params)

                rb.proc_vol_param = set_investigation_parameter(rb.proc_vol_param._obj, inv_proc_vol)
                self.logger.debug("Updated investigation statistic: Total volume of all processed datasets")

                # Total elapsed time
                rb.inv_elapsed_time_param = get_investigation_parameter(icat_client,
                                                                        INVESTIGATION_ELAPSE_TIME_PARAMETER,
                                                                        entity=investigation)

                elapsed_time_param_type: Entity = get_parameter_type(icat_client, DATASET_ELAPSE_TIME_PARAMETER)
                elapsed_time_params: filter = filter(
                    lambda x: x.type == elapsed_time_param_type, (j for i in investigation.datasets for j in
                                                                  i.parameters))

                elapsed_time: int = sum(
                    int(p.stringValue) if p.stringValue else p.numericValue for p in elapsed_time_params)

                rb.inv_elapsed_time_param = set_investigation_parameter(rb.inv_elapsed_time_param._obj, elapsed_time)
                self.logger.debug("Updated investigation statistic: Total elapsed time")

                # Total number of files
                rb.file_count_param = get_investigation_parameter(icat_client,
                                                                  INVESTIGATION_FILE_COUNT_PARAMETER,
                                                                  entity=investigation)

                file_count_param_type: Entity = get_parameter_type(icat_client, DATASET_FILE_COUNT_PARAMETER)
                file_count_params: filter = filter(
                    lambda x: x.type == file_count_param_type, (j for i in investigation.datasets for j in
                                                                i.parameters))

                file_count: int = sum(
                    int(p.stringValue) if p.stringValue else p.numericValue for p in file_count_params)

                rb.file_count_param = set_investigation_parameter(rb.file_count_param._obj, file_count)
                self.logger.debug("Updated investigation statistic: Total number of files")

                # Total number of raw files
                rb.acq_file_count_param = get_investigation_parameter(icat_client,
                                                                      INVESTIGATION_ACQUISITION_FILE_COUNT_PARAMETER,
                                                                      entity=investigation)
                acq_file_count_params: filter = filter(
                    lambda x: x.type == file_count_param_type, (j for i in investigation.datasets for j in
                                                                i.parameters if i.type.name == RAW_DATASET_TYPE_NAME))

                acq_file_count: int = sum(
                    int(p.stringValue) if p.stringValue else p.numericValue for p in acq_file_count_params)

                rb.acq_file_count_param = set_investigation_parameter(rb.acq_file_count_param._obj, acq_file_count)
                self.logger.debug("Updated investigation statistic: Total number of raw files")

                # Total number of processed files
                rb.proc_file_count_param = get_investigation_parameter(icat_client,
                                                                       INVESTIGATION_PROCESSED_FILE_COUNT_PARAMETER,
                                                                       entity=investigation)
                proc_file_count_params: filter = filter(
                    lambda x: x.type == file_count_param_type, (j for i in investigation.datasets for j in
                                                                i.parameters if
                                                                i.type.name == PROCESSED_DATASET_TYPE_NAME))

                proc_file_count: int = sum(
                    int(p.stringValue) if p.stringValue else p.numericValue for p in proc_file_count_params)

                rb.proc_file_count_param = set_investigation_parameter(rb.proc_file_count_param._obj, proc_file_count)
                self.logger.debug("Updated investigation statistic: Total number of processed files")

                self.logger.info(f"Updated investigation statistics for investigation={investigation_name}")
            except Exception as e:
                rb.rollback_all(force_delete=True)

                error_msg: str = f"Error: {e}"
                self.logger.error(error_msg)
                raise Exception(error_msg)

    def update_sample_statistics(self, icat_client: ICATClient, investigation_name: str, dataset_id: int, *_args,
                                 **_kwargs) -> None:
        if not dataset_id:
            raise Exception("Dataset ID not received")

        with ICATRollbackContext(icat_client, self.logger) as rb:
            rb.dataset = icat_client.search("Dataset", conditions={"id__eq": dataset_id}, flatten_single=True)
            dataset_sample = rb.dataset.sample
            if not rb.dataset:
                raise Exception("Dataset not found")

            try:
                # Total number of datasets referencing sample
                rb.sample_dataset_count_param = get_sample_parameter(icat_client,
                                                                     SAMPLE_DATASET_COUNT_PARAMETER,
                                                                     entity=dataset_sample)
                rb.sample_dataset_count_param = set_sample_parameter(rb.sample_dataset_count_param._obj,
                                                                     dataset_sample.count("datasets"))
                self.logger.debug("Updated sample statistic: Total number of datasets referencing sample")

                # Total number of raw datasets referencing sample
                rb.sample_acq_dataset_count_param = get_sample_parameter(icat_client,
                                                                         SAMPLE_ACQUISITION_DATASET_COUNT_PARAMETER,
                                                                         entity=dataset_sample)
                rb.sample_acq_dataset_count_param = set_sample_parameter(rb.sample_acq_dataset_count_param._obj,
                                                                         sum(1 for i in dataset_sample.datasets if
                                                                             i.type.name == RAW_DATASET_TYPE_NAME))
                self.logger.debug("Updated sample statistic: Total number of raw datasets referencing sample")

                # Total number of processed datasets referencing sample
                rb.sample_proc_dataset_count_param = get_sample_parameter(icat_client,
                                                                          SAMPLE_PROCESSED_DATASET_COUNT_PARAMETER,
                                                                          entity=dataset_sample)
                rb.sample_proc_dataset_count_param = set_sample_parameter(rb.sample_proc_dataset_count_param._obj,
                                                                          sum(1 for i in dataset_sample.datasets if
                                                                              i.type.name == PROCESSED_DATASET_TYPE_NAME))
                self.logger.debug("Updated sample statistic: Total number of processed datasets referencing sample")

                # Total number of files referencing sample
                rb.sample_file_count_param = get_sample_parameter(icat_client,
                                                                  SAMPLE_FILE_COUNT_PARAMETER,
                                                                  entity=dataset_sample)

                file_count_param_type: Entity = get_parameter_type(icat_client, DATASET_FILE_COUNT_PARAMETER)
                file_count_params: filter = filter(
                    lambda x: x.type == file_count_param_type, (j for i in dataset_sample.datasets for j in
                                                                i.parameters))

                sample_file_count: int = sum(
                    int(p.stringValue) if p.stringValue else p.numericValue for p in file_count_params)

                rb.sample_file_count_param = set_sample_parameter(rb.sample_file_count_param._obj,
                                                                  sample_file_count)
                self.logger.debug("Updated sample statistic: Total number of files referencing sample")

                # Total number of raw files referencing sample
                rb.sample_acq_file_count_param = get_sample_parameter(icat_client,
                                                                      SAMPLE_ACQUISITION_FILE_COUNT_PARAMETER,
                                                                      entity=dataset_sample)

                sample_acq_file_count_params: filter = filter(
                    lambda x: x.type == file_count_param_type, (j for i in dataset_sample.datasets for j in
                                                                i.parameters if i.type.name == RAW_DATASET_TYPE_NAME))

                sample_acq_file_count: int = sum(
                    int(p.stringValue) if p.stringValue else p.numericValue for p in sample_acq_file_count_params)

                rb.sample_acq_file_count_param = set_sample_parameter(rb.sample_acq_file_count_param._obj,
                                                                      sample_acq_file_count)
                self.logger.debug("Updated sample statistic: Total number of raw files referencing sample")

                # Total number of processed files referencing sample
                rb.sample_proc_file_count_param = get_sample_parameter(icat_client,
                                                                       SAMPLE_PROCESSED_FILE_COUNT_PARAMETER,
                                                                       entity=dataset_sample)

                sample_proc_file_count_params: filter = filter(
                    lambda x: x.type == file_count_param_type, (j for i in dataset_sample.datasets for j in
                                                                i.parameters if
                                                                i.type.name == PROCESSED_DATASET_TYPE_NAME))

                sample_proc_file_count: int = sum(
                    int(p.stringValue) if p.stringValue else p.numericValue for p in sample_proc_file_count_params)

                rb.sample_proc_file_count_param = set_sample_parameter(rb.sample_proc_file_count_param._obj,
                                                                       sample_proc_file_count)
                self.logger.debug("Updated sample statistic: Total number of processed files referencing sample")

                # Total volume of all datasets of sample
                rb.sample_vol_param = get_sample_parameter(icat_client,
                                                           SAMPLE_VOLUME_PARAMETER,
                                                           entity=dataset_sample)

                dataset_vol_param_type: Entity = get_parameter_type(icat_client, DATASET_VOLUME_PARAMETER)

                sample_vol_params: filter = filter(
                    lambda x: x.type == dataset_vol_param_type, (j for i in dataset_sample.datasets for j in
                                                                 i.parameters))

                sample_vol: int = sum(
                    int(p.stringValue) if p.stringValue else p.numericValue for p in sample_vol_params)

                rb.sample_vol_param = set_sample_parameter(rb.sample_vol_param._obj, sample_vol)
                self.logger.debug("Updated sample statistic: Total volume of all datasets of sample")

                # Total volume of all raw datasets of sample
                rb.sample_acq_vol_param = get_sample_parameter(icat_client,
                                                                      SAMPLE_ACQUISITION_VOLUME_PARAMETER,
                                                                      entity=dataset_sample)

                sample_acq_vol_params: filter = filter(
                    lambda x: x.type == dataset_vol_param_type, (j for i in dataset_sample.datasets for j in
                                                                 i.parameters if i.type.name == RAW_DATASET_TYPE_NAME))

                sample_acq_vol: int = sum(
                    int(p.stringValue) if p.stringValue else p.numericValue for p in sample_acq_vol_params)

                rb.sample_acq_vol_param = set_sample_parameter(rb.sample_acq_vol_param._obj, sample_acq_vol)
                self.logger.debug("Updated sample statistic: Total volume of all raw datasets of sample")

                # Total volume of all processed datasets of sample
                rb.sample_proc_vol_param = get_sample_parameter(icat_client,
                                                                       SAMPLE_PROCESSED_VOLUME_PARAMETER,
                                                                       entity=dataset_sample)

                sample_proc_vol_params: filter = filter(
                    lambda x: x.type == dataset_vol_param_type, (j for i in dataset_sample.datasets for j in
                                                                 i.parameters if
                                                                 i.type.name == PROCESSED_DATASET_TYPE_NAME))

                sample_proc_vol: int = sum(
                    int(p.stringValue) if p.stringValue else p.numericValue for p in sample_proc_vol_params)

                rb.sample_proc_vol_param = set_sample_parameter(rb.sample_proc_vol_param._obj, sample_proc_vol)
                self.logger.debug("Updated sample statistic: Total volume of all processed datasets of sample")

                self.logger.info(f"Updated sample statistics for dataset={dataset_id}")
            except Exception as e:
                rb.rollback_all(force_delete=True)

                error_msg: str = f"Error: {e}"
                self.logger.error(error_msg)
                raise Exception(error_msg)

    def update_per_dataset_parameter_statistics(self, icat_client: ICATClient, investigation_name: str, dataset_id: int, *_args,
                                 **_kwargs) -> None:
        investigation: Entity = icat_client.search("Investigation", conditions={"name__eq": investigation_name},
                                                   flatten_single=True)

        if not dataset_id:
            raise Exception("Dataset ID not received")

        with ICATRollbackContext(icat_client, self.logger) as rb:
            rb.dataset = icat_client.search("Dataset", conditions={"id__eq": dataset_id}, flatten_single=True)
            if not rb.dataset:
                raise Exception("Dataset not found")

            try:
                pass
            except Exception as e:
                rb.rollback_all(force_delete=True)

                error_msg: str = f"Error: {e}"
                self.logger.error(error_msg)
                raise Exception(error_msg)
