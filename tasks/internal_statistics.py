from __future__ import absolute_import, unicode_literals

import logging

from icat.entity import Entity

from exceptions.dataset import DatasetValidationError, DatasetNotFound
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
from helpers.utils.base_tasks import BaseTasks
from helpers.utils.dataset import set_dataset_parameter, get_dataset_parameter
from helpers.utils.icat_rollback_proxy import ICATRollbackContext
from helpers.utils.investigation import set_investigation_parameter, get_investigation_parameter
from helpers.utils.parameters import get_parameter_type
from helpers.utils.sample import get_sample_parameter, set_sample_parameter


class InternalStatisticsTasks(BaseTasks):

    def __init__(self, logger: logging.Logger = None):
        super().__init__(logger)

    def update_dataset_statistics(self, icat_client: ICATClient, dataset_id: int, *_args, **kwargs) -> None:

        if not dataset_id:
            raise DatasetValidationError("Dataset ID not received")
        with ICATRollbackContext(icat_client, self.logger) as rb:
            try:
                rb.dataset = icat_client.search("Dataset", conditions={"id__eq": dataset_id}, flatten_single=True)
                if not rb.dataset:
                    raise DatasetNotFound("Dataset not found")

                if not "visit_id" in kwargs.get("shared_obj_identifiers", {}):
                    kwargs.get("shared_obj_identifiers", {})["visit_id"] = rb.dataset.investigation.visitId

                # Dataset name
                rb.dataset_name_param = get_dataset_parameter(icat_client, DATASET_NAME_PARAMETER,
                                                              entity=rb.dataset._obj)
                rb.dataset_name_param = set_dataset_parameter(rb.dataset_name_param._obj, rb.dataset.name)
                self.logger.debug("Updated dataset statistic: Dataset name")

                # Dataset file count
                rb.file_count_param = get_dataset_parameter(icat_client, DATASET_FILE_COUNT_PARAMETER,
                                                            entity=rb.dataset._obj)
                datafile_count = icat_client.search("Datafile", conditions={"dataset.id__eq": dataset_id},
                                                    aggregate="COUNT")
                rb.file_count_param = set_dataset_parameter(rb.file_count_param._obj, datafile_count)
                self.logger.debug("Updated dataset statistic: Dataset file count")

                # Dataset file volume
                rb.volume_param = get_dataset_parameter(icat_client, DATASET_VOLUME_PARAMETER, entity=rb.dataset._obj)
                dataset_volume = icat_client.search("Datafile", conditions={"dataset.id__eq": dataset_id},
                                                    aggregate="SUM", attributes="fileSize")
                rb.volume_param = set_dataset_parameter(rb.volume_param._obj, dataset_volume)
                self.logger.debug("Updated dataset statistic: Dataset file volume")

                if rb.dataset.startDate is not None:
                    if rb.dataset.endDate is not None:
                        elapsed_time: float = int((rb.dataset.endDate - rb.dataset.startDate).total_seconds()) * 1000

                        rb.elapsed_time_param = get_dataset_parameter(icat_client,
                                                                      DATASET_ELAPSE_TIME_PARAMETER,
                                                                      entity=rb.dataset._obj)
                        rb.elapsed_time_param = set_dataset_parameter(rb.elapsed_time_param._obj, elapsed_time)

                self.logger.info(f"Updated dataset statistics for dataset={dataset_id}")
            except Exception as e:
                rb.rollback_all()

                error_msg: str = f"Error: {e}"
                self.logger.error(error_msg)
                raise e

    def update_investigation_statistics(self, icat_client: ICATClient, dataset_id: int, *_args,
                                        **kwargs) -> None:
        if not dataset_id:
            raise DatasetValidationError("Dataset ID not received")

        with ICATRollbackContext(icat_client, self.logger) as rb:
            rb.dataset = icat_client.search("Dataset", conditions={"id__eq": dataset_id}, flatten_single=True)

            if not rb.dataset:
                raise DatasetNotFound("Dataset not found")

            investigation: Entity = rb.dataset.investigation
            if not "visit_id" in kwargs.get("shared_obj_identifiers", {}):
                kwargs.get("shared_obj_identifiers", {})["visit_id"] = investigation.visitId

            try:
                # Total number of datasets
                rb.dataset_count_param = get_investigation_parameter(icat_client,
                                                                     INVESTIGATION_DATASET_COUNT_PARAMETER,
                                                                     entity=investigation)
                total_datasets = icat_client.search("Dataset", conditions={"investigation.id__eq": investigation.id},
                                                    aggregate="COUNT")
                rb.dataset_count_param = set_investigation_parameter(rb.dataset_count_param._obj,
                                                                     total_datasets)
                self.logger.debug("Updated investigation statistic: Total number of datasets")

                # Total number of raw datasets
                rb.acq_dataset_count_param = get_investigation_parameter(icat_client,
                                                                         INVESTIGATION_ACQUISITION_DATASET_COUNT_PARAMETER,
                                                                         entity=investigation)
                total_raw_datasets = icat_client.search("Dataset", conditions={"investigation.id__eq": investigation.id,
                                                                               "type.name__eq": RAW_DATASET_TYPE_NAME},
                                                        aggregate="COUNT")
                rb.acq_dataset_count_param = set_investigation_parameter(rb.acq_dataset_count_param._obj,
                                                                         total_raw_datasets
                                                                         )
                self.logger.debug("Updated investigation statistic: Total number of raw datasets")

                # Total number of processed datasets
                rb.proc_dataset_count_param = get_investigation_parameter(icat_client,
                                                                          INVESTIGATION_PROCESSED_DATASET_COUNT_PARAMETER,
                                                                          entity=investigation)
                total_proc_datasets = icat_client.search("Dataset",
                                                         conditions={"investigation.id__eq": investigation.id,
                                                                     "type.name__eq": PROCESSED_DATASET_TYPE_NAME},
                                                         aggregate="COUNT")

                rb.proc_dataset_count_param = set_investigation_parameter(rb.proc_dataset_count_param._obj,
                                                                          total_proc_datasets)
                self.logger.debug("Updated investigation statistic: Total number of processed datasets")

                # Total number of samples
                rb.sample_count_param = get_investigation_parameter(icat_client,
                                                                    INVESTIGATION_SAMPLE_COUNT_PARAMETER,
                                                                    entity=investigation)
                total_samples = icat_client.search("Sample", conditions={"investigation.id__eq": investigation.id},
                                                   aggregate="COUNT")
                rb.sample_count_param = set_investigation_parameter(rb.sample_count_param._obj, total_samples)
                self.logger.debug("Updated investigation statistic: Total number of samples")

                # Total volume of all datasets
                rb.inv_vol_param = get_investigation_parameter(icat_client,
                                                               INVESTIGATION_VOLUME_PARAMETER,
                                                               entity=investigation)

                inv_vol = icat_client.search("Datafile", conditions={"dataset.investigation.id__eq": investigation.id},
                                             aggregate="SUM", attributes="fileSize")

                rb.inv_vol_param = set_investigation_parameter(rb.inv_vol_param._obj, inv_vol)
                self.logger.debug("Updated investigation statistic: Total volume of all datasets")

                # Total volume of all raw datasets
                rb.acq_vol_param = get_investigation_parameter(icat_client,
                                                               INVESTIGATION_ACQUISITION_VOLUME_PARAMETER,
                                                               entity=investigation)

                inv_acq_vol = icat_client.search("Datafile",
                                                 conditions={"dataset.investigation.id__eq": investigation.id,
                                                             "dataset.type.name__eq": RAW_DATASET_TYPE_NAME},
                                                 aggregate="SUM", attributes="fileSize")

                rb.acq_vol_param = set_investigation_parameter(rb.acq_vol_param._obj, inv_acq_vol)
                self.logger.debug("Updated investigation statistic: Total volume of all raw datasets")

                # Total volume of all processed datasets
                rb.proc_vol_param = get_investigation_parameter(icat_client,
                                                                INVESTIGATION_PROCESSED_VOLUME_PARAMETER,
                                                                entity=investigation)

                inv_proc_vol = icat_client.search("Datafile",
                                                  conditions={"dataset.investigation.id__eq": investigation.id,
                                                              "dataset.type.name__eq": PROCESSED_DATASET_TYPE_NAME},
                                                  aggregate="SUM", attributes="fileSize")

                rb.proc_vol_param = set_investigation_parameter(rb.proc_vol_param._obj, inv_proc_vol)
                self.logger.debug("Updated investigation statistic: Total volume of all processed datasets")

                # Total elapsed time
                rb.inv_elapsed_time_param = get_investigation_parameter(icat_client,
                                                                        INVESTIGATION_ELAPSE_TIME_PARAMETER,
                                                                        entity=investigation)

                elapsed_time = icat_client.search("DatasetParameter", aggregate="SUM", attributes=["numericValue"],
                                                  conditions={"type.name__eq": DATASET_ELAPSE_TIME_PARAMETER,
                                                              "dataset.investigation.id__eq": investigation.id})

                rb.inv_elapsed_time_param = set_investigation_parameter(rb.inv_elapsed_time_param._obj, elapsed_time)
                self.logger.debug("Updated investigation statistic: Total elapsed time")

                # Total number of files
                rb.file_count_param = get_investigation_parameter(icat_client,
                                                                  INVESTIGATION_FILE_COUNT_PARAMETER,
                                                                  entity=investigation)

                file_count = icat_client.search("Datafile",
                                                conditions={"dataset.investigation.id__eq": investigation.id},
                                                aggregate="COUNT")

                rb.file_count_param = set_investigation_parameter(rb.file_count_param._obj, file_count)
                self.logger.debug("Updated investigation statistic: Total number of files")

                # Total number of raw files
                rb.acq_file_count_param = get_investigation_parameter(icat_client,
                                                                      INVESTIGATION_ACQUISITION_FILE_COUNT_PARAMETER,
                                                                      entity=investigation)
                acq_file_count = icat_client.search("Datafile",
                                                    conditions={"dataset.investigation.id__eq": investigation.id,
                                                                "dataset.type.name__eq": RAW_DATASET_TYPE_NAME},
                                                    aggregate="COUNT")

                rb.acq_file_count_param = set_investigation_parameter(rb.acq_file_count_param._obj, acq_file_count)
                self.logger.debug("Updated investigation statistic: Total number of raw files")

                # Total number of processed files
                rb.proc_file_count_param = get_investigation_parameter(icat_client,
                                                                       INVESTIGATION_PROCESSED_FILE_COUNT_PARAMETER,
                                                                       entity=investigation)
                proc_file_count = icat_client.search("Datafile",
                                                     conditions={"dataset.investigation.id__eq": investigation.id,
                                                                 "dataset.type.name__eq": PROCESSED_DATASET_TYPE_NAME},
                                                     aggregate="COUNT")

                rb.proc_file_count_param = set_investigation_parameter(rb.proc_file_count_param._obj, proc_file_count)
                self.logger.debug("Updated investigation statistic: Total number of processed files")

                self.logger.info(
                    f"Updated investigation statistics for investigation={investigation.name}/{investigation.visitId}")
            except Exception as e:
                rb.rollback_all()

                error_msg: str = f"Error: {e}"
                self.logger.error(error_msg)
                raise e

    def update_sample_statistics(self, icat_client: ICATClient, dataset_id: int, *_args, **kwargs) -> None:
        if not dataset_id:
            raise DatasetValidationError("Dataset ID not received")

        with ICATRollbackContext(icat_client, self.logger) as rb:
            rb.dataset = icat_client.search("Dataset", conditions={"id__eq": dataset_id}, flatten_single=True)

            if not rb.dataset:
                raise DatasetNotFound("Dataset not found")

            if not "visit_id" in kwargs.get("shared_obj_identifiers", {}):
                kwargs.get("shared_obj_identifiers", {})["visit_id"] = rb.dataset.investigation.visitId

            dataset_sample = rb.dataset.sample

            try:
                # Total number of datasets referencing sample
                rb.sample_dataset_count_param = get_sample_parameter(icat_client,
                                                                     SAMPLE_DATASET_COUNT_PARAMETER,
                                                                     entity=dataset_sample)
                dataset_count = icat_client.search("Dataset", conditions={"sample.id__eq": dataset_sample.id},
                                                   aggregate="COUNT")

                rb.sample_dataset_count_param = set_sample_parameter(rb.sample_dataset_count_param._obj,
                                                                     dataset_count)
                self.logger.debug("Updated sample statistic: Total number of datasets referencing sample")

                # Total number of raw datasets referencing sample
                rb.sample_acq_dataset_count_param = get_sample_parameter(icat_client,
                                                                         SAMPLE_ACQUISITION_DATASET_COUNT_PARAMETER,
                                                                         entity=dataset_sample)
                raw_dataset_count = icat_client.search("Dataset", conditions={"sample.id__eq": dataset_sample.id,
                                                                              "type.name__eq": RAW_DATASET_TYPE_NAME},
                                                       aggregate="COUNT")
                rb.sample_acq_dataset_count_param = set_sample_parameter(rb.sample_acq_dataset_count_param._obj,
                                                                         raw_dataset_count)
                self.logger.debug("Updated sample statistic: Total number of raw datasets referencing sample")

                # Total number of processed datasets referencing sample
                rb.sample_proc_dataset_count_param = get_sample_parameter(icat_client,
                                                                          SAMPLE_PROCESSED_DATASET_COUNT_PARAMETER,
                                                                          entity=dataset_sample)
                proc_dataset_count = icat_client.search("Dataset", conditions={"sample.id__eq": dataset_sample.id,
                                                                               "type.name__eq": PROCESSED_DATASET_TYPE_NAME},
                                                        aggregate="COUNT")

                rb.sample_proc_dataset_count_param = set_sample_parameter(rb.sample_proc_dataset_count_param._obj,
                                                                          proc_dataset_count)
                self.logger.debug("Updated sample statistic: Total number of processed datasets referencing sample")

                # Total number of files referencing sample
                rb.sample_file_count_param = get_sample_parameter(icat_client,
                                                                  SAMPLE_FILE_COUNT_PARAMETER,
                                                                  entity=dataset_sample)

                datafile_count = icat_client.search("Datafile", conditions={"dataset.sample.id__eq": dataset_sample.id},
                                                    aggregate="COUNT")

                rb.sample_file_count_param = set_sample_parameter(rb.sample_file_count_param._obj,
                                                                  datafile_count)
                self.logger.debug("Updated sample statistic: Total number of files referencing sample")

                # Total number of raw files referencing sample
                rb.sample_acq_file_count_param = get_sample_parameter(icat_client,
                                                                      SAMPLE_ACQUISITION_FILE_COUNT_PARAMETER,
                                                                      entity=dataset_sample)

                sample_acq_file_count = icat_client.search("Datafile",
                                                           conditions={"dataset.sample.id__eq": dataset_sample.id,
                                                                       "dataset.type.name__eq": RAW_DATASET_TYPE_NAME},
                                                           aggregate="COUNT")

                rb.sample_acq_file_count_param = set_sample_parameter(rb.sample_acq_file_count_param._obj,
                                                                      sample_acq_file_count)
                self.logger.debug("Updated sample statistic: Total number of raw files referencing sample")

                # Total number of processed files referencing sample
                rb.sample_proc_file_count_param = get_sample_parameter(icat_client,
                                                                       SAMPLE_PROCESSED_FILE_COUNT_PARAMETER,
                                                                       entity=dataset_sample)

                sample_proc_file_count = icat_client.search("Datafile",
                                                            conditions={"dataset.sample.id__eq": dataset_sample.id,
                                                                        "dataset.type.name__eq": PROCESSED_DATASET_TYPE_NAME},
                                                            aggregate="COUNT")

                rb.sample_proc_file_count_param = set_sample_parameter(rb.sample_proc_file_count_param._obj,
                                                                       sample_proc_file_count)
                self.logger.debug("Updated sample statistic: Total number of processed files referencing sample")

                # Total volume of all datasets of sample
                rb.sample_vol_param = get_sample_parameter(icat_client,
                                                           SAMPLE_VOLUME_PARAMETER,
                                                           entity=dataset_sample)

                dataset_vol_param_type: Entity = get_parameter_type(icat_client, DATASET_VOLUME_PARAMETER)

                sample_vol = icat_client.search("Datafile", conditions={"dataset.sample.id__eq": dataset_sample.id},
                                                aggregate="SUM", attributes="fileSize")

                rb.sample_vol_param = set_sample_parameter(rb.sample_vol_param._obj, sample_vol)
                self.logger.debug("Updated sample statistic: Total volume of all datasets of sample")

                # Total volume of all raw datasets of sample
                rb.sample_acq_vol_param = get_sample_parameter(icat_client,
                                                               SAMPLE_ACQUISITION_VOLUME_PARAMETER,
                                                               entity=dataset_sample)

                sample_acq_vol = icat_client.search("Datafile", conditions={"dataset.sample.id__eq": dataset_sample.id,
                                                                            "dataset.type.name__eq": RAW_DATASET_TYPE_NAME},
                                                    aggregate="SUM", attributes="fileSize")

                rb.sample_acq_vol_param = set_sample_parameter(rb.sample_acq_vol_param._obj, sample_acq_vol)
                self.logger.debug("Updated sample statistic: Total volume of all raw datasets of sample")

                # Total volume of all processed datasets of sample
                rb.sample_proc_vol_param = get_sample_parameter(icat_client,
                                                                SAMPLE_PROCESSED_VOLUME_PARAMETER,
                                                                entity=dataset_sample)

                sample_proc_vol = icat_client.search("Datafile", conditions={"dataset.sample.id__eq": dataset_sample.id,
                                                                             "dataset.type.name__eq": PROCESSED_DATASET_TYPE_NAME},
                                                     aggregate="SUM", attributes="fileSize")

                rb.sample_proc_vol_param = set_sample_parameter(rb.sample_proc_vol_param._obj, sample_proc_vol)
                self.logger.debug("Updated sample statistic: Total volume of all processed datasets of sample")

                self.logger.info(f"Updated sample statistics for dataset={dataset_id}")
            except Exception as e:
                rb.rollback_all()

                error_msg: str = f"Error: {e}"
                self.logger.error(error_msg)
                raise e

    """
    def update_per_dataset_parameter_statistics(self, icat_client: ICATClient, investigation_name: str, dataset_id: int,
                                                *_args,
                                                **_kwargs) -> None:
        # Not implemented
    """
