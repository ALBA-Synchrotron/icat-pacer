from __future__ import absolute_import, unicode_literals

import datetime
import logging

from icat.entity import Entity

from exceptions.dataset import DatasetTypeNotFound
from exceptions.investigation import InvestigationNotFound
from exceptions.sample import SampleTypeNotFound
from helpers.dataclasses.dataset import DatasetContext
from helpers.integrations.icat.extended_client import ICATClient
from helpers.utils.dataset import get_dataset_investigation, get_duplicated_processed_dataset_in_investigation
from helpers.utils.datetime import DATETIME_EU
from helpers.utils.icat_rollback_proxy import ICATRollbackContext


class DatasetsTasks:

    def __init__(self, logger: logging.Logger = None):
        self.logger = logger

    def create_base_dataset_icat(self, icat_client: ICATClient, dataset_ctx: DatasetContext, *_args, **_kwargs) -> \
            tuple[int, int, bool]:

        investigation: Entity = get_dataset_investigation(icat_client, self.logger, dataset_ctx)

        duplicate_proc_dataset = get_duplicated_processed_dataset_in_investigation(icat_client, dataset_ctx.name,
                                                                                   investigation.id)
        if duplicate_proc_dataset:
            self.logger.info(f"Duplicate processed dataset found (dataset id={duplicate_proc_dataset.id}), name={dataset_ctx.name}), skipping creation")
            return duplicate_proc_dataset.id, investigation.id, True

        with ICATRollbackContext(icat_client, self.logger) as rb:
            rb.new_dataset = icat_client.new("Dataset")
            rb.new_dataset_sample = icat_client.new("Sample")
            rb.new_investigation_instrument = icat_client.new("InvestigationInstrument")

            try:
                self.logger.info(
                    f"Creating dataset {dataset_ctx.name}, inv={dataset_ctx.investigation}, instr={dataset_ctx.instrument}")

                dataset_type: Entity = icat_client.search("DatasetType", conditions={"name__eq": dataset_ctx.type},
                                                          flatten_single=True)
                if dataset_type is None:
                    error_msg = f"Dataset type {dataset_ctx.type} not found."
                    self.logger.error(error_msg)
                    raise DatasetTypeNotFound(error_msg)

                sample: Entity | None = icat_client.search("Sample",
                                                           conditions={"name__eq": dataset_ctx.sample.name,
                                                                       "investigation.id__eq": investigation.id})
                if not sample:
                    if dataset_ctx.sample.type:
                        sample_type: Entity = icat_client.search("SampleType",
                                                                 conditions={"name__eq": dataset_ctx.sample.type},
                                                                 flatten_single=True)
                        if not sample_type:
                            error_msg: str = f"Could not create dataset {dataset_ctx.name}, sample type not found"
                            self.logger.error(error_msg)
                            raise SampleTypeNotFound(error_msg)

                        rb.new_dataset_sample.type = sample_type

                    rb.new_dataset_sample.name = dataset_ctx.sample.name
                    rb.new_dataset_sample.investigation = investigation
                    rb.new_dataset_sample.create()

                rb.new_dataset.complete = True
                rb.new_dataset.type = dataset_type
                rb.new_dataset.sample = sample if sample else rb.new_dataset_sample._obj
                rb.new_dataset.investigation = investigation
                rb.new_dataset.location = dataset_ctx.location
                rb.new_dataset.startDate = dataset_ctx.start_date
                rb.new_dataset.endDate = dataset_ctx.end_date

                same_name_dataset: list = icat_client.search("Dataset",
                                                             conditions={"name__eq": dataset_ctx.name,
                                                                         "investigation.id__eq": investigation.id})

                date: str = datetime.datetime.now().strftime(DATETIME_EU)
                rb.new_dataset.name = dataset_ctx.name if not same_name_dataset else f"{dataset_ctx.name} [{date}]"
                rb.new_dataset.create()
                self.logger.info(f"Created dataset {rb.new_dataset.name} with id {rb.new_dataset.id}")
                return rb.new_dataset.id, rb.new_dataset.investigation.id, False
            except Exception as e:
                rb.rollback_all()

                error_msg: str = f"Error: {e}"
                self.logger.error(error_msg)
                raise e
