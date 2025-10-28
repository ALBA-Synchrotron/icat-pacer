from __future__ import absolute_import, unicode_literals

from kombu import Message

from helpers.contexts.investigation_ops import create_investigation_ops_context
from helpers.dataclasses.dataset import DatasetContext
from helpers.utils.pacer_consumer import PACERConsumer
from tasks.datasets_internal import DatasetsInternalTasks


class InternalDatasetsConsumer(PACERConsumer):

    # BEFORE ADDING (COPYING AND PASTING THIS CONSUMER TO CREATE A NEW ONE), REPLACE THE `dashboard_message_type`
    # SPECIFIED IN THE CALL TO THE SUPERIOR CLASS CONSTRUCTOR WITH A NEW VALUE FOR THE NEW MESSAGES TYPE.

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(dashboard_message_type="internal-dataset-ingestion", *args, **kwargs)
        self.tasks = DatasetsInternalTasks(self.logger)

    def get_message_object_identifiers(self, message: Message) -> dict:
        try:
            dataset_str: str = message.payload or message.body
            dataset_ctx: DatasetContext = create_investigation_ops_context(dataset_str)
            return {"investigation": dataset_ctx.investigation, "dataset": dataset_ctx.name}
        except Exception as e:
            self.logger.error(f"Error getting message object identifiers: {e!r}")
            return {}


