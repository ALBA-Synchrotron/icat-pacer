import pytest

from exceptions.investigation import InvestigationNotFound
from exceptions.investigation_ops import InvestigationOpsValidationError


@pytest.fixture
def invalid_investigation_ops_investigation(request):
    return request.getfixturevalue(request.param)


class TestInvestigationOpsInvestigationValidation:

    @pytest.mark.parametrize("invalid_investigation_ops_investigation",
                             [
                                 "ops_investigation_with_doi",
                                 "ops_investigation_no_datasets",
                                 "ops_investigation_missing_end_date",
                                 "ops_investigation_missing_investigation_users",
                                 "ops_investigation_missing_instrument",
                                 "ops_investigation_future_end_date",
                             ],
                             indirect=True)
    def test_mint_proposal_invalid_investigation(self, icat_client, investigation_ops_tasks,
                                                 invalid_investigation_ops_investigation):
        with pytest.raises(InvestigationOpsValidationError):
            investigation_ops_tasks.mint_proposal(None, icat_client, None, invalid_investigation_ops_investigation)

    def test_mint_proposal_non_existent_investigation(self, icat_client, investigation_ops_tasks,
                                                      ops_non_existent_investigation):
        with pytest.raises(InvestigationNotFound):
            investigation_ops_tasks.mint_proposal(None, icat_client, None, ops_non_existent_investigation)

    def test_mint_proposal_valid_investigation(self, icat_client, investigation_ops_tasks,
                                               ops_valid_investigation, mock_psycopg_pool, datacite_client_mock):
        investigation_ops_tasks.mint_proposal(mock_psycopg_pool, icat_client, datacite_client_mock,
                                              ops_valid_investigation)
        investigation = icat_client.search("Investigation", conditions={"name__eq": ops_valid_investigation.name},
                                           flatten_single=True)

        assert investigation.doi is not None
        calls: list = mock_psycopg_pool.connection.return_value.__enter__.return_value.cursor.return_value.__enter__.return_value.execute.call_args_list
        sql_statements: list = [call.args[0] for call in calls]

        has_insert = any("UPDATE" in sql.upper() for sql in sql_statements)
        assert has_insert
