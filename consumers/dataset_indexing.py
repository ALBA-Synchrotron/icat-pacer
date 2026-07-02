from __future__ import absolute_import, unicode_literals

from kombu import Message

from helpers.contexts.dataset import create_dataset_indexing_context
from helpers.models.dataset import DatasetIndexingContext
from helpers.utils.pacer_consumer import PACERConsumer, callback_order
from tasks.datasets_indexing import DatasetsIndexingTasks


class DatasetIndexerConsumer(PACERConsumer):

    # BEFORE ADDING (COPYING AND PASTING THIS CONSUMER TO CREATE A NEW ONE), REPLACE THE `dashboard_message_type`
    # SPECIFIED IN THE CALL TO THE SUPERIOR CLASS CONSTRUCTOR WITH A NEW VALUE FOR THE NEW MESSAGES TYPE.

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(dashboard_message_type="dataset-index", *args, **kwargs)
        self.tasks = DatasetsIndexingTasks(self.logger)

    def get_message_object_identifiers(self, message: Message, shared_obj_identifiers: dict = {}) -> dict:
        try:
            index_str: str = message.payload or message.body
            index_ctx: DatasetIndexingContext = create_dataset_indexing_context(index_str)

            return {
                "dataset_id": index_ctx.dataset_id,
                "index_name": index_ctx.index_name,
                **shared_obj_identifiers}
        except Exception as e:
            self.logger.error(f"Error getting message object identifiers: {e!r}")
            return {}

    @callback_order(1)
    def callback_func_index_dataset(self, _body, message: Message, *args, **kwargs) -> None:
        self.logger.info(
            f"callback_func_callback_func_index_dataset > Processing message from {message.delivery_info['routing_key']}: {message.payload!r}")

        index_str: str = message.payload or message.body
        index_ctx: DatasetIndexingContext = create_dataset_indexing_context(index_str)

        self.tasks.index_dataset_elasticsearch(self.icat_client, index_ctx, *args, **kwargs)
