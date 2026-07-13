from __future__ import absolute_import, unicode_literals

from kombu import Message

import globals_var
from helpers.contexts.dataset import create_dataset_context
from helpers.models.dataset import DatasetContext, DatasetIndexingContext
from helpers.static_settings import RAW_DATASET_TYPE_NAME, PROCESSED_DATASET_TYPE_NAME
from helpers.utils.pacer_consumer import PACERConsumer, callback_order
from producers.generic import GenericProducer
from tasks.datasets_internal import DatasetsInternalTasks


class InternalDatasetsConsumer(PACERConsumer):

    # BEFORE ADDING (COPYING AND PASTING THIS CONSUMER TO CREATE A NEW ONE), REPLACE THE `dashboard_message_type`
    # SPECIFIED IN THE CALL TO THE SUPERIOR CLASS CONSTRUCTOR WITH A NEW VALUE FOR THE NEW MESSAGES TYPE.

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(dashboard_message_type="internal-dataset-ingestion", *args, **kwargs)
        self.reject_msg_at_first_callback_error = True

        self.tasks = DatasetsInternalTasks(self.logger)
        ingestion_settings: dict = globals_var.ingestion_settings.get("dataset", {})

        self.internal_dataset_exchange_name: str = ingestion_settings.get("internalDatasetExchangeName", "")
        self.internal_datasets_links_routing_key: str = ingestion_settings.get("internalDatasetLinksRoutingKey", "")
        self.internal_statistics_routing_key: str = ingestion_settings.get("internalStatisticsRoutingKey", "")
        self.dataset_indexing_routing_key: str = ingestion_settings.get("datasetIndexingRoutingKey", "")

        self.dataset_es_index_name: str = ingestion_settings.get("datasetElasticIndexName", "")

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
    def callback_func_create_dataset_datafiles(self, _body, message: Message, *args, **kwargs) -> None:
        self.logger.info(
            f"callback_func_create_dataset_datafiles > Processing message from {message.delivery_info['routing_key']}: {message.payload!r}")
        dataset_str: str = message.payload or message.body
        dataset_ctx: DatasetContext = create_dataset_context(dataset_str)
        dataset_id: int = message.headers.get("dataset_id", 0)
        is_duplicated: bool = message.headers.get("is_duplicated", False)

        self.tasks.create_dataset_datafiles(self.icat_client, dataset_ctx, dataset_id, is_duplicated, *args, **kwargs)

    @callback_order(2)
    def callback_func_create_dataset_parameters(self, _body, message: Message, *args, **kwargs) -> None:
        self.logger.info(
            f"callback_func_create_dataset_parameters > Processing message from {message.delivery_info['routing_key']}: {message.payload!r}")
        dataset_str: str = message.payload or message.body
        dataset_ctx: DatasetContext = create_dataset_context(dataset_str)
        dataset_id: int = message.headers.get("dataset_id", 0)
        is_duplicated: bool = message.headers.get("is_duplicated", False)

        self.tasks.create_dataset_parameters(self.icat_client, dataset_ctx, dataset_id, is_duplicated, *args, **kwargs)

    @callback_order(3)
    def callback_func_create_dataset_gallery(self, _body, message: Message, *args, **kwargs) -> None:
        self.logger.info(
            f"callback_func_create_dataset_gallery > Processing message from {message.delivery_info['routing_key']}: {message.payload!r}")
        dataset_str: str = message.payload or message.body
        dataset_ctx: DatasetContext = create_dataset_context(dataset_str)
        dataset_id: int = message.headers.get("dataset_id", 0)
        self.tasks.create_dataset_gallery(self.icat_plus_client, self.icat_client, dataset_ctx, dataset_id, *args,
                                          **kwargs)

    @callback_order(4)
    def callback_func_dataset_linkage(self, _body, message: Message, *args, **kwargs) -> None:
        self.logger.info(
            f"callback_func_dataset_linkage > Processing message from {message.delivery_info['routing_key']}: {message.payload!r}")
        dataset_str: str = message.payload or message.body
        dataset_ctx: DatasetContext = create_dataset_context(dataset_str)
        dataset_id: int = message.headers.get("dataset_id", 0)
        is_duplicated: bool = message.headers.get("is_duplicated", False)

        if is_duplicated:
            return

        if dataset_ctx.type == RAW_DATASET_TYPE_NAME:
            self.tasks.raw_dataset_linkage(self.icat_client, dataset_id, *args, **kwargs)
        elif dataset_ctx.type == PROCESSED_DATASET_TYPE_NAME:
            self.tasks.processed_dataset_linkage(self.icat_client, dataset_id, *args, **kwargs)

    # This callback must always be the last one. If you've got anything to add, add it before this function.
    @callback_order(9999999)
    def callback_func_forward_to_following_queues(self, _body, message: Message, *_args, **_kwargs) -> None:
        self.logger.info(
            f"callback_func_forward_to_following_queues > Processing message from {message.delivery_info['routing_key']}: {message.payload!r}")
        dataset_id: int = message.headers.get("dataset_id", 0)
        investigation_id: int = message.headers.get("investigation_id", 0)

        following_queues: list = [self.internal_statistics_routing_key, self.internal_datasets_links_routing_key,
                                  self.dataset_indexing_routing_key]
        msg = None
        for queue_routing_key in following_queues:
            match queue_routing_key:
                case self.dataset_indexing_routing_key:
                    if not self.dataset_es_index_name:
                        continue
                    msg = DatasetIndexingContext.model_validate(
                        {"dataset_id": dataset_id, "index_name": self.dataset_es_index_name}).model_dump_json()
                case _:
                    msg = message

            GenericProducer.send_message(self.connection, self.internal_dataset_exchange_name,
                                         queue_routing_key, msg,
                                         {"dataset_id": dataset_id, "investigation_id": investigation_id})
