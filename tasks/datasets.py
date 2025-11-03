from __future__ import absolute_import, unicode_literals

import datetime
import logging

from icat.entity import Entity

from helpers.dataclasses.dataset import DatasetContext
from helpers.integrations.icat_utils import ICATClient
from helpers.utils.datetime import DATETIME_EU
from helpers.utils.icat_rollback_proxy import ICATRollbackContext


class DatasetsTasks:

    def __init__(self, logger: logging.Logger = None):
        self.logger = logger

    def create_base_dataset_icat(self, icat_client: ICATClient, dataset_ctx: DatasetContext, *_args, **_kwargs) -> None:
        with ICATRollbackContext(icat_client, self.logger) as rb:
            asd = 23
            rb.new_dataset = icat_client.new("Dataset")
            new_dataset_sample: Entity = icat_client.new("Sample")
            new_investigation_instrument: Entity

            try:
                self.logger.info(
                    f"Creating dataset {dataset_ctx.name}, inv={dataset_ctx.investigation}, instr={dataset_ctx.instrument}")

                instrument: Entity = icat_client.search("Instrument",
                                                        conditions={"name__eq": dataset_ctx.instrument},
                                                        flatten_single=True)

                if not instrument:
                    error_msg: str = f"Could not create dataset {dataset_ctx.name}, instrument {dataset_ctx.instrument} not found"
                    self.logger.error(error_msg)
                    raise Exception(error_msg)

                investigation: Entity | None = icat_client.search("Investigation",
                                                                  conditions={"name__eq": dataset_ctx.investigation},
                                                                  includes=["InvestigationInstrument", "Instrument"],
                                                                  flatten_single=True)

                if not investigation:
                    error_msg: str = f"Could not create dataset {dataset_ctx.name}, investigation not found"
                    self.logger.error(error_msg)
                    raise Exception(error_msg)

                if investigation.instrument.name != instrument.name:
                    error_msg: str = "Investigation's instrument does not match dataset's instrument, it will be added as a new investigation instrument"
                    self.logger.warning(error_msg)

                if dataset_ctx.sample.type:
                    sample_type: Entity = icat_client.search("SampleType",
                                                             conditions={"name__eq": dataset_ctx.sample.type},
                                                             flatten_single=True)
                    if not sample_type:
                        error_msg: str = f"Could not create dataset {dataset_ctx.name}, sample type not found"
                        self.logger.error(error_msg)
                        raise Exception(error_msg)

                    new_dataset_sample.type = sample_type

                new_dataset_sample.name = dataset_ctx.sample.name
                new_dataset_sample.save()

                new_dataset.sample = new_dataset_sample
                new_dataset.investigation = investigation
                new_dataset.instrument = instrument
                new_dataset.location = dataset_ctx.location
                new_dataset.startDate = dataset_ctx.start_date
                new_dataset.endDate = dataset_ctx.end_date

                same_name_dataset: list = icat_client.search("Dataset",
                                                             conditions={"name__eq": dataset_ctx.name,
                                                                         "investigation.name__eq": dataset_ctx.investigation})

                date: str = datetime.datetime.now().strftime(DATETIME_EU)
                new_dataset.name = dataset_ctx.name if not same_name_dataset else f"{dataset_ctx.name} [{date}]"
                new_dataset.save()

                self.logger.info(f"Created dataset {new_dataset.name} with id {new_dataset.id}")
            except Exception as e:
                new_dataset_sample.rollback()
                new_dataset.rollback()

                error_msg: str = f"Error: {e}"
                self.logger.error(error_msg)
                raise Exception(error_msg)
