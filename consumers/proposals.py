from __future__ import absolute_import, unicode_literals

from kombu import Message

from helpers.dataclasses import InvestigationContext
from helpers.pacer_consumer import PACERConsumer
from helpers.proposals import create_investigation_context
from tasks.proposals import ProposalTasks


class ProposalConsumer(PACERConsumer):

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(dashboard_message_type="proposal-sync", *args, **kwargs)
        self.tasks = ProposalTasks(self.logger)

    def callback_func_sync_proposal_visa(self, body, message: Message) -> None:
        self.logger.info(f"VISA_proposal_sync_callback > Processing message from {message.delivery_info['routing_key']}: {message.payload!r}")
        proposal_str: str = message.payload or message.body
        investigation_context: InvestigationContext = create_investigation_context(proposal_str)

        self.tasks.sync_investigation_visa(self.visa_pg_pool, investigation_context, message=message, body=body)

    def callback_func_sync_proposal_icat(self, body, message: Message) -> None:
        self.logger.info(f"ICAT_proposal_sync_callback > Processing message from {message.delivery_info['routing_key']}: {message.payload!r}")
        proposal_str: str = message.payload or message.body
        investigation_context: InvestigationContext = create_investigation_context(proposal_str)

        self.tasks.sync_investigation_icat(self.icat_client, investigation_context, message=message, body=body)
