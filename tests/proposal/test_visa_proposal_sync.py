import logging
from datetime import datetime

import pytest
from psycopg_pool import ConnectionPool

from helpers.proposals import create_investigation_context, InvestigationContext
from tasks.investigations import ProposalTasks
from tests.utils.generic_unit_test import GenericPACERUnitTest

logger: logging.Logger = logging.getLogger(__name__)


class TestVISAProposalTasks(GenericPACERUnitTest):
    fixtures: list = ["user.json"]
    entities_teardown: list = []
    digit_only_prefix: bool = True

    @pytest.fixture(scope="class")
    def proposal_tasks(self) -> ProposalTasks:
        return ProposalTasks(logger)

    @pytest.fixture(scope="class")
    def new_visa_proposal(self, numeric_prefix: str, icat_facility) -> InvestigationContext:
        investigation_context: InvestigationContext = create_investigation_context(self.fixtures_dict.get("proposal"),
                                                                                   {
                                                                                       "defaultFacilityName": icat_facility.name,
                                                                                       "defaultEmbargoYears": 3},
                                                                                   name_prefix=numeric_prefix)
        return investigation_context

    def test_sync_visa_proposal(self, proposal_tasks: ProposalTasks, mock_psycopg_pool: ConnectionPool,
                                new_visa_proposal: InvestigationContext) -> None:
        proposal_tasks.sync_investigation_visa(mock_psycopg_pool, new_visa_proposal)

        calls: list = mock_psycopg_pool.connection.return_value.__enter__.return_value.cursor.return_value.__enter__.return_value.execute.call_args_list
        sql_statements: list = [call.args[0] for call in calls]

        has_insert = any("INSERT" in sql.upper() for sql in sql_statements)
        assert has_insert, "No INSERT statements executed"
