from __future__ import absolute_import, unicode_literals

from kombu import Message

from helpers.contexts.dataset import create_dataset_context
from helpers.dataclasses.dataset import DatasetContext
from helpers.utils.pacer_consumer import PACERConsumer
from producers.generic import GenericProducer
from tasks.datasets_internal import DatasetsInternalTasks
import globals_var


class InternalDatasetsConsumer(PACERConsumer):

    # BEFORE ADDING (COPYING AND PASTING THIS CONSUMER TO CREATE A NEW ONE), REPLACE THE `dashboard_message_type`
    # SPECIFIED IN THE CALL TO THE SUPERIOR CLASS CONSTRUCTOR WITH A NEW VALUE FOR THE NEW MESSAGES TYPE.

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(dashboard_message_type="internal-dataset-ingestion", *args, **kwargs)
        self.tasks = DatasetsInternalTasks(self.logger)
        ingestion_settings: dict = globals_var.ingestion_settings.get("dataset", {})

        self.internal_dataset_exchange_name: str = ingestion_settings.get("internalDatasetExchangeName", "")
        self.internal_statistics_routing_key: str = ingestion_settings.get("internalStatisticsRoutingKey", "")

    def get_message_object_identifiers(self, message: Message) -> dict:
        try:
            dataset_str: str = message.payload or message.body
            dataset_ctx: DatasetContext = create_dataset_context(dataset_str)
            dataset_id: int = message.headers.get("dataset_id", 0)

            return {"investigation": dataset_ctx.investigation, "dataset": dataset_ctx.name, "dataset_id": dataset_id}
        except Exception as e:
            self.logger.error(f"Error getting message object identifiers: {e!r}")
            return {}

    def callback_func_create_dataset_datafiles(self, _body, message: Message, *_args, **_kwargs) -> None:
        self.logger.info(
            f"callback_func_create_dataset_datafiles > Processing message from {message.delivery_info['routing_key']}: {message.payload!r}")
        dataset_str: str = message.payload or message.body
        dataset_ctx: DatasetContext = create_dataset_context(dataset_str)
        dataset_id: int = message.headers.get("dataset_id", 0)

        self.tasks.create_dataset_datafiles(self.icat_client, dataset_ctx, dataset_id)

    def callback_func_create_dataset_parameters(self, _body, message: Message, *_args, **_kwargs) -> None:
        self.logger.info(
            f"callback_func_create_dataset_parameters > Processing message from {message.delivery_info['routing_key']}: {message.payload!r}")
        dataset_str: str = message.payload or message.body
        dataset_ctx: DatasetContext = create_dataset_context(dataset_str)
        dataset_id: int = message.headers.get("dataset_id", 0)

        self.tasks.create_dataset_parameters(self.icat_client, dataset_ctx, dataset_id)

        GenericProducer.send_message(self.connection, self.internal_dataset_exchange_name,
                                     self.internal_statistics_routing_key, dataset_ctx,
                                     {"dataset_id": dataset_id})
