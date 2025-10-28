from __future__ import absolute_import, unicode_literals

from kombu import Message

from helpers.dataclasses import InvestigationOperationsContext, DatasetContext
from helpers.investigation_ops import create_investigation_ops_context
from helpers.pacer_consumer import PACERConsumer
from tasks.investigation_ops import InvestigationOpsTasks


class InternalDatasetsConsumer(PACERConsumer):

    # BEFORE ADDING (COPYING AND PASTING THIS CONSUMER TO CREATE A NEW ONE), REPLACE THE `dashboard_message_type`
    # SPECIFIED IN THE CALL TO THE SUPERIOR CLASS CONSTRUCTOR WITH A NEW VALUE FOR THE NEW MESSAGES TYPE.

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(dashboard_message_type="internal-dataset-ingestion", *args, **kwargs)
        self.tasks = InvestigationOpsTasks(self.logger)

    def get_message_object_identifiers(self, message: Message) -> dict:
        try:
            dataset_str: str = message.payload or message.body
            dataset_ctx: DatasetContext = create_investigation_ops_context(dataset_str)
            return {"investigation": dataset_ctx.investigation, "dataset": dataset_ctx.name}
        except Exception as e:
            self.logger.error(f"Error getting message object identifiers: {e!r}")
            return {}

    def callback_func_investigation_mint(self, _body, message: Message, *_args, **_kwargs) -> None:
        self.logger.info(
            f"investigation_mint_callback > Processing message from {message.delivery_info['routing_key']}: {message.payload!r}")
        inv_ops_str: str = message.payload or message.body
        inv_ops_ctx: InvestigationOperationsContext = create_investigation_ops_context(inv_ops_str)

        if "mint-proposal" in inv_ops_ctx.operations and self.datacite_client is not None:
            self.tasks.mint_proposal(self.visa_pg_pool, self.icat_client, self.datacite_client, inv_ops_ctx)
        if "create-panosc-item" in inv_ops_ctx.operations:
            self.tasks.create_panosc_item(self.icat_client, inv_ops_ctx, self.panosc_client)
