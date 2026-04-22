from __future__ import absolute_import, unicode_literals

from kombu import Message

from helpers.dataclasses.investigation import InvestigationOperationsContext
from helpers.contexts.investigation_ops import create_investigation_ops_context
from helpers.utils.pacer_consumer import PACERConsumer, callback_order
from tasks.investigation_ops import InvestigationOpsTasks


class InvestigationOperationsConsumer(PACERConsumer):

    # BEFORE ADDING (COPYING AND PASTING THIS CONSUMER TO CREATE A NEW ONE), REPLACE THE `dashboard_message_type`
    # SPECIFIED IN THE CALL TO THE SUPERIOR CLASS CONSTRUCTOR WITH A NEW VALUE FOR THE NEW MESSAGES TYPE.

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(dashboard_message_type="investigation-ops", *args, **kwargs)
        self.tasks = InvestigationOpsTasks(self.logger)

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

        if "mint-proposal" in inv_ops_ctx.operations and self.datacite_client is not None:
            self.tasks.mint_proposal(self.visa_pg_pool, self.icat_client, self.datacite_client, inv_ops_ctx, *args,
                                     **kwargs)
        if "create-panosc-item" in inv_ops_ctx.operations:
            self.tasks.create_panosc_item(self.icat_client, inv_ops_ctx, self.panosc_client, *args, **kwargs)
