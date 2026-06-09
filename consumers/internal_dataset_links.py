from __future__ import absolute_import, unicode_literals

from kombu import Message

from helpers.contexts.dataset import create_dataset_context
from helpers.models.dataset import DatasetContext
from helpers.utils.pacer_consumer import PACERConsumer, callback_order
from tasks.internal_dataset_links import InternalDatasetLinksTasks


class InternalDatasetsLinksConsumer(PACERConsumer):

    # BEFORE ADDING (COPYING AND PASTING THIS CONSUMER TO CREATE A NEW ONE), REPLACE THE `dashboard_message_type`
    # SPECIFIED IN THE CALL TO THE SUPERIOR CLASS CONSTRUCTOR WITH A NEW VALUE FOR THE NEW MESSAGES TYPE.

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(dashboard_message_type="internal-dataset-links", *args, **kwargs)
        self.reject_msg_at_first_callback_error = True

        self.tasks = InternalDatasetLinksTasks(self.logger)


    def get_message_object_identifiers(self, message: Message, shared_obj_identifiers: dict = {}) -> dict:
        try:
            dataset_str: str = message.payload or message.body
            dataset_ctx: DatasetContext = create_dataset_context(dataset_str)
            dataset_id: int = message.headers.get("dataset_id", 0)
            investigation_id: int = message.headers.get("investigation_id", 0)

            return {
                "instrument": dataset_ctx.instrument,
                "investigation": dataset_ctx.investigation if dataset_ctx.investigation else f"id={investigation_id}",
                "dataset": dataset_ctx.name, "dataset_id": dataset_id, **shared_obj_identifiers}
        except Exception as e:
            self.logger.error(f"Error getting message object identifiers: {e!r}")
            return {}

    @callback_order(1)
    def callback_func_build_dataset_full_links_information(self, _body, message: Message, *args, **kwargs) -> None:
        self.logger.info(
            f"callback_func_build_dataset_full_links_information > Processing message from {message.delivery_info['routing_key']}: {message.payload!r}")
        dataset_id: int = message.headers.get("dataset_id", 0)

        self.tasks.build_dataset_full_links_information(self.icat_client, dataset_id, *args, **kwargs)


