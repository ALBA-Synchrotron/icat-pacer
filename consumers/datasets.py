from __future__ import absolute_import, unicode_literals

from kombu import Message

from helpers.contexts.dataset import create_dataset_context
from helpers.dataclasses.dataset import DatasetContext
from helpers.utils.pacer_consumer import PACERConsumer
from tasks.datasets import DatasetsTasks


class DatasetsConsumer(PACERConsumer):

    # BEFORE ADDING (COPYING AND PASTING THIS CONSUMER TO CREATE A NEW ONE), REPLACE THE `dashboard_message_type`
    # SPECIFIED IN THE CALL TO THE SUPERIOR CLASS CONSTRUCTOR WITH A NEW VALUE FOR THE NEW MESSAGES TYPE.

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(dashboard_message_type="dataset-ingestion", *args, **kwargs)
        self.tasks = DatasetsTasks(self.logger)

    def get_message_object_identifiers(self, message: Message) -> dict:
        try:
            dataset_str: str = message.payload or message.body
            dataset_ctx: DatasetContext = create_dataset_context(dataset_str, self.__get_ingestion_settings())
            return {"investigation": dataset_ctx.investigation, "dataset": dataset_ctx.name}
        except Exception as e:
            self.logger.error(f"Error getting message object identifiers: {e!r}")
            return {}

    def callback_func_main_dataset_creation(self, _body, message: Message, *_args, **_kwargs) -> None:
        self.logger.info(
            f"callback_func_main_dataset_ingestion > Processing message from {message.delivery_info['routing_key']}: {message.payload!r}")
        dataset_str: str = message.payload or message.body
        dataset_ctx: DatasetContext = create_dataset_context(dataset_str, self.__get_ingestion_settings())

        self.tasks.create_base_dataset_icat(icat_client=self.icat_client, dataset_ctx=dataset_ctx, *_args, **_kwargs)

    def __get_ingestion_settings(self) -> dict:
        return self.pacer_config.get("ingestionSettings", {}).get("dataset", {})
