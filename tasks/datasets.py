from __future__ import absolute_import, unicode_literals

import logging

from icat.entity import Entity

from helpers.dataclasses.dataset import DatasetContext
from helpers.integrations.icat_utils import ICATClient
from helpers.utils.icat_rollback_proxy import rollbackable


class DatasetsTasks:

    def __init__(self, logger: logging.Logger = None):
        self.logger = logger

    @rollbackable
    def create_base_dataset_icat(self, icat_client: ICATClient, dataset_ctx: DatasetContext, *_args, **_kwargs) -> None:
        rb_new_dataset: Entity = icat_client.new("Dataset")


