import logging

import pytest
from icat.entity import Entity
from psycopg_pool import ConnectionPool

from helpers.integrations.datacite import DataciteClient
from helpers.dataclasses.investigation import InvestigationOperationsContext
from helpers.integrations.icat.extended_client import ICATClient
from tasks.investigation_ops import InvestigationOpsTasks
from tests.utils.generic_unit_test import GenericPACERUnitTest

logger: logging.Logger = logging.getLogger(__name__)


class TestInvestigationOpsMint(GenericPACERUnitTest):
    # entities_teardown: list = ["User"]

    def test_mint_non_existent_investigation(self, investigation_ops_tasks: InvestigationOpsTasks,
                                             mock_psycopg_pool: ConnectionPool,
                                             icat_client: ICATClient,
                                             datacite_client_mock: DataciteClient,
                                             non_existent_investigation: InvestigationOperationsContext) -> None:
        with pytest.raises(Exception) as exc_info:
            investigation_ops_tasks.mint_proposal(
                mock_psycopg_pool, icat_client, datacite_client_mock, non_existent_investigation)
        assert "Investigation non-existent-investigation not found" in str(exc_info.value)

    def test_mint_investigation_already_minted(self, investigation_ops_tasks: InvestigationOpsTasks,
                                               mock_psycopg_pool: ConnectionPool,
                                               icat_client: ICATClient,
                                               datacite_client_mock: DataciteClient,
                                               investigation_with_doi: InvestigationOperationsContext) -> None:
        with pytest.raises(Exception) as exc_info:
            investigation_ops_tasks.mint_proposal(
                mock_psycopg_pool, icat_client, datacite_client_mock, investigation_with_doi)
        assert "already has a DOI" in str(exc_info.value)

    def test_mint_investigation_with_no_datasets(self, investigation_ops_tasks: InvestigationOpsTasks,
                                                 mock_psycopg_pool: ConnectionPool,
                                                 icat_client: ICATClient,
                                                 datacite_client_mock: DataciteClient,
                                                 investigation_with_no_datasets: InvestigationOperationsContext) -> None:
        with pytest.raises(Exception) as exc_info:
            investigation_ops_tasks.mint_proposal(
                mock_psycopg_pool, icat_client, datacite_client_mock, investigation_with_no_datasets)
        assert "has no datasets, it will not be minted" in str(exc_info.value)

    def test_mint_investigation_with_no_users(self, investigation_ops_tasks: InvestigationOpsTasks,
                                              mock_psycopg_pool: ConnectionPool,
                                              icat_client: ICATClient,
                                              datacite_client_mock: DataciteClient,
                                              investigation_with_no_users: InvestigationOperationsContext) -> None:
        with pytest.raises(Exception) as exc_info:
            investigation_ops_tasks.mint_proposal(
                mock_psycopg_pool, icat_client, datacite_client_mock, investigation_with_no_users)
        assert "has no users, it will not be minted" in str(exc_info.value)

    def test_mint_investigation_with_no_dates(self, investigation_ops_tasks: InvestigationOpsTasks,
                                              mock_psycopg_pool: ConnectionPool,
                                              icat_client: ICATClient,
                                              datacite_client_mock: DataciteClient,
                                              investigation_with_no_dates: InvestigationOperationsContext) -> None:
        with pytest.raises(Exception) as exc_info:
            investigation_ops_tasks.mint_proposal(
                mock_psycopg_pool, icat_client, datacite_client_mock, investigation_with_no_dates)
        assert "has no releaseDate, endDate or startDate, it will not be minted" in str(exc_info.value)

    def test_mint_investigation_with_no_instruments(self, investigation_ops_tasks: InvestigationOpsTasks,
                                                    mock_psycopg_pool: ConnectionPool,
                                                    icat_client: ICATClient,
                                                    datacite_client_mock: DataciteClient,
                                                    investigation_with_no_instrument: InvestigationOperationsContext) -> None:
        with pytest.raises(Exception) as exc_info:
            investigation_ops_tasks.mint_proposal(
                mock_psycopg_pool, icat_client, datacite_client_mock, investigation_with_no_instrument)
        assert "has no instruments, it will not be minted" in str(exc_info.value)

    def test_mint_investigation_future_end_date(self, investigation_ops_tasks: InvestigationOpsTasks,
                                                mock_psycopg_pool: ConnectionPool,
                                                icat_client: ICATClient,
                                                datacite_client_mock: DataciteClient,
                                                investigation_with_future_end_date: InvestigationOperationsContext) -> None:
        with pytest.raises(Exception) as exc_info:
            investigation_ops_tasks.mint_proposal(
                mock_psycopg_pool, icat_client, datacite_client_mock, investigation_with_future_end_date)
        assert "has an end date in the future, it will not be minted" in str(exc_info.value)

    def test_mint_investigation(self, investigation_ops_tasks: InvestigationOpsTasks,
                                mock_psycopg_pool: ConnectionPool,
                                icat_client: ICATClient,
                                datacite_client_mock: DataciteClient,
                                investigation_good_for_doi: InvestigationOperationsContext) -> None:
        investigation_ops_tasks.mint_proposal(
            mock_psycopg_pool, icat_client, datacite_client_mock, investigation_good_for_doi)

        investigation: Entity = icat_client.search("Investigation",
                                                   conditions={"name__eq": investigation_good_for_doi.name},
                                                   flatten_single=True)
        assert investigation.doi is not None

        calls: list = mock_psycopg_pool.connection.return_value.__enter__.return_value.cursor.return_value.__enter__.return_value.execute.call_args_list
        sql_statements: list = [call.args[0] for call in calls]

        has_insert = any("UPDATE" in sql.upper() for sql in sql_statements)
        assert has_insert, "No INSERT statements executed"
