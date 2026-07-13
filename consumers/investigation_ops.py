from __future__ import absolute_import, unicode_literals

import globals_var

from kombu import Message

from helpers.models.investigation_operations import InvestigationOperationsContext
from helpers.contexts.investigation_ops import create_investigation_ops_context
from helpers.static_settings import INV_OPS_MINT_PROPOSAL, INV_OPS_CREATE_PANOSC_ITEM
from helpers.utils.pacer_consumer import PACERConsumer, callback_order
from models.dataset import DatasetIndexingContext
from producers.generic import GenericProducer
from tasks.investigation_ops import InvestigationOpsTasks


class InvestigationOperationsConsumer(PACERConsumer):

    # BEFORE ADDING (COPYING AND PASTING THIS CONSUMER TO CREATE A NEW ONE), REPLACE THE `dashboard_message_type`
    # SPECIFIED IN THE CALL TO THE SUPERIOR CLASS CONSTRUCTOR WITH A NEW VALUE FOR THE NEW MESSAGES TYPE.

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(dashboard_message_type="investigation-ops", *args, **kwargs)
        self.tasks = InvestigationOpsTasks(self.logger)

        ingestion_settings: dict = globals_var.ingestion_settings.get("dataset", {})
        self.reject_msg_at_first_callback_error = True

        self.internal_dataset_exchange_name: str = ingestion_settings.get("internalDatasetExchangeName", "")
        self.dataset_indexing_routing_key: str = ingestion_settings.get("datasetIndexingRoutingKey", "")
        self.dataset_es_index_name: str = ingestion_settings.get("datasetElasticIndexName", "")

    def get_message_object_identifiers(self, message: Message, shared_obj_identifiers: dict = {}) -> dict:
        try:
            inv_ops_str: str = message.payload or message.body
            inv_ops_ctx: InvestigationOperationsContext = create_investigation_ops_context(inv_ops_str)
            return {"investigation": inv_ops_ctx.name, "operations": inv_ops_ctx.operations,
                    "visit_id": inv_ops_ctx.visit_id, **shared_obj_identifiers}
        except Exception as e:
            self.logger.error(f"Error getting message object identifiers: {e!r}")
            return {}

    @callback_order(1)
    def callback_func_investigation_mint(self, _body, message: Message, *args, **kwargs) -> None:
        self.logger.info(
            f"investigation_mint_callback > Processing message from {message.delivery_info['routing_key']}: {message.payload!r}")
        inv_ops_str: str = message.payload or message.body
        inv_ops_ctx: InvestigationOperationsContext = create_investigation_ops_context(inv_ops_str)

        if INV_OPS_MINT_PROPOSAL in inv_ops_ctx.operations and self.datacite_client is not None:
            self.tasks.mint_proposal(self.visa_pg_pool, self.icat_client, self.datacite_client, inv_ops_ctx, *args,
                                     **kwargs)

    @callback_order(2)
    def callback_func_pss_item(self, _body, message: Message, *args, **kwargs) -> None:
        self.logger.info(
            f"pss_item_callback > Processing message from {message.delivery_info['routing_key']}: {message.payload!r}")
        inv_ops_str: str = message.payload or message.body
        inv_ops_ctx: InvestigationOperationsContext = create_investigation_ops_context(inv_ops_str)

        if INV_OPS_CREATE_PANOSC_ITEM in inv_ops_ctx.operations:
            self.tasks.create_panosc_item(self.icat_client, inv_ops_ctx, self.panosc_client, *args, **kwargs)

    @callback_order(3)
    def callback_func_reindex_investigation_datasets(self, _body, message: Message, *args, **kwargs) -> None:
        self.logger.info(
            f"reindex_investigation_datasets > Processing message from {message.delivery_info['routing_key']}: {message.payload!r}")

        if not self.dataset_es_index_name:
            return

        inv_ops_str: str = message.payload or message.body
        inv_ops_ctx: InvestigationOperationsContext = create_investigation_ops_context(inv_ops_str)

        reindex_datasets: list = self.tasks.fetch_investigation_datasets_reindex(self.icat_client, inv_ops_ctx, *args,
                                                                                 **kwargs)
        self.logger.info(f"reindex_investigation_datasets > Found {len(reindex_datasets)} datasets to reindex")

        for dataset_id in reindex_datasets:
            GenericProducer.send_message(self.connection, self.internal_dataset_exchange_name,
                                         self.dataset_indexing_routing_key,
                                         DatasetIndexingContext.model_validate(
                                             {
                                                 "dataset_id": dataset_id,
                                                 "index_name": self.dataset_es_index_name}).model_dump_json())
