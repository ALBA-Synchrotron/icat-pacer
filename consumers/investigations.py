from __future__ import absolute_import, unicode_literals

from kombu import Message

from helpers.dataclasses.investigation import InvestigationContext
from helpers.utils.pacer_consumer import PACERConsumer
from helpers.contexts.proposals import create_investigation_context
from tasks.investigations import ProposalTasks


class InvestigationConsumer(PACERConsumer):

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(dashboard_message_type="proposal-sync", *args, **kwargs)
        self.tasks = ProposalTasks(self.logger)

    def get_message_object_identifiers(self, message: Message) -> dict:
        try:
            investigation_str: str = message.payload or message.body
            investigation_context: InvestigationContext = create_investigation_context(investigation_str)
            return {"name": investigation_context.name, "instrument": investigation_context.instrument.code}
        except Exception as e:
            self.logger.error(f"Error getting message object identifiers: {e!r}")
            return {}

    def callback_func_sync_proposal_visa(self, body, message: Message, *_args, **_kwargs) -> None:
        self.logger.info(
            f"VISA_proposal_sync_callback > Processing message from {message.delivery_info['routing_key']}: {message.payload!r}")
        investigation_str: str = message.payload or message.body
        investigation_context: InvestigationContext = create_investigation_context(investigation_str)

        if not investigation_context.visa_sync:
            return

        self.tasks.sync_investigation_visa(self.visa_pg_pool, investigation_context, message=message, body=body)

    def callback_func_sync_proposal_icat(self, body, message: Message, *_args, **_kwargs) -> None:
        self.logger.info(
            f"ICAT_proposal_sync_callback > Processing message from {message.delivery_info['routing_key']}: {message.payload!r}")
        investigation_str: str = message.payload or message.body
        investigation_context: InvestigationContext = create_investigation_context(investigation_str)

        if not investigation_context.icat_sync:
            return

        self.tasks.sync_investigation_icat(self.icat_client, investigation_context, message=message, body=body)
