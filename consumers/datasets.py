from __future__ import absolute_import, unicode_literals

import globals_var
from kombu import Message

from helpers.contexts.dataset import create_dataset_context
from helpers.dataclasses.dataset import DatasetContext
from helpers.utils.pacer_consumer import PACERConsumer
from producers.generic import GenericProducer
from tasks.datasets import DatasetsTasks


class DatasetsConsumer(PACERConsumer):

    # BEFORE ADDING (COPYING AND PASTING THIS CONSUMER TO CREATE A NEW ONE), REPLACE THE `dashboard_message_type`
    # SPECIFIED IN THE CALL TO THE SUPERIOR CLASS CONSTRUCTOR WITH A NEW VALUE FOR THE NEW MESSAGES TYPE.

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(dashboard_message_type="dataset-ingestion", *args, **kwargs)
        self.reject_msg_at_first_callback_error = True

        self.tasks = DatasetsTasks(self.logger)
        ingestion_settings: dict = globals_var.ingestion_settings.get("dataset", {})

        self.internal_dataset_exchange_name: str = ingestion_settings.get("internalDatasetExchangeName", "")
        self.internal_dataset_routing_key: str = ingestion_settings.get("internalDatasetRoutingKey", "")

    def get_message_object_identifiers(self, message: Message) -> dict:
        try:
            dataset_str: str = message.payload or message.body
            dataset_ctx: DatasetContext = create_dataset_context(dataset_str)
            return {
                "instrument": dataset_ctx.instrument,
                "investigation": dataset_ctx.investigation if dataset_ctx.investigation else f"id={dataset_ctx.investigation_id}",
                "dataset": dataset_ctx.name}
        except Exception as e:
            self.logger.error(f"Error getting message object identifiers: {e!r}")
            return {}

    def callback_func_main_dataset_creation(self, _body, message: Message, *_args, **_kwargs) -> None:
        self.logger.info(
            f"callback_func_main_dataset_ingestion > Processing message from {message.delivery_info['routing_key']}: {message.payload!r}")
        dataset_str: str = message.payload or message.body
        dataset_ctx: DatasetContext = create_dataset_context(dataset_str)

        new_dataset_id, investigation_id, is_duplicated = self.tasks.create_base_dataset_icat(
            icat_client=self.icat_client,
            dataset_ctx=dataset_ctx,
            *_args, **_kwargs)
        if new_dataset_id:
            self.logger.info(
                f"callback_func_main_dataset_ingestion > Forwarding message to internal ingest queue")
            GenericProducer.send_message(self.connection, self.internal_dataset_exchange_name,
                                         self.internal_dataset_routing_key, message,
                                         {"dataset_id": new_dataset_id, "investigation_id": investigation_id,
                                          "is_duplicated": is_duplicated})
