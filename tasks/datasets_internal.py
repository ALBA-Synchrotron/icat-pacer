from __future__ import absolute_import, unicode_literals

import logging

from helpers.dataclasses.dataset import DatasetContext
from helpers.integrations.icat_utils import ICATClient
from helpers.utils.icat_rollback_proxy import ICATRollbackContext


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



            except Exception as e:
                rb.rollback_all(force_delete=True)

                error_msg: str = f"Error: {e}"
                self.logger.error(error_msg)
                raise Exception(error_msg)
