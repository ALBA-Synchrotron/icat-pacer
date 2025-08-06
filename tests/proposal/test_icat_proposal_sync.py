import logging
from datetime import datetime

import pytest

from helpers.icat_utils import ICATClient
from helpers.proposals import create_investigation_context, InvestigationContext
from tasks.proposals import ProposalTasks
from tests.utils.generic_unit_test import GenericPACERUnitTest

logger: logging.Logger = logging.getLogger(__name__)


class TestICATProposalTasks(GenericPACERUnitTest):
    fixtures: list = ["proposal.json"]
    entities_teardown: list = ["Investigation", "InvestigationInstrument", "InvestigationUser",
                               "InvestigationParameter", "InvestigationType", "Facility"]
    digit_only_prefix: bool = False

    @pytest.fixture(scope="class")
    def proposal_tasks(self) -> ProposalTasks:
        return ProposalTasks(logger)

    @pytest.fixture(scope="class")
    def new_icat_proposal(self, unittest_prefix: str) -> InvestigationContext:
        investigation_context: InvestigationContext = create_investigation_context(self.fixtures_dict.get("proposal"),
                                                                                   name_prefix=unittest_prefix)
        return investigation_context

    @pytest.fixture(scope="class")
    def updated_icat_proposal(self, new_icat_proposal: InvestigationContext) -> InvestigationContext:
        new_icat_proposal.start_date = datetime.now()
        return new_icat_proposal

    def test_create_new_proposal(self, proposal_tasks: ProposalTasks, icat_client: ICATClient,
                                 new_icat_proposal: InvestigationContext) -> None:
        proposal_tasks.sync_investigation_icat(icat_client, new_icat_proposal)
        proposals: list = icat_client.search("Investigation", conditions={"name__eq": new_icat_proposal.name},
                                             flatten_single=False)

        assert len(proposals) == 1
        assert proposals[0].name == new_icat_proposal.name

    def test_update_proposal(self, proposal_tasks: ProposalTasks, icat_client: ICATClient,
                             updated_icat_proposal: InvestigationContext) -> None:
        proposal_tasks.sync_investigation_icat(icat_client, updated_icat_proposal)
        proposals: list = icat_client.search("Investigation", conditions={"name__eq": updated_icat_proposal.name},
                                             flatten_single=False)

        assert len(proposals) == 1
        assert proposals[0].name == updated_icat_proposal.name
